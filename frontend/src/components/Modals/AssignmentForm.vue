<template>
	<Dialog
		v-model="show"
		:options="{
			title: dialogTitle,
			size: '3xl',
		}"
	>
		<template #body-title>
			<div class="bhasha-dialog-heading">
				<div class="bhasha-dialog-icon" aria-hidden="true">
					<ClipboardPenLine class="size-5 stroke-1.75" />
				</div>
				<div>
					<h3 class="bhasha-dialog-title">{{ dialogTitle }}</h3>
					<p class="bhasha-dialog-description">
						{{
							assignmentID === 'new'
								? __(
										'Set the brief, submission format, and optional course connection in one place.',
									)
								: __(
										'Update the brief or submission settings without losing learner responses.',
									)
						}}
					</p>
				</div>
			</div>
		</template>
		<template #body-content>
			<div class="bhasha-assignment-form text-base">
				<section class="bhasha-assignment-form-overview">
					<div class="bhasha-assignment-section-copy">
						<span class="bhasha-assignment-form-kicker">{{
							__('Essentials')
						}}</span>
						<h4>{{ __('Assignment details') }}</h4>
						<p>
							{{
								__(
									'Use a clear title and tell learners exactly what they need to submit.',
								)
							}}
						</p>
					</div>
					<div class="bhasha-assignment-fields">
						<FormControl
							v-model="assignment.title"
							:label="__('Assignment title')"
							:placeholder="__('e.g. Customer interview reflection')"
							:required="true"
							size="md"
							variant="outline"
						/>
						<div class="bhasha-assignment-fields-grid">
							<FormControl
								v-model="assignment.type"
								type="select"
								:options="assignmentOptions"
								:label="__('Submission type')"
								:required="true"
								size="md"
								variant="outline"
							/>
							<Link
								v-model="assignment.course"
								:label="__('Course')"
								doctype="LMS Course"
								:placeholder="__('Optional course')"
								size="md"
								variant="outline"
							/>
						</div>
					</div>
				</section>

				<section class="bhasha-assignment-form-section">
					<div class="bhasha-assignment-form-section-heading">
						<div class="bhasha-assignment-form-section-icon" aria-hidden="true">
							<FileText class="size-4 stroke-1.5" />
						</div>
						<div>
							<h4>{{ __('Brief and instructions') }}</h4>
							<p>
								{{
									__(
										'Include the task, expected outcome, and any useful constraints.',
									)
								}}
							</p>
						</div>
					</div>
					<div class="bhasha-assignment-editor">
						<div class="mb-2 text-xs text-ink-gray-5">
							{{ __('Question') }}
							<span class="text-ink-red-3">*</span>
						</div>
						<TextEditor
							:content="assignment.question"
							@change="(val) => (assignment.question = val)"
							:editable="true"
							:fixedMenu="true"
							editorClass="prose-sm max-w-none border-b border-x border-outline-gray-modals bg-surface-gray-2 rounded-b-md py-1 px-2 min-h-[10rem] max-h-[18rem] overflow-y-auto"
						/>
					</div>
				</section>
			</div>
		</template>
		<template #actions="{ close }">
			<div class="bhasha-assignment-form-actions">
				<router-link
					v-if="assignmentID !== 'new'"
					:to="{
						name: 'AssignmentSubmissionList',
						query: {
							assignmentID: assignmentID,
						},
					}"
				>
					<Button class="bhasha-dialog-secondary" variant="outline" size="md">
						{{ __('Check submissions') }}
					</Button>
				</router-link>
				<div class="bhasha-assignment-form-actions-right">
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
						@click="saveAssignment"
					>
						{{
							assignmentID === 'new'
								? __('Create assignment')
								: __('Save changes')
						}}
					</Button>
				</div>
			</div>
		</template>
	</Dialog>
</template>
<script setup lang="ts">
import { Button, Dialog, FormControl, TextEditor, toast } from 'frappe-ui'
import { computed, reactive, watch } from 'vue'
import { sanitizeHTML } from '@/utils'
import Link from '@/components/Controls/Link.vue'
import { ClipboardPenLine, FileText } from 'lucide-vue-next'
import '@/styles/assessment-management.css'

const show = defineModel()
const assignments = defineModel<Assignments>('assignments')

interface Assignment {
	title: string
	type: string
	question: string
	course?: string
}

interface Assignments {
	data: Assignment[]
	get: (params: { doctype: string; name: string }) => Promise<Assignment>
	insert: {
		submit: (params: Assignment, options: { onSuccess: () => void }) => void
	}
}

const assignment = reactive({
	title: '',
	type: '',
	question: '',
	course: '',
})

const props = defineProps({
	assignmentID: {
		type: String,
		default: 'new',
	},
})

const dialogTitle = computed(() =>
	props.assignmentID === 'new'
		? __('Create an assignment')
		: __('Edit assignment'),
)

watch(
	() => props.assignmentID,
	(val) => {
		if (val !== 'new') {
			assignments.value?.data.forEach((row) => {
				if (row.name === val) {
					assignment.title = row.title
					assignment.type = row.type
					assignment.question = row.question
					assignment.course = row.course || ''
				}
			})
		}
	},
	{ flush: 'post' }
)

watch(show, (newVal) => {
	if (newVal && props.assignmentID === 'new') {
		assignment.title = ''
		assignment.type = ''
		assignment.question = ''
		assignment.course = ''
	}
})

const validateFields = () => {
	assignment.title = sanitizeHTML(assignment.title.trim())
	assignment.question = sanitizeHTML(assignment.question)
}

const saveAssignment = () => {
	validateFields()
	if (!assignment.title || !assignment.type || !assignment.question) {
		toast.error(__('Title, submission type, and question are required'))
		return
	}
	if (props.assignmentID == 'new') {
		createAssignment()
	} else {
		updateAssignment()
	}
}

const createAssignment = () => {
	assignments.value.insert.submit(
		{
			...assignment,
		},
		{
			onSuccess() {
				show.value = false
				toast.success(__('Assignment created successfully'))
			},
		}
	)
}

const updateAssignment = () => {
	assignments.value.setValue.submit(
		{
			...assignment,
			name: props.assignmentID,
		},
		{
			onSuccess() {
				show.value = false
				toast.success(__('Assignment updated successfully'))
			},
		}
	)
}

const assignmentOptions = computed(() => {
	return [
		{ label: 'PDF', value: 'PDF' },
		{ label: 'Image', value: 'Image' },
		{ label: 'Document', value: 'Document' },
		{ label: 'Text', value: 'Text' },
		{ label: 'URL', value: 'URL' },
	]
})
</script>
