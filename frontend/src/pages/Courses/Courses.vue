<template>
	<LayoutHeader>
		<template #left-header>
			<Breadcrumbs :items="breadcrumbs" />
		</template>
		<template #right-header>
			<Dropdown
				placement="right"
				side="bottom"
				v-if="canCreateCourse()"
				:options="courseMenu"
			>
				<template v-slot="{ open }">
					<Button
						variant="solid"
						class="bhasha-primary bhasha-course-create-button"
					>
						<template #prefix>
							<Plus class="size-4 stroke-2" />
						</template>
						{{ __('Create course') }}
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
	<main class="bhasha-courses-page flex min-h-0 flex-1 flex-col">
		<section class="bhasha-courses-toolbar">
			<div class="bhasha-courses-toolbar-heading">
				<div>
					<h1 class="bhasha-courses-title">{{ pageHeading }}</h1>
					<p class="bhasha-courses-description">{{ pageDescription }}</p>
				</div>
				<div
					v-if="!courses.list.loading && courses.data?.length"
					class="bhasha-course-result-count"
					aria-live="polite"
				>
					{{ courses.data.length }}{{ courses.hasNextPage ? '+' : '' }}
					{{ courses.data.length === 1 ? __('course') : __('courses') }}
				</div>
			</div>

			<div class="bhasha-course-tabs-scroll">
				<div
					class="bhasha-course-tabs"
					role="group"
					:aria-label="__('Course status')"
				>
					<button
						v-for="tab in courseTabs"
						:key="tab.value"
						type="button"
						class="bhasha-course-tab"
						:class="{ 'is-active': currentTab === tab.value }"
						:aria-pressed="currentTab === tab.value"
						@click="currentTab = tab.value"
					>
						{{ tab.label }}
					</button>
				</div>
			</div>

			<div class="bhasha-course-filters">
				<FormControl
					v-model="title"
					:placeholder="__('Search courses')"
					type="text"
					size="md"
					variant="outline"
					class="bhasha-course-search"
					@input="debouncedUpdateCourses"
				>
					<template #prefix>
						<Search class="size-4 stroke-1.5 text-ink-gray-5" />
					</template>
					<template v-if="title" #suffix>
						<button
							type="button"
							class="bhasha-course-search-clear"
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
					class="bhasha-course-category-filter"
					@update:modelValue="updateCourses()"
				/>

				<button
					type="button"
					class="bhasha-course-filter-toggle"
					:class="{ 'is-active': certification }"
					:aria-pressed="certification"
					@click="toggleCertification"
				>
					<GraduationCap class="size-4 stroke-1.5" />
					{{ __('Certificate') }}
				</button>

				<button
					v-if="hasActiveFilters"
					type="button"
					class="bhasha-course-clear-filters"
					@click="resetFilters"
				>
					<X class="size-3.5 stroke-2" />
					{{ __('Clear filters') }}
				</button>
			</div>
		</section>

		<div
			v-if="courses.data?.length"
			class="bhasha-course-grid-shell bhasha-course-grid"
		>
			<router-link
				v-for="course in courses.data"
				:key="course.name"
				:to="{ name: 'CourseDetail', params: { courseName: course.name } }"
			>
				<CourseCard :course="course" />
			</router-link>
		</div>
		<section v-else-if="!courses.list.loading" class="bhasha-courses-empty">
			<div class="bhasha-courses-empty-icon">
				<BookOpen class="size-6 stroke-1.5" />
			</div>
			<h2>{{ emptyStateTitle }}</h2>
			<p>{{ emptyStateDescription }}</p>
			<Button v-if="hasActiveFilters" class="mt-2" @click="resetFilters">
				{{ __('Clear filters') }}
			</Button>
		</section>
		<div
			v-if="!courses.list.loading && courses.hasNextPage"
			class="flex justify-center mt-5"
		>
			<Button class="bhasha-course-load-more" @click="courses.next()">
				{{ __('Load More') }}
			</Button>
		</div>
	</main>
	<NewCourseModal
		v-if="showCourseModal"
		v-model="showCourseModal"
		:courses="courses"
	/>

	<CourseImportModal
		v-if="showCourseImportModal"
		v-model="showCourseImportModal"
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
import {
	BookOpen,
	ChevronDown,
	GraduationCap,
	Plus,
	Search,
	X,
} from 'lucide-vue-next'
import { useDebounceFn } from '@vueuse/core'
import { sessionStore } from '@/stores/session'
import { canCreateCourse } from '@/utils'
import CourseCard from '@/components/CourseCard.vue'
import LayoutHeader from '@/components/Layouts/LayoutHeader.vue'
import { useRouter } from 'vue-router'
import NewCourseModal from '@/pages/Courses/NewCourseModal.vue'
import CourseImportModal from '@/pages/Courses/CourseImportModal.vue'
import '@/styles/course-creation.css'

