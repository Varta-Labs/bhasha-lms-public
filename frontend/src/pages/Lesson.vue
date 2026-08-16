<template>
	<div v-if="lesson.data" class="">
		<header
			v-if="!embedded"
			class="bhasha-product-header bhasha-lesson-header bhasha-lesson-desktop-header sticky top-0 z-10 flex items-center justify-between border-b bg-surface-white px-3 py-2.5 sm:px-5"
		>
			<router-link
				class="bhasha-lesson-back-link"
				:to="{
					name: 'CourseDetail',
					params: { courseName: courseName },
				}"
			>
				<Button class="bhasha-lesson-back-button">
					<template #prefix>
						<ChevronLeft class="w-4 h-4 stroke-1.5" />
					</template>
					<span class="truncate">
						{{ __('Back to {0}').format(lesson.data.course_title) }}
					</span>
				</Button>
			</router-link>
			<div class="flex items-center gap-x-2">
				<Tooltip v-if="canGoZen()" :text="__('Zen Mode')">
					<Button class="bhasha-lesson-icon-button" @click="goFullScreen()">
						<template #icon>
							<Focus class="w-4 h-4 stroke-2" />
						</template>
					</Button>
				</Tooltip>
				<Button v-if="isAdmin" @click="showVideoStats()">
					<template #icon>
						<TrendingUp class="size-4 stroke-1.5" />
					</template>
				</Button>
				<CertificationLinks :courseName="courseName" />
				<Button
					class="bhasha-lesson-nav-button"
					v-if="lesson.data.prev"
					@click="switchLesson('prev')"
				>
					<template #prefix>
						<ChevronLeft class="w-4 h-4 stroke-1" />
					</template>
					<span>
						{{ __('Previous') }}
					</span>
				</Button>

				<Button
					class="bhasha-lesson-nav-button is-next"
					v-if="lesson.data.next"
					@click="switchLesson('next')"
				>
					<template #suffix>
						<ChevronRight class="w-4 h-4 stroke-1" />
					</template>
					<span>
						{{ __('Next') }}
					</span>
				</Button>

				<router-link
					v-else
					:to="{
						name: 'CourseDetail',
						params: { courseName: courseName },
					}"
				>
					<Button>
						{{ __('Back to Course') }}
					</Button>
				</router-link>
			</div>
		</header>
		<header v-if="!embedded" class="bhasha-lesson-mobile-header">
			<div class="bhasha-lesson-mobile-header__main">
				<router-link
					class="bhasha-lesson-mobile-header__back"
					:aria-label="__('Back to course')"
					:to="{
						name: 'CourseDetail',
						params: { courseName: courseName },
					}"
				>
					<ChevronLeft class="size-6 stroke-[1.8]" />
				</router-link>
				<div class="bhasha-lesson-mobile-header__titles">
					<div class="bhasha-lesson-mobile-header__course">
						{{ lesson.data.course_title }}
					</div>
					<div class="bhasha-lesson-mobile-header__context">
						<span>{{ lesson.data.chapter_title }}</span>
						<span aria-hidden="true">&bull;</span>
						<span>
							{{ __('Lesson') }} {{ mobileLessonPosition }}
						</span>
					</div>
				</div>
				<button
					v-if="canGoZen()"
					class="bhasha-lesson-mobile-header__action"
					:aria-label="__('Zen Mode')"
					@click="goFullScreen()"
				>
					<Focus class="size-5 stroke-[1.7]" />
				</button>
			</div>
			<div class="bhasha-lesson-mobile-progress">
				<span>
					{{ __('Lesson') }} {{ mobileLessonPosition }}
					<span v-if="outlineMeta.total"> {{ __('of') }} {{ outlineMeta.total }}</span>
				</span>
				<div class="bhasha-lesson-mobile-progress__track" aria-hidden="true">
					<div :style="{ width: `${displayedLessonProgress}%` }" />
				</div>
				<span>{{ displayedLessonProgress }}%</span>
			</div>
		</header>
		<div
			class="bhasha-lesson-layout"
			:class="
				embedded
					? 'grid grid-cols-1 h-full'
					: 'grid md:grid-cols-[70%,30%] h-[94vh]'
			"
		>
			<div v-if="lesson.data.no_preview" class="bhasha-lesson-locked">
				<div class="bhasha-lesson-locked__decoration" aria-hidden="true" />
				<section class="bhasha-lesson-locked__card" role="status">
					<div class="bhasha-lesson-locked__icon">
						<LockKeyholeIcon class="size-7 stroke-[1.7]" />
					</div>
					<div class="bhasha-lesson-locked__eyebrow">
						{{ __('Enrollment required') }}
					</div>
					<h1>{{ __('This lesson is locked') }}</h1>
					<p>
						{{
							__(
								'This lesson is not available for preview. Please enroll in the course to access it.',
							)
						}}
					</p>
					<div class="bhasha-lesson-locked__action">
						<Button
							v-if="user.data && !lesson.data.disable_self_learning"
							@click="enrollStudent()"
							variant="solid"
						>
							{{ __('Start Learning') }}
						</Button>
						<Badge
							theme="blue"
							size="lg"
							v-else-if="lesson.data.disable_self_learning"
							class="mt-2"
						>
							{{ __('Please contact support to enroll.') }}
						</Badge>
						<Button v-else @click="redirectToLogin()">
							<template #prefix>
								<LogIn class="w-4 h-4 stroke-1" />
							</template>
							{{ __('Login') }}
						</Button>
					</div>
					<div class="bhasha-lesson-locked__hint">
						<ShieldCheck class="size-4 shrink-0 stroke-[1.7]" />
						{{
							__(
								'Enroll once to unlock the complete course structure and lessons.',
							)
						}}
					</div>
				</section>
			</div>
			<div
				v-else
				ref="lessonContainer"
				class="bhasha-lesson-content bg-surface-white"
				:class="{
					'overflow-y-auto': zenModeEnabled,
				}"
			>
				<div
					class="bhasha-lesson-canvas border-e pt-5 pb-10 h-full"
					:class="{
						'w-full md:w-3/5 mx-auto border-none !pt-10': zenModeEnabled,
					}"
				>
					<div class="px-5">
						<div
							class="flex flex-col space-y-3 md:space-y-0 md:flex-row md:items-center justify-between"
						>
							<div class="flex flex-col">
								<div class="text-3xl font-semibold text-ink-gray-9">
									{{ lesson.data.title }}
								</div>

								<div
									v-if="zenModeEnabled"
									class="relative flex items-center gap-x-2 text-sm mt-1 text-ink-gray-7 group w-fit mt-2"
								>
									<span>
										{{ lesson.data.chapter_title }} -
										{{ lesson.data.course_title }}
									</span>
									<Info class="size-3" />
									<div
										class="hidden group-hover:block rounded bg-gray-900 px-2 py-1 text-xs text-white shadow-xl absolute start-0 top-full mt-2"
									>
										{{ Math.ceil(lesson.data.membership.progress) }}%
										{{ __('completed') }}
									</div>
								</div>
							</div>

							<div
								v-if="zenModeEnabled"
								class="flex items-center gap-x-2 mt-2 md:mt-0"
							>
								<Button class="bhasha-lesson-icon-button" @click="showDiscussionsInZenMode()">
									<template #icon>
										<MessageCircleQuestion class="w-4 h-4 stroke-1.5" />
									</template>
								</Button>
								<Button class="bhasha-lesson-nav-button" v-if="lesson.data.prev" @click="switchLesson('prev')">
									<template #prefix>
										<ChevronLeft class="w-4 h-4 stroke-1" />
									</template>
									<span>
										{{ __('Previous') }}
									</span>
								</Button>

								<Button class="bhasha-lesson-nav-button is-next" v-if="lesson.data.next" @click="switchLesson('next')">
									<template #suffix>
										<ChevronRight class="w-4 h-4 stroke-1" />
									</template>
									<span>
										{{ __('Next') }}
									</span>
								</Button>

								<router-link
									v-else
									:to="{
										name: 'CourseDetail',
										params: { courseName: courseName },
									}"
								>
									<Button>
										{{ __('Back to Course') }}
									</Button>
								</router-link>
							</div>
						</div>

						<div v-if="!zenModeEnabled" class="flex items-center mt-4 md:mt-2">
							<span
								class="h-6 me-1"
								:class="{
									'avatar-group overlap': lesson.data.instructors?.length > 1,
								}"
							>
								<UserAvatar
									v-for="instructor in lesson.data.instructors"
									:user="instructor"
								/>
							</span>
							<CourseInstructors
								v-if="lesson.data?.instructors"
								:instructors="lesson.data.instructors"
							/>
						</div>

						<div
							v-if="
								lesson.data.instructor_content &&
								JSON.parse(lesson.data.instructor_content)?.blocks?.length >
									1 &&
								allowInstructorContent()
							"
							class="bg-surface-gray-2 p-3 rounded-md mt-6"
						>
							<div class="text-ink-gray-5 font-medium">
								{{ __('Instructor Notes') }}
							</div>
							<div
								id="instructor-content"
								class="ProseMirror prose prose-table:table-fixed prose-td:p-2 prose-th:p-2 prose-td:border prose-th:border prose-td:border-outline-gray-2 prose-th:border-outline-gray-2 prose-td:relative prose-th:relative prose-th:bg-surface-gray-2 prose-sm max-w-none !whitespace-normal"
							></div>
						</div>
						<div
							v-else-if="lesson.data.instructor_notes"
							class="ProseMirror prose prose-table:table-fixed prose-td:p-2 prose-th:p-2 prose-td:border prose-th:border prose-td:border-outline-gray-2 prose-th:border-outline-gray-2 prose-td:relative prose-th:relative prose-th:bg-surface-gray-2 prose-sm max-w-none !whitespace-normal mt-8"
						>
							<LessonContent :content="lesson.data.instructor_notes" />
						</div>
						<div
							v-if="lesson.data.content"
							@mouseup="toggleInlineMenu"
							class="bhasha-lesson-body ProseMirror prose prose-table:table-fixed prose-td:p-2 prose-th:p-2 prose-td:border prose-th:border prose-td:border-outline-gray-2 prose-th:border-outline-gray-2 prose-td:relative prose-th:relative prose-th:bg-surface-gray-2 prose-sm max-w-none !whitespace-normal mt-8"
						>
							<div id="editor"></div>
						</div>
						<div
							v-else
							class="bhasha-lesson-body ProseMirror prose prose-table:table-fixed prose-td:p-2 prose-th:p-2 prose-td:border prose-th:border prose-td:border-outline-gray-2 prose-th:border-outline-gray-2 prose-td:relative prose-th:relative prose-th:bg-surface-gray-2 prose-sm max-w-none !whitespace-normal mt-8"
						>
							<LessonContent
								v-if="lesson.data?.body"
								:content="lesson.data.body"
								:youtube="lesson.data.youtube"
								:quizId="lesson.data.quiz_id"
							/>
						</div>
					</div>
					<nav
						v-if="!zenModeEnabled"
						class="bhasha-lesson-mobile-nav"
						:aria-label="__('Lesson navigation')"
					>
						<button
							class="bhasha-lesson-mobile-nav__button"
							:disabled="!lesson.data.prev"
							@click="lesson.data.prev && switchLesson('prev')"
						>
							<ChevronLeft class="size-5 stroke-[1.7]" />
							<span>{{ __('Previous lesson') }}</span>
						</button>
						<button
							v-if="lesson.data.next"
							class="bhasha-lesson-mobile-nav__button"
							@click="switchLesson('next')"
						>
							<span>{{ __('Next lesson') }}</span>
							<ChevronRight class="size-5 stroke-[1.7]" />
						</button>
						<router-link
							v-else
							class="bhasha-lesson-mobile-nav__button"
							:to="{
								name: 'CourseDetail',
								params: { courseName: courseName },
							}"
						>
							<span>{{ __('Back to course') }}</span>
							<ChevronRight class="size-5 stroke-[1.7]" />
						</router-link>
					</nav>
					<section
						v-if="lesson.data && (allowDiscussions || tabs.length > 1)"
						class="bhasha-lesson-engagement mt-10 pb-20 pt-5 border-t px-5"
						ref="discussionsContainer"
					>
						<TabButtons
							v-if="tabs.length > 1"
							:buttons="tabs"
							v-model="currentTab"
							class="w-fit mb-10"
						/>
						<Notes
							v-if="currentTab === 'Notes'"
							:lesson="lesson.data?.name"
							v-model:notes="notes"
							@updateNotes="updateNotes"
						/>
						<Discussions
							v-else-if="allowDiscussions"
							:title="'Questions'"
							:doctype="'Course Lesson'"
							:docname="lesson.data.name"
							:key="lesson.data.name"
							:emptyStateText="
								__('Ask a question to get help from the community.')
							"
						/>
					</section>
				</div>
			</div>
			<aside
				v-if="!embedded"
				class="bhasha-lesson-sidebar bhasha-lesson-desktop-sidebar sticky top-10 h-[94vh]"
			>
				<StudentLessonSidebar
					:courseName="courseName"
					:courseTitle="lesson.data.course_title"
					:progress="lessonProgress"
					:selectedLessonNumber="`${chapterNumber}-${lessonNumber}`"
					:completedLesson="completedLesson"
					:withProgress="lesson.data.membership ? true : false"
					@outline-meta="updateOutlineMeta"
				/>
			</aside>
		</div>
		<Teleport v-if="!embedded" to="body">
			<Transition name="bhasha-sheet-fade">
				<button
					v-if="mobileCourseOpen"
					class="bhasha-lesson-mobile-sheet__backdrop"
					:aria-label="__('Close course contents')"
					@click="mobileCourseOpen = false"
				/>
			</Transition>
			<section
				class="bhasha-lesson-mobile-sheet"
				:class="{ 'is-open': mobileCourseOpen }"
				:aria-expanded="mobileCourseOpen"
			>
				<div class="bhasha-lesson-mobile-sheet__handle" aria-hidden="true" />
				<button
					class="bhasha-lesson-mobile-sheet__toggle"
					@click="mobileCourseOpen = !mobileCourseOpen"
				>
					<ListTree class="size-5 stroke-[1.7]" />
					<span>{{ __('Course contents') }}</span>
					<ChevronDown
						class="size-5 stroke-[1.8] transition-transform"
						:class="{ 'rotate-180': mobileCourseOpen }"
					/>
				</button>
				<div class="bhasha-lesson-mobile-sheet__body">
					<StudentLessonSidebar
						:courseName="courseName"
						:courseTitle="lesson.data.course_title"
						:progress="lessonProgress"
						:selectedLessonNumber="`${chapterNumber}-${lessonNumber}`"
						:completedLesson="completedLesson"
						:withProgress="lesson.data.membership ? true : false"
						:mobileSheet="true"
						@outline-meta="updateOutlineMeta"
					/>
					<button
						class="bhasha-lesson-mobile-sheet__continue"
						@click="mobileCourseOpen = false"
					>
						{{ __('Continue lesson') }}
					</button>
				</div>
			</section>
		</Teleport>
	</div>
	<InlineLessonMenu
		v-if="lesson.data?.name"
		v-model="showInlineMenu"
		:lesson="lesson.data?.name"
		v-model:notes="notes"
		@updateNotes="updateNotes"
	/>
	<VideoStatistics
		v-if="isAdmin"
		v-model="showStatsDialog"
		:lessonName="lesson.data?.name"
		:lessonTitle="lesson.data?.title"
	/>
