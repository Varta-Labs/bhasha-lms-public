<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
  </LayoutHeader>

  <main class="bhasha-statistics-page">
    <div class="bhasha-statistics-shell">
      <section
        class="bhasha-statistics-intro"
        aria-labelledby="statistics-title"
      >
        <div>
          <div class="bhasha-statistics-eyebrow">
            <BarChart3 class="size-4 stroke-2" />
            {{ __('Learning insights') }}
          </div>
          <h1 id="statistics-title">{{ __('Statistics') }}</h1>
          <p>
            {{
              __(
                'Track learner growth, course activity, and certification progress.',
              )
            }}
          </p>
        </div>
        <div class="bhasha-statistics-summary" aria-hidden="true">
          <Sparkles class="size-4 stroke-1.5" />
          {{ __('Learning at a glance') }}
        </div>
      </section>

      <section aria-labelledby="overview-title">
        <div class="bhasha-statistics-section-heading">
          <div>
            <span>{{ __('Overview') }}</span>
            <h2 id="overview-title">{{ __('Platform activity') }}</h2>
          </div>
        </div>

        <div
          v-if="chartDetails.loading"
          class="bhasha-statistics-metrics"
          aria-hidden="true"
        >
          <div
            v-for="index in 5"
            :key="index"
            class="bhasha-statistics-metric is-loading"
          >
            <div class="bhasha-statistics-skeleton is-icon" />
            <div class="bhasha-statistics-skeleton is-value" />
            <div class="bhasha-statistics-skeleton is-label" />
          </div>
        </div>

        <div v-else-if="chartDetails.data" class="bhasha-statistics-metrics">
          <Tooltip
            v-for="metric in metricCards"
            :key="metric.key"
            :text="metric.tooltip"
          >
            <article class="bhasha-statistics-metric">
              <div
                class="bhasha-statistics-metric-icon"
                :class="`is-${metric.tone}`"
              >
                <component :is="metric.icon" class="size-5 stroke-1.75" />
              </div>
              <strong>{{ formatMetric(chartDetails.data[metric.key]) }}</strong>
              <span>{{ metric.label }}</span>
            </article>
          </Tooltip>
        </div>
      </section>

      <section class="bhasha-statistics-trends" aria-labelledby="trends-title">
        <div class="bhasha-statistics-section-heading">
          <div>
            <span>{{ __('Trends') }}</span>
            <h2 id="trends-title">{{ __('Learning activity over time') }}</h2>
          </div>
          <p>
            {{
              __('Daily growth and completion patterns across your courses.')
            }}
          </p>
        </div>

        <div class="bhasha-statistics-chart-grid">
          <article class="bhasha-statistics-chart-card">
            <AxisChart
              v-if="signupsChart.data"
              :config="{
                data: signupsChart.data,
                title: __('Signups'),
                subtitle: __('Signups per day'),
                colors: ['#6532c5'],
                xAxis: {
                  key: 'date',
                  type: 'time',
                  title: __('Date'),
                  timeGrain: 'day',
                },
                yAxis: {
                  title: __('Signups'),
                },
                series: [
                  { name: 'signups', type: 'line', showDataPoints: true },
                ],
              }"
            />
            <div
              v-else
              class="bhasha-statistics-chart-loading"
              aria-hidden="true"
            />
          </article>
          <article class="bhasha-statistics-chart-card">
            <AxisChart
              v-if="enrollmentChart.data"
              :config="{
                data: enrollmentChart.data,
                title: __('Enrollments'),
                subtitle: __('Enrollments per day'),
                colors: ['#8150df'],
                xAxis: {
                  key: 'date',
                  type: 'time',
                  title: __('Date'),
                  timeGrain: 'day',
                },
                yAxis: {
                  title: __('Enrollments'),
                },
                series: [
                  { name: 'enrollments', type: 'line', showDataPoints: true },
                ],
              }"
            />
            <div
              v-else
              class="bhasha-statistics-chart-loading"
              aria-hidden="true"
            />
          </article>
          <article class="bhasha-statistics-chart-card">
            <AxisChart
              v-if="certification.data"
              :config="{
                data: certification.data,
                title: __('Certifications'),
                subtitle: __('Certifications per day'),
                colors: ['#5125a7'],
                xAxis: {
                  key: 'date',
                  type: 'time',
                  title: __('Date'),
                  timeGrain: 'day',
                },
                yAxis: {
                  title: __('Certifications'),
                },
                series: [
                  {
                    name: 'certifications',
                    type: 'line',
                    showDataPoints: true,
                  },
                ],
              }"
            />
            <div
              v-else
              class="bhasha-statistics-chart-loading"
              aria-hidden="true"
            />
          </article>
          <article class="bhasha-statistics-chart-card">
            <DonutChart
              v-if="courseCompletion.data"
              :config="{
                data: courseCompletion.data,
                title: __('Completions'),
                subtitle: __('Course Completion'),
                categoryColumn: 'label',
                valueColumn: 'value',
                colors: ['#6532c5', '#a77cf5', '#dfd2ff', '#eee7ff'],
              }"
            />
            <div
              v-else
              class="bhasha-statistics-chart-loading"
              aria-hidden="true"
            />
          </article>
        </div>
      </section>
    </div>
  </main>
