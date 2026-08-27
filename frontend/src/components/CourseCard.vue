<template>
	<div
		v-if="course.title"
		class="bhasha-course-card flex h-full flex-col overflow-hidden bg-surface-cards text-ink-gray-9"
	>
		<div class="bhasha-course-card-media">
			<img
				v-if="course.image && !thumbnailFailed"
				:src="course.image"
				:alt="course.title"
				class="bhasha-course-card-image"
				loading="lazy"
				@error="handleThumbnailError"
			/>
			<div v-else class="bhasha-course-card-fallback">
				<BookOpen class="size-8 stroke-1.5" aria-hidden="true" />
				<span>{{ course.category || __('Course') }}</span>
			</div>
			<div
				v-if="
					course.featured ||
					course.upcoming ||
					course.published === 0 ||
					course.membership
				"
				class="bhasha-course-card-badges"
			>
				<div
					v-if="course.featured"
					class="bhasha-course-card-badge is-featured"
				>
					<Award class="size-3.5 stroke-2" aria-hidden="true" />
					{{ __('Featured') }}
				</div>
				<div
					v-if="course.upcoming"
					class="bhasha-course-card-badge is-upcoming"
				>
					<Clock class="size-3.5 stroke-2" aria-hidden="true" />
					{{ __('Upcoming') }}
				</div>
				<div
					v-else-if="course.published === 0"
					class="bhasha-course-card-badge is-draft"
				>
					<FileText class="size-3.5 stroke-2" aria-hidden="true" />
					{{ __('Draft') }}
				</div>
				<div
					v-if="course.membership"
					class="bhasha-course-card-badge is-enrolled"
				>
					<Check class="size-3.5 stroke-2" aria-hidden="true" />
					{{ __('Enrolled') }}
				</div>
			</div>
		</div>

		<div class="flex flex-auto flex-col p-5">
			<div
				v-if="course.category"
				class="bhasha-course-card-category mb-2 text-xs font-semibold uppercase tracking-wide"
			>
				{{ course.category }}
			</div>

			<div class="bhasha-course-card-title text-lg font-semibold leading-6">
				{{ course.title }}
			</div>

			<div v-if="course.short_introduction" class="short-introduction text-sm">
				{{ course.short_introduction }}
			</div>

			<div
				v-if="course.lessons || course.enrollments || course.rating"
				class="bhasha-course-card-stats"
			>
				<div v-if="course.lessons">
					<Tooltip :text="__('Lessons')">
						<span class="flex items-center">
							<BookOpen class="bhasha-card-stat-icon h-4 w-4 stroke-1.5 me-1" />
							{{ course.lessons }}
						</span>
					</Tooltip>
				</div>

				<div v-if="course.enrollments">
					<Tooltip :text="__('Enrolled Students')">
						<span class="flex items-center">
							<Users class="bhasha-card-stat-icon h-4 w-4 stroke-1.5 me-1" />
							{{ formatAmount(course.enrollments) }}
						</span>
					</Tooltip>
				</div>

				<div v-if="course.rating">
					<Tooltip :text="__('Average Rating')">
						<span class="flex items-center">
							<Star class="bhasha-card-stat-icon h-4 w-4 stroke-1.5 me-1" />
							{{ formatRating(course.rating) }}
						</span>
					</Tooltip>
				</div>
			</div>

			<ProgressBar
				v-if="user && course.membership"
				:progress="course.membership.progress"
				class="bhasha-course-card-progress mt-4"
			/>

			<div
				v-if="user && course.membership"
				class="mb-4 mt-2 text-xs text-ink-gray-6"
			>
				{{ Math.ceil(course.membership.progress) }}% {{ __('completed') }}
			</div>

			<div
				class="mt-auto flex flex-wrap items-center justify-between gap-3 pt-4"
			>
				<div
					v-if="course.instructors?.length"
					class="avatar-group overlap min-w-0 text-sm"
				>
					<div
						class="h-6 me-1"
						:class="{ 'avatar-group overlap': course.instructors.length > 1 }"
					>
						<UserAvatar
							v-for="instructor in course.instructors"
							:key="instructor.username || instructor.full_name"
							:user="instructor"
						/>
					</div>
					<CourseInstructors
						:instructors="course.instructors"
						:linkable="false"
					/>
				</div>

				<div class="flex shrink-0 items-center gap-x-2">
					<div v-if="course.paid_course" class="flex items-baseline gap-2 font-semibold">
						<span>{{ course.price }}</span>
						<s v-if="hasEarlyBirdOffer" class="text-xs font-medium text-ink-gray-5">₹2,999</s>
					</div>

					<div
						v-if="course.paid_certificate || course.enable_certification"
						class="bhasha-course-card-certificate"
					>
						<GraduationCap class="size-4 stroke-1.5" aria-hidden="true" />
						<span>{{ __('Certificate') }}</span>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>
<script setup>
import {
	Award,
	BookOpen,
	Check,
	Clock,
	FileText,
	GraduationCap,
	Star,
	Users,
} from 'lucide-vue-next'
import { sessionStore } from '@/stores/session'
import { Tooltip } from 'frappe-ui'
import { formatAmount, formatRating } from '@/utils'
import { computed, ref, watch } from 'vue'
import CourseInstructors from '@/components/CourseInstructors.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import ProgressBar from '@/components/ProgressBar.vue'

const { user } = sessionStore()

const props = defineProps({
	course: {
		type: Object,
		default: null,
	},
})

const thumbnailFailed = ref(false)

const handleThumbnailError = () => {
	thumbnailFailed.value = true
}

const hasEarlyBirdOffer = computed(() => {
	const identity = `${props.course?.name || ''} ${props.course?.title || ''}`.toLowerCase()
	return Boolean(props.course?.paid_course && (identity.includes('hindi') || identity.includes('kannada')))
})

watch(
	() => props.course?.image,
	() => {
		thumbnailFailed.value = false
	},
)
</script>
<style>
.course-card-pills {
	background: #ffffff;
	margin-left: 0;
	margin-right: 0.5rem;
	padding: 3.5px 8px;
	font-size: 11px;
	text-align: center;
	letter-spacing: 0.011em;
	text-transform: uppercase;
	font-weight: 600;
	width: fit-content;
}

.avatar-group {
	display: inline-flex;
	align-items: center;
}

.avatar-group .avatar {
	transition: margin 0.1s ease-in-out;
}

.avatar-group.overlap .avatar + .avatar {
	margin-inline-start: calc(-8px);
}

.short-introduction {
	display: -webkit-box;
	-webkit-line-clamp: 2;
	-webkit-box-orient: vertical;
	text-overflow: ellipsis;
	width: 100%;
	overflow: hidden;
	margin: 0.4rem 0 1rem;
	line-height: 1.5;
}
</style>
