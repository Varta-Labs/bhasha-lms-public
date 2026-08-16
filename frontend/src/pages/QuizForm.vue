<template>
	<header
		class="bhasha-product-header bhasha-quiz-builder-header sticky top-0 z-10 flex items-center justify-between border-b bg-surface-white px-3 py-2.5 sm:px-5"
	>
		<Breadcrumbs :items="breadcrumbs" />
		<div
			v-if="!readOnlyMode"
			class="bhasha-quiz-builder-header-actions flex items-center gap-x-2"
		>
			<Badge v-if="quizDetails.isDirty" theme="orange">
				{{ __('Not Saved') }}
			</Badge>
			<router-link
				v-if="quizDetails.doc?.name"
				:to="{
					name: 'QuizPage',
					params: {
						quizID: quizDetails.doc.name,
					},
				}"
			>
				<Button class="bhasha-quiz-secondary-action">
					<template #prefix>
						<ListChecks class="size-4 stroke-1.5" />
					</template>
					{{ __('Test Quiz') }}
				</Button>
			</router-link>
			<router-link
				v-if="quizDetails.doc?.name"
				:to="{
					name: 'QuizSubmissionList',
					params: {
						quizID: quizDetails.doc.name,
					},
				}"
			>
				<Button class="bhasha-quiz-secondary-action">
					<template #prefix>
						<ClipboardList class="size-4 stroke-1.5" />
					</template>
					{{ __('Check Submissions') }}
				</Button>
			</router-link>
			<Button
				variant="solid"
				class="bhasha-primary bhasha-assessment-create-button"
				@click="submitQuiz()"
			>
				{{ __('Save quiz') }}
			</Button>
		</div>
	</header>
	<main v-if="quizDetails.doc" class="bhasha-quiz-builder-page">
		<div class="bhasha-quiz-builder-shell">
			<section class="bhasha-quiz-builder-card bhasha-quiz-details-card">
				<div class="bhasha-quiz-section-heading">
					<div class="bhasha-quiz-section-icon" aria-hidden="true">
						<FileQuestion class="size-5 stroke-1.5" />
					</div>
					<div>
						<span class="bhasha-quiz-section-kicker">{{ __('Quiz setup') }}</span>
						<h1>{{ __('Details and scoring') }}</h1>
						<p>
							{{
								__(
									'Set the learner-facing title, attempt limit, timing, and pass criteria.',
								)
							}}
						</p>
					</div>
				</div>
				<div class="bhasha-quiz-details-grid">
					<div class="space-y-5">
						<FormControl
							v-model="quizDetails.doc.title"
							:label="__('Title')"
							:required="true"
							size="md"
							variant="outline"
						/>
						<FormControl
							type="number"
							v-model="quizDetails.doc.max_attempts"
							:label="__('Maximum attempts')"
							size="md"
							variant="outline"
						/>
						<FormControl
							type="number"
							v-model="quizDetails.doc.duration"
							:label="__('Duration (in minutes)')"
							size="md"
							variant="outline"
						/>
					</div>
					<div class="space-y-5">
						<FormControl
							v-model="quizDetails.doc.total_marks"
							:label="__('Total marks')"
							disabled
							size="md"
							variant="outline"
						/>
						<FormControl
							v-model="quizDetails.doc.passing_percentage"
							:label="__('Passing percentage')"
							:required="true"
							size="md"
							variant="outline"
						/>
						<div class="bhasha-quiz-score-note">
							<Target class="size-4 stroke-1.5" />
							<span>{{
								__(
									'Total marks update automatically from the questions below.',
								)
							}}</span>
						</div>
					</div>
				</div>
			</section>

			<section class="bhasha-quiz-builder-card">
				<div class="bhasha-quiz-section-heading">
					<div class="bhasha-quiz-section-icon" aria-hidden="true">
						<SlidersHorizontal class="size-5 stroke-1.5" />
					</div>
					<div>
						<span class="bhasha-quiz-section-kicker">{{ __('Behaviour') }}</span>
						<h2>{{ __('Quiz settings') }}</h2>
						<p>
							{{ __('Control feedback, question order, and marking rules.') }}
						</p>
					</div>
				</div>
				<div class="bhasha-quiz-settings-grid">
					<div class="bhasha-quiz-setting-group">
						<Switch
							v-model="quizDetails.doc.show_answers"
							size="sm"
							:label="__('Show answers')"
							:description="
								__('Display correct answers after each question is attempted.')
							"
						/>
						<Switch
							v-model="quizDetails.doc.show_submission_history"
							size="sm"
							:label="__('Show submission history')"
							:description="__('Allow users to view their past quiz attempts.')"
						/>
					</div>
					<div class="bhasha-quiz-setting-group">
						<Switch
							v-model="quizDetails.doc.shuffle_questions"
							size="sm"
							:label="__('Shuffle questions')"
							:description="
								__('Randomize the order of questions for each attempt.')
							"
						/>
						<FormControl
							v-if="quizDetails.doc.shuffle_questions"
							v-model="quizDetails.doc.limit_questions_to"
							:label="__('Limit questions to')"
							size="md"
							variant="outline"
						/>
					</div>
					<div class="bhasha-quiz-setting-group">
						<Switch
							v-model="quizDetails.doc.enable_negative_marking"
							size="sm"
							:label="__('Enable negative marking')"
							:description="__('Deduct marks for incorrect answers.')"
						/>
						<FormControl
							v-if="quizDetails.doc.enable_negative_marking"
							v-model="quizDetails.doc.marks_to_cut"
							:label="__('Marks to deduct')"
							size="md"
							variant="outline"
						/>
					</div>
				</div>
			</section>

			<section class="bhasha-quiz-builder-card">
				<div class="bhasha-quiz-questions-heading">
					<div class="bhasha-quiz-section-heading">
						<div class="bhasha-quiz-section-icon" aria-hidden="true">
							<ListChecks class="size-5 stroke-1.5" />
						</div>
						<div>
							<span class="bhasha-quiz-section-kicker">{{ __('Content') }}</span>
							<h2>{{ __('Questions') }}</h2>
							<p>
								{{
									__(
										'Add questions in the order learners should encounter them.',
									)
								}}
							</p>
						</div>
					</div>
					<Button
						v-if="!readOnlyMode"
						class="bhasha-quiz-add-question"
						variant="outline"
						@click="openQuestionModal()"
					>
						<template #prefix>
							<Plus class="h-4 w-4 stroke-2" />
						</template>
						{{ __('Add question') }}
					</Button>
				</div>
				<ListView
					v-if="questions.length"
					:columns="questionColumns"
					:rows="questions"
					row-key="name"
					:options="{
						showTooltip: false,
					}"
					class="bhasha-quiz-question-list"
				>
					<ListHeader
						class="bhasha-assessment-list-header grid items-center gap-x-4 p-2"
					>
						<ListHeaderItem :item="item" v-for="item in questionColumns" />
					</ListHeader>
					<ListRows>
						<ListRow
							:row="row"
							v-slot="{ column, item }"
							v-for="row in questions"
							:key="row.name"
							@click="openQuestionModal(row)"
							class="bhasha-assessment-list-row cursor-pointer"
						>
							<ListRowItem :item="item">
								<div
									v-if="column.key == 'question_detail'"
									class="h-4 truncate text-xs"
									v-html="item"
								></div>
								<div v-else class="text-xs">
									{{ item }}
								</div>
							</ListRowItem>
						</ListRow>
					</ListRows>
					<ListSelectBanner>
						<template #actions="{ unselectAll, selections }">
							<div class="flex gap-2">
								<Button
									variant="ghost"
									@click="deleteQuestions(selections, unselectAll)"
								>
									<Trash2 class="h-4 w-4 stroke-1.5" />
								</Button>
							</div>
						</template>
					</ListSelectBanner>
				</ListView>
				<div v-else class="bhasha-quiz-questions-empty">
					<ListChecks class="size-5 stroke-1.5" />
					<div>
						<strong>{{ __('No questions added yet') }}</strong>
						<span>{{
							__('Add the first question to start building this assessment.')
						}}</span>
					</div>
				</div>
			</section>
		</div>
	</main>

	<Question
		v-model="showQuestionModal"
		:questionDetail="currentQuestion"
		v-model:quiz="quizDetails"
		:title="currentQuestion.question ? __('Edit Question') : __('Add Question')"
	/>
