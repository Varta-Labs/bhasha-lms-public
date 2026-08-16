<template>
	<div class="course-dashboard">
		<header class="course-dashboard__intro">
			<div>
				<p class="course-dashboard__kicker">{{ __('Course health') }}</p>
				<h2>{{ __('Dashboard') }}</h2>
				<p>
					{{
						__(
							'Monitor enrollment, progress, and lesson performance at a glance.',
						)
					}}
				</p>
			</div>
			<div class="course-dashboard__enroll">
				<Button variant="solid" @click="showEnrollmentModal = true">
					<template #prefix><UserPlus class="size-4 stroke-2" /></template>
					{{ __('Enroll student') }}
				</Button>
			</div>
		</header>

		<div class="course-dashboard__metrics">
			<NumberChartGraph
				:title="__('Enrolled')"
				:value="formatAmount(course.data?.enrollments)"
			>
				<template #prefix><UsersRound class="size-5 stroke-[1.8]" /></template>
			</NumberChartGraph>
			<NumberChartGraph
				:title="__('Average Completion Rate')"
				:value="averageCompletionRate"
			>
				<template #prefix><Gauge class="size-5 stroke-[1.8]" /></template>
			</NumberChartGraph>
			<NumberChartGraph
				:title="__('Average Rating')"
				:value="course.data?.rating || 0"
			>
				<template #prefix>
					<Star class="size-5 fill-[#f59e0b] text-[#f59e0b]" />
				</template>
			</NumberChartGraph>
			<NumberChartGraph :title="__('Lessons')" :value="course.data?.lessons">
				<template #prefix
					><BookOpenCheck class="size-5 stroke-[1.8]"
				/></template>
			</NumberChartGraph>
		</div>
		<div class="course-dashboard__content">
			<section class="course-dashboard__panel course-dashboard__students">
				<div class="course-dashboard__panel-header">
					<div>
						<h3>{{ __('Students') }}</h3>
						<p>{{ __('Open a learner to review individual progress.') }}</p>
					</div>
					<div class="course-dashboard__search">
						<FormControl
							v-model="searchFilter"
							:placeholder="__('Search by name')"
							type="text"
						/>
					</div>
				</div>
				<div
					v-if="progressList.loading || progressList.data?.length"
					class="course-dashboard__table"
				>
					<ListView
						:columns="progressColumns"
						:rows="progressList.data"
						rowKey="name"
						:options="{
							selectable: false,
							showTooltip: false,
						}"
					>
						<ListHeader
							class="course-dashboard__list-header mb-2 grid items-center gap-x-4 p-2"
						>
							<ListHeaderItem
								:item="item"
								v-for="item in progressColumns"
								:key="item.key"
							>
							</ListHeaderItem>
						</ListHeader>
						<ListRows v-for="row in progressList.data" class="max-h-[500px]">
							<ListRow
								:row="row"
								@click="
									() => {
										showProgressModal = true
										currentStudent = row
									}
								"
								class="course-dashboard__student-row cursor-pointer"
							>
								<template #default="{ column, item }">
									<ListRowItem
										:item="row[column.key]"
										:align="column.align"
										class="w-full"
									>
										<template #prefix>
											<div v-if="column.key == 'member_name'">
												<Avatar
													class="flex items-center"
													:image="row['member_image']"
													:label="item"
													size="sm"
												/>
											</div>
											<ProgressBar
												v-else-if="column.key == 'progress'"
												:progress="Math.ceil(row[column.key])"
												class="!mx-0 !me-4"
											/>
										</template>
										<div v-if="column.key == 'creation'">
											{{ dayjs(row[column.key]).format('DD MMM YYYY') }}
										</div>
										<div
											v-else-if="column.key == 'progress'"
											class="text-xs !mx-0 w-5"
										>
											{{ Math.ceil(row[column.key]) }}%
										</div>
										<div v-else>
											{{ row[column.key].toString() }}
										</div>
									</ListRowItem>
								</template>
							</ListRow>
						</ListRows>
					</ListView>
					<div
						v-if="progressList.data && progressList.hasNextPage"
						class="flex justify-center my-4"
					>
						<Button @click="progressList.next()">
							{{ __('Load More') }}
						</Button>
					</div>
				</div>
				<div v-else class="course-dashboard__empty">
					<UsersRound class="size-7 stroke-[1.6]" />
					<strong>{{ __('No students enrolled yet') }}</strong>
					<span>{{
						__('Enroll a learner to begin tracking course progress.')
					}}</span>
				</div>
			</section>
			<div class="course-dashboard__side">
				<div
					v-if="chartDetails.data?.average_progress > 0"
					class="course-dashboard__panel course-dashboard__progress"
				>
					<div class="course-dashboard__panel-title">
						{{ __('Progress summary') }}
					</div>
					<div
						class="grid grid-cols-[2fr_1fr] items-center justify-between text-ink-gray-9"
					>
						<div class="flex flex-col space-y-4 flex-1 text-sm">
							<div
								class="flex items-center text-ink-gray-7"
								v-for="row in chartDetails.data?.progress_distribution"
							>
								<div
									class="size-2 rounded"
									:style="{
										backgroundColor:
											colors[theme][
												row.name.startsWith('Just')
													? 'red'
													: row.name.startsWith('In')
														? 'amber'
														: row.name.startsWith('Adv')
															? 'blue'
															: 'green'
											][400],
									}"
								></div>
								<Tooltip :text="row.name.split('(')[1].replace(')', '')">
									<div class="ms-2">
										{{ row.name.split('(')[0] }}
									</div>
								</Tooltip>
								<Tooltip :text="String(row.value)">
									<div class="ms-auto">
										{{
											Math.round((row.value / course.data?.enrollments) * 100)
										}}%
									</div>
								</Tooltip>
							</div>
						</div>
						<ECharts
							class="w-40 h-20"
							:options="{
								color: progressColors,
								series: [
									{
										type: 'pie',
										radius: ['50%', '70%'],
										center: ['50%', '50%'],
										label: {
											show: false,
										},
										labelLine: {
											show: false,
										},
										emphasis: {
											label: {
												show: false,
											},
											scale: false,
										},
										legend: {
											show: false,
										},
										data: chartDetails.data?.progress_distribution || [],
									},
								],
								showInlineLabels: false,
							}"
						/>
					</div>
				</div>
				<div
					v-if="lessonProgress.data?.length"
					class="course-dashboard__panel course-dashboard__lessons"
				>
					<div class="course-dashboard__panel-header is-compact">
						<div class="course-dashboard__panel-title">
							{{ __('Lesson Completion') }}
						</div>
						<Select
							:options="lessonProgressSortingOptions"
							@update:modelValue="
								(value: string) => updateLessonProgress(value)
							"
							:placeholder="__('Sort by')"
							class="!w-32"
						/>
					</div>
					<div class="course-dashboard__lesson-list">
						<div
							v-for="progress in lessonProgress.data"
							class="course-dashboard__lesson-row"
						>
							<div class="">
								<span class="me-3 text-xs">
									{{ progress.chapter_idx }}.{{ progress.idx }}
								</span>
								<span>
									{{ progress.title }}
								</span>
							</div>
							<Tooltip :text="String(progress.completion_count)">
								<div>
									{{
										Math.ceil(
											(progress.completion_count / course.data?.enrollments) *
												100,
										)
									}}%
								</div>
							</Tooltip>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
	<CourseEnrollmentModal
		v-if="showEnrollmentModal"
		v-model="showEnrollmentModal"
		:course="course"
		:students="progressList"
	/>
	<StudentCourseProgress
		v-if="showProgressModal"
		v-model="showProgressModal"
		:course="course"
		:student="currentStudent"
		:lessons="lessonProgress"
	/>
