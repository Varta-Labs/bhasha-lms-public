<template>
	<Dialog
		v-model="show"
		:options="{
			title: __('New Course'),
			size: '3xl',
		}"
	>
		<template #body-title>
			<div class="bhasha-dialog-heading">
				<div class="bhasha-dialog-icon" aria-hidden="true">
					<BookOpen class="size-5 stroke-1.75" />
				</div>
				<div>
					<h3 class="bhasha-dialog-title">{{ __('Create a new course') }}</h3>
					<p class="bhasha-dialog-description">
						{{
							__(
								'Add the course essentials now. You can build the curriculum and publishing settings next.',
							)
						}}
					</p>
				</div>
			</div>
		</template>
		<template #body-content>
			<div class="bhasha-course-form text-base">
				<div class="bhasha-course-form-grid">
					<FormControl
						v-model="course.title"
						:label="__('Title')"
						:required="true"
						autocomplete="off"
						size="md"
						variant="outline"
					/>
					<Link
						v-model="course.category"
						doctype="LMS Category"
						:label="__('Category')"
						:inlineCreate="true"
						:onCreate="createCategory"
						size="md"
						variant="outline"
					/>
					<MultiLink
						ref="instructorsRef"
						v-model="course.instructors"
						class="bhasha-instructor-field"
						doctype="User"
						url="lms.lms.api.search_users_by_role"
						:searchParams="{ roles: JSON.stringify(INSTRUCTOR_ROLES) }"
						:transform="transformUsers"
						:extraOptions="resolvedSelected"
						:label="__('Instructors')"
						:placeholder="__('Select instructors')"
						:required="true"
						:onCreate="openMemberModal"
						variant="outline"
					>
						<template #prefix>
							<div v-if="visibleAvatars.length" class="flex -space-x-1.5">
								<Avatar
									v-for="m in visibleAvatars"
									:key="m.value"
									:image="m.image"
									:label="m.label"
									size="sm"
								/>
								<span
									v-if="overflowCount > 0"
									class="z-10 grid size-5 place-items-center rounded-full bg-surface-gray-3 text-xs font-medium text-ink-gray-7"
								>
									+{{ overflowCount }}
								</span>
							</div>
							<Users v-else class="size-4 stroke-1.5 text-ink-gray-5" />
						</template>
						<template #item-prefix="{ item }">
							<Avatar :image="item.image" :label="item.label" size="sm" />
						</template>
						<template #item-label="{ item }">
							<div class="min-w-0 flex justify-between gap-2">
								<div class="truncate">{{ item.label }}</div>
								<div class="truncate text-xs text-ink-gray-5">
									{{ item.value }}
								</div>
							</div>
						</template>
					</MultiLink>
					<Uploader
						v-model="course.image"
						class="bhasha-course-thumbnail-field"
						:label="__('Course thumbnail')"
						:required="false"
						:description="thumbnailGuidelines"
					/>
				</div>
				<div class="bhasha-course-form-details">
					<FormControl
						v-model="course.short_introduction"
						:label="__('Short introduction')"
						type="textarea"
						:required="true"
						:rows="4"
						size="md"
						variant="outline"
					/>
					<div class="bhasha-course-description space-y-1.5">
						<FormLabel
							:label="__('Course description')"
							:id="descriptionId"
							:required="true"
						/>
						<TextEditor
							:id="descriptionId"
							class="bhasha-course-description-editor"
							:content="course.description"
							@change="(val: string) => (course.description = val)"
							:editable="true"
							:fixedMenu="true"
							editorClass="prose-sm max-w-none border-b border-x border-outline-gray-modals bg-surface-gray-2 rounded-b-md py-1 px-2 min-h-[10rem] max-h-[17rem] overflow-auto"
						/>
					</div>
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
					:loading="props.courses.insert.loading"
					@click="saveCourse(close)"
				>
					{{ __('Create course') }}
				</Button>
			</div>
		</template>
	</Dialog>
	<NewMemberModal
		v-model="showMemberModal"
		:defaultRoles="['course_creator']"
		@created="onInstructorCreated"
	/>
</template>