</template>
<script setup>
import {
  AxisChart,
  Breadcrumbs,
  createResource,
  DonutChart,
  Tooltip,
  usePageMeta,
} from 'frappe-ui'
import { computed } from 'vue'
import { sessionStore } from '../stores/session'
import LayoutHeader from '@/components/Layouts/LayoutHeader.vue'
import {
  Award,
  BarChart3,
  BookOpen,
  CircleCheckBig,
  Sparkles,
  UserPlus,
  UsersRound,
} from 'lucide-vue-next'
import '@/styles/statistics.css'

const { brand } = sessionStore()

const metricCards = [
  {
    key: 'courses',
    label: __('Courses'),
    tooltip: __('Published Courses'),
    icon: BookOpen,
    tone: 'purple',
  },
  {
    key: 'users',
    label: __('Signups'),
    tooltip: __('Active Members'),
    icon: UserPlus,
    tone: 'violet',
  },
  {
    key: 'enrollments',
    label: __('Enrollments'),
    tooltip: __('Course Enrollments'),
    icon: UsersRound,
    tone: 'blue',
  },
  {
    key: 'completions',
    label: __('Completions'),
    tooltip: __('Course Completions'),
    icon: CircleCheckBig,
    tone: 'green',
  },
  {
    key: 'certifications',
    label: __('Certifications'),
    tooltip: __('Certified Members'),
    icon: Award,
    tone: 'amber',
  },
]

const formatMetric = (value) => new Intl.NumberFormat().format(value || 0)

const breadcrumbs = computed(() => {
  return [
    {
      label: __('Statistics'),
      route: {
        name: 'Statistics',
      },
    },
  ]
})

const chartDetails = createResource({
  url: 'lms.lms.api.get_chart_details',
  cache: ['statistics'],
  auto: true,
})

const signupsChart = createResource({
  url: 'lms.lms.utils.get_chart_data',
  params: {
    chart_name: 'New Signups',
  },
  auto: true,
  transform(data) {
    return data.map((item) => {
      return {
        date: new Date(item.date),
        signups: item.count,
      }
    })
  },
})

const enrollmentChart = createResource({
  url: 'lms.lms.utils.get_chart_data',
  cache: ['enrollments'],
  params: {
    chart_name: 'Course Enrollments',
  },
  auto: true,
  transform(data) {
    return data.map((item) => {
      return {
        date: new Date(item.date),
        enrollments: item.count,
      }
    })
  },
})

const certification = createResource({
  url: 'lms.lms.utils.get_chart_data',
  cache: ['certifications'],
  params: {
    chart_name: 'Certification',
  },
  auto: true,
  transform(data) {
    return data.map((item) => {
      return {
        date: new Date(item.date),
        certifications: item.count,
      }
    })
  },
})

const courseCompletion = createResource({
  url: 'lms.lms.utils.get_course_completion_data',
  auto: true,
  cache: ['courseCompletion'],
})

usePageMeta(() => {
  return {
    title: __('Statistics'),
    icon: brand.favicon,
  }
})
</script>