</template>
<script setup lang="ts">
import {
	Avatar,
	Button,
	createListResource,
	createResource,
	ECharts,
	FormControl,
	ListView,
	ListHeader,
	ListHeaderItem,
	ListRows,
	ListRow,
	ListRowItem,
	Tooltip,
} from 'frappe-ui'
import Select from '@/components/Controls/Select.vue'
import { computed, inject, ref, watch } from 'vue'
import type dayjsType from 'dayjs'
import {
	BookOpenCheck,
	Gauge,
	Star,
	UserPlus,
	UsersRound,
} from 'lucide-vue-next'
import { formatAmount } from '@/utils'
import colors from '@/utils/frappe-ui-colors.json'
import CourseEnrollmentModal from '@/pages/Courses/CourseEnrollmentModal.vue'
import NumberChartGraph from '@/components/NumberChartGraph.vue'
import ProgressBar from '@/components/ProgressBar.vue'
import StudentCourseProgress from '@/pages/Courses/StudentCourseProgress.vue'

import type { CourseDetails, Resource } from '@/types/api'

const props = defineProps<{
	course: Resource<CourseDetails | null>
}>()

const dayjs = inject<typeof dayjsType>('$dayjs')!
const showEnrollmentModal = ref<boolean>(false)
const searchFilter = ref<string | null>(null)
const showProgressModal = ref<boolean>(false)
const currentStudent = ref<Record<string, unknown> | null>(null)
const theme = ref<'darkMode' | 'lightMode'>(
	localStorage.getItem('theme') == 'dark' ? 'darkMode' : 'lightMode',
)
type Filters = {
	course: string | undefined
	member_name?: string[]
}