<script setup lang="ts">
import {
	Avatar,
	Button,
	Dialog,
	FormControl,
	FormLabel,
	TextEditor,
	createResource,
	toast,
} from 'frappe-ui'
import { useOnboarding, useTelemetry } from 'frappe-ui/frappe'
import { BookOpen, Users } from 'lucide-vue-next'
import {
	computed,
	inject,
	onBeforeUnmount,
	onMounted,
	ref,
	useId,
	watch,
} from 'vue'
import { useRouter } from 'vue-router'
import Link from '@/components/Controls/Link.vue'
import MultiLink from '@/components/Controls/MultiLink.vue'
import Uploader from '@/components/Controls/Uploader.vue'
import NewMemberModal from '@/components/Modals/NewMemberModal.vue'
import { cleanError, sanitizeHTML, createLMSCategory } from '@/utils'
import type { Resource } from '@/types/api'

interface InstructorOption {
	label: string
	value: string
	image: string
	description: string
}
interface RawUserHit {
	label?: string
	value?: string
	name?: string
	user_image?: string
	description?: string
}

const show = defineModel<boolean>({ required: true, default: false })
const router = useRouter()
const { capture } = useTelemetry()
const { updateOnboardingStep } = useOnboarding('learning')
const user = inject<any>('$user')
const courseCreated = ref(false)
const showMemberModal = ref<boolean>(false)

const props = defineProps<{
	courses: any
}>()

type Course = {
	title: string
	short_introduction: string
	description: string
	instructors: string[]
	category?: string
	image?: string
}

const course = ref<Course>({
	title: '',
	short_introduction: '',
	description: '',
	instructors: [],
	category: undefined,
	image: undefined,
})

const INSTRUCTOR_ROLES = ['Course Creator', 'Batch Evaluator']
const MAX_VISIBLE_AVATARS = 3
const thumbnailGuidelines = __(
	'Upload a 750×422 image (.jpg, .jpeg, .gif, or .png) — shown on the catalog card and lesson hero.'
)
const descriptionId = useId()

const instructorsRef = ref<{
	optionByValue: Map<string, InstructorOption>
	reload: () => void
} | null>(null)

function transformUsers(rows: Record<string, unknown>[]): InstructorOption[] {
	return (rows as RawUserHit[]).map((o) => ({
		label: o.label || o.value || o.name || '',
		value: o.value || o.name || '',
		image: o.user_image || '',
		description: o.description || o.value || '',
	}))
}

// Hydrate avatars/names for instructor IDs that aren't in the dropdown's
// current result set (e.g. after a fresh-created member was just added).
const resolvedDetails = ref<Map<string, InstructorOption>>(new Map())

const selectedDetails = createResource({
	url: 'lms.lms.api.search_users_by_role',
	method: 'POST',
	makeParams: () => ({
		roles: JSON.stringify(INSTRUCTOR_ROLES),
		names: JSON.stringify(course.value.instructors),
	}),
	onSuccess(rows: RawUserHit[]) {
		const next = new Map(resolvedDetails.value)
		for (const u of rows) {
			const value = u.value || u.name || ''
			if (!value) continue
			next.set(value, {
				label: u.label || u.description || value,
				value,
				image: u.user_image || '',
				description: u.description || value,
			})
		}
		resolvedDetails.value = next
	},
}) as Resource<RawUserHit[] | null>

watch(
	() => course.value.instructors,
	(vals) => {
		const missing = (vals || []).filter((v) => !resolvedDetails.value.has(v))
		if (missing.length) selectedDetails.reload()
	}
)

const resolvedSelected = computed<InstructorOption[]>(() =>
	course.value.instructors
		.map((v) => resolvedDetails.value.get(v))
		.filter((o): o is InstructorOption => Boolean(o))
)

const optionByValue = computed<Map<string, InstructorOption>>(() => {
	const merged = new Map<string, InstructorOption>(resolvedDetails.value)
	const fromMultiLink = instructorsRef.value?.optionByValue
	if (fromMultiLink) fromMultiLink.forEach((v, k) => merged.set(k, v))
	return merged
})