</template>
<script setup>
import {
	Badge,
	Button,
	call,
	createListResource,
	createResource,
	TabButtons,
	Tooltip,
	usePageMeta,
	toast,
} from 'frappe-ui'
import {
	computed,
	watch,
	inject,
	ref,
	onMounted,
	onBeforeUnmount,
	nextTick,
} from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
	ChevronLeft,
	ChevronRight,
	LockKeyholeIcon,
	LogIn,
	Focus,
	Info,
	MessageCircleQuestion,
	TrendingUp,
	ShieldCheck,
	ListTree,
} from 'lucide-vue-next'
import {
	getEditorTools,
	enablePlyr,
	highlightText,
	sanitizeEditorJs,
} from '@/utils'
import { sessionStore } from '@/stores/session'
import { useSidebar } from '@/stores/sidebar'
import { useSettings } from '@/stores/settings'
import {
	resolveDwellSeconds,
	isVideoComplete,
	shouldStartDwellTimer,
	shouldAttachVideoFallback,
} from '@/utils/lessonProgress'
import EditorJS from '@editorjs/editorjs'
import LessonContent from '@/components/LessonContent.vue'
import CourseInstructors from '@/components/CourseInstructors.vue'
import ProgressBar from '@/components/ProgressBar.vue'
import Discussions from '@/components/Discussions.vue'
import CertificationLinks from '@/components/CertificationLinks.vue'
import VideoStatistics from '@/components/Modals/VideoStatistics.vue'
import CourseOutline from '@/components/CourseOutline.vue'
import StudentLessonSidebar from '@/components/StudentLessonSidebar.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import Notes from '@/components/Notes/Notes.vue'
import InlineLessonMenu from '@/components/Notes/InlineLessonMenu.vue'
import { getLmsRoute } from '@/utils/basePath'

