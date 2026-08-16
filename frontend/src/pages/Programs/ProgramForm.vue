<template>
	<Dialog
		v-model="show"
		:options="{
			title: dialogTitle,
			size: '3xl',
		}"
	>
		<template #body-title>
			<div class="bhasha-dialog-heading w-full">
				<div class="bhasha-dialog-icon" aria-hidden="true">
					<Route class="size-5 stroke-1.75" />
				</div>
				<div class="min-w-0 flex-1">
					<div class="flex items-start justify-between gap-3">
						<div>
							<h3 class="bhasha-dialog-title">{{ dialogTitle }}</h3>
							<p class="bhasha-dialog-description">{{ dialogDescription }}</p>
						</div>
						<span v-if="dirty" class="bhasha-unsaved-badge">
							{{ __('Unsaved changes') }}
						</span>
					</div>
				</div>
			</div>
		</template>
		<template #body-content>
			<div class="bhasha-program-form text-base">
				<section class="bhasha-program-form-overview">
					<div class="bhasha-program-form-section-copy">
						<span class="bhasha-program-form-kicker">{{
							__('Essentials')
						}}</span>
						<h4>{{ __('Program details') }}</h4>
						<p>
							{{
								__(
									'Give this learning path a clear name and choose how it should work.',
								)
							}}
						</p>
					</div>
					<div class="bhasha-program-form-essentials">
						<FormControl
							v-model="program.name"
							:label="__('Program title')"
							type="text"
							:required="true"
							autocomplete="off"
							size="md"
							variant="outline"
							@change="dirty = true"
						/>
						<div class="bhasha-program-settings-grid">
							<div class="bhasha-program-setting">
								<div>
									<strong>{{ __('Published') }}</strong>
									<span>{{
										__('Make this program available to learners.')
									}}</span>
								</div>
								<FormControl
									v-model="program.published"
									type="checkbox"
									@change="dirty = true"
								/>
							</div>
							<div class="bhasha-program-setting">
								<div>
									<strong>{{ __('Course order') }}</strong>
									<span>{{
										__('Require learners to complete courses in sequence.')
									}}</span>
								</div>
								<FormControl
									v-model="program.enforce_course_order"
									type="checkbox"
									@change="dirty = true"
								/>
							</div>
						</div>
					</div>
				</section>

				<section class="bhasha-program-form-section">
					<div class="bhasha-program-form-section-header">
						<div class="bhasha-program-form-section-heading">
							<div class="bhasha-program-form-section-icon" aria-hidden="true">
								<BookOpen class="size-4 stroke-1.5" />
							</div>
							<div>
								<h4>{{ __('Courses') }}</h4>
								<p>
									{{
										__(
											'Add courses and drag them into the right learning order.',
										)
									}}
								</p>
							</div>
						</div>
						<Button
							class="bhasha-program-add-button"
							variant="outline"
							@click="openForm('course')"
						>
							<template #prefix>
								<Plus class="size-4 stroke-2" />
							</template>
							{{ __('Add course') }}
						</Button>
					</div>
					<ListView
						v-if="program.program_courses?.length > 0"
						:columns="courseColumns"
						:rows="program.program_courses"
						:options="{
							selectable: true,
							resizeColumn: true,
							showTooltip: false,
						}"
						:rowKey="programName === 'new' ? 'course' : 'name'"
						class="bhasha-program-list"
					>
						<ListHeader
							class="bhasha-program-list-header mb-2 grid items-center gap-x-4 p-2"
						>
							<ListHeaderItem :item="item" v-for="item in courseColumns" />
						</ListHeader>
						<ListRows>
							<Draggable
								:list="program.program_courses"
								:item-key="programName === 'new' ? 'course' : 'name'"
								group="items"
								@end="updateOrder"
								class="cursor-move"
							>
								<template #item="{ element: row }">
									<ListRow :row="row" />
								</template>
							</Draggable>
						</ListRows>
						<ListSelectBanner>
							<template #actions="{ unselectAll, selections }">
								<div class="flex gap-2">
									<Button
										variant="ghost"
										@click="remove(selections, unselectAll, 'courses')"
									>
										<Trash2 class="h-4 w-4 stroke-1.5" />
									</Button>
								</div>
							</template>
						</ListSelectBanner>
					</ListView>
					<div v-else class="bhasha-program-form-empty">
						<BookOpen class="size-5 stroke-1.5" />
						<div>
							<strong>{{ __('No courses added yet') }}</strong>
							<span>{{
								__('Add the first course to shape this learning path.')
							}}</span>
						</div>
					</div>
				</section>

				<section class="bhasha-program-form-section">
					<div class="bhasha-program-form-section-header">
						<div class="bhasha-program-form-section-heading">
							<div class="bhasha-program-form-section-icon" aria-hidden="true">
								<Users class="size-4 stroke-1.5" />
							</div>
							<div>
								<h4>{{ __('Members') }}</h4>
								<p>
									{{ __('Enroll learners now or return to add them later.') }}
								</p>
							</div>
						</div>

						<div class="bhasha-program-section-actions">
							<Button
								v-if="programMembers.data.length > 0"
								class="bhasha-program-add-button"
								variant="outline"
								@click="
									() => {
										showProgressDialog = true
									}
								"
							>
								<template #prefix>
									<TrendingUp class="size-4 stroke-1.5" />
								</template>
								{{ __('Progress Summary') }}
							</Button>
							<Button
								class="bhasha-program-add-button"
								variant="outline"
								@click="openForm('member')"
							>
								<template #prefix>
									<Plus class="size-4 stroke-2" />
								</template>
								{{ __('Add member') }}
							</Button>
						</div>
					</div>
					<ListView
						v-if="program.program_members?.length > 0"
						:columns="memberColumns"
						:rows="program.program_members"
						:options="{
							selectable: true,
							resizeColumn: true,
						}"
						:rowKey="programName === 'new' ? 'member' : 'name'"
						class="bhasha-program-list"
					>
						<ListHeader
							class="bhasha-program-list-header mb-2 grid items-center gap-x-4 p-2"
						>
							<ListHeaderItem :item="item" v-for="item in memberColumns" />
						</ListHeader>
						<ListRows>
							<ListRow :row="row" v-for="row in program.program_members" />
						</ListRows>
						<ListSelectBanner>
							<template #actions="{ unselectAll, selections }">
								<div class="flex gap-2">
									<Button
										variant="ghost"
										@click="remove(selections, unselectAll, 'members')"
									>
										<Trash2 class="h-4 w-4 stroke-1.5" />
									</Button>
								</div>
							</template>
						</ListSelectBanner>
					</ListView>
					<div v-else class="bhasha-program-form-empty">
						<Users class="size-5 stroke-1.5" />
						<div>
							<strong>{{ __('No members enrolled yet') }}</strong>
							<span>{{
								__('Add learners when this program is ready for them.')
							}}</span>
						</div>
					</div>
				</section>
			</div>
			<Dialog
				v-model="showFormDialog"
				:options="{
					title: addDialogTitle,
					size: 'lg',
				}"
			>
				<template #body-title>
					<div class="bhasha-dialog-heading">
						<div class="bhasha-dialog-icon" aria-hidden="true">
							<BookOpen
								v-if="currentForm === 'course'"
								class="size-5 stroke-1.75"
							/>
							<Users v-else class="size-5 stroke-1.75" />
						</div>
						<div>
							<h3 class="bhasha-dialog-title">{{ addDialogTitle }}</h3>
							<p class="bhasha-dialog-description">
								{{ addDialogDescription }}
							</p>
						</div>
					</div>
				</template>
				<template #body-content>
					<div class="bhasha-program-add-form" @click.stop>
						<Link
							v-if="currentForm == 'course'"
							v-model="course"
							doctype="LMS Course"
							:label="__('Course')"
							size="md"
							variant="outline"
						/>

						<Link
							v-if="currentForm == 'member'"
							v-model="member"
							doctype="User"
							:filters="{
								ignore_user_type: 1,
							}"
							:label="__('Program Member')"
							size="md"
							variant="outline"
							:onCreate="
								(value: string, close: () => void) =>
									openSettings('Members', close)
							"
						/>
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
							@click="
								currentForm === 'course' ? addCourse(close) : addMember(close)
							"
						>
							{{
								currentForm === 'course' ? __('Add course') : __('Add member')
							}}
						</Button>
					</div>
				</template>
			</Dialog>

			<ProgramProgressSummary
				v-model="showProgressDialog"
				:programName="programName"
				:programMembers="programMembers.data"
			/>
		</template>
		<template #actions="{ close }">
			<div class="bhasha-program-form-actions">
				<Button
					v-if="programName != 'new'"
					@click="deleteProgram(close)"
					variant="outline"
					theme="red"
					class="bhasha-program-delete-button"
				>
					<template #prefix>
						<Trash2 class="size-4 stroke-1.5" />
					</template>
					{{ __('Delete') }}
				</Button>
				<div class="bhasha-program-form-actions-right">
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
						:loading="saveLoading"
						@click="saveProgram(close)"
					>
						{{
							programName === 'new' ? __('Create program') : __('Save changes')
						}}
					</Button>
				</div>
			</div>
		</template>
	</Dialog>
