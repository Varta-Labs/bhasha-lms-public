<template>
	<SkeletonLoader
		v-if="!courseResource.doc"
		variant="form"
		class="flex-1 min-h-0"
	/>
	<div
		v-else
		class="course-settings grid grid-cols-1 md:grid-cols-[70%,30%] flex-1 min-h-0"
	>
		<div class="course-settings__main overflow-y-auto">
			<header class="course-settings__intro">
				<p>{{ __('Course setup') }}</p>
				<h2>{{ __('Settings') }}</h2>
				<span>{{
					__(
						'Shape how this course looks, who can discover it, and how learners enroll.',
					)
				}}</span>
			</header>
			<div class="course-settings__form-card">
				<CourseDetailsSection />
				<CourseOverviewSection />
			</div>
		</div>
		<aside class="course-settings__aside overflow-y-auto">
			<div class="course-settings__aside-heading">
				<p>{{ __('Publishing') }}</p>
				<span>{{ __('Visibility, pricing, and certificates') }}</span>
			</div>
			<CoursePublishSettings />
		</aside>
	</div>
</template>

<script setup lang="ts">
import { createResource, createDocumentResource, toast } from 'frappe-ui'
import {
	computed,
	getCurrentInstance,
	inject,
	onBeforeUnmount,
	onMounted,
	provide,
	reactive,
	ref,
	watch,
} from 'vue'
import { useRouter } from 'vue-router'
import { getMetaInfo, updateMetaInfo } from '@/utils'
import { exportCourseAsZip } from '@/utils/exportCourse'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import CourseDetailsSection from '@/pages/Courses/CourseDetailsSection.vue'
import CourseOverviewSection from '@/pages/Courses/CourseOverviewSection.vue'
import CoursePublishSettings from '@/pages/Courses/CoursePublishSettings.vue'
import type { LMSCourse } from '@/types/lms/LMSCourse'
import type { CourseInstructor } from '@/types/lms/CourseInstructor'
import type { RelatedCourses as RelatedCoursesRow } from '@/types/lms/RelatedCourses'
import type {
	CourseDetails,
	CourseFormContext,
	CourseFormMeta,
	Resource,
	SessionUser,
} from '@/types/api'

interface DialogAction {
	label: string
	theme?: string
	variant?: string
	onClick: (close: () => void) => void
}
type DialogFn = (opts: {
	title: string
	message: string
	actions: DialogAction[]
}) => void

interface CourseMenuItem {
	label: string
	icon: string
	theme?: string
	onClick: () => void
}

const props = defineProps<{
	course: Resource<CourseDetails | null>
}>()

const user = inject<SessionUser>('$user')!
const router = useRouter()
const app = getCurrentInstance()!
const { $dialog } = app.appContext.config.globalProperties as {
	$dialog: DialogFn
}

const isDirty = ref<boolean>(false)
const instructors = ref<string[]>([])
const related_courses = ref<string[]>([])
const meta = reactive<CourseFormMeta>({ description: '', keywords: '' })

const courseResource = createDocumentResource({
	doctype: 'LMS Course',
	name: props.course.data?.name,
	auto: true,
}) as Resource<LMSCourse | null>

const markDirty = (): void => {
	isDirty.value = true
}

const courseFormContext: CourseFormContext = {
	resource: courseResource,
	instructors,
	relatedCourses: related_courses,
	meta,
	markDirty,
}
provide<CourseFormContext>('courseForm', courseFormContext)

onMounted(() => {
	if (!user.data?.is_moderator && !user.data?.is_instructor) {
		router.push({ name: 'Courses' })
	}
	window.addEventListener('keydown', keyboardShortcut)
})

onBeforeUnmount(() => {
	window.removeEventListener('keydown', keyboardShortcut)
})

watch(
	() => courseResource.doc,
	() => {
		// A failed/empty fetch still fires this watch; the body assumes a
		// loaded doc.
		if (!courseResource.doc) return
		getMetaInfo('courses', courseResource.doc?.name, meta)
		updateCourseData()
		checkPermission()
	},
)

const updateCourseData = (): void => {
	const doc = courseResource.doc
	if (!doc) return
	Object.keys(doc).forEach((key) => {
		if (key === 'instructors') {
			instructors.value = []
			doc.instructors?.forEach((i: CourseInstructor) => {
				if (i.instructor) instructors.value.push(i.instructor)
			})
		} else if (key === 'related_courses') {
			related_courses.value = []
			doc.related_courses?.forEach((c: RelatedCoursesRow) => {
				if (c.course) related_courses.value.push(c.course)
			})
		}
	})
	const checkboxes: (keyof LMSCourse)[] = [
		'published',
		'upcoming',
		'disable_self_learning',
		'paid_course',
		'featured',
		'enable_certification',
		'paid_certificate',
	]
	for (const key of checkboxes) {
		;(doc as Record<string, unknown>)[key] = doc[key] ? true : false
	}
}