const user = inject('$user')
const socket = inject('$socket')
const router = useRouter()
const route = useRoute()
const allowDiscussions = ref(false)
const editor = ref(null)
const instructorEditor = ref(null)
const lessonProgress = ref(0)
const lessonContainer = ref(null)
const zenModeEnabled = ref(false)
const showStatsDialog = ref(false)
const hasQuiz = ref(false)
const discussionsContainer = ref(null)
const timer = ref(0)
const { brand } = sessionStore()
const sidebarStore = useSidebar()
const plyrSources = ref([])
const showInlineMenu = ref(false)
const currentTab = ref(null)
const completedLesson = ref(null)
const mobileCourseOpen = ref(false)
const outlineMeta = ref({ total: 0, completed: 0, current: 0 })
const settingsStore = useSettings()
let timerInterval = null

const tabs = ref([])

const props = defineProps({
	courseName: {
		type: String,
		required: true,
	},
	chapterNumber: {
		type: String,
		required: true,
	},
	lessonNumber: {
		type: String,
		required: true,
	},
	embedded: {
		type: Boolean,
		default: false,
	},
})

const emit = defineEmits([
	'select-lesson',
	'lesson-completed',
	'progress-updated',
])

const displayedLessonProgress = computed(() => {
	const progressValue = Number(lessonProgress.value)
	if (!Number.isFinite(progressValue)) return 0
	return Math.min(Math.max(Math.ceil(progressValue), 0), 100)
})
const mobileLessonPosition = computed(
	() => outlineMeta.value.current || Number(props.lessonNumber) || 1,
)

const updateOutlineMeta = (meta) => {
	outlineMeta.value = meta
}

const handleMobileSheetKeydown = (event) => {
	if (event.key === 'Escape') mobileCourseOpen.value = false
}

// Exposed for the parent so the CourseEditor preview can render the same
// Prev / Next / Zen-mode controls as the student header but place them in
// the page-level LayoutHeader instead of inside the lesson body.
defineExpose({
	switchLesson: (direction) => switchLesson(direction),
	goFullScreen: () => goFullScreen(),
	canGoZen: () => canGoZen(),
	hasPrev: computed(() => Boolean(lesson.data?.prev)),
	hasNext: computed(() => Boolean(lesson.data?.next)),
})

onMounted(() => {
	startTimer()
	if (!props.embedded) sidebarStore.isSidebarCollapsed = true
	document.addEventListener('fullscreenchange', attachFullscreenEvent)
	document.addEventListener('keydown', handleMobileSheetKeydown)
	socket.on('update_lesson_progress', (data) => {
		if (data.course === props.courseName) {
			lessonProgress.value = data.progress
			emit('progress-updated', data.progress)
		}
	})
})

const attachFullscreenEvent = () => {
	if (document.fullscreenElement) {
		zenModeEnabled.value = true
		allowDiscussions.value = false
	} else {
		zenModeEnabled.value = false
		if (!hasQuiz.value) {
			allowDiscussions.value = true
		}
	}
}

onBeforeUnmount(() => {
	document.removeEventListener('fullscreenchange', attachFullscreenEvent)
	document.removeEventListener('keydown', handleMobileSheetKeydown)
	document.body.classList.remove('bhasha-mobile-sheet-open')
	if (!props.embedded) sidebarStore.isSidebarCollapsed = false
	trackVideoWatchDuration()
})