const user = inject('$user')
const dayjs = inject('$dayjs')
const start = ref(0)
const pageLength = ref(30)
const categories = ref([
	{
		label: '',
		value: null,
	},
])
const currentCategory = ref(null)
const title = ref('')
const certification = ref(false)
const filters = ref({})
const currentTab = ref('live')
const { brand } = sessionStore()
const router = useRouter()
const showCourseModal = ref(false)
const showCourseImportModal = ref(false)

onMounted(() => {
	setFiltersFromQuery()
	updateCourses()
})

const setFiltersFromQuery = () => {
	let queries = new URLSearchParams(location.search)
	title.value = queries.get('title') || ''
	currentCategory.value = queries.get('category') || null
	certification.value = ['1', 'true'].includes(queries.get('certification'))
	if (queries.get('newCourse') == '1') {
		showCourseModal.value = true
	}
}

const courses = createListResource({
	doctype: 'LMS Course',
	url: 'lms.lms.utils.get_courses',
	cache: ['courses', user.data?.name],
	pageLength: pageLength.value,
	start: start.value,
})

const setCategories = (data) => {
	let allCategories = data.map((course) => course.category)
	allCategories = allCategories.filter(
		(category, index) => allCategories.indexOf(category) === index && category,
	)
	if (categories.value.length <= allCategories.length) {
		updateCategories(data)
	}
}

const updateCourses = () => {
	updateFilters()
	courses.update({
		filters: filters.value,
	})
	courses.reload().then((data) => {
		setCategories(data)
	})
}

const debouncedUpdateCourses = useDebounceFn(updateCourses, 300)

const clearSearch = () => {
	title.value = ''
	updateCourses()
}

const toggleCertification = () => {
	certification.value = !certification.value
	updateCourses()
}

const resetFilters = () => {
	title.value = ''
	currentCategory.value = null
	certification.value = false
	updateCourses()
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
	delete filters.value['live']
	delete filters.value['created']
	delete filters.value['published_on']
	delete filters.value['upcoming']

	if (currentTab.value == 'enrolled' && user.data?.is_student) {
		filters.value['enrolled'] = 1
		delete filters.value['published']
	} else {
		delete filters.value['published']
		delete filters.value['enrolled']

		if (currentTab.value == 'live') {
			filters.value['published'] = 1
			filters.value['upcoming'] = 0
			filters.value['live'] = 1
		} else if (currentTab.value == 'upcoming') {
			filters.value['upcoming'] = 1
		} else if (currentTab.value == 'new') {
			filters.value['published'] = 1
			filters.value['published_on'] = [
				'>=',
				dayjs().add(-3, 'month').format('YYYY-MM-DD'),
			]
		} else if (currentTab.value == 'created') {
			filters.value['created'] = 1
		} else if (currentTab.value == 'unpublished') {
			filters.value['published'] = 0
		}
	}
}