const submitCourse = (): void => updateCourse()

const updateCourse = (): void => {
	courseResource.setValue.submit(
		{
			...courseResource.doc,
			instructors: instructors.value.map((i) => ({ instructor: i })),
			related_courses: related_courses.value.map((c) => ({ course: c })),
		},
		{
			onSuccess() {
				updateMetaInfo('courses', courseResource.doc?.name, meta)
				toast.success(__('Course updated successfully'))
				isDirty.value = false
				courseResource.reload()
			},
			onError(err: { messages?: string[] } | string) {
				const msg =
					typeof err === 'string' ? err : (err.messages?.[0] ?? 'Error')
				toast.error(msg)
				console.error(err)
			},
		},
	)
}

const keyboardShortcut = (e: KeyboardEvent): void => {
	if (
		e.key === 's' &&
		(e.ctrlKey || e.metaKey) &&
		!(e.target as HTMLElement | null)?.classList.contains('ProseMirror')
	) {
		submitCourse()
		e.preventDefault()
	}
}

const deleteCourse = createResource({
	url: 'lms.lms.api.delete_course',
	makeParams() {
		return { course: courseResource.doc?.name }
	},
	onSuccess() {
		toast.success(__('Course deleted successfully'))
		router.push({ name: 'Courses' })
	},
}) as Resource<unknown>

const trashCourse = (): void => {
	$dialog({
		title: __('Delete Course'),
		message: __(
			'Deleting the course will also delete all its chapters and lessons. Are you sure you want to delete this course?',
		),
		actions: [
			{
				label: __('Delete'),
				theme: 'red',
				variant: 'solid',
				onClick(close) {
					deleteCourse.submit()
					close()
				},
			},
		],
	})
}

const courseMenu = computed<CourseMenuItem[]>(() => [
	{
		label: __('Export'),
		icon: 'lucide-download',
		onClick: () => exportCourseAsZip(courseResource.doc?.name),
	},
	{
		label: __('Delete'),
		icon: 'lucide-trash-2',
		theme: 'red',
		onClick: () => trashCourse(),
	},
])

const checkPermission = (): void => {
	if (user.data?.is_moderator) return
	const isInstructor = instructors.value?.some(
		(i: string) => i == user.data?.name,
	)
	if (!isInstructor) router.push({ name: 'Courses' })
}

defineExpose({ isDirty, submitCourse, trashCourse, courseMenu })
</script>

<style scoped>
.course-settings {
	background: #faf9fc;
}

.course-settings__main {
	padding: clamp(1.25rem, 3vw, 2rem);
}

.course-settings__intro {
	margin: 0 auto 1.25rem;
	max-width: 58rem;
}

.course-settings__intro p,
.course-settings__aside-heading p {
	color: #4a38c2;
	font-size: 0.72rem;
	font-weight: 800;
	letter-spacing: 0.1em;
	text-transform: uppercase;
}

.course-settings__intro h2 {
	margin-top: 0.3rem;
	color: #171717;
	font-family: var(--bhasha-font-display);
	font-size: clamp(1.8rem, 3vw, 2.35rem);
	font-weight: 800;
	letter-spacing: -0.03em;
	line-height: 1.15;
}

.course-settings__intro span,
.course-settings__aside-heading span {
	display: block;
	margin-top: 0.4rem;
	color: #7c7c7c;
	font-size: 0.8125rem;
	line-height: 1.55;
}

.course-settings__form-card {
	max-width: 58rem;
	margin-inline: auto;
	padding: clamp(1.25rem, 3vw, 2rem);
	border: 1px solid #e7e2ec;
	border-radius: 1.35rem;
	background: #fff;
	box-shadow: 0 12px 34px rgba(44, 31, 69, 0.05);
}

.course-settings__aside {
	border-inline-start: 1px solid #e7e2ec;
	background:
		linear-gradient(180deg, rgba(108, 92, 231, 0.06), transparent 9rem), #fff;
}

.course-settings__aside-heading {
	padding: 1.5rem 1.25rem 1rem;
	border-bottom: 1px solid #eeeaf1;
}

@media (max-width: 767px) {
	.course-settings {
		overflow-y: auto;
	}

	.course-settings__main {
		overflow: visible;
		padding: 1rem;
	}

	.course-settings__aside {
		overflow: visible;
		border-inline-start: 0;
		border-top: 1px solid #e7e2ec;
	}
}
</style>
