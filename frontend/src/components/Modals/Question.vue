<template>
	<Dialog
		v-model="show"
		:options="{
			title: __(props.title),
			size: '3xl',
		}"
	>
		<template #body-title>
			<div class="bhasha-dialog-heading">
				<div class="bhasha-dialog-icon" aria-hidden="true">
					<MessageCircleQuestion class="size-5 stroke-1.75" />
				</div>
				<div>
					<h3 class="bhasha-dialog-title">{{ __(props.title) }}</h3>
					<p class="bhasha-dialog-description">
						{{
							editMode
								? __('Refine the prompt, answers, and scoring for this question.')
								: __('Create a new prompt or reuse a question from your question bank.')
						}}
					</p>
				</div>
			</div>
		</template>
		<template #body-content>
			<div class="bhasha-question-form">
				<Switch
					v-if="!editMode"
					size="sm"
					:label="__('Choose an existing question')"
					:description="__('Select from questions you have already created')"
					v-model="chooseFromExisting"
					class="bhasha-question-source-switch"
				/>
				<div
					v-if="!chooseFromExisting || editMode"
					class="bhasha-question-form-content"
				>
					<div>
						<label class="mb-2 block text-xs text-ink-gray-5">
							{{ __('Question prompt') }}
						</label>
						<TextEditor
							:content="question.question"
							@change="(val) => (question.question = val)"
							:editable="true"
							:fixedMenu="true"
							editorClass="prose-sm max-w-none border-b border-x border-outline-gray-modals bg-surface-gray-2 rounded-b-md py-1 px-2 min-h-[7rem]"
						/>
					</div>
					<div class="bhasha-question-meta-grid">
						<FormControl
							v-model="question.marks"
							:label="__('Marks')"
							type="number"
						/>
						<FormControl
							:label="__('Type')"
							v-model="question.type"
							type="select"
							:options="['Choices', 'User Input', 'Open Ended']"
							class="pb-2"
							:required="true"
						/>
					</div>
					<div
						v-if="question.type == 'Choices'"
						class="bhasha-question-subheading"
					>
						{{ __('Options') }}
					</div>
					<div
						v-else-if="question.type == 'User Input'"
						class="bhasha-question-subheading"
					>
						{{ __('Possibilities') }}
					</div>
					<div
						v-if="question.type == 'Choices'"
						class="bhasha-question-options-grid"
					>
						<div v-for="n in 4" :key="n" class="bhasha-question-option-card">
							<div class="bhasha-question-option-number">{{ n }}</div>
							<FormControl
								:label="__('Option') + ' ' + n"
								v-model="question[`option_${n}`]"
								:required="n <= 2 ? true : false"
							/>
							<FormControl
								:label="__('Explanation')"
								v-model="question[`explanation_${n}`]"
							/>
							<Switch
								size="sm"
								:label="__('Correct Answer')"
								:description="__('Mark this option as a correct answer.')"
								v-model="question[`is_correct_${n}`]"
							/>
						</div>
					</div>
					<div
						v-else-if="question.type == 'User Input'"
						class="bhasha-question-options-grid"
					>
						<div v-for="n in 4" :key="n" class="bhasha-question-option-card">
							<div class="bhasha-question-option-number">{{ n }}</div>
							<FormControl
								:label="__('Possibility') + ' ' + n"
								v-model="question[`possibility_${n}`]"
								:required="n == 1 ? true : false"
							/>
						</div>
					</div>
				</div>
				<div v-else-if="chooseFromExisting" class="bhasha-question-existing">
					<Link
						v-model="existingQuestion.question"
						:label="__('Select a question')"
						doctype="LMS Question"
					/>
					<FormControl
						v-model="existingQuestion.marks"
						:label="__('Marks')"
						type="number"
					/>
				</div>
			</div>
		</template>
		<template #actions="{ close }">
			<div class="bhasha-dialog-actions">
				<Button
					class="bhasha-dialog-secondary"
					variant="outline"
					size="md"
					@click="close"
				>
					{{ __('Cancel') }}
				</Button>
				<Button
					class="bhasha-primary bhasha-dialog-primary"
					variant="solid"
					size="md"
					@click="submitQuestion()"
				>
					{{ editMode ? __('Save changes') : __('Add question') }}
				</Button>
			</div>
		</template>
	</Dialog>
</template>
<script setup>
import {
	Dialog,
	FormControl,
	TextEditor,
	createResource,
	Button,
	toast,
} from 'frappe-ui'
import Switch from '@/components/Controls/Switch.vue'
import { watch, reactive, ref, inject } from 'vue'
import Link from '@/components/Controls/Link.vue'
import { useOnboarding } from 'frappe-ui/frappe'
import { MessageCircleQuestion } from 'lucide-vue-next'
import '@/styles/assessment-management.css'