const lesson = createResource({
	url: 'lms.lms.utils.get_lesson',
	makeParams(values) {
		return {
			course: props.courseName,
			chapter: values ? values.chapter : props.chapterNumber,
			lesson: values ? values.lesson : props.lessonNumber,
		}
	},
	auto: true,
})

const setupLesson = (data) => {
	if (Object.keys(data).length === 0) {
		router.push({
			name: 'CourseDetail',
			params: { courseName: props.courseName },
		})
		return
	}
	if (data.is_scorm_package) {
		router.push({
			name: 'SCORMChapter',
			params: {
				courseName: props.courseName,
				chapterName: data.chapter_name,
			},
		})
	}
	lessonProgress.value = data.membership?.progress
	if (data.content) editor.value = renderEditor('editor', data.content)
	if (
		data.instructor_content &&
		JSON.parse(data.instructor_content)?.blocks?.length > 1
	)
		instructorEditor.value = renderEditor(
			'instructor-content',
			data.instructor_content,
		)
	editor.value?.isReady.then(() => {
		checkIfDiscussionsAllowed()
	})
	checkQuiz()
}

const checkQuiz = () => {
	if (!editor.value && lesson.body) {
		const quizRegex = /\{\{ Quiz\(".*"\) \}\}/
		hasQuiz.value = quizRegex.test(lesson.body)
		if (!hasQuiz.value && !zenModeEnabled) {
			allowDiscussions.value = true
		} else {
			allowDiscussions.value = false
		}
	}
}

const renderEditor = (holder, content) => {
	if (document.getElementById(holder))
		document.getElementById(holder).innerHTML = ''
	return new EditorJS({
		holder: holder,
		tools: getEditorTools(),
		data: sanitizeEditorJs(JSON.parse(content)),
		readOnly: true,
		defaultBlock: 'embed',
		i18n: {
			direction: document.documentElement.dir === 'rtl' ? 'rtl' : 'ltr',
		},
	})
}

// Video-ended fires markProgress + trackVideoWatchDuration in parallel,
// and trackVideoWatchDuration's getPlyrSourceDetails calls markProgress
// again. Without an in-flight guard the two save_progress requests race
// and the second one fails with TimestampMismatchError on LMS Enrollment.
let progressSubmitting = false
const markProgress = () => {
	if (progressSubmitting) return
	// Only enrolled students record progress; a moderator previewing has no
	// membership row so save_progress would no-op server-side but still
	// flip the in-memory `completedLesson` and show a green tick that
	// vanishes on refresh.
	if (
		!user.data ||
		!lesson.data ||
		!lesson.data.membership ||
		lesson.data.progress
	)
		return
	progressSubmitting = true
	progress.submit(
		{},
		{
			onSuccess() {
				progressSubmitting = false
			},
			onError(err) {
				progressSubmitting = false
				console.error(err)
			},
		},
	)
}

const progress = createResource({
	url: 'lms.lms.doctype.course_lesson.course_lesson.save_progress',
	makeParams() {
		return {
			lesson: lesson.data.name,
			course: props.courseName,
		}
	},
	onSuccess(data) {
		lessonProgress.value = data
		const name = lesson.data?.name
		completedLesson.value = name
		// Tell the parent (CourseEditor preview) so it can flip the
		// sidebar's green tick and update the percentage without waiting
		// for a refresh of the course resource.
		if (name) emit('lesson-completed', name)
		emit('progress-updated', data)
	},
})

const notes = createListResource({
	doctype: 'LMS Lesson Note',
	filters: {
		lesson: lesson.data?.name,
		member: user.data?.name,
	},
	fields: ['name', 'color', 'highlighted_text', 'note'],
	cache: ['notes', lesson.data?.name, user.data?.name],
	onSuccess(data) {
		data.forEach((note) => {
			setTimeout(() => {
				highlightText(note)
			}, 500)
		})
	},
})

const switchLesson = (direction) => {
	trackVideoWatchDuration()
	let lessonIndex =
		direction === 'prev'
			? lesson.data.prev.split('.')
			: lesson.data.next.split('.')

	const [chapterNumber, lessonNumber] = lessonIndex
	// In the embedded editor preview, navigate the parent's selection so the
	// pane swaps in place instead of routing away to /lesson/...
	if (props.embedded) {
		emit('select-lesson', { chapterNumber, lessonNumber })
		return
	}

	router.push({
		name: 'Lesson',
		params: {
			courseName: props.courseName,
			chapterNumber,
			lessonNumber,
		},
	})
}

const scrollLessonToTop = () => {
	const scrollContainer = document.getElementById('scrollContainer')
	if (scrollContainer) {
		scrollContainer.scrollTo({ top: 0, left: 0, behavior: 'auto' })
		return
	}

	window.scrollTo({ top: 0, left: 0, behavior: 'auto' })
}

watch(
	[() => route.params.chapterNumber, () => route.params.lessonNumber],
	async (
		[newChapterNumber, newLessonNumber],
		[oldChapterNumber, oldLessonNumber],
	) => {
		if (newChapterNumber || newLessonNumber) {
			mobileCourseOpen.value = false
			plyrSources.value = []
			await nextTick()
			scrollLessonToTop()
			resetLessonState(newChapterNumber, newLessonNumber)
			updateNotes()
			checkIfDiscussionsAllowed()
			checkQuiz()
		}
	},
)

watch(mobileCourseOpen, (isOpen) => {
	document.body.classList.toggle('bhasha-mobile-sheet-open', isOpen)
})

const resetLessonState = (newChapterNumber, newLessonNumber) => {
	editor.value = null
	instructorEditor.value = null
	allowDiscussions.value = false
	lesson.submit({
		chapter: newChapterNumber,
		lesson: newLessonNumber,
	})
	videoFallbackArmed = false
	fallbackGeneration++
	clearInterval(timerInterval)
	timer.value = 0
}

const trackVideoWatchDuration = () => {
	if (!lesson.data?.membership) return
	let videoDetails = getVideoDetails()
	videoDetails = videoDetails.concat(getPlyrSourceDetails())
	call('lms.lms.api.track_video_watch_duration', {
		lesson: lesson.data.name,
		videos: videoDetails,
	})
}

const getVideoDetails = () => {
	let details = []
	const videos = document.querySelectorAll('video')
	if (videos.length > 0) {
		videos.forEach((video) => {
			if (isVideoComplete(video.currentTime, video.duration)) markProgress()
			details.push({
				source: video.src,
				watch_time: video.currentTime,
			})
		})
	}
	return details
}

const getPlyrSourceDetails = () => {
	let details = []
	plyrSources.value.forEach((source) => {
		if (isVideoComplete(source.currentTime, source.duration)) markProgress()
		let src = cleanYouTubeUrl(source.source)
		details.push({
			source: src,
			watch_time: source.currentTime,
		})
	})
	return details
}

