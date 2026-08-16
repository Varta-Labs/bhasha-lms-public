<template>
	<Dialog
		v-model="show"
		:options="{
			title: __('Progress Summary for {0}').format(programName),
			size: '2xl',
		}"
	>
		<template #body-title>
			<div class="bhasha-dialog-heading">
				<div class="bhasha-dialog-icon" aria-hidden="true">
					<TrendingUp class="size-5 stroke-1.75" />
				</div>
				<div>
					<h3 class="bhasha-dialog-title">{{ __('Program progress') }}</h3>
					<p class="bhasha-dialog-description">
						{{
							__('A snapshot of enrollment and completion for {0}.').format(
								programName,
							)
						}}
					</p>
				</div>
			</div>
		</template>
		<template #body-content>
			<div class="bhasha-program-progress-summary text-base">
				<div class="bhasha-program-progress-stats">
					<NumberChart
						class="bhasha-program-progress-stat"
						:config="{
							title: __('Enrollments'),
							value: programMembers.length || 0,
						}"
					/>
					<NumberChart
						class="bhasha-program-progress-stat"
						:config="{
							title: __('Average Progress %'),
							value: averageProgress || 0,
						}"
					/>
				</div>
				<DonutChart
					:config="{
						data: progressDistribution || [],
						title: __('Progress Distribution'),
						categoryColumn: 'category',
						valueColumn: 'count',
						colors: [
							getColor('red', 400),
							getColor('amber', 400),
							getColor('pink', 400),
							getColor('blue', 400),
							getColor('green', 400),
						],
					}"
				/>

				<div class="bhasha-program-progress-members">
					<FormControl
						v-model="searchFilter"
						:placeholder="__('Search by Member')"
						class="mb-4"
						size="md"
						variant="outline"
					/>
					<ListView
						v-if="progressList.length"
						:columns="progressColumns"
						:rows="progressList"
						rowKey="name"
						:options="{
							selectable: false,
							showTooltip: false,
						}"
					/>
					<div v-else class="bhasha-program-progress-empty">
						{{ __('No members found.') }}
					</div>
				</div>
			</div>
		</template>
	</Dialog>
</template>
<script setup lang="ts">
import {
	Dialog,
	DonutChart,
	FormControl,
	ListView,
	NumberChart,
} from 'frappe-ui'
import type { ProgramMember } from '@/types'
import { computed, ref, watch } from 'vue'
import { getColor } from '@/utils'
import { TrendingUp } from 'lucide-vue-next'

const show = defineModel<boolean>({ default: false })
const searchFilter = ref<string | null>(null)

const props = defineProps<{
	programName: string
	programMembers: ProgramMember[]
}>()

const progressList = ref<ProgramMember[]>(props.programMembers || [])

const progressDistribution = computed(() => {
	const categories = ['0-20%', '20-40%', '40-60%', '60-80%', '80-100%']
	const distribution = categories.map((category) => {
		const [min, max] = category.slice(0, -1).split('-').map(Number)
		return {
			category,
			count: props.programMembers.filter((member) => {
				const progress = member.progress || 0
				return progress >= min && progress < max
			}).length,
		}
	})
	return distribution
})

const averageProgress = computed(() => {
	if (props.programMembers.length === 0) return 0
	const totalProgress = props.programMembers.reduce(
		(sum, member) => sum + (member.progress || 0),
		0,
	)
	return totalProgress / props.programMembers.length
})

watch(searchFilter, () => {
	if (searchFilter.value) {
		progressList.value = props.programMembers.filter((member) =>
			member.full_name
				.toLowerCase()
				.includes(searchFilter.value?.toLowerCase()),
		)
	} else {
		progressList.value = props.programMembers
	}
})

const progressColumns = computed(() => {
	return [
		{
			label: __('Member'),
			key: 'full_name',
			width: '50%',
		},
		{
			label: __('Progress (%)'),
			key: 'progress',
			align: 'right',
		},
	]
})
</script>
