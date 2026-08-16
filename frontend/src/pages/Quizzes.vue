<template>
	<LayoutHeader>
		<template #left-header>
			<Breadcrumbs :items="breadcrumbs" />
		</template>
		<template #right-header>
			<Button
				v-if="!readOnlyMode"
				variant="solid"
				class="bhasha-primary bhasha-assessment-create-button"
				@click="showForm = true"
			>
				<template #prefix>
					<Plus class="size-4 stroke-2" />
				</template>
				{{ __('Create quiz') }}
			</Button>
		</template>
	</LayoutHeader>

	<main class="bhasha-assessments-page flex min-h-0 flex-1 flex-col">
		<section class="bhasha-assessments-toolbar">
			<div class="bhasha-assessments-toolbar-heading">
				<div>
					<h1 class="bhasha-assessments-title">{{ __('Manage quizzes') }}</h1>
					<p class="bhasha-assessments-description">
						{{
							__(
								'Create reusable knowledge checks, set scoring rules, and review learner attempts.',
							)
						}}
					</p>
				</div>
				<div
					v-if="!quizzes.list.loading && quizzes.data?.length"
					class="bhasha-assessment-result-count"
					aria-live="polite"
				>
					{{ quizzes.data.length }}{{ quizzes.hasNextPage ? '+' : '' }}
					{{ quizzes.data.length === 1 ? __('quiz') : __('quizzes') }}
				</div>
			</div>
			<FormControl
				v-model="search"
				type="text"
				:placeholder="__('Search quizzes')"
				size="md"
				variant="outline"
				class="bhasha-assessment-search"
			>
				<template #prefix>
					<Search class="size-4 stroke-1.5 text-ink-gray-5" />
				</template>
				<template v-if="search" #suffix>
					<button
						type="button"
						class="bhasha-assessment-search-clear"
						:aria-label="__('Clear search')"
						@click="search = ''"
					>
						<X class="size-3.5 stroke-2" />
					</button>
				</template>
			</FormControl>
		</section>
		<section
			v-if="quizzes.data?.length"
			class="bhasha-assessment-list-shell"
		>
			<ListView
				:columns="quizColumns"
				:rows="quizzes.data"
				row-key="name"
				:options="{ showTooltip: false, selectable: true }"
				class="bhasha-assessment-list flex-1 overflow-y-auto"
			>
				<ListHeader class="bhasha-assessment-list-header grid items-center p-2">
					<ListHeaderItem :item="item" v-for="item in quizColumns">
						<template #prefix="{ item }">
							<FeatherIcon
								:name="item.icon?.toString()"
								class="h-4 w-4"
							/>
						</template>
					</ListHeaderItem>
				</ListHeader>
				<ListRows>
					<router-link
						v-for="row in quizzes.data"
						:key="row.name"
						:to="{
							name: 'QuizForm',
							params: {
								quizID: row.name,
							},
						}"
					>
						<ListRow :row="row" class="bhasha-assessment-list-row">
							<template #default="{ column }">
								<ListRowItem :item="row[column.key]" :align="column.align">
									<div v-if="column.key == 'show_answers'">
										<Checkbox v-model="row[column.key]" :disabled="true" />
									</div>
									<div
										v-else-if="column.key == 'modified'"
										class="text-sm text-ink-gray-5"
									>
										{{ row[column.key] }}
									</div>
									<div v-else>
										{{ row[column.key] }}
									</div>
								</ListRowItem>
							</template>
						</ListRow>
					</router-link>
				</ListRows>
				<ListSelectBanner class="bottom-50">
					<template #actions="{ unselectAll, selections }">
						<div class="flex gap-2">
							<Button
								variant="ghost"
								@click="deleteQuiz(selections, unselectAll)"
							>
								<FeatherIcon name="trash-2" class="h-4 w-4 stroke-1.5" />
							</Button>
						</div>
					</template>
				</ListSelectBanner>
			</ListView>
		</section>
		<section v-else-if="!quizzes.list.loading" class="bhasha-assessments-empty">
			<div class="bhasha-assessments-empty-icon">
				<CircleHelp class="size-6 stroke-1.5" />
			</div>
			<h2>{{ search ? __('No matching quizzes') : __('Create your first quiz') }}</h2>
			<p>
				{{
					search
						? __('Try another search term or clear the current search.')
						: __('Build a reusable assessment and add questions, scoring, and attempt rules.')
				}}
			</p>
			<Button v-if="search" class="mt-2" @click="search = ''">
				{{ __('Clear search') }}
			</Button>
			<Button
				v-else-if="!readOnlyMode"
				variant="solid"
				class="bhasha-primary mt-2"
				@click="showForm = true"
			>
				<template #prefix><Plus class="size-4 stroke-2" /></template>
				{{ __('Create quiz') }}
			</Button>
		</section>
		<ListFooter
			v-model="pageLength"
			v-if="quizzes.data?.length"
			class="bhasha-assessment-footer"
			:options="{
				rowCount: quizzes.data?.length,
				totalCount: totalQuizzes.data,
			}"
		>
			<template #right>
				<div class="flex items-center">
					<Button
						v-if="quizzes.hasNextPage"
						:label="__('Load More')"
						@click="quizzes.next()"
					/>
					<div v-if="quizzes.hasNextPage" class="mx-3 h-[80%] border-l" />
					<div class="flex items-center gap-1 text-base text-ink-gray-5">
						<div>{{ quizzes.data?.length || 0 }}</div>
						<div>{{ __('of') }}</div>
						<div>{{ totalQuizzes.data || 0 }}</div>
					</div>
				</div>
			</template>
		</ListFooter>
	</main>
	<Dialog
		v-model="showForm"
		:options="{
			title: __('Create a Quiz'),
			size: 'lg',
		}"
	>
		<template #body-title>
			<div class="bhasha-dialog-heading">
				<div class="bhasha-dialog-icon" aria-hidden="true">
					<CircleHelp class="size-5 stroke-1.75" />
				</div>
				<div>
					<h3 class="bhasha-dialog-title">{{ __('Create a new quiz') }}</h3>
					<p class="bhasha-dialog-description">
						{{
							__(
								'Start with a clear title. You will add questions and scoring rules on the next screen.',
							)
						}}
					</p>
				</div>
			</div>
		</template>
		<template #body-content>
			<div class="bhasha-assessment-quick-form">
				<FormControl
					v-model="title"
					:label="__('Quiz title')"
					:placeholder="__('e.g. Module 1 knowledge check')"
					type="text"
					:required="true"
					autocomplete="off"
					size="md"
					variant="outline"
					@keydown.enter="insertQuiz(() => (showForm = false))"
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
					:loading="quizzes.insert.loading"
					@click="insertQuiz(close)"
				>
					{{ __('Continue to questions') }}
				</Button>
			</div>
		</template>
	</Dialog>