const cleanYouTubeUrl = (url) => {
	if (!url) return url
	const urlObj = new URL(url)
	urlObj.searchParams.delete('t')
	return urlObj.toString()
}

watch(
	() => lesson.data,
	async (data) => {
		setupLesson(data)
		// Settings drive dwell + enforcement; if they haven't resolved yet
		// the timer reads undefined and falls back to 30s. Await the
		// resource so the admin-configured dwell time wins from the first
		// lesson load.
		if (settingsStore.settings?.promise) {
			try {
				await settingsStore.settings.promise
			} catch {}
		}
		startTimer()
		await getPlyrSource()
		updateNotes()
		const hasVideoListener =
			plyrSources.value.length > 0 || !!document.querySelector('video')
		const enforceVideo = Number(
			settingsStore.settings?.data?.enforce_video_completion ?? 0,
		)
		// When the lesson has video AND enforcement is on, suppress dwell so
		// completion is gated on play-to-end. When enforcement is off, dwell
		// runs for every lesson type — including YouTube/Plyr — so admins can
		// set a short dwell to mark video lessons complete without a full
		// playthrough.
		if (!shouldStartDwellTimer({ hasVideo: hasVideoListener, enforceVideo })) {
			clearInterval(timerInterval)
		}
		if (
			shouldAttachVideoFallback({ hasVideo: hasVideoListener, enforceVideo })
		) {
			document.querySelectorAll('video').forEach((video) => {
				if (video._lmsErrorAttached) return
				video._lmsErrorAttached = true
				const gen = fallbackGeneration
				video.addEventListener(
					'error',
					() => {
						if (gen !== fallbackGeneration) return
						fallbackToDwellTimer('html5-video-error')
					},
					{ once: true },
				)
			})
		}
	},
)

const getPlyrSource = async () => {
	await nextTick()
	if (plyrSources.value.length == 0) {
		plyrSources.value = await enablePlyr()
		const enforceVideo = Number(
			settingsStore.settings?.data?.enforce_video_completion ?? 0,
		)
		if (
			shouldAttachVideoFallback({
				hasVideo: plyrSources.value.length > 0,
				enforceVideo,
			})
		) {
			plyrSources.value.forEach((player) => {
				let readyFired = false
				const gen = fallbackGeneration
				player.on('ready', () => {
					readyFired = true
				})
				player.on('error', (event) => {
					if (gen !== fallbackGeneration) return
					fallbackToDwellTimer(
						'plyr-error: ' + (event?.detail?.message || 'unknown'),
					)
				})
				setTimeout(() => {
					if (!readyFired && gen === fallbackGeneration) {
						fallbackToDwellTimer('plyr-no-ready-15s')
					}
				}, 15000)
			})
		}
	}
	updateVideoWatchDuration()
}

const updateVideoWatchDuration = () => {
	if (lesson.data.videos && lesson.data.videos.length > 0) {
		lesson.data.videos.forEach((video) => {
			if (video.source.includes('youtube') || video.source.includes('vimeo')) {
				updatePlyrVideoTime(video)
			} else {
				updateVideoTime(video)
			}
		})
	}
	attachVideoEndedListeners()
}

const attachVideoEndedListeners = () => {
	const onVideoEnded = () => {
		markProgress()
		trackVideoWatchDuration()
	}

	document.querySelectorAll('video').forEach((video) => {
		if (!video._lmsEndedAttached) {
			video.addEventListener('ended', onVideoEnded)
			video._lmsEndedAttached = true
		}
	})

	plyrSources.value.forEach((plyrSource) => {
		if (!plyrSource._lmsEndedAttached) {
			plyrSource.on('ended', onVideoEnded)
			plyrSource.on('statechange', (event) => {
				if (event.detail?.code === 0) onVideoEnded()
			})
			plyrSource._lmsEndedAttached = true
		}
	})
}

const updatePlyrVideoTime = (video) => {
	plyrSources.value.forEach((plyrSource) => {
		let lastWatchedTime = 0
		let isSeeking = false

		plyrSource.on('ready', () => {
			if (plyrSource.source === video.source) {
				plyrSource.embed.seekTo(video.watch_time, true)
				plyrSource.play()
				plyrSource.pause()
			}
		})
	})
}

const updateVideoTime = (video) => {
	const videos = document.querySelectorAll('video')
	if (videos.length > 0) {
		videos.forEach((vid) => {
			if (vid.src === video.source) {
				let watch_time = video.watch_time < vid.duration ? video.watch_time : 0
				if (vid.readyState >= 1) {
					vid.currentTime = watch_time
				} else {
					vid.addEventListener('loadedmetadata', () => {
						vid.currentTime = watch_time
					})
				}
			}
		})
	}
}

let videoFallbackArmed = false
let fallbackGeneration = 0
const fallbackToDwellTimer = (reason) => {
	if (videoFallbackArmed) return
	videoFallbackArmed = true
	console.warn('[Lesson] video fallback engaged:', reason)
	toast.warning(
		__('Video failed to load — you can still mark this lesson as viewed.'),
	)
	clearInterval(timerInterval)
	timer.value = 0
	startTimer()
}

const startTimer = () => {
	if (!lesson.data?.membership) return
	const dwell = resolveDwellSeconds(
		settingsStore.settings?.data?.lesson_dwell_time,
	)
	if (dwell === null) return
	timerInterval = setInterval(() => {
		timer.value++
		if (timer.value >= dwell) {
			clearInterval(timerInterval)
			markProgress()
		}
	}, 1000)
}

onBeforeUnmount(() => {
	clearInterval(timerInterval)
})

const checkIfDiscussionsAllowed = () => {
	hasQuiz.value = false
	if (lesson.data?.content) {
		try {
			JSON.parse(lesson.data.content)?.blocks?.forEach((block) => {
				if (block.type === 'quiz') {
					hasQuiz.value = true
				}
			})
		} catch {
			// legacy markdown lessons
		}
	}

	if (
		!hasQuiz.value &&
		!zenModeEnabled.value &&
		(lesson.data?.membership ||
			user.data?.is_moderator ||
			user.data?.is_instructor)
	) {
		allowDiscussions.value = true
	} else {
		allowDiscussions.value = false
	}
}

const isAdmin = computed(() => {
	let isInstructor = lesson.data?.instructors?.includes(user.data?.name)
	return user.data?.is_moderator || isInstructor
})

const allowInstructorContent = () => {
	if (window.read_only_mode) return false
	return isAdmin.value
}

const enrollment = createResource({
	url: 'frappe.client.insert',
	makeParams() {
		return {
			doc: {
				doctype: 'LMS Enrollment',
				course: props.courseName,
				member: user.data?.name,
			},
		}
	},
})

