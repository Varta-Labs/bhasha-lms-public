<template>
	<div class="course-enrollment-card">
		<div class="course-preview relative group overflow-hidden bg-ink-gray-9">
			<iframe
				v-if="video_link"
				:src="video_link"
				class="h-full w-full"
				:title="__('Course introduction video')"
				allow="autoplay; fullscreen; picture-in-picture"
				allowfullscreen
			/>
			<div v-else class="relative h-full w-full">
				<img
					:src="previewImage"
					:alt="course.data?.title || __('Course preview')"
					class="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
				/>
			</div>
		</div>
		<div class="p-5 sm:p-6">
			<div
				class="mb-1 text-xs font-semibold uppercase tracking-[0.12em] text-ink-gray-5"
			>
				{{
					hasEarlyBirdOffer
						? __('Early bird offer')
						: course.data?.paid_course
						? __('Course fee')
						: __('Full course access')
				}}
			</div>
			<div class="mb-5 flex items-baseline gap-3">
				<strong class="text-3xl font-bold tracking-tight text-ink-gray-9">{{ priceLabel }}</strong>
				<s v-if="hasEarlyBirdOffer" class="text-lg font-semibold text-ink-gray-5">₹2,999</s>
			</div>
			<div v-if="!readOnlyMode">
				<div v-if="course.data?.membership" class="space-y-2 mb-8">
					<router-link
						:to="{
							name: 'Lesson',
							params: {
								courseName: course.data?.name,
								chapterNumber: course?.data?.current_lesson
									? course?.data?.current_lesson.split('-')[0]
									: 1,
								lessonNumber: course?.data?.current_lesson
									? course?.data?.current_lesson.split('-')[1]
									: 1,
							},
						}"
					>
						<Button
							variant="solid"
							size="md"
							class="bhasha-primary w-full"
						>
							<template #prefix>
								<BookText class="size-4 stroke-1.5" />
							</template>
							<span>
								{{ __('Continue Learning') }}
							</span>
						</Button>
					</router-link>
					<CertificationLinks
						:courseName="course.data.name"
						class="w-full"
					/>
				</div>
				<a
					v-else-if="course.data?.paid_course && !isAdmin && !user.data"
					:href="signupUrl"
				>
					<Button
						variant="solid"
						size="md"
						class="bhasha-primary mb-8 w-full"
					>
						<template #prefix>
							<CreditCard class="size-4 stroke-1.5" />
						</template>
						<span>
							{{ guestEnrollLabel }}
						</span>
					</Button>
				</a>
				<router-link
					v-else-if="course.data?.paid_course && !isAdmin"
					:to="{
						name: 'Billing',
						params: {
							type: 'course',
							name: course.data.name,
						},
					}"
				>
					<Button
						variant="solid"
						size="md"
						class="bhasha-primary mb-8 w-full"
					>
						<template #prefix>
							<CreditCard class="size-4 stroke-1.5" />
						</template>
						<span>
							{{ enrollLabel }}
						</span>
					</Button>
				</router-link>
				<Badge
					v-else-if="course.data?.disable_self_learning && !isAdmin"
					theme="blue"
					size="lg"
					class="mb-4"
				>
					{{
						__(
							'Please contact support to enroll',
						)
					}}
				</Badge>
				<Button
					v-else-if="!isAdmin"
					@click="enrollStudent()"
					variant="solid"
					class="bhasha-primary mb-8 w-full"
					size="md"
				>
					<template #prefix>
						<BookText class="size-4 stroke-1.5" />
					</template>
					<span>
						{{ enrollLabel }}
					</span>
				</Button>
				<Button
					v-if="canGetCertificate"
					@click="fetchCertificate()"
					variant="subtle"
					class="w-full mt-2"
					size="md"
				>
					<template #prefix>
						<GraduationCap class="size-4 stroke-1.5" />
					</template>
					{{ __('Get Certificate') }}
				</Button>
			</div>
			<section class="course-includes">
				<div class="mb-3 text-sm font-semibold text-ink-gray-9">
					{{ __('This course includes:') }}
				</div>
				<div class="course-include-row">
					<Users class="size-4.5 stroke-2 shrink-0 text-indigo-600 dark:text-indigo-400" />
					<span>{{ enrolledLabel ? `${enrolledLabel} ${__('enrolled')}` : __('Active learner community') }}</span>
				</div>
				<div class="course-include-row">
					<MonitorPlay
						class="size-4.5 stroke-2 shrink-0 text-bhasha-purple dark:text-purple-400"
					/>
					<span>{{ course.data?.video_link ? __('On demand course video') : __('On demand practice audio & video') }}</span>
				</div>
				<div class="course-include-row">
					<BookOpen
						class="size-4.5 stroke-2 shrink-0 text-emerald-600 dark:text-emerald-400"
					/>
					<span>
						{{ course.data?.lessons ? `${course.data.lessons} ${course.data.lessons === 1 ? __('Lesson') : __('Lessons')}` : __('Comprehensive structured modules') }}
					</span>
				</div>
				<div class="course-include-row">
					<HelpCircle
						class="size-4.5 stroke-2 shrink-0 text-amber-500 dark:text-amber-400"
					/>
					<span>
						{{ (course.data?.quiz_count || 0) > 0 ? `${course.data.quiz_count} ${course.data.quiz_count === 1 ? __('Quiz topic') : __('Quiz topics')}` : __('Interactive exercises & roleplays') }}
					</span>
				</div>
				<div class="course-include-row">
					<Award class="size-4.5 stroke-2 shrink-0 text-rose-500 dark:text-rose-400" />
					<span>{{ __('Verifiable certificate of completion') }}</span>
				</div>
				<div class="course-include-row">
					<BookText class="size-4.5 stroke-2 shrink-0 text-cyan-600 dark:text-cyan-400" />
					<span>{{ __('Full lifetime online access') }}</span>
				</div>
			</section>
		</div>
	</div>
