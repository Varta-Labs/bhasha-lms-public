<template>
	<LayoutHeader>
		<template #left-header>
			<Breadcrumbs :items="breadcrumbs" />
		</template>
		<template #right-header>
			<Dropdown
				placement="right"
				side="bottom"
				v-if="canCreateBatch()"
				:options="batchMenu"
			>
				<template v-slot="{ open }">
					<Button
						variant="solid"
						class="bhasha-primary bhasha-batch-create-button"
					>
						<template #prefix>
							<Plus class="size-4 stroke-2" />
						</template>
						{{ __('Create batch') }}
						<template #suffix>
							<ChevronDown
								:class="[
									'ms-1 size-4 transform stroke-1.5 transition-transform',
									open ? 'rotate-180' : '',
								]"
							/>
						</template>
					</Button>
				</template>
			</Dropdown>
		</template>
	</LayoutHeader>
	<main class="bhasha-batches-page flex min-h-0 flex-1 flex-col">
		<section class="bhasha-batches-toolbar">
			<div class="bhasha-batches-toolbar-heading">
				<div>
					<h1 class="bhasha-batches-title">{{ pageHeading }}</h1>
					<p class="bhasha-batches-description">{{ pageDescription }}</p>
				</div>
				<div
					v-if="!batches.list.loading && batches.data?.length"
					class="bhasha-batch-result-count"
					aria-live="polite"
				>
					{{ batches.data.length }}{{ batches.hasNextPage ? '+' : '' }}
					{{ batches.data.length === 1 ? __('batch') : __('batches') }}
				</div>
			</div>

			<div v-if="user.data" class="bhasha-batch-tabs-scroll">
				<div
					class="bhasha-batch-tabs"
					role="group"
					:aria-label="__('Batch status')"
				>
					<button
						v-for="tab in batchTabs"
						:key="tab.value"
						type="button"
						class="bhasha-batch-tab"
						:class="{ 'is-active': currentTab === tab.value }"
						:aria-pressed="currentTab === tab.value"
						@click="currentTab = tab.value"
					>
						{{ tab.label }}
					</button>
				</div>
			</div>

			<div class="bhasha-batch-filters">
				<FormControl
					v-model="title"
					:placeholder="__('Search batches')"
					type="text"
					size="md"
					variant="outline"
					class="bhasha-batch-search"
					@input="debouncedUpdateBatches"
				>
					<template #prefix>
						<Search class="size-4 stroke-1.5 text-ink-gray-5" />
					</template>
					<template v-if="title" #suffix>
						<button
							type="button"
							class="bhasha-batch-search-clear"
							:aria-label="__('Clear search')"
							@click="clearSearch"
						>
							<X class="size-3.5 stroke-2" />
						</button>
					</template>
				</FormControl>

				<Select
					v-if="categories.length"
					v-model="currentCategory"
					:options="categories"
					:placeholder="__('All categories')"
					size="md"
					variant="outline"
					class="bhasha-batch-category-filter"
					@update:modelValue="updateBatches()"
				/>

				<button
					type="button"
					class="bhasha-batch-filter-toggle"
					:class="{ 'is-active': certification }"
					:aria-pressed="certification"
					:title="__('Only show batches that offer a certificate')"
					@click="toggleCertification"
				>
					<GraduationCap class="size-4 stroke-1.5" />
					{{ __('Certificate') }}
				</button>

				<button
					v-if="hasActiveFilters"
					type="button"
					class="bhasha-batch-clear-filters"
					@click="resetFilters"
				>
					<X class="size-3.5 stroke-2" />
					{{ __('Clear filters') }}
				</button>
			</div>
		</section>
		<div
			v-if="batches.data?.length"
			class="bhasha-batch-grid-shell bhasha-batch-grid"
		>
			<router-link
				v-for="batch in batches.data"
				:key="batch.name"
				:to="{ name: 'BatchDetail', params: { batchName: batch.name } }"
			>
				<BatchCard :batch="batch" />
			</router-link>
		</div>
		<section v-else-if="!batches.list.loading" class="bhasha-batches-empty">
			<div class="bhasha-batches-empty-icon">
				<UsersRound class="size-6 stroke-1.5" />
			</div>
			<h2>{{ emptyStateTitle }}</h2>
			<p>{{ emptyStateDescription }}</p>
			<Button v-if="hasActiveFilters" class="mt-2" @click="resetFilters">
				{{ __('Clear filters') }}
			</Button>
		</section>

		<div
			v-if="!batches.list.loading && batches.hasNextPage"
			class="mt-5 flex justify-center"
		>
			<Button class="bhasha-batch-load-more" @click="batches.next()">
				{{ __('Load More') }}
			</Button>
		</div>
	</main>
	<NewBatchModal
		v-if="showBatchModal"
		v-model="showBatchModal"
		:batches="batches"
	/>