const enrollStudent = () => {
	enrollment.submit(
		{},
		{
			onSuccess() {
				window.location.reload()
			},
			onError(err) {
				toast.error(__(err.messages?.[0] || err))
				console.error(err)
			},
		},
	)
}

const toggleInlineMenu = async () => {
	showInlineMenu.value = false
	await nextTick()
	let selection = window.getSelection()
	if (selection.toString()) {
		showInlineMenu.value = true
	}
}

const showVideoStats = () => {
	showStatsDialog.value = true
}

const canGoZen = () => {
	if (
		user.data?.is_moderator ||
		user.data?.is_instructor ||
		user.data?.is_evaluator
	)
		return true
	if (lesson.data?.membership) return true
	return false
}

const goFullScreen = () => {
	if (lessonContainer.value.requestFullscreen) {
		lessonContainer.value.requestFullscreen()
	} else if (lessonContainer.value.mozRequestFullScreen) {
		lessonContainer.value.mozRequestFullScreen()
	} else if (lessonContainer.value.webkitRequestFullscreen) {
		lessonContainer.value.webkitRequestFullscreen()
	} else if (lessonContainer.value.msRequestFullscreen) {
		lessonContainer.value.msRequestFullscreen()
	}
}

const showDiscussionsInZenMode = () => {
	if (allowDiscussions.value) {
		allowDiscussions.value = false
	} else {
		allowDiscussions.value = true
		currentTab.value = 'Community'
		scrollDiscussionsIntoView()
	}
}

const scrollDiscussionsIntoView = () => {
	nextTick(() => {
		discussionsContainer.value?.scrollIntoView({
			behavior: 'smooth',
			block: 'center',
			inline: 'nearest',
		})
	})
}

const updateNotes = () => {
	if (!user.data) return
	notes.update({
		filters: {
			lesson: lesson.data?.name,
			member: user.data?.name,
		},
	})
	notes.reload()
}

watch(allowDiscussions, () => {
	if (!isAdmin.value) {
		if (!tabs.value.find((tab) => tab.value === 'Notes')) {
			tabs.value.push({
				label: __('Notes'),
				value: 'Notes',
			})
		}
		currentTab.value = 'Notes'
	} else {
		currentTab.value = allowDiscussions.value ? 'Community' : null
	}
	if (allowDiscussions.value) {
		if (!tabs.value.find((tab) => tab.value === 'Community')) {
			tabs.value.push({
				label: __('Community'),
				value: 'Community',
			})
		}
	}
})

const redirectToLogin = () => {
	window.location.href = `/login?redirect-to=${getLmsRoute(
		`courses/${props.courseName}`,
	)}`
}

usePageMeta(() => {
	return {
		title: lesson?.data?.title,
		icon: brand.favicon,
	}
})
</script>
<style>
.avatar-group {
	display: inline-flex;
	align-items: center;
}

.avatar-group .avatar {
	transition: margin 0.1s ease-in-out;
}

.lesson-content p {
	margin-bottom: 1rem;
	line-height: 1.7;
}

.lesson-content li {
	line-height: 1.7;
}

.lesson-content ol {
	list-style: auto;
	margin: revert;
	padding: 1rem;
}

.lesson-content ul {
	list-style: auto;
	padding: 1rem;
	margin: revert;
}

.lesson-content img {
	border: 1px solid theme('colors.gray.200');
	border-radius: 0.5rem;
}

.lesson-content code {
	display: block;
	overflow-x: auto;
	padding: 1rem 1.25rem;
	background: #011627;
	color: #d6deeb;
	border-radius: 0.5rem;
	margin: 1rem 0;
}

.lesson-content a {
	color: theme('colors.gray.900');
	text-decoration: underline;
	font-weight: 500;
}

.embed-tool__caption,
.cdx-simple-image__caption {
	display: none;
}

.ce-block__content {
	max-width: unset;
}

.codex-editor__redactor {
	padding-bottom: 0px !important;
}

.codeBoxHolder {
	display: flex;
	flex-direction: column;
	justify-content: flex-start;
	align-items: flex-start;
}

.codeBoxTextArea {
	width: 100%;
	min-height: 30px;
	padding: 10px;
	border-radius: 2px 2px 2px 0;
	border: none !important;
	outline: none !important;
	font: 14px monospace;
}

.codeBoxSelectDiv {
	display: flex;
	flex-direction: column;
	justify-content: flex-start;
	align-items: flex-start;
	position: relative;
}

.codeBoxSelectInput {
	border-radius: 0 0 20px 2px;
	padding: 2px 26px;
	padding-top: 0;
	padding-inline-end: 0;
	text-align: start;
	cursor: pointer;
	border: none !important;
	outline: none !important;
}

.codeBoxSelectDropIcon {
	position: absolute !important;
	inset-inline-start: 10px !important;
	bottom: 0 !important;
	width: unset !important;
	height: unset !important;
	font-size: 16px !important;
}

.codeBoxSelectPreview {
	display: none;
	flex-direction: column;
	justify-content: flex-start;
	align-items: flex-start;
	border-radius: 2px;
	box-shadow: 0 3px 15px -3px rgba(13, 20, 33, 0.13);
	position: absolute;
	top: 100%;
	margin: 5px 0;
	max-height: 30vh;
	overflow-x: hidden;
	overflow-y: auto;
	z-index: 10000;
}

.codeBoxSelectItem {
	width: 100%;
	padding: 5px 20px;
	margin: 0;
	cursor: pointer;
}

.codeBoxSelectItem:hover {
	opacity: 0.7;
}

.codeBoxSelectedItem {
	background-color: lightblue !important;
}

.codeBoxShow {
	display: flex !important;
}

.dark {
	color: #abb2bf;
	background-color: #282c34;
}

.light {
	color: #383a42;
	background-color: #fafafa;
}

.codeBoxTextArea {
	line-height: 1.7;
}

.tc-table {
	border-inline-start: 1px solid #e8e8eb;
}

.plyr__volume input[type='range'] {
	display: none;
}

.plyr__control--overlaid {
	background: radial-gradient(
		circle,
		rgba(0, 0, 0, 0.4) 0%,
		rgba(0, 0, 0, 0.5) 50%
	);
}

.plyr__control:hover {
	background: none;
}

.plyr--video {
	border: 1px solid theme('colors.gray.200');
	border-radius: 8px;
}

.bhasha-lesson-layout {
	background: var(--bhasha-page);
}

.bhasha-lesson-header > :last-child {
	flex-wrap: wrap;
	justify-content: flex-end;
}

.bhasha-lesson-back-link {
	min-width: 0;
	max-width: min(30rem, 50vw);
}

.bhasha-lesson-back-button {
	max-width: 100%;
}

.bhasha-lesson-nav-button,
.bhasha-lesson-icon-button {
	min-height: 2.35rem;
	border: 1px solid rgba(108, 92, 231, 0.2) !important;
	border-radius: 9999px !important;
	background: #fff !important;
	color: #4a38c2 !important;
	font-weight: 700 !important;
	box-shadow: 0 4px 12px rgba(74, 56, 194, 0.06);
}