</template>
<script setup lang="ts">
import {
	Button,
	createListResource,
	Dialog,
	FormControl,
	ListSelectBanner,
	ListView,
	ListHeader,
	ListHeaderItem,
	ListRows,
	ListRow,
	toast,
} from 'frappe-ui'
import { computed, ref, watch, getCurrentInstance } from 'vue'
import {
	BookOpen,
	Plus,
	Route,
	Trash2,
	TrendingUp,
	Users,
} from 'lucide-vue-next'
import { Programs, Program } from '@/types/programs'
import { sanitizeHTML, openSettings } from '@/utils'
import Link from '@/components/Controls/Link.vue'
import Draggable from 'vuedraggable'
import ProgramProgressSummary from '@/pages/Programs/ProgramProgressSummary.vue'

const show = defineModel<boolean>()
const programs = defineModel<Programs>('programs')
const showFormDialog = ref(false)
const currentForm = ref<'course' | 'member'>('course')
const course = ref<string>('')
const member = ref<string>('')
const showProgressDialog = ref(false)
const dirty = ref(false)

const dialogTitle = computed(() =>
	props.programName === 'new' ? __('Create program') : __('Edit program'),
)

const dialogDescription = computed(() =>
	props.programName === 'new'
		? __('Create a guided path, then add its courses and learners.')
		: __('Update the learning path, course sequence, and enrolled members.'),
)