const chartDetails = createResource({
	url: 'lms.lms.api.get_course_progress_distribution',
	makeParams() {
		return {
			course: props.course.data?.name,
		}
	},
	auto: true,
})

const progressList = createListResource({
	doctype: 'LMS Enrollment',
	filters: {
		course: props.course.data?.name,
	},
	fields: [
		'name',
		'member',
		'member_name',
		'member_image',
		'member_username',
		'progress',
		'creation',
	],
	pageLength: 100,
	auto: true,
	cache: ['courseProgress', props.course.data?.name],
})

const lessonProgress = createResource({
	url: 'lms.lms.api.get_lesson_completion_stats',
	params: {
		course: props.course.data?.name,
	},
	auto: true,
})

const updateLessonProgress = (value: string) => {
	if (value == 'completion_rate') {
		lessonProgress.data?.sort((a: any, b: any) => {
			const rateA = a.completion_count / (props.course.data?.enrollments || 1)
			const rateB = b.completion_count / (props.course.data?.enrollments || 1)
			return rateB - rateA
		})
	} else if (value == 'index') {
		lessonProgress.data?.sort((a: any, b: any) => {
			return a.chapter_idx - b.chapter_idx || a.idx - b.idx
		})
	}
}

watch([searchFilter], () => {
	let filters: Filters = {
		course: props.course.data?.name,
	}

	if (searchFilter.value) {
		filters.member_name = ['like', `%${searchFilter.value}%`]
	}

	progressList.update({
		filters: filters,
	})
	progressList.reload()
})

const averageCompletionRate = computed(() => {
	let value = Math.ceil(chartDetails.data?.average_progress) || 0
	return value + '%'
})

const progressColors = computed(() => {
	let colorList = []
	colorList.push(colors[theme.value]['red'][400])
	colorList.push(colors[theme.value]['amber'][400])
	colorList.push(colors[theme.value]['blue'][400])
	colorList.push(colors[theme.value]['green'][400])
	return colorList
})

const progressColumns = computed(() => {
	return [
		{
			label: __('Name'),
			key: 'member_name',
			width: '40%',
		},
		{
			label: __('Progress'),
			key: 'progress',
			width: '30%',
		},
		{
			label: __('Enrolled On'),
			key: 'creation',
			align: 'right',
		},
	]
})

const lessonProgressSortingOptions = [
	{
		label: __('Lesson Index'),
		value: 'index',
		onClick() {
			updateLessonProgress('index')
		},
	},
	{
		label: __('Completion Rate'),
		value: 'completion_rate',
		onClick() {
			updateLessonProgress('completion_rate')
		},
	},
]
</script>

<style scoped>
.course-dashboard {
	height: 100%;
	overflow-y: auto;
	padding: clamp(1.25rem, 3vw, 2rem);
	background: #faf9fc;
}

.course-dashboard__intro {
	display: flex;
	align-items: flex-end;
	justify-content: space-between;
	gap: 1.5rem;
	margin-bottom: 1.5rem;
}

.course-dashboard__kicker {
	color: #4a38c2;
	font-size: 0.75rem;
	font-weight: 800;
	letter-spacing: 0.11em;
	text-transform: uppercase;
}

.course-dashboard__intro h2 {
	margin-top: 0.35rem;
	color: #171717;
	font-family: var(--bhasha-font-display);
	font-size: clamp(1.8rem, 3vw, 2.35rem);
	font-weight: 800;
	letter-spacing: -0.03em;
	line-height: 1.15;
}

.course-dashboard__intro p:not(.course-dashboard__kicker) {
	margin-top: 0.5rem;
	color: #6f6879;
	font-size: 0.875rem;
	line-height: 1.55;
}