const updateStudentFilter = () => {
	if (!user.data || (user.data?.is_student && currentTab.value != 'enrolled')) {
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

	let queryString = ''
	if (queries.toString()) {
		queryString = `?${queries.toString()}`
	}

	history.replaceState({}, '', `${location.pathname}${queryString}`)
}

const updateCategories = (data) => {
	data.forEach((course) => {
		if (
			course.category &&
			!categories.value.find((category) => category.value === course.category)
		)
			categories.value.push({
				label: course.category,
				value: course.category,
			})
	})
}

watch(currentTab, () => {
	updateCourses()
})

const isCourseManager = computed(
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
	isCourseManager.value ? __('Manage courses') : __('Explore courses'),
)

const pageDescription = computed(() =>
	isCourseManager.value
		? __('Review published courses, upcoming releases, and drafts.')
		: __('Find the right course and continue learning at your own pace.'),
)

const emptyStateTitle = computed(() => {
	if (hasActiveFilters.value) return __('No matching courses')

	const emptyTitles = {
		live: isCourseManager.value
			? __('No published courses yet')
			: __('No available courses yet'),
		new: __('No new courses yet'),
		upcoming: __('No upcoming courses yet'),
		created: __('No courses created by you yet'),
		unpublished: __('No drafts yet'),
		enrolled: __('No enrolled courses yet'),
	}
	return emptyTitles[currentTab.value] || __('No courses yet')
})

const emptyStateDescription = computed(() =>
	hasActiveFilters.value
		? __('Try another search term or clear one of the active filters.')
		: __(
				'Courses in this section will appear here when they become available.',
			),
)

const courseTabs = computed(() => {
	let tabs = [
		{
			label: isCourseManager.value ? __('Published') : __('Available'),
			value: 'live',
		},
		{
			label: __('New'),
			value: 'new',
		},
		{
			label: __('Upcoming'),
			value: 'upcoming',
		},
	]
	if (
		user.data?.is_moderator ||
		user.data?.is_instructor ||
		user.data?.is_evaluator
	) {
		tabs.push({ label: __('Created by me'), value: 'created' })
		tabs.push({ label: __('Drafts'), value: 'unpublished' })
	} else if (user.data) {
		tabs.push({ label: __('My courses'), value: 'enrolled' })
	}
	return tabs
})

const courseMenu = computed(() => {
	return [
		{
			label: __('Start from scratch'),
			icon: 'book-open',
			onClick() {
				showCourseModal.value = true
			},
		},
		{
			label: __('Import data'),
			icon: 'upload',
			onClick() {
				router.push({
					name: 'NewDataImport',
					params: { doctype: 'LMS Course' },
				})
			},
		},
		{
			label: __('Import ZIP'),
			icon: 'folder-plus',
			onClick() {
				showCourseImportModal.value = true
			},
		},
	]
})

const breadcrumbs = computed(() => [
	{
		label: __('Courses'),
		route: { name: 'Courses' },
	},
])

usePageMeta(() => {
	return {
		title: __('Courses'),
		icon: brand.favicon,
	}
})
</script>

<style scoped>
.bhasha-courses-page {
	padding: clamp(1rem, 2.5vw, 1.75rem) clamp(1rem, 3vw, 2rem) 2.5rem;
	background:
		radial-gradient(
			circle at 10% 0%,
			rgba(129, 80, 223, 0.075),
			transparent 23rem
		),
		var(--bhasha-page);
}

.bhasha-courses-toolbar,
.bhasha-course-grid-shell,
.bhasha-courses-empty {
	width: min(100%, 80rem);
	margin-inline: auto;
}

.bhasha-courses-toolbar {
	margin-bottom: 1.5rem;
	padding: clamp(1rem, 2vw, 1.35rem);
	border: 1px solid var(--bhasha-border-brand);
	border-radius: var(--bhasha-radius-card);
	background: rgba(255, 255, 255, 0.9);
	box-shadow: 0 10px 30px rgba(61, 34, 111, 0.055);
}

.bhasha-courses-toolbar-heading {
	display: flex;
	align-items: flex-start;
	justify-content: space-between;
	gap: 1rem;
	margin-bottom: 1.1rem;
}

.bhasha-courses-title {
	color: var(--bhasha-text);
	font-family: var(--bhasha-font-display);
	font-size: 1.25rem;
	font-weight: 750;
	letter-spacing: -0.02em;
	line-height: 1.3;
}

.bhasha-courses-description {
	max-width: 60ch;
	margin-top: 0.2rem;
	color: var(--bhasha-text-muted);
	font-size: 0.8125rem;
	line-height: 1.5;
}

.bhasha-course-result-count {
	flex-shrink: 0;
	padding: 0.35rem 0.65rem;
	border: 1px solid var(--bhasha-border-brand);
	border-radius: 9999px;
	background: var(--bhasha-50);
	color: var(--bhasha-700);
	font-size: 0.75rem;
	font-weight: 650;
	font-variant-numeric: tabular-nums;
}

.bhasha-course-tabs-scroll {
	margin-inline: -0.1rem;
	padding: 0.1rem;
	overflow-x: auto;
	scrollbar-width: none;
}

.bhasha-course-tabs-scroll::-webkit-scrollbar {
	display: none;
}

.bhasha-course-tabs {
	display: inline-flex;
	min-width: max-content;
	align-items: center;
	gap: 0.25rem;
	padding: 0.25rem;
	border: 1px solid var(--bhasha-border-brand);
	border-radius: 9999px;
	background: var(--bhasha-50);
}

.bhasha-course-tab {
	min-height: 2.1rem;
	padding: 0.4rem 0.8rem;
	border-radius: 9999px;
	color: var(--bhasha-text-muted);
	font-size: 0.8125rem;
	font-weight: 650;
	line-height: 1;
	white-space: nowrap;
	transition:
		background-color 160ms ease,
		color 160ms ease,
		box-shadow 160ms ease,
		transform 160ms ease;
}

.bhasha-course-tab:hover {
	background: rgba(255, 255, 255, 0.82);
	color: var(--bhasha-700);
}

.bhasha-course-tab.is-active {
	background: linear-gradient(135deg, var(--bhasha-600), var(--bhasha-700));
	color: #fff;
	box-shadow: 0 6px 16px rgba(101, 50, 197, 0.24);
}

.bhasha-course-tab:focus-visible,
.bhasha-course-filter-toggle:focus-visible,
.bhasha-course-clear-filters:focus-visible,
.bhasha-course-search-clear:focus-visible {
	outline: none;
	box-shadow: var(--bhasha-focus-ring);
}

.bhasha-course-tab:active {
	transform: scale(0.98);
}

.bhasha-course-filters {
	display: flex;
	align-items: center;
	gap: 0.65rem;
	margin-top: 0.85rem;
	padding-top: 0.85rem;
	border-top: 1px solid var(--bhasha-border-brand);
}

.bhasha-course-search {
	min-width: 14rem;
	flex: 1 1 24rem;
}

.bhasha-course-search :deep(input),
.bhasha-course-category-filter :deep(button) {
	background: var(--bhasha-surface);
}

.bhasha-course-category-filter :deep([data-slot='trigger'] .truncate) {
	display: block;
	overflow: visible;
	min-height: 1.6rem;
	padding-block: 0.125rem 0.25rem;
	line-height: 1.25rem;
	text-overflow: clip;
}

.bhasha-course-search-clear {
	display: inline-grid;
	width: 1.5rem;
	height: 1.5rem;
	place-items: center;
	border-radius: 9999px;
	color: var(--bhasha-text-muted);
}

.bhasha-course-search-clear:hover {
	background: var(--bhasha-100);
	color: var(--bhasha-700);
}

.bhasha-course-category-filter {
	width: 12rem;
	flex: 0 1 12rem;
}

.bhasha-course-filter-toggle,
.bhasha-course-clear-filters {
	display: inline-flex;
	min-height: 2.4rem;
	flex-shrink: 0;
	align-items: center;
	justify-content: center;
	gap: 0.4rem;
	border-radius: var(--bhasha-radius-control);
	font-size: 0.8125rem;
	font-weight: 650;
	transition:
		border-color 160ms ease,
		background-color 160ms ease,
		color 160ms ease;
}

.bhasha-course-filter-toggle {
	padding: 0.45rem 0.75rem;
	border: 1px solid var(--bhasha-border);
	background: var(--bhasha-surface);
	color: var(--bhasha-text-muted);
}

.bhasha-course-filter-toggle:hover,
.bhasha-course-filter-toggle.is-active {
	border-color: var(--bhasha-border-brand);
	background: var(--bhasha-50);
	color: var(--bhasha-700);
}

.bhasha-course-filter-toggle.is-active {
	box-shadow: inset 0 0 0 1px rgba(101, 50, 197, 0.08);
}

.bhasha-course-clear-filters {
	padding: 0.4rem 0.3rem;
	color: var(--bhasha-text-muted);
}

.bhasha-course-clear-filters:hover {
	color: var(--bhasha-700);
}

.bhasha-courses-empty {
	display: flex;
	min-height: min(26rem, calc(100vh - 17rem));
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: 3rem 1.5rem;
	border: 1px dashed rgba(101, 50, 197, 0.22);
	border-radius: var(--bhasha-radius-card);
	background: rgba(255, 255, 255, 0.72);
	text-align: center;
}

.bhasha-courses-empty-icon {
	display: grid;
	width: 3.25rem;
	height: 3.25rem;
	place-items: center;
	margin-bottom: 1rem;
	border-radius: 1rem;
	background: var(--bhasha-100);
	color: var(--bhasha-700);
}

.bhasha-courses-empty h2 {
	color: var(--bhasha-text);
	font-size: 1.125rem;
	font-weight: 700;
}

.bhasha-courses-empty p {
	max-width: 34rem;
	margin-top: 0.35rem;
	color: var(--bhasha-text-muted);
	font-size: 0.875rem;
	line-height: 1.55;
}

.bhasha-course-load-more {
	border-color: var(--bhasha-border-brand);
	background: var(--bhasha-surface);
	color: var(--bhasha-700);
}

:global(html[data-theme='dark'] .bhasha-courses-page) {
	background: var(--surface-white);
}

:global(html[data-theme='dark'] .bhasha-courses-toolbar),
:global(html[data-theme='dark'] .bhasha-courses-empty) {
	border-color: rgba(199, 174, 255, 0.16);
	background: var(--surface-white);
	box-shadow: none;
}

:global(html[data-theme='dark'] .bhasha-course-tabs),
:global(html[data-theme='dark'] .bhasha-course-filter-toggle),
:global(html[data-theme='dark'] .bhasha-course-search) :deep(input),
:global(html[data-theme='dark'] .bhasha-course-category-filter) :deep(button) {
	border-color: rgba(199, 174, 255, 0.16);
	background: rgba(129, 80, 223, 0.1);
}

@media (min-width: 768px) {
	.bhasha-course-category-filter :deep([data-slot='trigger']) {
		height: 2.5rem;
	}

	.bhasha-course-category-filter :deep([data-slot='trigger'] > .grid) {
		height: 100%;
		align-content: center;
		padding-bottom: 0.125rem;
	}

	.bhasha-course-category-filter :deep([data-slot='trigger'] .truncate) {
		min-height: 1.75rem;
		padding-block: 0.125rem 0.25rem;
		line-height: 1.375rem;
	}
}

@media (max-width: 767px) {
	.bhasha-courses-page {
		padding: 0.75rem 0.75rem 2rem;
	}

	.bhasha-courses-toolbar {
		padding: 0.9rem;
		border-radius: 1rem;
	}

	.bhasha-course-filters {
		flex-wrap: wrap;
	}

	.bhasha-course-search {
		min-width: 100%;
		flex-basis: 100%;
	}

	.bhasha-course-category-filter {
		min-width: 0;
		flex: 1 1 10rem;
	}

	.bhasha-course-filter-toggle {
		flex: 0 0 auto;
	}
}

@media (max-width: 479px) {
	.bhasha-courses-toolbar-heading {
		align-items: center;
	}

	.bhasha-courses-description {
		display: none;
	}

	.bhasha-course-category-filter {
		flex-basis: 100%;
	}

	.bhasha-course-filter-toggle {
		flex: 1;
	}
}

@media (prefers-reduced-motion: reduce) {
	.bhasha-course-tab,
	.bhasha-course-filter-toggle,
	.bhasha-course-clear-filters {
		transition: none;
	}
}
</style>