const addDialogTitle = computed(() =>
	currentForm.value === 'course'
		? __('Add course to program')
		: __('Add member to program'),
)

const addDialogDescription = computed(() =>
	currentForm.value === 'course'
		? __('Choose a course to include in this learning path.')
		: __('Choose a learner to enroll in this program.'),
)

const saveLoading = computed(() =>
	props.programName === 'new'
		? Boolean(programs.value?.insert?.loading)
		: Boolean(programs.value?.setValue?.loading),
)

const app = getCurrentInstance()
const { $dialog } = app.appContext.config.globalProperties

const props = withDefaults(
	defineProps<{
		programName: string | null
	}>(),
	{
		programName: 'new',
	},
)

const program = ref<Program>({
	name: '',
	title: '',
	published: false,
	enforce_course_order: false,
	program_courses: [],
	program_members: [],
})

watch([() => props.programName, () => show.value], ([, isOpen]) => {
	if (!isOpen) return
	setProgramData()
	if (props.programName !== 'new') {
		fetchCourses()
		fetchMembers()
	}
})

const setProgramData = () => {
	let isNew = true
	programs.value?.data.forEach((p: Program) => {
		if (p.name === props.programName) {
			isNew = false
			program.value = { ...p }
		}
	})

	if (isNew) {
		program.value = {
			name: '',
			title: '',
			published: false,
			enforce_course_order: false,
			program_courses: [],
			program_members: [],
		}
	}
	dirty.value = false
}

const programCourses = createListResource({
	doctype: 'LMS Program Course',
	fields: ['course', 'course_title', 'name', 'idx'],
	cache: ['programCourses', props.programName],
	parent: 'LMS Program',
	orderBy: 'idx',
	onSuccess(data: ProgramCourse[]) {
		program.value.program_courses = data
	},
})

const programMembers = createListResource({
	doctype: 'LMS Program Member',
	fields: ['member', 'full_name', 'progress', 'name'],
	cache: ['programMembers', props.programName],
	parent: 'LMS Program',
	orderBy: 'creation desc',
	onSuccess(data: ProgramMember[]) {
		program.value.program_members = data
	},
})

const fetchCourses = () => {
	programCourses.update({
		filters: {
			parent: props.programName,
			parenttype: 'LMS Program',
			parentfield: 'program_courses',
		},
	})
	programCourses.reload()
}

const fetchMembers = () => {
	programMembers.update({
		filters: {
			parent: props.programName,
			parenttype: 'LMS Program',
			parentfield: 'program_members',
		},
	})
	programMembers.reload()
}

const validateTitle = () => {
	program.value.name = sanitizeHTML(program.value.name.trim())
	if (!program.value.name) {
		toast.warning(__('Please enter a program title'))
		return false
	}
	return true
}

const saveProgram = (close: () => void) => {
	if (!validateTitle()) return
	if (props.programName === 'new') createNewProgram(close)
	else updateProgram(close)
}

const createNewProgram = (close: () => void) => {
	programs.value.insert.submit(
		{
			...program.value,
			title: program.value.name,
		},
		{
			onSuccess() {
				dirty.value = false
				close()
				programs.value.reload()
				toast.success(__('Program created successfully'))
			},
			onError(err: any) {
				toast.warning(__(err.messages?.[0] || err))
			},
		},
	)
}

