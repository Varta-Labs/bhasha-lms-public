<template>
	<div
		class="bhasha-course-structure flex flex-col h-full"
		:class="{ 'is-mobile-sheet': mobileSheet }"
	>
		<div class="bhasha-course-structure__header px-5 py-5 border-b">
			<div v-if="!mobileSheet" class="bhasha-course-structure__eyebrow">
				<BookOpen class="size-3.5 stroke-2" />
				{{ __('Course structure') }}
			</div>
			<div
				v-if="!mobileSheet"
				class="text-lg font-semibold text-ink-gray-9 leading-snug"
			>
				{{ courseTitle }}
			</div>
			<div
				v-if="withProgress && !mobileSheet"
				class="mt-4 flex items-center gap-2 text-sm text-ink-gray-7"
			>
				<Cloud class="size-4 stroke-1.5" />
				<span>{{ __('Completed') }} {{ displayedProgress }}%</span>
			</div>
			<div v-if="mobileSheet" class="bhasha-course-structure__summary">
				<span>
					{{ completedLessons }} {{ __('of') }} {{ totalLessons }}
					{{ __('lessons completed') }}
				</span>
				<span>{{ displayedProgress }}%</span>
			</div>
			<div
				v-if="withProgress"
				class="h-1 w-full rounded-full bg-surface-gray-2 overflow-hidden mt-2"
			>
				<div
					class="h-full bg-surface-green-3 transition-all"
					:style="{ width: `${displayedProgress}%` }"
				/>
			</div>
		</div>

		<div
			class="bhasha-course-structure__chapters flex-1 overflow-y-auto px-3 py-4"
		>
			<Disclosure
				v-for="chapter in outline.data || []"
				:key="chapter.name"
				v-slot="{ open }"
				:defaultOpen="chapterDefaultOpen(chapter)"
			>
				<DisclosureButton
					class="bhasha-course-structure__chapter w-full flex items-center justify-between px-3 py-2 text-left"
				>
					<div
						class="flex items-center gap-2 text-sm font-medium text-ink-gray-9 min-w-0"
					>
						<ChevronDown
							class="size-4 stroke-1.5 shrink-0 transition-transform"
							:class="{ '-rotate-90': !open }"
						/>
						<span class="truncate">
							{{ mobileSheet ? `${chapter.idx}. ${chapter.title}` : chapter.title }}
						</span>
					</div>
					<span
						v-if="chapter.lessons?.length"
						class="text-xs text-ink-gray-5 shrink-0"
					>
						{{ chapter.lessons.length }}
					</span>
				</DisclosureButton>
				<DisclosurePanel>
					<component
						:is="inlineSelect ? 'div' : 'router-link'"
						v-for="lesson in chapter.lessons || []"
						:key="lesson.name"
						:to="
							inlineSelect
								? undefined
								: {
										name: 'Lesson',
										params: {
											courseName,
											chapterNumber: lesson.number.split('-')[0],
											lessonNumber: lesson.number.split('-')[1],
										},
									}
						"
						class="bhasha-course-structure__lesson flex items-center gap-3 ps-9 pe-3 py-2 text-sm text-ink-gray-8"
						:class="[
							inlineSelect ? 'cursor-pointer' : '',
							isActive(lesson.number) ? 'is-active text-ink-gray-9' : '',
						]"
						@click="
							inlineSelect &&
							emit('select-lesson', {
								chapterNumber: lesson.number.split('-')[0],
								lessonNumber: lesson.number.split('-')[1],
							})
						"
					>
						<component
							:is="iconFor(lesson.icon)"
							class="size-4 stroke-1.5 shrink-0 text-ink-gray-7"
						/>
						<span class="truncate flex-1">
							{{
								mobileSheet
									? `${lesson.number.replace('-', '.')} ${lesson.title}`
									: lesson.title
							}}
						</span>
						<span
							v-if="mobileSheet && isActive(lesson.number)"
							class="bhasha-course-structure__current"
						>
							{{ __('Current') }}
						</span>
						<CircleCheck
							v-if="lesson.is_complete"
							class="size-4 stroke-1.5 shrink-0 text-green-700 fill-none"
						/>
						<Circle v-else class="size-4 stroke-1.5 shrink-0 text-ink-gray-4" />
					</component>
				</DisclosurePanel>
			</Disclosure>
		</div>
	</div>
</template>

<script setup>
import { computed, watch, watchEffect } from 'vue'
import { createResource } from 'frappe-ui'
import { Disclosure, DisclosureButton, DisclosurePanel } from '@headlessui/vue'
import {
	ChevronDown,
	Circle,
	CircleCheck,
	Cloud,
	BookOpen,
	FileText,
	HelpCircle,
	LockKeyhole,
	MonitorPlay,
	NotebookPen,
	SquareCode,
} from 'lucide-vue-next'

const props = defineProps({
	courseName: { type: String, required: true },
	courseTitle: { type: String, default: '' },
	progress: { type: Number, default: 0 },
	selectedLessonNumber: { type: String, default: '' },
	completedLesson: { type: String, default: null },
	inlineSelect: { type: Boolean, default: false },
	withProgress: { type: Boolean, default: true },
	mobileSheet: { type: Boolean, default: false },
})

const emit = defineEmits(['select-lesson', 'outline-meta'])

const outline = createResource({
	url: 'lms.lms.utils.get_course_outline',
	cache: [
		'course_outline_student',
		props.courseName,
		props.withProgress ? 'progress' : 'no-progress',
	],
	makeParams() {
		return {
			course: props.courseName,
			progress: props.withProgress,
		}
	},
	auto: true,
})