</template>
<script setup lang="ts">
import {
	Award,
	BookOpen,
	BookText,
	CreditCard,
	GraduationCap,
	HelpCircle,
	MonitorPlay,
	Users,
} from 'lucide-vue-next'
import { computed, inject } from 'vue'
import { Badge, Button, call, createResource, toast } from 'frappe-ui'
import { useRouter } from 'vue-router'
import CertificationLinks from '@/components/CertificationLinks.vue'
import { useTelemetry } from 'frappe-ui/frappe'
import { getLmsRoute, getSignupUrl } from '@/utils/basePath'
import type {
	CourseDetails,
	CourseInstructorInfo,
	Resource,
	SessionUser,
} from '@/types/api'

const router = useRouter()
const user = inject<SessionUser>('$user')!
const readOnlyMode = (window as Window & { read_only_mode?: boolean })
	.read_only_mode
const { capture } = useTelemetry()

const props = withDefaults(
	defineProps<{
		course: Resource<CourseDetails | null>
	}>(),
	{},
)

const video_link = computed<string | undefined>(() => {
	let link = props.course.data?.video_link
	if (!link && (props.course.data?.name?.includes('kannada') || props.course.data?.title?.includes('Kannada'))) {
		link = 'dQw4w9WgXcQ'
	}
	if (!link) return undefined
	return link.startsWith('http') ? link : 'https://www.youtube.com/embed/' + link
})

const previewImage = computed<string | undefined>(() => {
	if (props.course.data?.image) return props.course.data.image
	return `${import.meta.env.BASE_URL}kannada-course-hero-v1.png`
})

const signupUrl = computed(() =>
	getSignupUrl(getLmsRoute(`billing/course/${props.course.data?.name || ''}`)),
)

function enrollStudent() {
	if (!user.data) {
		toast.warning(__('You need to login first to enroll for this course'))
		setTimeout(() => {
			window.location.href = `/login?redirect-to=${window.location.pathname}`
		}, 500)
		return
	}
	const courseName = props.course.data?.name
	if (!courseName) return
	call('frappe.client.insert', {
		doc: {
			doctype: 'LMS Enrollment',
			course: courseName,
			member: user.data.name,
		},
	})
		.then(() => {
			capture('enrolled_in_course', { course: courseName })
			toast.success(__('You have been enrolled in this course'))
			setTimeout(() => {
				router.push({
					name: 'Lesson',
					params: {
						courseName,
						chapterNumber: 1,
						lessonNumber: 1,
					},
				})
			}, 1000)
		})
		.catch((err: { messages?: string[] } | string) => {
			const msg =
				typeof err === 'string' ? err : (err.messages?.[0] ?? 'Error')
			toast.warning(__(msg))
			console.error(err)
		})
}

const is_instructor = (): boolean => {
	let user_is_instructor = false
	props.course.data?.instructors.forEach(
		(instructor: CourseInstructorInfo) => {
			if (!user_is_instructor && instructor.name == user.data?.name) {
				user_is_instructor = true
			}
		},
	)
	return user_is_instructor
}

const priceLabel = computed<string>(() => {
	if (props.course.data?.paid_course) return props.course.data?.price || __('Paid course')
	return __('Free')
})

const hasEarlyBirdOffer = computed<boolean>(() => {
	const identity = `${props.course.data?.name || ''} ${props.course.data?.title || ''}`.toLowerCase()
	return Boolean(props.course.data?.paid_course && (identity.includes('hindi') || identity.includes('kannada')))
})

const guestEnrollLabel = computed(() => __('Sign up and Enroll'))

const enrollLabel = computed(() => `${__('Enroll for')} ${priceLabel.value}`)

const enrolledLabel = computed<string>(() => {
	const n = props.course.data?.enrollments ?? 0
	if (!n) return ''
	if (n < 50) return String(n)
	const tier = n < 1000 ? 50 : 100
	return `${Math.floor(n / tier) * tier}+`
})

const hasCourseStats = computed<boolean>(() =>
	Boolean(
		enrolledLabel.value ||
		props.course.data?.video_link ||
		props.course.data?.lessons ||
		(props.course.data?.quiz_count ?? 0) > 0 ||
		props.course.data?.enable_certification,
	),
)

const canGetCertificate = computed<boolean>(() => {
	return Boolean(
		props.course.data?.enable_certification &&
		(props.course.data?.membership?.progress ?? 0) >= 100,
	)
})

const certificate = createResource({
	url: 'lms.lms.doctype.lms_certificate.lms_certificate.create_certificate',
	makeParams(values: { course?: string }) {
		return {
			course: values.course,
		}
	},
	onSuccess(data: { name: string; template: string }) {
		window.open(
			`/api/method/frappe.utils.print_format.download_pdf?doctype=LMS+Certificate&name=${
				data.name
			}&format=${encodeURIComponent(data.template)}`,
			'_blank',
		)
	},
}) as Resource<{ name: string; template: string } | null>

const fetchCertificate = () => {
	certificate.submit({
		course: props.course.data?.name,
		member: user.data?.name,
	})
}

defineExpose({ enrollStudent })

const isAdmin = computed<boolean>(() => {
	return Boolean(user.data?.is_moderator) || is_instructor()
})
</script>