const visibleAvatars = computed<InstructorOption[]>(() =>
	course.value.instructors
		.slice(0, MAX_VISIBLE_AVATARS)
		.map(
			(v) =>
				optionByValue.value.get(v) ||
				({
					value: v,
					label: v,
					image: '',
					description: '',
				} as InstructorOption)
		)
		.filter((o): o is InstructorOption => Boolean(o))
)

const overflowCount = computed<number>(() =>
	Math.max(0, course.value.instructors.length - MAX_VISIBLE_AVATARS)
)

function openMemberModal(close: () => void) {
	close()
	showMemberModal.value = true
}

const createCategory = (name: string, done: () => void) => {
	createLMSCategory(name).then((categoryName: string) => {
		if (!categoryName) return
		course.value.category = categoryName
		done()
	})
}

const onInstructorCreated = (newUser: any) => {
	course.value.instructors = [...course.value.instructors, newUser.name]
	instructorsRef.value?.reload()
}

const validateFields = () => {
	Object.keys(course.value).forEach((key) => {
		if (typeof course.value[key as keyof Course] === 'string') {
			course.value[key as keyof Course] = sanitizeHTML(
				course.value[key as keyof Course] as string
			)
		}
	})
}

const saveCourse = (close: () => void = () => {}) => {
	validateFields()
	props.courses.insert.submit(
		{
			...course.value,
			instructors: course.value.instructors.map((instructor) => ({
				instructor: instructor,
			})),
		},
		{
			onSuccess(data: any) {
				toast.success(__('Course created successfully'))
				close()
				capture('course_created')
				courseCreated.value = true
				router.push({
					name: 'CourseDetail',
					params: { courseName: data.name },
					hash: '#settings',
				})
				if (user.data?.is_system_manager) {
					updateOnboardingStep('create_first_course', true, false, () => {
						localStorage.setItem('firstCourse', data.name)
					})
				}
			},
			onError(err: any) {
				toast.error(cleanError(err.messages?.[0]))
				console.error(err)
			},
		}
	)
}

const keyboardShortcut = (e: KeyboardEvent) => {
	if (
		e.key === 's' &&
		(e.ctrlKey || e.metaKey) &&
		e.target &&
		e.target instanceof HTMLElement &&
		!e.target.classList.contains('ProseMirror')
	) {
		saveCourse()
		e.preventDefault()
	}
}

onMounted(() => {
	window.addEventListener('keydown', keyboardShortcut)
	capture('course_form_opened')
})

onBeforeUnmount(() => {
	window.removeEventListener('keydown', keyboardShortcut)
	if (!courseCreated.value) {
		capture('course_form_closed', {
			data: course.value,
		})
	}
})
</script>

<style>
.bhasha-course-form,
.bhasha-course-form-grid {
	min-width: 0;
	max-width: 100%;
}

.bhasha-course-form-grid {
	display: grid;
	grid-template-columns: repeat(2, minmax(0, 1fr));
	gap: 1.25rem;
	padding-bottom: 1.5rem;
	border-bottom: 1px solid var(--bhasha-border-brand);
}

.bhasha-course-form-details {
	display: grid;
	min-width: 0;
	max-width: 100%;
	gap: 1.25rem;
	padding-top: 1.5rem;
}

.bhasha-course-description,
.bhasha-course-description-editor {
	width: 100%;
	min-width: 0;
	max-width: 100%;
}

.bhasha-course-description-editor {
	overflow: hidden;
}

.bhasha-course-description-editor > [class~='overflow-x-auto'] {
	width: 100%;
	max-width: 100%;
	overscroll-behavior-x: contain;
	scrollbar-width: thin;
}

.bhasha-instructor-field > button {
	min-height: 2rem;
	border-radius: var(--bhasha-radius-control);
}

.bhasha-course-thumbnail-field > div:first-child {
	color: var(--bhasha-text-muted);
}

.bhasha-course-thumbnail-field [class*='aspect-'] {
	border-color: var(--bhasha-border-brand);
	border-radius: var(--bhasha-radius-control);
	background: var(--bhasha-50);
}

@media (max-width: 767px) {
	.bhasha-course-form-grid {
		grid-template-columns: minmax(0, 1fr);
	}
}
</style>
