<template>
	<div
		class="course-detail-shell flex h-full flex-col"
		:class="{ 'is-admin': isAdmin }"
	>
		<LayoutHeader
			v-if="!user.data || isAdmin || isMobile"
			:isLoading="!course.data"
			:variant="user.data ? 'product' : 'marketing'"
		>
			<template #left-header>
				<router-link
					v-if="!user.data"
					to="/"
					class="hidden sm:flex items-center gap-2 mr-4 py-1 hover:opacity-90 transition-opacity"
				>
					<LMSLogo class="h-7 sm:h-8 w-auto flex-shrink-0" />
				</router-link>
				<router-link v-if="isMobile" :to="{ name: 'Courses' }">
					<Button>
						<template #prefix>
							<ChevronLeft class="size-4 stroke-1.5" />
						</template>
						{{ __('Back to Courses') }}
					</Button>
				</router-link>
				<Badge v-if="isAdmin && course.data?.published" theme="green">
					{{ __('Published') }}
				</Badge>
			</template>
			<template #right-header>
				<div v-if="!user.data" class="flex items-center gap-2.5"></div>
				<template v-if="tabIndex === 3 && courseFormRef">
					<Badge v-if="courseFormRef.isDirty" theme="orange">
						{{ __('Not Saved') }}
					</Badge>
					<Dropdown
						:options="courseFormRef.courseMenu"
						:button="{ icon: 'lucide-ellipsis', variant: 'ghost' }"
						side="bottom"
						align="end"
					/>
					<Tooltip
						:text="courseFormRef.isDirty ? '' : __('No changes to save')"
						:hoverDelay="0.1"
					>
						<Button
							variant="solid"
							:disabled="!courseFormRef.isDirty"
							@click="courseFormRef.submitCourse()"
						>
							{{ __('Save') }}
						</Button>
					</Tooltip>
				</template>
				<template v-if="tabIndex === 2 && editorSelected">
					<template v-if="editorMode === 'edit'">
						<Badge v-if="courseEditorRef?.isDirty" theme="orange">
							{{ __('Not Saved') }}
						</Badge>
						<Tooltip
							:text="courseEditorRef?.isDirty ? '' : __('No changes to save')"
							:hoverDelay="0.1"
						>
							<Button
								variant="solid"
								:disabled="!courseEditorRef?.isDirty"
								@click="courseEditorRef?.saveSelectedLesson()"
							>
								{{ __('Save') }}
							</Button>
						</Tooltip>
					</template>
					<template v-else-if="editorMode === 'preview'">
						<Tooltip v-if="courseEditorRef?.canGoZen" :text="__('Zen Mode')">
							<Button @click="courseEditorRef?.previewZen()">
								<template #icon>
									<Focus class="size-4 stroke-2" />
								</template>
							</Button>
						</Tooltip>
						<Button
							v-if="courseEditorRef?.hasPrev"
							@click="courseEditorRef?.previewPrev()"
						>
							<template #prefix>
								<ChevronLeft class="size-4 stroke-1.5" />
							</template>
							{{ __('Previous') }}
						</Button>
						<Button
							v-if="courseEditorRef?.hasNext"
							@click="courseEditorRef?.previewNext()"
						>
							<template #suffix>
								<ChevronRight class="size-4 stroke-1.5" />
							</template>
							{{ __('Next') }}
						</Button>
					</template>
					<Button
						variant="outline"
						@click="editorMode = editorMode === 'preview' ? 'edit' : 'preview'"
					>
						<template #prefix>
							<X v-if="editorMode === 'preview'" class="size-4 stroke-1.5" />
							<Eye v-else class="size-4 stroke-1.5" />
						</template>
						{{ editorMode === 'preview' ? __('Close preview') : __('Preview') }}
					</Button>
				</template>
				<Button
					v-if="user.data?.is_moderator"
					:variant="course.data?.published ? 'subtle' : 'solid'"
					:theme="course.data?.published ? 'red' : 'gray'"
					:loading="publishToggle.loading"
					@click="togglePublishCourse"
				>
					{{ course.data?.published ? __('Unpublish') : __('Publish') }}
				</Button>
			</template>
		</LayoutHeader>

		<div v-if="!isAdmin" class="flex-1 min-h-0">
			<CourseMarketing v-if="!user.data" :course="course" />
			<CourseProductOverview v-else :course="course" />
		</div>
		<div
			v-else
			class="course-admin-workspace relative flex flex-1 min-h-0 flex-col"
		>
			<Tabs class="bhasha-secondary-tabs" :tabs="tabs" v-model="tabIndex">
				<template #tab-panel="{ tab }">
					<template v-if="course.data">
						<CourseEditor
							v-if="tab.component === CourseEditor"
							ref="courseEditorRef"
							:course="course"
							v-model:selected="editorSelected"
							v-model:mode="editorMode"
						/>
						<CourseForm
							v-else-if="tab.component === CourseForm"
							ref="courseFormRef"
							:course="course"
						/>
						<component v-else :is="tab.component" :course="course" />
					</template>
				</template>
			</Tabs>
			<div
				v-if="tabIndex === 2 && course.data && editorMode === 'edit'"
				class="pointer-events-none absolute inset-x-0 top-0 z-10 hidden md:flex"
			>
				<div class="w-[70%]" />
				<div
					class="course-editor-outline-header pointer-events-auto flex w-[30%] items-center justify-between gap-x-2 border-s border-b p-1 px-5"
				>
					<div class="py-2.5 font-medium text-base text-ink-gray-9">
						{{ __('Chapters') }}
					</div>
					<Button size="sm" @click="courseEditorRef?.openAddChapter()">
						<template #prefix>
							<Plus class="size-4 stroke-1.5" />
						</template>
						{{ __('Add') }}
					</Button>
				</div>
			</div>
		</div>
	</div>
