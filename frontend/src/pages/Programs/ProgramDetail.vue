<template>
	<LayoutHeader>
		<template #left-header>
			<Breadcrumbs :items="breadcrumbs" />
		</template>
	</LayoutHeader>
	<main v-if="program.data" class="bhasha-program-detail-page">
		<section class="bhasha-program-detail-hero">
			<div class="bhasha-program-detail-identity">
				<div class="bhasha-program-detail-icon" aria-hidden="true">
					<BookOpen class="size-6 stroke-1.5" />
				</div>
				<div>
					<span class="bhasha-program-detail-kicker">{{
						__('Learning program')
					}}</span>
					<h1>{{ program.data.name }}</h1>
					<p>
						{{
							__('A guided path with {0} courses.').format(
								program.data.courses?.length || 0,
							)
						}}
					</p>
				</div>
			</div>
			<div class="bhasha-program-detail-progress-card">
				<div class="bhasha-program-detail-progress-label">
					<span>{{ __('Your progress') }}</span>
					<strong>{{ Math.ceil(program.data.progress || 0) }}%</strong>
				</div>
				<div
					class="bhasha-program-detail-progress-track"
					role="progressbar"
					:aria-label="__('Program progress')"
					:aria-valuenow="Math.ceil(program.data.progress || 0)"
					aria-valuemin="0"
					aria-valuemax="100"
				>
					<span
						:style="{ width: `${Math.min(program.data.progress || 0, 100)}%` }"
					/>
				</div>
				<Tooltip
					v-if="program.data.enforce_course_order"
					placement="bottom"
					:text="
						__(
							'Courses must be completed in order. You can only start the next course after completing the previous one.',
						)
					"
				>
					<span class="bhasha-program-order-note">
						<Info class="size-3.5 stroke-1.5" />
						{{ __('Courses unlock in order') }}
					</span>
				</Tooltip>
			</div>
		</section>

		<section class="bhasha-program-detail-courses">
			<div class="bhasha-program-detail-section-heading">
				<h2>{{ __('Your learning path') }}</h2>
				<p>{{ __('Complete each course to move through this program.') }}</p>
			</div>
			<div class="bhasha-program-detail-grid">
				<div
					v-for="course in program.data.courses"
					:key="course.name"
					class="relative group"
					:class="
						(course.eligible && program.data.enforce_course_order) ||
						!program.data.enforce_course_order
							? 'cursor-pointer'
							: 'cursor-default'
					"
				>
					<CourseCard
						:course="course"
						@click="openCourse(course, program.data.enforce_course_order)"
					/>
					<div
						v-if="!course.eligible && program.data.enforce_course_order"
						class="bhasha-program-course-lock absolute inset-0 invisible group-hover:visible"
					>
						<LockKeyhole class="size-5" />
						<span>{{
							__('Please complete the previous course to unlock this one.')
						}}</span>
					</div>
				</div>
			</div>
		</section>
	</main>
</template>
<script setup lang="ts">
import { computed, inject, onMounted } from 'vue'
import {
	Breadcrumbs,
	call,
	createResource,
	Tooltip,
	usePageMeta,
} from 'frappe-ui'
import { sessionStore } from '@/stores/session'
import { BookOpen, LockKeyhole, Info } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import CourseCard from '@/components/CourseCard.vue'
import LayoutHeader from '@/components/Layouts/LayoutHeader.vue'
import '@/styles/program-management.css'

const { brand } = sessionStore()
const router = useRouter()
const user = inject<any>('$user')

const props = defineProps<{
	programName: string
}>()

onMounted(() => {
	checkIfEnrolled()
})

const checkIfEnrolled = () => {
	call('frappe.client.get_value', {
		doctype: 'LMS Program Member',
		filters: {
			member: user.data.name,
			parent: props.programName,
		},
		parent: 'LMS Program',
		fieldname: 'name',
	}).then((data: { name: string }) => {
		if (data.name) {
			program.reload()
		} else {
			router.push({ name: 'Programs' })
		}
	})
}

const program = createResource({
	url: 'lms.lms.utils.get_program_details',
	params: {
		program_name: props.programName,
	},
})

const openCourse = (course: any, enforceCourseOrder: boolean) => {
	if (!course.eligible && enforceCourseOrder) return
	router.push({
		name: 'CourseDetail',
		params: { courseName: course.name },
	})
}

const breadcrumbs = computed(() => {
	return [
		{ label: __('Programs'), route: { name: 'Programs' } },
		{
			label: props.programName,
			route: {
				name: 'ProgramDetail',
				params: { programName: props.programName },
			},
		},
	]
})

usePageMeta(() => {
	return {
		title: props.programName,
		icon: brand.favicon,
	}
})
</script>
