<template>
	<div class="bhasha-batch-card">
		<div class="bhasha-batch-card-accent" aria-hidden="true"></div>
		<div class="bhasha-batch-card-body">
			<div class="bhasha-batch-card-topline">
				<div v-if="batch.category" class="bhasha-batch-card-category">
					{{ batch.category }}
				</div>
				<div class="bhasha-batch-card-badges">
					<span class="bhasha-batch-card-status" :class="statusClass">
						{{ statusLabel }}
					</span>
					<span
						v-if="batch.seat_count && batch.seats_left <= 0"
						class="bhasha-batch-card-status is-sold-out"
					>
						{{ __('Sold out') }}
					</span>
				</div>
			</div>

			<h2 class="bhasha-batch-card-title">{{ batch.title }}</h2>
			<p v-if="batch.description" class="bhasha-batch-card-description">
				{{ batch.description }}
			</p>

			<div class="bhasha-batch-card-schedule">
				<DateRange
					:startDate="batch.start_date"
					:endDate="batch.end_date"
					class="bhasha-batch-card-meta"
				/>
				<div class="bhasha-batch-card-meta">
					<Clock class="size-4 shrink-0 stroke-1.5" />
					<span dir="ltr">
						{{ formatTime(batch.start_time) }}–{{ formatTime(batch.end_time) }}
					</span>
				</div>
				<div v-if="batch.timezone" class="bhasha-batch-card-meta">
					<Globe class="size-4 shrink-0 stroke-1.5" />
					<span class="truncate">{{ batch.timezone }}</span>
				</div>
			</div>

			<div class="bhasha-batch-card-details">
				<div
					v-if="batch.seat_count && batch.seats_left > 0"
					class="bhasha-batch-card-detail is-available"
				>
					<Armchair class="size-4 stroke-1.5" />
					{{ batch.seats_left }}
					{{ batch.seats_left === 1 ? __('seat left') : __('seats left') }}
				</div>
				<div v-if="batch.certification" class="bhasha-batch-card-detail">
					<GraduationCap class="size-4 stroke-1.5" />
					{{ __('Certificate') }}
				</div>
				<div v-if="batch.amount" class="bhasha-batch-card-price">
					{{ batch.price }}
				</div>
			</div>

			<div class="bhasha-batch-card-footer">
				<div
					v-if="batch.instructors?.length"
					class="bhasha-batch-card-instructors avatar-group overlap"
				>
					<div
						class="h-6 me-1"
						:class="{ 'avatar-group overlap': batch.instructors.length > 1 }"
					>
						<UserAvatar
							v-for="instructor in batch.instructors"
							:key="instructor.username || instructor.full_name"
							:user="instructor"
						/>
					</div>
					<CourseInstructors
						:instructors="batch.instructors"
						:linkable="false"
					/>
				</div>
				<div v-else class="text-xs text-ink-gray-5">{{ __('Cohort') }}</div>
				<ArrowUpRight class="size-4 shrink-0 stroke-1.75" aria-hidden="true" />
			</div>
		</div>
	</div>
</template>
<script setup>
import { formatTime } from '@/utils'
import {
	Armchair,
	ArrowUpRight,
	Clock,
	Globe,
	GraduationCap,
} from 'lucide-vue-next'
import DateRange from '@/components/Common/DateRange.vue'
import CourseInstructors from '@/components/CourseInstructors.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import { computed, inject } from 'vue'

const props = defineProps({
	batch: {
		type: Object,
		default: null,
	},
})

const dayjs = inject('$dayjs')
const today = dayjs().format('YYYY-MM-DD')

const status = computed(() => {
	if (props.batch?.published === 0) return 'draft'
	if (props.batch?.end_date && props.batch.end_date < today) return 'archived'
	if (props.batch?.start_date && props.batch.start_date > today)
		return 'upcoming'
	return 'active'
})

const statusLabel = computed(() => {
	const labels = {
		draft: __('Draft'),
		archived: __('Archived'),
		upcoming: __('Upcoming'),
		active: __('Active'),
	}
	return labels[status.value]
})

const statusClass = computed(() => `is-${status.value}`)
</script>