</template>
<script setup>
import {
	Breadcrumbs,
	createResource,
	FormControl,
	ListView,
	ListHeader,
	ListHeaderItem,
	ListRows,
	ListRow,
	ListRowItem,
	ListSelectBanner,
	Button,
	usePageMeta,
	toast,
	createDocumentResource,
	Badge,
} from 'frappe-ui'
import Switch from '@/components/Controls/Switch.vue'
import {
	computed,
	reactive,
	ref,
	onMounted,
	inject,
	onBeforeUnmount,
} from 'vue'
import { sessionStore } from '../stores/session'
import {
	ClipboardList,
	FileQuestion,
	ListChecks,
	Plus,
	SlidersHorizontal,
	Target,
	Trash2,
} from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { sanitizeHTML } from '@/utils'
import Question from '@/components/Modals/Question.vue'
import '@/styles/assessment-management.css'

const { brand } = sessionStore()
const showQuestionModal = ref(false)
const currentQuestion = reactive({
	question: '',
	marks: 0,
	name: '',
})
const user = inject('$user')
const router = useRouter()
const readOnlyMode = window.read_only_mode

const props = defineProps({
	quizID: {
		type: String,
		required: true,
	},
})

const questions = computed(() => {
	return quizDetails.doc?.questions || []
})