const updateProgram = (close: () => void) => {
	programs.value.setValue.submit(
		{
			name: props.programName,
			...program.value,
		},
		{
			onSuccess() {
				dirty.value = false
				close()
				programs.value.reload()
				toast.success(__('Program updated successfully'))
			},
			onError(err: any) {
				toast.warning(__(err.messages?.[0] || err))
			},
		},
	)
}

const openForm = (formType: 'course' | 'member') => {
	currentForm.value = formType
	showFormDialog.value = true
	if (formType === 'course') {
		course.value = ''
	} else {
		member.value = ''
	}
}

const addCourse = (close: () => void) => {
	if (!course.value) {
		toast.warning(__('Please select a course'))
		return
	}

	const existingCourse = program.value.program_courses.find(
		(c: any) => c.course === course.value,
	)
	if (!existingCourse) {
		program.value.program_courses.push({
			course: course.value,
			idx: program.value.program_courses.length + 1,
		})
		dirty.value = true
		close()
		toast.success(__('Course added to program successfully'))
	} else {
		toast.warning(__('Course already added to program'))
	}
}

const addMember = (close: () => void) => {
	if (!member.value) {
		toast.warning(__('Please select a member'))
		return
	}

	const existingMember = program.value.program_members.find(
		(m) => m.member === member.value,
	)
	if (!existingMember) {
		program.value.program_members.push({
			member: member.value,
		})
		dirty.value = true
		close()
		toast.success(__('Member added to program successfully'))
	} else {
		toast.warning(__('Member already added to program'))
	}
}

const updateCounts = async (
	type: 'member' | 'course',
	action: 'add' | 'remove',
) => {
	if (!props.programName) return

	let memberCount = programMembers.data?.length || 0
	let courseCount = programCourses.data?.length || 0

	if (type === 'member') {
		memberCount += action === 'add' ? 1 : -1
	} else {
		courseCount += action === 'add' ? 1 : -1
	}

	await programs.value.setValue.submit(
		{
			name: props.programName,
			member_count: memberCount,
			course_count: courseCount,
		},
		{
			onSuccess() {
				setProgramData()
			},
			onError(err: any) {
				toast.warning(__(err.messages?.[0] || err))
			},
		},
	)
}

const updateOrder = async (e: DragEvent) => {
	let sourceIdx = e.from.dataset.idx
	let targetIdx = e.to.dataset.idx

	if (props.programName === 'new') {
		let courses = program.value.program_courses
		courses.splice(targetIdx, 0, courses.splice(sourceIdx, 1)[0])
		courses.forEach((course, index) => {
			course.idx = index + 1
		})
		dirty.value = true
	} else {
		let courses = programCourses.data
		courses.splice(targetIdx, 0, courses.splice(sourceIdx, 1)[0])

		for (const [index, course] of courses.entries()) {
			programCourses.setValue.submit(
				{
					name: course.name,
					idx: index + 1,
				},
				{
					onError(err: any) {
						toast.warning(__(err.messages?.[0] || err))
					},
				},
			)
			await wait(100)
		}
	}
}

const wait = (ms: number) => new Promise((res) => setTimeout(res, ms))

const remove = (
	selections: string[],
	unselectAll: () => void,
	type: string,
) => {
	const selectionsArray = Array.from(selections)
	if (type === 'courses') {
		program.value.program_courses = program.value.program_courses.filter(
			(c: any) => !selectionsArray.includes(c.name || c.course),
		)
	} else {
		program.value.program_members = program.value.program_members.filter(
			(m: any) => !selectionsArray.includes(m.name || m.member),
		)
	}
	dirty.value = true
	unselectAll()
}

const deleteProgram = (close: () => void) => {
	if (props.programName == 'new') return
	$dialog({
		title: __('Delete Program'),
		message: __(
			'Are you sure you want to delete this program? This action cannot be undone.',
		),
		actions: [
			{
				label: __('Delete'),
				theme: 'red',
				variant: 'solid',
				onClick(closeDialog) {
					programs.value?.delete.submit(props.programName, {
						onSuccess() {
							toast.success(__('Program deleted successfully'))
							close()
							closeDialog()
						},
						onError(err: any) {
							toast.warning(__(err.messages?.[0] || err))
							closeDialog()
						},
					})
				},
			},
		],
	})
}

const courseColumns = computed(() => {
	return [
		{
			label: 'Title',
			key: props.programName === 'new' ? 'course' : 'course_title',
			width: 1,
		},
	]
})

const memberColumns = computed(() => {
	return [
		{
			label: 'Member',
			key: 'member',
			width: 3,
			align: 'left',
		},
		{
			label: 'Full Name',
			key: 'full_name',
			width: 3,
			align: 'left',
		},
	]
})
</script>