</template>
<script setup>
import {
	Breadcrumbs,
	Button,
	createListResource,
	createResource,
	Dialog,
	FeatherIcon,
	FormControl,
	ListView,
	ListRows,
	ListRow,
	ListRowItem,
	ListHeader,
	ListHeaderItem,
	ListFooter,
	ListSelectBanner,
	toast,
	usePageMeta,
	Checkbox,
} from 'frappe-ui'
import { useRouter, useRoute } from 'vue-router'
import { computed, inject, onMounted, ref, watch } from 'vue'
import { CircleHelp, Plus, Search, X } from 'lucide-vue-next'
import { sessionStore } from '@/stores/session'
import { sanitizeHTML } from '@/utils'
import { useTelemetry } from 'frappe-ui/frappe'
import LayoutHeader from '@/components/Layouts/LayoutHeader.vue'
import '@/styles/assessment-management.css'

const { brand } = sessionStore()
const { capture } = useTelemetry()
const user = inject('$user')
const dayjs = inject('$dayjs')
const router = useRouter()
const route = useRoute()
const search = ref('')
const readOnlyMode = window.read_only_mode
const quizFilters = ref({})
const showForm = ref(false)
const title = ref('')

onMounted(() => {
	if (
		!user.data?.is_moderator &&
		!user.data?.is_instructor &&
		!user.data?.is_evaluator
	) {
		router.push({ name: 'Courses' })
	}
	if (route.query.new === 'true') {
		showForm.value = true
	}
})

