<template>
	<LayoutHeader>
		<template #left-header>
			<Breadcrumbs :items="breadcrumbs" />
		</template>
		<template #right-header>
			<Button
				v-if="!readOnlyMode"
				variant="solid"
				class="bhasha-primary bhasha-assessment-create-button"
				@click="
					() => {
						assignmentID = 'new'
						showAssignmentForm = true
					}
				"
			>
				<template #prefix>
					<Plus class="size-4 stroke-2" />
				</template>
				{{ __('Create assignment') }}
			</Button>
		</template>
	</LayoutHeader>

	<main class="bhasha-assessments-page flex min-h-0 flex-1 flex-col">
		<section class="bhasha-assessments-toolbar">
			<div class="bhasha-assessments-toolbar-heading">
				<div>
					<h1 class="bhasha-assessments-title">
						{{ __('Manage assignments') }}
					</h1>
					<p class="bhasha-assessments-description">
						{{
							__(
								'Create practical work, define how learners submit it, and review responses.',
							)
						}}
					</p>
				</div>
				<div
					v-if="!assignments.list.loading && assignments.data?.length"
					class="bhasha-assessment-result-count"
					aria-live="polite"
				>
					{{ assignments.data.length }}{{ assignments.hasNextPage ? '+' : '' }}
					{{
						assignments.data.length === 1
							? __('assignment')
							: __('assignments')
					}}
				</div>
			</div>
			<div class="bhasha-assessment-filters">
				<FormControl
					type="text"
					v-model="titleFilter"
					:placeholder="__('Search assignments')"
					size="md"
					variant="outline"
					class="bhasha-assessment-search"
				>
					<template #prefix>
						<Search class="size-4 stroke-1.5 text-ink-gray-5" />
					</template>
					<template v-if="titleFilter" #suffix>
						<button
							type="button"
							class="bhasha-assessment-search-clear"
							:aria-label="__('Clear search')"
							@click="titleFilter = ''"
						>
							<X class="size-3.5 stroke-2" />
						</button>
					</template>
				</FormControl>
				<Select
					v-model="typeFilter"
					:options="assignmentTypes"
					:placeholder="__('All submission types')"
					size="md"
					variant="outline"
					class="bhasha-assessment-type-filter"
				/>
				<button
					v-if="hasActiveFilters"
					type="button"
					class="bhasha-assessment-clear-filters"
					@click="resetFilters"
				>
					<X class="size-3.5 stroke-2" />
					{{ __('Clear filters') }}
				</button>
			</div>
		</section>
		<section
			v-if="assignments.data?.length"
			class="bhasha-assessment-list-shell"
		>
			<ListView
				:columns="assignmentColumns"
				:rows="assignments.data"
				row-key="name"
				:options="{
					showTooltip: false,
					selectable: true,
					onRowClick: (row) => {
						if (readOnlyMode) return
						assignmentID = row.name
						showAssignmentForm = true
					},
				}"
				class="bhasha-assessment-list flex-1"
			>
				<ListHeader class="bhasha-assessment-list-header grid items-center p-2">
					<ListHeaderItem :item="item" v-for="item in assignmentColumns">
						<template #prefix="{ item }">
							<FeatherIcon
								:name="item.icon?.toString()"
								class="h-4 w-4"
							/>
						</template>
					</ListHeaderItem>
				</ListHeader>
				<ListRows>
					<ListRow
						v-for="row in assignments.data"
						:key="row.name"
						:row="row"
						class="bhasha-assessment-list-row"
					>
						<template #default="{ column }">
							<ListRowItem :item="row[column.key]" :align="column.align">
								<div
									v-if="column.key == 'type'"
									class="bhasha-assessment-type-badge"
								>
									{{ row[column.key] }}
								</div>
								<div
									v-else-if="column.key == 'modified'"
									class="text-sm text-ink-gray-5"
								>
									{{ row[column.key] }}
								</div>
								<div v-else>
									{{ row[column.key] }}
								</div>
							</ListRowItem>
						</template>
					</ListRow>
				</ListRows>
				<ListSelectBanner class="bottom-50">
					<template #actions="{ unselectAll, selections }">
						<div class="flex gap-2">
							<Button
								variant="ghost"
								@click="deleteAssignment(selections, unselectAll)"
							>
								<FeatherIcon name="trash-2" class="h-4 w-4 stroke-1.5" />
							</Button>
						</div>
					</template>
				</ListSelectBanner>
			</ListView>
		</section>
		<section
			v-else-if="!assignments.list.loading"
			class="bhasha-assessments-empty"
		>
			<div class="bhasha-assessments-empty-icon">
				<ClipboardPenLine class="size-6 stroke-1.5" />
			</div>
			<h2>
				{{
					hasActiveFilters
						? __('No matching assignments')
						: __('Create your first assignment')
				}}
			</h2>
			<p>
				{{
					hasActiveFilters
						? __('Try a different title or submission type.')
						: __('Give learners practical work and choose the format they should submit.')
				}}
			</p>
			<Button v-if="hasActiveFilters" class="mt-2" @click="resetFilters">
				{{ __('Clear filters') }}
			</Button>
			<Button
				v-else-if="!readOnlyMode"
				variant="solid"
				class="bhasha-primary mt-2"
				@click="openNewAssignment"
			>
				<template #prefix><Plus class="size-4 stroke-2" /></template>
				{{ __('Create assignment') }}
			</Button>
		</section>
		<ListFooter
			v-model="pageLength"
			v-if="assignments.data?.length"
			class="bhasha-assessment-footer"
			:options="{
				rowCount: assignments.data?.length,
				totalCount: totalAssignments.data,
			}"
		>
			<template #right>
				<div class="flex items-center">
					<Button
						v-if="assignments.hasNextPage"
						:label="__('Load More')"
						@click="assignments.next()"
					/>
					<div v-if="assignments.hasNextPage" class="mx-3 h-[80%] border-l" />
					<div class="flex items-center gap-1 text-base text-ink-gray-5">
						<div>{{ assignments.data?.length || 0 }}</div>
						<div>{{ __('of') }}</div>
						<div>{{ totalAssignments.data || 0 }}</div>
					</div>
				</div>
			</template>
		</ListFooter>
	</main>
	<AssignmentForm
		v-model="showAssignmentForm"
		v-model:assignments="assignments"
		:assignmentID="assignmentID"
	/>