watch(
	() => props.courseName,
	() => outline.reload(),
)

// Re-runs whenever either source updates so a completion event that
// lands before outline.data finishes loading still gets applied (and a
// late-arriving outline reload doesn't wipe an already-marked lesson).
watchEffect(() => {
	const lessonName = props.completedLesson
	if (!lessonName || !outline.data) return
	for (const chapter of outline.data) {
		const found = chapter.lessons?.find((l) => l.name === lessonName)
		if (found) {
			found.is_complete = true
			return
		}
	}
})

const displayedProgress = computed(() => {
	const progressValue = Number(props.progress)
	if (!Number.isFinite(progressValue)) return 0
	return Math.min(Math.max(Math.ceil(progressValue), 0), 100)
})
const flatLessons = computed(() =>
	(outline.data || []).flatMap((chapter) => chapter.lessons || []),
)
const totalLessons = computed(() => flatLessons.value.length)
const completedLessons = computed(
	() => flatLessons.value.filter((lesson) => lesson.is_complete).length,
)

watchEffect(() => {
	if (!outline.data) return
	const currentIndex = flatLessons.value.findIndex(
		(lesson) => lesson.number === props.selectedLessonNumber,
	)
	emit('outline-meta', {
		total: totalLessons.value,
		completed: completedLessons.value,
		current: currentIndex >= 0 ? currentIndex + 1 : 0,
	})
})

function iconFor(icon) {
	switch (icon) {
		case 'icon-youtube':
			return MonitorPlay
		case 'icon-quiz':
			return HelpCircle
		case 'icon-assignment':
			return NotebookPen
		case 'icon-code':
			return SquareCode
		case 'icon-lock':
			return LockKeyhole
		default:
			return FileText
	}
}

function isActive(number) {
	return props.selectedLessonNumber === number
}

function chapterDefaultOpen(chapter) {
	if (!props.selectedLessonNumber) return chapter.idx === 1
	return (
		chapter.lessons?.some((l) => l.number === props.selectedLessonNumber) ||
		false
	)
}
</script>

<style scoped>
.bhasha-course-structure {
	background:
		linear-gradient(180deg, rgba(108, 92, 231, 0.045), transparent 10rem), #fff;
}

.bhasha-course-structure__header {
	border-bottom-color: rgba(108, 92, 231, 0.16);
	background: linear-gradient(145deg, rgba(248, 246, 255, 0.95), #fff);
}

.bhasha-course-structure__eyebrow {
	display: flex;
	align-items: center;
	gap: 0.4rem;
	margin-bottom: 0.55rem;
	color: #4a38c2;
	font-size: 0.7rem;
	font-weight: 800;
	letter-spacing: 0.1em;
	text-transform: uppercase;
}

.bhasha-course-structure__header > div:nth-last-child(1) > div {
	background: linear-gradient(90deg, #6c5ce7, #4a38c2);
}

.bhasha-course-structure__chapters {
	scrollbar-color: rgba(108, 92, 231, 0.28) transparent;
	scrollbar-width: thin;
}

.bhasha-course-structure__chapter,
.bhasha-course-structure__lesson {
	border: 1px solid transparent;
	border-radius: 0.8rem;
	transition:
		background 160ms ease,
		border-color 160ms ease,
		color 160ms ease;
}

.bhasha-course-structure__chapter {
	margin-top: 0.2rem;
	color: #383838;
}

.bhasha-course-structure__chapter:hover,
.bhasha-course-structure__lesson:hover {
	border-color: rgba(108, 92, 231, 0.12);
	background: #f8f6ff;
}

.bhasha-course-structure__lesson {
	margin-block: 0.15rem;
}

.bhasha-course-structure__lesson.is-active {
	border-color: rgba(108, 92, 231, 0.24);
	background: linear-gradient(135deg, rgba(108, 92, 231, 0.12), #f8f6ff);
	color: #4a38c2;
	font-weight: 700;
	box-shadow: 0 6px 16px rgba(74, 56, 194, 0.07);
}

.bhasha-course-structure__lesson.is-active svg:first-child {
	color: #6c5ce7;
}

.bhasha-course-structure__summary {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 1rem;
	color: var(--bhasha-text-muted);
	font-size: 0.82rem;
	font-weight: 650;
}

.bhasha-course-structure__current {
	flex-shrink: 0;
	padding: 0.2rem 0.5rem;
	border: 1px solid var(--bhasha-border);
	border-radius: 9999px;
	background: #fff;
	color: var(--bhasha-700);
	font-size: 0.65rem;
	font-weight: 800;
}

.bhasha-course-structure.is-mobile-sheet {
	background: #fff;
}

.bhasha-course-structure.is-mobile-sheet .bhasha-course-structure__header {
	margin: 0 1rem;
	padding: 0.9rem 1rem;
	border: 1px solid var(--bhasha-border);
	border-radius: 0.9rem;
	background: var(--bhasha-50);
}

.bhasha-course-structure.is-mobile-sheet .bhasha-course-structure__chapters {
	padding: 0.8rem 1rem 1rem;
}

.bhasha-course-structure.is-mobile-sheet .bhasha-course-structure__chapter {
	min-height: 3.6rem;
	margin-top: 0.55rem;
	padding: 0.8rem 0.9rem;
	border-color: var(--bhasha-border);
	border-radius: 0.9rem;
	background: #fff;
}

.bhasha-course-structure.is-mobile-sheet .bhasha-course-structure__lesson {
	min-height: 3rem;
	margin-block: 0.15rem;
	padding-inline-start: 1rem;
	border-radius: 0.7rem;
}
</style>
