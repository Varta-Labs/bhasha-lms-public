<template>
	<LayoutHeader>
		<template #left-header>
			<Breadcrumbs :items="breadcrumbs" />
		</template>
		<template #right-header>
			<Button
				v-if="canCreateProgram()"
				@click="openForm('new')"
				variant="solid"
				class="bhasha-primary bhasha-program-create-button"
			>
				<template #prefix>
					<Plus class="size-4 stroke-2" />
				</template>
				{{ __('Create program') }}
			</Button>
		</template>
	</LayoutHeader>
	<main v-if="!isStudent" class="bhasha-programs-page">
		<section class="bhasha-programs-toolbar">
			<div>
				<h1 class="bhasha-programs-title">{{ __('Manage programs') }}</h1>
				<p class="bhasha-programs-description">
					{{
						__(
							'Build guided learning paths, organize courses, and enroll members.',
						)
					}}
				</p>
			</div>
			<div
				v-if="programs.data?.length"
				class="bhasha-program-result-count"
				aria-live="polite"
			>
				{{ programs.data.length }}
				{{ programs.data.length === 1 ? __('program') : __('programs') }}
			</div>
		</section>

		<section v-if="programs.data?.length" class="bhasha-program-grid">
			<button
				v-for="program in programs.data"
				:key="program.name"
				type="button"
				@click="openForm(program.name)"
				class="bhasha-program-card"
			>
				<div class="bhasha-program-card-topline">
					<div class="bhasha-program-card-icon" aria-hidden="true">
						<BookOpen class="size-5 stroke-1.5" />
					</div>
					<span
						class="bhasha-program-status"
						:class="program.published ? 'is-published' : 'is-draft'"
					>
						{{ program.published ? __('Published') : __('Draft') }}
					</span>
				</div>
				<div>
					<h2 class="bhasha-program-card-title">{{ program.name }}</h2>
					<p class="bhasha-program-card-hint">
						{{ __('Open to manage courses and members') }}
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
			</button>
		</section>

		<section v-else-if="!programs.list.loading" class="bhasha-programs-empty">
			<div class="bhasha-programs-empty-icon">
				<BookOpen class="size-6 stroke-1.5" />
			</div>
			<h2>{{ __('Create your first program') }}</h2>
			<p>
				{{
					__(
						'Combine courses into a clear learning path and invite members when you are ready.',
					)
				}}
			</p>
			<Button
				v-if="canCreateProgram()"
				variant="solid"
				class="bhasha-primary mt-2"
				@click="openForm('new')"
			>
				<template #prefix><Plus class="size-4 stroke-2" /></template>
				{{ __('Create program') }}
			</Button>
		</section>
	</main>
	<StudentPrograms v-else-if="isStudent" />
	<ProgramForm
		v-model="showForm"
		:programName="currentProgram"
		v-model:programs="programs"
	/>
</template>
<script setup>
import { Breadcrumbs, Button, usePageMeta, createListResource } from 'frappe-ui'
import { computed, inject, onMounted, ref } from 'vue'
import { BookOpen, Plus, User } from 'lucide-vue-next'
import { sessionStore } from '@/stores/session'
import ProgramForm from '@/pages/Programs/ProgramForm.vue'
import LayoutHeader from '@/components/Layouts/LayoutHeader.vue'
import StudentPrograms from '@/pages/Programs/StudentPrograms.vue'
import '@/styles/program-management.css'

const { brand } = sessionStore()
const user = inject('$user')
const showForm = ref(false)
const currentProgram = ref(null)
const readOnlyMode = window.read_only_mode

onMounted(() => {
	if (!user.data) {
		window.location.href = '/login'
	}
	if (user.data?.is_moderator || user.data?.is_instructor) {
		programs.reload()
	}
})

const programs = createListResource({
	doctype: 'LMS Program',
	cache: ['program'],
	fields: [
		'name',
		'title',
		'member_count',
		'course_count',
		'published',
		'enforce_course_order',
	],
	auto: false,
	orderBy: 'creation desc',
})

const canCreateProgram = () => {
	if (readOnlyMode) return false
	if (user.data?.is_moderator || user.data?.is_instructor) return true
	return false
}

const openForm = (programName) => {
	if (!canCreateProgram()) return
	currentProgram.value = programName
	showForm.value = true
}

const isStudent = computed(() => {
	return user.data?.is_student || false
})

const breadcrumbs = computed(() => [
	{
		label: __('Programs'),
	},
])

usePageMeta(() => {
	return {
		title: __('Programs'),
		icon: brand.favicon,
	}
})
</script>