</template>
<script setup lang="ts">
import { computed, inject, markRaw, onMounted, ref, watch } from 'vue'
import type { Component, ComputedRef, Ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { RouteLocationNormalizedLoadedGeneric, Router } from 'vue-router'
import {
	Badge,
	Button,
	createResource,
	Dropdown,
	Tabs,
	Tooltip,
	toast,
	usePageMeta,
} from 'frappe-ui'
import {
	BookOpen,
	ChevronLeft,
	ChevronRight,
	Eye,
	Focus,
	List,
	Plus,
	Settings2,
	TrendingUp,
	X,
} from 'lucide-vue-next'
import { sessionStore } from '@/stores/session'
import LayoutHeader from '@/components/Layouts/LayoutHeader.vue'
import LMSLogo from '@/components/Icons/LMSLogo.vue'
import CourseMarketing from '@/pages/Courses/CourseMarketing.vue'
import CourseProductOverview from '@/pages/Courses/CourseProductOverview.vue'
import CourseDashboard from '@/pages/Courses/CourseDashboard.vue'
import CourseEditor from '@/pages/Courses/CourseEditor.vue'
import CourseForm from '@/pages/Courses/CourseForm.vue'
import { getLmsRoute, getSignupUrl } from '@/utils/basePath'
import { useScreenSize } from '@/utils/composables'
import type {
	CourseDetails,
	CourseInstructorInfo,
	Resource,
	SessionUser,
} from '@/types/api'

type Brand = { name?: string; logo?: string; favicon?: string }
interface TabDef {
	label: string
	component: ReturnType<typeof markRaw>
	icon: Component
}

const { brand } = sessionStore() as { brand: Brand }
const router: Router = useRouter()
const route: RouteLocationNormalizedLoadedGeneric = useRoute()
const user = inject<SessionUser>('$user')!
const tabIndex: Ref<number> = ref(0)
const { isMobile } = useScreenSize()

interface EditorSelection {
	chapterNumber: string
	lessonNumber: string
	number: string
	title?: string
}

const editorSelected = ref<EditorSelection | null>(null)
const editorMode = ref<'edit' | 'preview'>('edit')

// Settings tab (CourseForm) exposes the API the LayoutHeader actions need.
type CourseMenuItem = {
	label: string
	icon: string
	theme?: string
	onClick: () => void
}
// `isDirty` is exposed as a Ref (defineExpose doesn't unwrap); `courseMenu`
// is a ComputedRef. Templates auto-unwrap both, but script-side access needs
// the wrapped types so callers don't accidentally truth-check a Ref object.
type CourseFormApi = {
	isDirty: Ref<boolean>
	submitCourse: () => void
	trashCourse: () => void
	courseMenu: ComputedRef<CourseMenuItem[]>
}
const courseFormRef = ref<CourseFormApi | null>(null)

type CourseEditorApi = {
	saveSelectedLesson: () => void
	isDirty: ComputedRef<boolean>
	hasPrev: ComputedRef<boolean>
	hasNext: ComputedRef<boolean>
	canGoZen: ComputedRef<boolean>
	previewPrev: () => void
	previewNext: () => void
	previewZen: () => void
	openAddChapter: () => void
}
const courseEditorRef = ref<CourseEditorApi | null>(null)

const publishToggle = createResource({
	url: 'frappe.client.set_value',
	makeParams() {
		return {
			doctype: 'LMS Course',
			name: course.data?.name,
			fieldname: 'published',
			value: course.data?.published ? 0 : 1,
		}
	},
	onSuccess() {
		toast.success(
			course.data?.published
				? __('Course unpublished')
				: __('Course published'),
		)
		course.reload()
	},
	onError(err: { messages?: string[] } | string) {
		const msg =
			typeof err === 'string'
				? err
				: (err.messages?.[0] ?? __('Could not update publish status'))
		toast.error(msg)
	},
}) as Resource<unknown>

function togglePublishCourse() {
	publishToggle.submit()
}

const props = defineProps<{
	courseName: string
}>()

onMounted(() => {
	updateTabIndex()
})

const updateTabIndex = () => {
	const hash = route.hash
	if (hash) {
		tabs.value.forEach((tab, index) => {
			if (tab.label?.toLowerCase() === hash.replace('#', '')) {
				tabIndex.value = index
			}
		})
	}
}

watch(tabIndex, () => {
	const tab = tabs.value[tabIndex.value]
	if (tab.label != route.hash.replace('#', '')) {
		router.push({ ...route, hash: `#${tab.label.toLowerCase()}` })
	}
})

// Switch tabs when the hash is changed programmatically (e.g. deep-links).
watch(() => route.hash, updateTabIndex)

const course = createResource({
	url: 'lms.lms.utils.get_course_details',
	cache: ['course', props.courseName],
	makeParams() {
		return {
			course: props.courseName,
		}
	},
	auto: true,
}) as Resource<CourseDetails | null>

const signupUrl = computed(() =>
	getSignupUrl(getLmsRoute(`billing/course/${props.courseName}`)),
)

const tabs = ref<TabDef[]>([
	{
		label: __('Overview'),
		component: markRaw(CourseProductOverview),
		icon: markRaw(List),
	},
	{
		label: __('Dashboard'),
		component: markRaw(CourseDashboard),
		icon: markRaw(TrendingUp),
	},
	{
		label: __('Course editor'),
		component: markRaw(CourseEditor),
		icon: markRaw(BookOpen),
	},
	{
		label: __('Settings'),
		component: markRaw(CourseForm),
		icon: markRaw(Settings2),
	},
])

watch(
	() => props.courseName,
	() => {
		course.reload()
	},
)

watch(course, () => {
	if (!isAdmin.value && !course.data?.published && !course.data?.upcoming) {
		router.push({
			name: 'Courses',
		})
	}
})

const isInstructor = (): boolean => {
	let user_is_instructor = false
	course.data?.instructors.forEach((instructor: CourseInstructorInfo) => {
		if (!user_is_instructor && instructor.name == user.data?.name) {
			user_is_instructor = true
		}
	})
	return user_is_instructor
}

const isAdmin = computed<boolean>(() => {
	return Boolean(user.data?.is_moderator) || isInstructor()
})

usePageMeta(() => {
	return {
		title: course.data?.title,
		icon: brand.favicon,
	}
})
</script>

<style scoped>
.course-detail-shell.is-admin,
.course-admin-workspace {
	background: #faf9fc;
}

.course-editor-outline-header {
	border-color: #e7e2ec;
	background: rgba(255, 255, 255, 0.96);
	box-shadow: 0 8px 20px rgba(44, 31, 69, 0.035);
}

.course-editor-outline-header :deep(button) {
	border-color: rgba(108, 92, 231, 0.2) !important;
	border-radius: 9999px !important;
	background: #f8f6ff !important;
	color: #4a38c2 !important;
	font-weight: 700;
}

/* frappe-ui Tabs: TabsContent has no flex-1, so when the active panel's
   content is intrinsically tall (Course editor with many lessons), the
   flex-col layout shrinks the TabsList strip. Pin it so the strip keeps
   its content height. */
:deep([role='tablist']) {
	flex-shrink: 0;
}

/* frappe-ui TabsContent is `flex flex-col` with no flex-1, so the active
   panel collapses to its content height and the editor's `flex-1 min-h-0`
   grid has no space to fill. Stretch the active panel to fill TabsRoot. */
:deep([role='tabpanel'][data-state='active']) {
	flex: 1 1 0%;
	min-height: 0;
}
</style>