.course-dashboard__enroll :deep(button) {
	min-height: 2.75rem;
	padding-inline: 1rem !important;
	border-color: transparent !important;
	border-radius: 9999px !important;
	background: linear-gradient(135deg, #6c5ce7, #4a38c2) !important;
	color: #fff !important;
	font-weight: 800 !important;
	box-shadow: 0 12px 24px -8px rgba(108, 92, 231, 0.4);
}

.course-dashboard__metrics {
	display: grid;
	grid-template-columns: repeat(4, minmax(0, 1fr));
	gap: 1rem;
	margin-bottom: 1.25rem;
}

.course-dashboard__content {
	display: grid;
	grid-template-columns: minmax(0, 2fr) minmax(18rem, 1fr);
	align-items: start;
	gap: 1.25rem;
}

.course-dashboard__panel {
	min-width: 0;
	border: 1px solid #e7e2ec;
	border-radius: 1.25rem;
	background: #fff;
	box-shadow: 0 10px 30px rgba(44, 31, 69, 0.045);
}

.course-dashboard__students {
	overflow: hidden;
	padding: 1.25rem;
}

.course-dashboard__panel-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 1rem;
	margin-bottom: 1rem;
}

.course-dashboard__panel-header h3,
.course-dashboard__panel-title {
	color: #27222e;
	font-family: var(--bhasha-font-display);
	font-size: 1.05rem;
	font-weight: 700;
}

.course-dashboard__panel-header p {
	margin-top: 0.2rem;
	color: #7c7c7c;
	font-size: 0.75rem;
}

.course-dashboard__search {
	width: min(100%, 15rem);
}

.course-dashboard__table {
	max-height: 63vh;
	overflow-y: auto;
}

.course-dashboard__list-header {
	position: sticky;
	top: 0;
	z-index: 1;
	border: 0 !important;
	border-radius: 0.7rem !important;
	background: #f8f6fb !important;
	color: #6f6879;
	font-size: 0.75rem;
	font-weight: 700;
}

.course-dashboard__student-row {
	border-bottom: 1px solid #f0edf2;
	transition: background 150ms ease;
}

.course-dashboard__student-row:hover {
	background: #faf8ff;
}

.course-dashboard__empty {
	display: flex;
	min-height: 18rem;
	align-items: center;
	justify-content: center;
	flex-direction: column;
	gap: 0.55rem;
	color: #8a8490;
	text-align: center;
}

.course-dashboard__empty strong {
	color: #383838;
	font-family: var(--bhasha-font-display);
}

.course-dashboard__empty span {
	max-width: 24rem;
	font-size: 0.8125rem;
}

.course-dashboard__side {
	display: grid;
	gap: 1.25rem;
}

.course-dashboard__progress,
.course-dashboard__lessons {
	padding: 1.25rem;
}

.course-dashboard__progress .course-dashboard__panel-title {
	margin-bottom: 1rem;
}

.course-dashboard__panel-header.is-compact {
	margin-bottom: 1rem;
}

.course-dashboard__lesson-list {
	max-height: 40vh;
	overflow-y: auto;
	border-top: 1px solid #eeeaf1;
	color: #625d68;
}

.course-dashboard__lesson-row {
	display: flex;
	justify-content: space-between;
	gap: 1rem;
	padding-block: 0.75rem;
	border-bottom: 1px solid #f0edf2;
	font-size: 0.8125rem;
}

@media (max-width: 1099px) {
	.course-dashboard__metrics {
		grid-template-columns: repeat(2, minmax(0, 1fr));
	}

	.course-dashboard__content {
		grid-template-columns: minmax(0, 1fr);
	}

	.course-dashboard__side {
		grid-template-columns: repeat(2, minmax(0, 1fr));
	}
}

@media (max-width: 639px) {
	.course-dashboard {
		padding: 1rem;
	}

	.course-dashboard__intro,
	.course-dashboard__panel-header {
		align-items: stretch;
		flex-direction: column;
	}

	.course-dashboard__enroll,
	.course-dashboard__search {
		width: 100%;
	}

	.course-dashboard__enroll :deep(button) {
		width: 100%;
	}

	.course-dashboard__metrics,
	.course-dashboard__side {
		grid-template-columns: minmax(0, 1fr);
	}
}
</style>