const show = defineModel()
const quiz = defineModel('quiz')
const chooseFromExisting = ref(false)
const editMode = ref(false)
const user = inject('$user')
const { updateOnboardingStep } = useOnboarding('learning')

const existingQuestion = reactive({
	question: '',
	marks: 1,
})

const question = reactive({
	question: '',
	type: 'Choices',
	marks: 1,
})

const populateFields = () => {
	let fields = ['option', 'is_correct', 'explanation', 'possibility']
	let counter = 1
	fields.forEach((field) => {
		while (counter <= 4) {
			question[`${field}_${counter}`] = field === 'is_correct' ? false : null
			counter++
		}
	})
}

populateFields()

const props = defineProps({
	title: {
		type: String,
		default: __('Add new question'),
	},
	questionDetail: {
		type: [Object, null],
		required: true,
	},
})

const questionData = createResource({
	url: 'frappe.client.get',
	makeParams() {
		return {
			doctype: 'LMS Question',
			name: props.questionDetail.question,
		}
	},
	auto: false,
	onSuccess(data) {
		let counter = 1
		editMode.value = true
		Object.keys(data).forEach((key) => {
			if (Object.hasOwn(question, key)) question[key] = data[key]
		})
		while (counter <= 4) {
			question[`is_correct_${counter}`] = data[`is_correct_${counter}`]
				? true
				: false
			counter++
		}
		question.marks = props.questionDetail.marks
	},
})

watch(show, () => {
	if (show.value) {
		editMode.value = false
		if (props.questionDetail.question) questionData.fetch()
		else {
			question.question = ''
			question.marks = 1
			question.type = 'Choices'
			existingQuestion.question = ''
			existingQuestion.marks = 1
			chooseFromExisting.value = false
			populateFields()
		}

		if (props.questionDetail.marks) question.marks = props.questionDetail.marks
	}
})

const questionRow = createResource({
	url: 'frappe.client.insert',
	makeParams(values) {
		return {
			doc: {
				doctype: 'LMS Quiz Question',
				parent: quiz.value.doc.name,
				parentfield: 'questions',
				parenttype: 'LMS Quiz',
				...values,
			},
		}
	},
})

const questionCreation = createResource({
	url: 'frappe.client.insert',
	makeParams(values) {
		return {
			doc: {
				doctype: 'LMS Question',
				...question,
			},
		}
	},
})

const submitQuestion = () => {
	if (props.questionDetail?.question) updateQuestion()
	else addQuestion()
}

const addQuestion = () => {
	if (chooseFromExisting.value) {
		addQuestionRow({
			question: existingQuestion.question,
			marks: existingQuestion.marks,
		})
	} else {
		questionCreation.submit(
			{},
			{
				onSuccess(data) {
					addQuestionRow({
						question: data.name,
						marks: question.marks,
					})
				},
				onError(err) {
					toast.error(err.messages?.[0] || err)
				},
			}
		)
	}
}

const addQuestionRow = (question) => {
	questionRow.submit(
		{
			...question,
		},
		{
			onSuccess() {
				if (user.data?.is_system_manager)
					updateOnboardingStep('create_first_quiz')

				show.value = false
				toast.success(__('Question added successfully'))
				quiz.value.reload()
				show.value = false
			},
			onError(err) {
				toast.error(err.messages?.[0] || err)
				show.value = false
			},
		}
	)
}

const questionUpdate = createResource({
	url: 'frappe.client.set_value',
	auto: false,
	makeParams(values) {
		return {
			doctype: 'LMS Question',
			name: questionData.data?.name,
			fieldname: {
				...question,
			},
		}
	},
})

const marksUpdate = createResource({
	url: 'frappe.client.set_value',
	auto: false,
	makeParams(values) {
		return {
			doctype: 'LMS Quiz Question',
			name: props.questionDetail.name,
			fieldname: {
				marks: question.marks,
			},
		}
	},
})

const updateQuestion = () => {
	questionUpdate.submit(
		{},
		{
			onSuccess() {
				marksUpdate.submit(
					{},
					{
						onSuccess() {
							show.value = false
							toast.success(__('Question updated successfully'))
							quiz.value.reload()
						},
					}
				)
			},
			onError(err) {
				toast.error(err.messages?.[0] || err)
			},
		}
	)
}
</script>
<style>
input[type='radio']:checked {
	background-color: theme('colors.gray.900') !important;
	border-color: theme('colors.gray.900') !important;
	--tw-ring-color: theme('colors.gray.900') !important;
}
</style>