</template>
<script setup>
import {
	Breadcrumbs,
	Button,
	createListResource,
	Dropdown,
	FormControl,
	usePageMeta,
} from 'frappe-ui'
import Select from '@/components/Controls/Select.vue'
import { computed, inject, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
	ChevronDown,
	GraduationCap,
	Plus,
	Search,
	UsersRound,
	X,
} from 'lucide-vue-next'
import { useDebounceFn } from '@vueuse/core'
import { sessionStore } from '@/stores/session'
import BatchCard from '@/pages/Batches/components/BatchCard.vue'
import LayoutHeader from '@/components/Layouts/LayoutHeader.vue'
import NewBatchModal from '@/pages/Batches/components/NewBatchModal.vue'
import '@/styles/batch-management.css'

const user = inject('$user')
const dayjs = inject('$dayjs')
const { brand } = sessionStore()
const start = ref(0)
const pageLength = ref(20)
const categories = ref([])
const currentCategory = ref(null)
const title = ref('')
const certification = ref(false)
const filters = ref({})
const is_student = computed(() => user.data?.is_student)
const currentTab = ref(is_student.value ? 'all' : 'upcoming')
const orderBy = ref('start_date')
const readOnlyMode = window.read_only_mode
const router = useRouter()
const showBatchModal = ref(false)

onMounted(() => {
	setFiltersFromQuery()
	updateBatches()
	categories.value = [
		{
			label: '',
			value: null,
		},
	]
})

const setFiltersFromQuery = () => {
	let queries = new URLSearchParams(location.search)
	title.value = queries.get('title') || ''
	currentCategory.value = queries.get('category') || null
	certification.value = ['1', 'true'].includes(queries.get('certification'))
}

const batches = createListResource({
	doctype: 'LMS Batch',
	url: 'lms.lms.utils.get_batches',
	cache: ['batches', user.data?.name],
	pageLength: pageLength.value,
	start: start.value,
})

const setCategories = (data) => {
	let allCategories = data.map((batch) => batch.category)
	allCategories = allCategories.filter(
		(category, index) => allCategories.indexOf(category) === index && category,
	)
	if (categories.value.length <= allCategories.length) {
		updateCategories(data)
	}
}

const updateBatches = () => {
	updateFilters()
	batches.update({
		filters: filters.value,
		orderBy: orderBy.value,
	})
	batches.reload().then((data) => {
		setCategories(data)
	})
}

const debouncedUpdateBatches = useDebounceFn(updateBatches, 300)

const clearSearch = () => {
	title.value = ''
	updateBatches()
}

const toggleCertification = () => {
	certification.value = !certification.value
	updateBatches()
}

const resetFilters = () => {
	title.value = ''
	currentCategory.value = null
	certification.value = false
	updateBatches()
}

const updateFilters = () => {
	updateCategoryFilter()
	updateTitleFilter()
	updateCertificationFilter()
	updateTabFilter()
	updateStudentFilter()
	setQueryParams()
}

const updateCategoryFilter = () => {
	if (currentCategory.value) {
		filters.value['category'] = currentCategory.value
	} else {
		delete filters.value['category']
	}
}

const updateTitleFilter = () => {
	if (title.value) {
		filters.value['title'] = ['like', `%${title.value}%`]
	} else {
		delete filters.value['title']
	}
}

const updateCertificationFilter = () => {
	if (certification.value) {
		filters.value['certification'] = 1
	} else {
		delete filters.value['certification']
	}
}