</template>
<script setup>
import {
	Breadcrumbs,
	Button,
	createListResource,
	createResource,
	ListView,
	ListHeader,
	ListHeaderItem,
	ListRows,
	ListRow,
	ListRowItem,
	ListFooter,
	ListSelectBanner,
	FeatherIcon,
	toast,
	usePageMeta,
	FormControl,
} from 'frappe-ui'
import Select from '@/components/Controls/Select.vue'
import { computed, inject, onMounted, ref, watch } from 'vue'
import { ClipboardPenLine, Plus, Search, X } from 'lucide-vue-next'
import { useRouter, useRoute } from 'vue-router'
import { sessionStore } from '../stores/session'
import AssignmentForm from '@/components/Modals/AssignmentForm.vue'
import LayoutHeader from '@/components/Layouts/LayoutHeader.vue'
import '@/styles/assessment-management.css'

const user = inject('$user')
const dayjs = inject('$dayjs')
const titleFilter = ref('')
const typeFilter = ref('')
const showAssignmentForm = ref(false)
const assignmentID = ref('new')
const { brand } = sessionStore()
const router = useRouter()
const route = useRoute()
const readOnlyMode = window.read_only_mode
const hasActiveFilters = computed(
	() => Boolean(titleFilter.value) || Boolean(typeFilter.value?.trim()),
)

const resetFilters = () => {
	titleFilter.value = ''
	typeFilter.value = ''
}

const openNewAssignment = () => {
	assignmentID.value = 'new'
	showAssignmentForm.value = true
}

onMounted(() => {
	if (!user.data?.is_moderator && !user.data?.is_instructor) {
		router.push({ name: 'Courses' })
	}
	if (route.query.new === 'true') {
		assignmentID.value = 'new'
		showAssignmentForm.value = true
	}
	titleFilter.value = router.currentRoute.value.query.title
	typeFilter.value = router.currentRoute.value.query.type
})

watch([titleFilter, typeFilter], () => {
	router.push({
		query: {
			title: titleFilter.value,
			type: typeFilter.value,
		},
	})
	reloadAssignments()
	totalAssignments.update({
		filters: assignmentFilter.value,
	})
	totalAssignments.reload()
})

const reloadAssignments = () => {
	assignments.update({
		filters: assignmentFilter.value,
	})
	assignments.reload()
}

const assignmentFilter = computed(() => {
	let filters = {}
	if (titleFilter.value) {
		filters.title = ['like', `%${titleFilter.value}%`]
	}
	if (typeFilter.value && typeFilter.value.trim() !== '') {
		filters.type = typeFilter.value
	}
	return filters
})

const assignments = createListResource({
	doctype: 'LMS Assignment',
	fields: ['name', 'title', 'type', 'modified', 'question', 'course'],
	orderBy: 'modified desc',
	cache: ['assignments'],
	transform(data) {
		return data.map((row) => {
			return {
				...row,
				modified: dayjs(row.modified).format('DD MMM YYYY'),
			}
		})
	},
})

const pageLength = computed({
	get: () => assignments.pageLength,
	set: (value) => {
		assignments.update({ pageLength: value })
		assignments.reload()
	},
})

const totalAssignments = createResource({
	url: 'frappe.client.get_count',
	params: {
		doctype: 'LMS Assignment',
		filters: assignmentFilter.value,
	},
	auto: true,
	cache: ['assignments_count', user.data?.name],
	onError(err) {
		toast.error(err.messages?.[0] || err)
		console.error(err)
	},
})

const assignmentColumns = computed(() => {
	return [
		{
			label: __('Title'),
			key: 'title',
			width: 1,
			icon: 'file-text',
		},
		{
			label: __('Type'),
			key: 'type',
			width: 1,
			align: 'left',
			icon: 'tag',
		},
		{
			label: __('Updated On'),
			key: 'modified',
			width: 1,
			align: 'right',
			icon: 'clock',
		},
	]
})

const assignmentTypes = computed(() => {
	let types = [' ', 'Document', 'Image', 'PDF', 'URL', 'Text']
	return types.map((type) => {
		return {
			label: __(type),
			value: type,
		}
	})
})

const deleteAssignment = (selections, unselectAll) => {
	Array.from(selections).forEach(async (assignmentName) => {
		await assignments.delete.submit(assignmentName)
	})
	unselectAll()
	toast.success(__('Assignments deleted successfully'))
}

const breadcrumbs = computed(() => [
	{
		label: __('Assignments'),
		route: { name: 'Assignments' },
	},
])

usePageMeta(() => {
	return {
		title: __('Assignments'),
		icon: brand.favicon,
	}
})
</script>