watch(search, () => {
	quizFilters.value['title'] = ['like', `%${search.value}%`]
	quizzes.update({
		filters: quizFilters.value,
	})
	quizzes.reload()
	totalQuizzes.update({
		filters: quizFilters.value,
	})
	totalQuizzes.reload()
})

const quizzes = createListResource({
	doctype: 'LMS Quiz',
	filters: quizFilters,
	fields: [
		'name',
		'title',
		'passing_percentage',
		'total_marks',
		'show_answers',
		'max_attempts',
		'modified',
	],
	auto: true,
	cache: ['quizzes', user.data?.name],
	orderBy: 'modified desc',
	transform(data) {
		return data.map((quiz) => {
			return {
				...quiz,
				modified: dayjs(quiz.modified).format('DD MMM YYYY'),
			}
		})
	},
})

const pageLength = computed({
	get: () => quizzes.pageLength,
	set: (value) => {
		quizzes.update({ pageLength: value })
		quizzes.reload()
	},
})

const totalQuizzes = createResource({
	url: 'frappe.client.get_count',
	params: {
		doctype: 'LMS Quiz',
		filters: quizFilters.value,
	},
	auto: true,
	cache: ['quizzes_count', user.data?.name],
	onError(err) {
		toast.error(err.messages?.[0] || err)
		console.error(err)
	},
})

const validateTitle = () => {
	title.value = sanitizeHTML(title.value.trim())
}

const insertQuiz = (close) => {
	validateTitle()
	if (!title.value) {
		toast.error(__('Quiz title is required'))
		return
	}
	quizzes.insert.submit(
		{
			title: title.value,
		},
		{
			onSuccess(data) {
				toast.success(__('Quiz created successfully'))
				close()
				title.value = ''
				capture('quiz_created')
				router.push({
					name: 'QuizForm',
					params: {
						quizID: data.name,
					},
				})
			},
			onError(error) {
				toast.error(__('Error creating quiz: {0}', error.message))
			},
		}
	)
}

const deleteQuiz = (selections, unselectAll) => {
	Array.from(selections).forEach(async (quizName) => {
		await quizzes.delete.submit(quizName)
	})
	unselectAll()
	toast.success(__('Quizzes deleted successfully'))
}

const quizColumns = computed(() => {
	return [
		{
			label: __('Title'),
			key: 'title',
			width: 2,
			icon: 'file-text',
		},
		{
			label: __('Total Marks'),
			key: 'total_marks',
			width: 0.5,
			align: 'center',
			icon: 'hash',
		},
		{
			label: __('Passing Percentage'),
			key: 'passing_percentage',
			width: 1,
			align: 'center',
			icon: 'percent',
		},
		{
			label: __('Max Attempts'),
			key: 'max_attempts',
			width: 0.5,
			align: 'center',
			icon: 'repeat',
		},
		{
			label: __('Show Answers'),
			key: 'show_answers',
			width: 0.5,
			align: 'center',
			icon: 'eye',
		},
		{
			label: __('Updated On'),
			key: 'modified',
			width: 1,
			align: 'right',
			icon: 'clock',
		},
	]
})

const breadcrumbs = computed(() => {
	return [
		{
			label: __('Quizzes'),
			route: {
				name: 'Quizzes',
			},
		},
	]
})

usePageMeta(() => {
	return {
		title: __('Quizzes'),
		icon: brand.favicon,
	}
})
</script>