onMounted(() => {
	if (!user.data?.is_moderator && !user.data?.is_instructor) {
		router.push({ name: 'Courses' })
	}
	quizDetails.reload()
	window.addEventListener('keydown', keyboardShortcut)
})

const keyboardShortcut = (e) => {
	if (e.key === 's' && (e.ctrlKey || e.metaKey)) {
		submitQuiz()
		e.preventDefault()
	}
}

onBeforeUnmount(() => {
	window.removeEventListener('keydown', keyboardShortcut)
})

const quizDetails = createDocumentResource({
	doctype: 'LMS Quiz',
	name: props.quizID,
	auto: false,
})

const validateTitle = () => {
	quizDetails.doc.title = sanitizeHTML(quizDetails.doc.title.trim())
}

const submitQuiz = () => {
	validateTitle()
	if (!quizDetails.doc.title) {
		toast.error(__('Quiz title is required'))
		return
	}
	quizDetails.setValue.submit(
		{
			...quizDetails.doc,
			total_marks: calculateTotalMarks(),
		},
		{
			onSuccess(data) {
				quizDetails.doc.total_marks = data.total_marks
				toast.success(__('Quiz updated successfully'))
			},
			onError(err) {
				toast.error(err.messages?.[0] || err)
			},
		}
	)
}

const calculateTotalMarks = () => {
	let totalMarks = 0
	if (
		quizDetails.doc?.limit_questions_to &&
		quizDetails.doc?.questions.length > 0
	)
		return (
			quizDetails.doc.questions[0].marks * quizDetails.doc.limit_questions_to
		)

	quizDetails.doc?.questions.forEach((question) => {
		totalMarks += question.marks
	})
	return totalMarks
}

const questionColumns = computed(() => {
	return [
		{
			label: __('ID'),
			key: 'question',
			width: '10rem',
		},
		{
			label: __('Question'),
			key: __('question_detail'),
			width: '40rem',
		},
		{
			label: __('Marks'),
			key: 'marks',
			width: '5rem',
		},
	]
})

const openQuestionModal = (question = null) => {
	if (question) {
		currentQuestion.question = question.question
		currentQuestion.marks = question.marks
		currentQuestion.name = question.name
	} else {
		currentQuestion.question = ''
		currentQuestion.marks = 0
		currentQuestion.name = ''
	}
	showQuestionModal.value = true
}

const deleteQuestionResource = createResource({
	url: 'lms.lms.api.delete_documents',
	makeParams(values) {
		return {
			doctype: 'LMS Quiz Question',
			documents: values.questions,
		}
	},
})

const deleteQuestions = (selections, unselectAll) => {
	deleteQuestionResource.submit(
		{
			questions: Array.from(selections),
		},
		{
			onSuccess() {
				toast.success(__('Questions deleted successfully'))
				quizDetails.reload()
				unselectAll()
			},
		}
	)
}

const breadcrumbs = computed(() => {
	let crumbs = [
		{
			label: __('Quizzes'),
			route: {
				name: 'Quizzes',
			},
		},
	]

	crumbs.push({
		label: quizDetails.doc?.title,
		route: { name: 'QuizForm', params: { quizID: props.quizID } },
	})
	return crumbs
})

usePageMeta(() => {
	return {
		title: quizDetails.doc?.title,
		icon: brand.favicon,
	}
})
</script>
