<template>
	<Dialog
		v-model="show"
		:options="{
			title: __('Program enrollment'),
			size: '2xl',
		}"
	>
		<template #body-title>
			<div v-if="program.data" class="bhasha-dialog-heading">
				<div class="bhasha-dialog-icon" aria-hidden="true">
					<Route class="size-5 stroke-1.75" />
				</div>
				<div>
					<h3 class="bhasha-dialog-title">
						{{ __('Enroll in {0}').format(program.data?.name) }}
					</h3>
					<p class="bhasha-dialog-description">
						{{ __('Review the learning path before you begin.') }}
					</p>
				</div>
			</div>
		</template>
		<template #body-content>
			<div v-if="program.data" class="bhasha-program-enrollment text-base">
				<div class="bhasha-program-enrollment-note">
					<BookOpen class="size-5 shrink-0 stroke-1.5" />
					<p>
						<span>
							{{
								__('This program consists of {0} courses').format(
									program.data.courses.length,
								)
							}}
						</span>
						<span v-if="program.data.enforce_course_order">
							{{
								__(
									' designed as a structured learning path to guide your progress. Courses in this program must be taken in order, and each course will unlock as you complete the previous one. ',
								)
							}}
						</span>
						<span v-else>
							{{
								__(
									' designed as a learning path to guide your progress. You may take the courses in any order that suits you. ',
								)
							}}
						</span>
						<span>
							{{ __('Are you sure you want to enroll?') }}
						</span>
					</p>
				</div>

				<div class="bhasha-program-enrollment-courses">
					<div class="bhasha-program-enrollment-section-title">
						{{ __('Courses in this Program') }}
					</div>
					<div class="bhasha-program-enrollment-grid">
						<div
							v-for="course in program.data.courses"
							:key="course.name"
							class="bhasha-program-enrollment-course"
						>
							<div class="bhasha-program-enrollment-course-title">
								{{ course.title }}
							</div>

							<!-- <div class="text-sm text-ink-gray-7 mb-8">
                                {{ course.short_introduction }}
                            </div> -->

							<div class="bhasha-program-enrollment-course-meta">
								<Tooltip :text="__('Lessons')">
									<span class="flex items-center gap-x-1">
										<BookOpen class="size-3 stroke-1.5" />
										<span> {{ course.lessons }} {{ __('lessons') }} </span>
									</span>
								</Tooltip>

								<Tooltip :text="__('Enrolled Students')">
									<span class="flex items-center gap-x-1">
										<User class="size-3 stroke-1.5" />
										<span> {{ course.enrollments }} {{ __('students') }} </span>
									</span>
								</Tooltip>

								<!-- <Tooltip v-if="course.rating" :text="__('Average Rating')">
                                    <span class="flex items-center gap-x-1">
                                        <Star class="size-3 stroke-1.5" />
                                        <span>
                                            {{ course.rating }} {{ __("rating") }}
                                        </span>
                                    </span>
                                </Tooltip> -->
							</div>

							<div
								v-if="course.instructors?.length"
								class="bhasha-program-enrollment-instructor"
							>
								<UserAvatar :user="course.instructors[0]" />
								<span>
									{{ course.instructors[0].full_name }}
								</span>
							</div>
						</div>
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
					@click="enrollInProgram(close)"
				>
					{{ __('Confirm Enrollment') }}
				</Button>
			</div>
		</template>
	</Dialog>
</template>
<script setup lang="ts">
import { Button, call, createResource, Dialog, toast, Tooltip } from 'frappe-ui'
import { inject, watch } from 'vue'
import { BookOpen, Route, User } from 'lucide-vue-next'
import { useRouter } from 'vue-router'

const show = defineModel()
const user = inject<any>('$user')
const router = useRouter()

const props = defineProps<{
	programName: any
}>()

const program = createResource({
	url: 'lms.lms.utils.get_program_details',
	makeParams(values: any) {
		return {
			program_name: props.programName,
		}
	},
	auto: false,
})

watch(
	() => props.programName,
	() => {
		if (props.programName) {
			program.reload()
		}
	},
)

const enrollInProgram = (close: () => void) => {
	call('lms.lms.utils.enroll_in_program', {
		program: props.programName,
	})
		.then(() => {
			toast.success(__('Successfully enrolled in program'))
			router.push({
				name: 'ProgramDetail',
				params: { programName: props.programName },
			})
			close()
		})
		.catch((error: any) => {
			toast.error(__('Failed to enroll in program: {0}').format(error.message))
			console.error('Enrollment Error:', error)
		})
}
</script>
