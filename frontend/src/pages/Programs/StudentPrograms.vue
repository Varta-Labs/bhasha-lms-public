<template>
	<main class="bhasha-programs-page">
		<section class="bhasha-programs-toolbar bhasha-student-programs-toolbar">
			<div>
				<h1 class="bhasha-programs-title">{{ __('Learning programs') }}</h1>
				<p class="bhasha-programs-description">
					{{
						__('Follow a guided collection of courses and track your progress.')
					}}
				</p>
			</div>
			<div
				class="bhasha-program-tabs"
				role="group"
				:aria-label="__('Program status')"
			>
				<button
					v-for="tab in tabs"
					:key="tab.value"
					type="button"
					class="bhasha-program-tab"
					:class="{ 'is-active': currentTab === tab.value }"
					:aria-pressed="currentTab === tab.value"
					@click="currentTab = tab.value"
				>
					{{ tab.label }}
				</button>
			</div>
		</section>

		<section v-if="currentPrograms.length" class="bhasha-program-grid">
			<button
				v-for="program in currentPrograms"
				:key="program.name"
				type="button"
				class="bhasha-program-card"
				@click="openDetails(program.name, currentTab)"
			>
				<div class="bhasha-program-card-topline">
					<div class="bhasha-program-card-icon" aria-hidden="true">
						<BookOpen class="size-5 stroke-1.5" />
					</div>
					<span class="bhasha-program-status is-published">
						{{
							currentTab === 'enrolled' ? __('In progress') : __('Available')
						}}
					</span>
				</div>
				<div>
					<h2 class="bhasha-program-card-title">{{ program.name }}</h2>
					<p class="bhasha-program-card-hint">
						{{
							currentTab === 'enrolled'
								? __('Continue your learning path')
								: __('View the path and enroll')
						}}
					</p>
				</div>
				<div class="bhasha-program-card-meta">
					<span>
						<BookOpen class="size-4 stroke-1.5" />
						{{ program.course_count }}
						{{ program.course_count == 1 ? __('course') : __('courses') }}
					</span>
					<span>
						<User class="size-4 stroke-1.5" />
						{{ program.member_count || 0 }}
						{{ program.member_count == 1 ? __('member') : __('members') }}
					</span>
				</div>
				<div
					v-if="Object.prototype.hasOwnProperty.call(program, 'progress')"
					class="bhasha-program-progress"
				>
					<div class="bhasha-program-progress-label">
						<span>{{ __('Progress') }}</span>
						<strong>{{ Math.ceil(program.progress) }}%</strong>
					</div>
					<ProgressBar :progress="program.progress" />
				</div>
			</button>
		</section>

		<section v-else-if="!programs.loading" class="bhasha-programs-empty">
			<div class="bhasha-programs-empty-icon">
				<BookOpen class="size-6 stroke-1.5" />
			</div>
			<h2>{{ emptyStateTitle }}</h2>
			<p>{{ emptyStateDescription }}</p>
		</section>
	</main>
	<ProgramEnrollment
		v-model="showEnrollmentConfirmation"
		:programName="enrollmentProgram"
	/>
</template>
<script setup lang="ts">
import { createResource } from 'frappe-ui'
import { computed, ref } from 'vue'
import { BookOpen, User } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import ProgressBar from '@/components/ProgressBar.vue'
import ProgramEnrollment from '@/pages/Programs/ProgramEnrollment.vue'

const currentTab = ref('enrolled')
const router = useRouter()
const showEnrollmentConfirmation = ref(false)
const enrollmentProgram = ref(null)

const programs = createResource({
	url: 'lms.lms.utils.get_programs',
	auto: true,
})

const currentPrograms = computed(() => programs.data?.[currentTab.value] || [])

const emptyStateTitle = computed(() =>
	currentTab.value === 'enrolled'
		? __('No enrolled programs yet')
		: __('No programs available yet'),
)

const emptyStateDescription = computed(() =>
	currentTab.value === 'enrolled'
		? __('Explore published programs and choose a learning path to begin.')
		: __('New guided learning paths will appear here when they are published.'),
)

const openDetails = (programName: any, category: string) => {
	if (category === 'enrolled') {
		router.push({
			name: 'ProgramDetail',
			params: { programName: programName },
		})
	} else {
		showEnrollmentConfirmation.value = true
		enrollmentProgram.value = programName
	}
}

const tabs = computed(() => {
	return [
		{
			label: __('Enrolled'),
			value: 'enrolled',
		},
		{
			label: __('Published'),
			value: 'published',
		},
	]
})
</script>