.bhasha-lesson-nav-button.is-next {
	border-color: transparent !important;
	background: linear-gradient(135deg, #6c5ce7, #4a38c2) !important;
	color: #fff !important;
	box-shadow: 0 10px 22px -8px rgba(108, 92, 231, 0.48);
}

.bhasha-lesson-locked {
	position: relative;
	display: grid;
	min-height: 100%;
	overflow: hidden;
	place-items: center;
	padding: clamp(2rem, 6vw, 5rem) 1.25rem;
	border-inline-end: 1px solid rgba(108, 92, 231, 0.14);
	background:
		radial-gradient(
			circle at 12% 10%,
			rgba(255, 255, 255, 0.82),
			transparent 30%
		),
		radial-gradient(
			circle at 86% 82%,
			rgba(210, 189, 153, 0.2),
			transparent 34%
		),
		linear-gradient(135deg, #f7f2e8, #f3ecdf 58%, #f8f4eb);
}

.bhasha-lesson-locked__decoration {
	position: absolute;
	top: -10rem;
	right: -8rem;
	width: 28rem;
	aspect-ratio: 1;
	border: 1px solid rgba(113, 91, 61, 0.13);
	border-radius: 50%;
	box-shadow:
		0 0 0 4rem rgba(113, 91, 61, 0.04),
		0 0 0 8rem rgba(113, 91, 61, 0.025);
}

.bhasha-lesson-locked__card {
	position: relative;
	z-index: 1;
	width: min(100%, 36rem);
	padding: clamp(2rem, 5vw, 3.25rem);
	border: 1px solid rgba(108, 92, 231, 0.2);
	border-radius: 2rem;
	background: rgba(255, 255, 255, 0.93);
	box-shadow: 0 24px 60px -20px rgba(74, 47, 25, 0.28);
	text-align: center;
	backdrop-filter: blur(16px);
}

.bhasha-lesson-locked__icon {
	display: grid;
	width: 3.75rem;
	height: 3.75rem;
	margin: 0 auto 1.25rem;
	place-items: center;
	border: 1px solid rgba(108, 92, 231, 0.24);
	border-radius: 1rem;
	background: rgba(108, 92, 231, 0.1);
	color: #6c5ce7;
}

.bhasha-lesson-locked__eyebrow {
	color: #4a38c2;
	font-size: 0.75rem;
	font-weight: 800;
	letter-spacing: 0.12em;
	text-transform: uppercase;
}

.bhasha-lesson-locked h1 {
	margin-top: 0.65rem;
	color: #171717;
	font-family: var(--bhasha-font-display);
	font-size: clamp(1.85rem, 4vw, 2.5rem);
	font-weight: 800;
	letter-spacing: -0.03em;
	line-height: 1.15;
}

.bhasha-lesson-locked p {
	max-width: 30rem;
	margin: 1rem auto 0;
	color: #625d68;
	font-size: 1rem;
	line-height: 1.65;
}

.bhasha-lesson-locked__action {
	display: flex;
	justify-content: center;
	margin-top: 1.75rem;
}

.bhasha-lesson-locked__action button {
	min-height: 3rem;
	padding-inline: 1.35rem !important;
	border-color: transparent !important;
	border-radius: 9999px !important;
	background: linear-gradient(135deg, #6c5ce7, #4a38c2) !important;
	color: #fff !important;
	font-weight: 800 !important;
	box-shadow: 0 14px 28px -8px rgba(108, 92, 231, 0.44);
}

.bhasha-lesson-locked__hint {
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 0.45rem;
	margin-top: 1.5rem;
	color: #7c7c7c;
	font-size: 0.75rem;
	font-weight: 600;
}

.bhasha-lesson-content {
	min-width: 0;
}

.bhasha-lesson-canvas {
	background: #fff;
}

.bhasha-lesson-engagement {
	margin-inline: 1.25rem;
	padding: clamp(1.25rem, 3vw, 2rem) !important;
	border: 1px solid rgba(108, 92, 231, 0.16) !important;
	border-radius: 1.5rem;
	background: linear-gradient(145deg, #fff, #f8f6ff);
	box-shadow: 0 12px 32px rgba(74, 56, 194, 0.055);
}

.bhasha-lesson-engagement [role='tablist'] {
	padding: 0.25rem;
	border: 1px solid rgba(108, 92, 231, 0.14);
	border-radius: 9999px;
	background: #f8f6ff;
}

.bhasha-lesson-sidebar {
	top: 3.75rem;
	height: calc(100vh - 3.75rem);
	border-inline-start: 1px solid rgba(108, 92, 231, 0.16);
	background: #fff;
}

.bhasha-lesson-mobile-header,
.bhasha-lesson-mobile-nav,
.bhasha-lesson-mobile-sheet,
.bhasha-lesson-mobile-sheet__backdrop {
	display: none;
}

.bhasha-sheet-fade-enter-active,
.bhasha-sheet-fade-leave-active {
	transition: opacity 180ms ease;
}

.bhasha-sheet-fade-enter-from,
.bhasha-sheet-fade-leave-to {
	opacity: 0;
}

@media (max-width: 767px) {
	.bhasha-lesson-desktop-header,
	.bhasha-lesson-desktop-sidebar {
		display: none !important;
	}

	.bhasha-lesson-mobile-header {
		position: sticky;
		top: 0;
		z-index: 20;
		display: block;
		border-bottom: 1px solid var(--bhasha-border);
		background: rgba(255, 255, 255, 0.97);
		backdrop-filter: blur(14px);
	}

	.bhasha-lesson-mobile-header__main {
		display: grid;
		grid-template-columns: 2.5rem minmax(0, 1fr) 2.5rem;
		align-items: center;
		gap: 0.65rem;
		min-height: 4.6rem;
		padding: 0.75rem 1rem 0.7rem;
	}

	.bhasha-lesson-mobile-header__back,
	.bhasha-lesson-mobile-header__action {
		display: grid;
		width: 2.5rem;
		height: 2.5rem;
		place-items: center;
		border: 1px solid transparent;
		border-radius: 9999px;
		color: var(--bhasha-text);
	}

	.bhasha-lesson-mobile-header__back:active,
	.bhasha-lesson-mobile-header__action:active {
		border-color: var(--bhasha-border-brand);
		background: var(--bhasha-50);
	}

	.bhasha-lesson-mobile-header__titles {
		min-width: 0;
	}

	.bhasha-lesson-mobile-header__course {
		overflow: hidden;
		color: var(--bhasha-text);
		font-family: var(--bhasha-font-display);
		font-size: 1rem;
		font-weight: 800;
		line-height: 1.3;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.bhasha-lesson-mobile-header__context {
		display: flex;
		align-items: center;
		gap: 0.45rem;
		min-width: 0;
		margin-top: 0.15rem;
		color: var(--bhasha-text-muted);
		font-size: 0.75rem;
		line-height: 1.25;
	}

	.bhasha-lesson-mobile-header__context span:first-child {
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.bhasha-lesson-mobile-header__action {
		border-color: var(--bhasha-border-brand);
		background: var(--bhasha-50);
		color: var(--bhasha-700);
	}

	.bhasha-lesson-mobile-progress {
		display: grid;
		grid-template-columns: auto minmax(4rem, 1fr) auto;
		align-items: center;
		gap: 0.8rem;
		padding: 0.8rem 1.25rem;
		border-top: 1px solid color-mix(in srgb, var(--bhasha-border) 75%, transparent);
		color: var(--bhasha-text-muted);
		font-size: 0.72rem;
		font-weight: 700;
	}

	.bhasha-lesson-mobile-progress__track {
		height: 0.35rem;
		overflow: hidden;
		border-radius: 9999px;
		background: var(--bhasha-100);
	}

	.bhasha-lesson-mobile-progress__track > div {
		height: 100%;
		border-radius: inherit;
		background: linear-gradient(90deg, var(--bhasha-500), var(--bhasha-700));
		transition: width 220ms ease;
	}

	.bhasha-lesson-layout {
		display: flex !important;
		height: auto !important;
		min-height: auto;
		flex-direction: column;
		background: #fff;
	}

	.bhasha-lesson-content {
		overflow: visible;
		padding-bottom: calc(4.8rem + env(safe-area-inset-bottom));
	}

	.bhasha-lesson-canvas {
		height: auto !important;
		padding-top: 2rem !important;
		padding-bottom: 1rem !important;
		border-inline-end: 0;
	}

	.bhasha-lesson-canvas > .px-5 {
		padding-inline: 1.25rem;
	}

	.bhasha-lesson-canvas .text-3xl.font-semibold {
		font-size: 1.7rem;
		font-weight: 800;
		letter-spacing: -0.025em;
		line-height: 1.2;
	}

	.bhasha-lesson-body {
		margin-top: 1.75rem !important;
		padding: 1.1rem;
		border: 1px solid var(--bhasha-border);
		border-radius: 1.15rem;
		background: var(--bhasha-surface);
		box-shadow: 0 8px 24px rgba(73, 38, 135, 0.045);
		font-size: 0.95rem;
		line-height: 1.7;
	}

	.bhasha-lesson-body :where(iframe, video, img, .plyr) {
		max-width: 100%;
		border-radius: 0.8rem;
	}

	.bhasha-lesson-body .youtube-video {
		height: auto !important;
		aspect-ratio: 16 / 9;
	}

	.bhasha-lesson-body iframe[src*='docs.google.com/presentation/'] {
		display: block;
		width: 100% !important;
		height: auto !important;
		aspect-ratio: 16 / 9;
		background: #fff;
	}

	.bhasha-lesson-mobile-nav {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 0.75rem;
		padding: 2rem 1.25rem 0;
	}

	.bhasha-lesson-mobile-nav__button {
		display: flex;
		min-width: 0;
		min-height: 3.25rem;
		align-items: center;
		justify-content: space-between;
		gap: 0.4rem;
		padding: 0.75rem 0.8rem;
		border: 1px solid var(--bhasha-border);
		border-radius: 0.85rem;
		background: #fff;
		color: var(--bhasha-text);
		font-size: 0.78rem;
		font-weight: 750;
		text-align: center;
	}

	.bhasha-lesson-mobile-nav__button span {
		min-width: 0;
		flex: 1;
	}

	.bhasha-lesson-mobile-nav__button:disabled {
		cursor: not-allowed;
		opacity: 0.42;
	}

	.bhasha-lesson-engagement {
		margin: 1.5rem 1.25rem 0;
		padding: 1rem !important;
		border-radius: 1.15rem;
	}

	.bhasha-lesson-mobile-sheet__backdrop {
		position: fixed;
		z-index: 40;
		inset: 0;
		display: block;
		width: 100%;
		height: 100%;
		border: 0;
		background: rgba(31, 23, 43, 0.52);
		backdrop-filter: blur(2px);
	}

	.bhasha-lesson-mobile-sheet {
		position: fixed;
		z-index: 50;
		inset-inline: 0;
		bottom: 0;
		display: flex;
		height: calc(4.65rem + env(safe-area-inset-bottom));
		max-height: 86dvh;
		flex-direction: column;
		padding-bottom: env(safe-area-inset-bottom);
		border: 1px solid var(--bhasha-border);
		border-bottom: 0;
		border-radius: 1.35rem 1.35rem 0 0;
		background: #fff;
		box-shadow: 0 -16px 40px rgba(31, 23, 43, 0.14);
		transition: height 260ms cubic-bezier(0.22, 1, 0.36, 1);
	}

	.bhasha-lesson-mobile-sheet.is-open {
		height: min(86dvh, 46rem);
	}

	.bhasha-lesson-mobile-sheet__handle {
		width: 2.7rem;
		height: 0.28rem;
		flex: 0 0 auto;
		margin: 0.65rem auto 0.25rem;
		border-radius: 9999px;
		background: var(--bhasha-200);
	}

	.bhasha-lesson-mobile-sheet__toggle {
		display: grid;
		grid-template-columns: 1.5rem 1fr 1.5rem;
		align-items: center;
		gap: 0.75rem;
		min-height: 3.2rem;
		padding: 0.35rem 1.25rem 0.7rem;
		color: var(--bhasha-text);
		font-family: var(--bhasha-font-display);
		font-size: 1rem;
		font-weight: 800;
		text-align: start;
	}

	.bhasha-lesson-mobile-sheet__body {
		display: flex;
		min-height: 0;
		flex: 1;
		flex-direction: column;
		overflow: hidden;
		opacity: 0;
		pointer-events: none;
		transition: opacity 120ms ease;
	}

	.bhasha-lesson-mobile-sheet.is-open .bhasha-lesson-mobile-sheet__body {
		opacity: 1;
		pointer-events: auto;
		transition-delay: 90ms;
	}

	.bhasha-lesson-mobile-sheet__body > .bhasha-course-structure {
		min-height: 0;
		flex: 1;
	}

	.bhasha-lesson-mobile-sheet__continue {
		min-height: 3.25rem;
		margin: 0 1rem 1rem;
		padding: 0.8rem 1rem;
		border: 0;
		border-radius: 0.85rem;
		background: linear-gradient(135deg, var(--bhasha-600), var(--bhasha-700));
		color: #fff;
		font-weight: 800;
		box-shadow: 0 10px 24px rgba(101, 50, 197, 0.24);
	}

	body.bhasha-mobile-sheet-open {
		overflow: hidden;
	}
}

:root {
	--plyr-range-fill-background: white;
	--plyr-video-control-background-hover: transparent;
}
</style>