const updateTabFilter = () => {
	orderBy.value = 'start_date'
	if (!user.data) {
		return
	}
	if (currentTab.value == 'enrolled' && is_student.value) {
		filters.value['enrolled'] = 1
		delete filters.value['start_date']
		delete filters.value['published']
		orderBy.value = 'start_date desc'
	} else if (is_student.value) {
		delete filters.value['enrolled']
	} else {
		delete filters.value['start_date']
		delete filters.value['published']
		orderBy.value = 'start_date desc'
		if (currentTab.value == 'upcoming') {
			filters.value['start_date'] = ['>=', dayjs().format('YYYY-MM-DD')]
			filters.value['published'] = 1
			orderBy.value = 'start_date'
		} else if (currentTab.value == 'archived') {
			filters.value['start_date'] = ['<=', dayjs().format('YYYY-MM-DD')]
		} else if (currentTab.value == 'unpublished') {
			filters.value['published'] = 0
		}
	}
}

const updateStudentFilter = () => {
	if (!user.data || (is_student.value && currentTab.value != 'enrolled')) {
		filters.value['start_date'] = ['>=', dayjs().format('YYYY-MM-DD')]
		filters.value['published'] = 1
	}
}

const setQueryParams = () => {
	let queries = new URLSearchParams(location.search)
	let filterKeys = {
		title: title.value,
		category: currentCategory.value,
		certification: certification.value,
	}

	Object.keys(filterKeys).forEach((key) => {
		if (filterKeys[key]) {
			queries.set(key, filterKeys[key])
		} else {
			queries.delete(key)
		}
	})

	history.replaceState(
		{},
		'',
		`${location.pathname}${queries.size > 0 ? `?${queries.toString()}` : ''}`,
	)
}

const updateCategories = (data) => {
	data.forEach((batch) => {
		if (
			batch.category &&
			!categories.value.find((category) => category.value === batch.category)
		)
			categories.value.push({
				label: batch.category,
				value: batch.category,
			})
	})
}

watch(currentTab, () => {
	updateBatches()
})

const isBatchManager = computed(
	() =>
		user.data?.is_moderator ||
		user.data?.is_instructor ||
		user.data?.is_evaluator,
)

const hasActiveFilters = computed(
	() =>
		Boolean(title.value.trim()) ||
		Boolean(currentCategory.value) ||
		certification.value,
)

const pageHeading = computed(() =>
	isBatchManager.value ? __('Manage batches') : __('Explore batches'),
)

const pageDescription = computed(() =>
	isBatchManager.value
		? __('Review upcoming cohorts, past batches, and unpublished drafts.')
		: __('Find a cohort that fits your schedule and learning goals.'),
)

const emptyStateTitle = computed(() => {
	if (hasActiveFilters.value) return __('No matching batches')

	const emptyTitles = {
		all: __('No batches yet'),
		upcoming: __('No upcoming batches yet'),
		archived: __('No archived batches yet'),
		unpublished: __('No batch drafts yet'),
		enrolled: __('No enrolled batches yet'),
	}
	return emptyTitles[currentTab.value] || __('No batches yet')
})

const emptyStateDescription = computed(() =>
	hasActiveFilters.value
		? __('Try another search term or clear one of the active filters.')
		: __(
				'Batches in this section will appear here when they become available.',
			),
)

const batchTabs = computed(() => {
	let tabs = [
		{
			label: __('All'),
			value: 'all',
		},
	]

	if (
		user.data?.is_moderator ||
		user.data?.is_instructor ||
		user.data?.is_evaluator
	) {
		tabs.push({ label: __('Upcoming'), value: 'upcoming' })
		tabs.push({ label: __('Archived'), value: 'archived' })
		tabs.push({ label: __('Unpublished'), value: 'unpublished' })
	} else if (user.data) {
		tabs.push({ label: __('Enrolled'), value: 'enrolled' })
	}
	return tabs
})

const canCreateBatch = () => {
	if (readOnlyMode) return false
	if (
		user.data?.is_moderator ||
		user.data?.is_instructor ||
		user.data?.is_evaluator
	)
		return true
	return false
}

const batchMenu = computed(() => [
	{
		label: __('Start from scratch'),
		icon: 'users',
		onClick() {
			showBatchModal.value = true
		},
	},
	{
		label: __('Import data'),
		icon: 'upload',
		onClick() {
			router.push({
				name: 'NewDataImport',
				params: { doctype: 'LMS Batch' },
			})
		},
	},
])

const breadcrumbs = computed(() => [
	{
		label: __('Batches'),
		route: { name: 'Batches' },
	},
])

usePageMeta(() => {
	return {
		title: __('Batches'),
		icon: brand.favicon,
	}
})
</script>
