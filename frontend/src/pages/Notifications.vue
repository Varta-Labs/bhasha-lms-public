<template>
	<LayoutHeader>
		<template #left-header>
			<Breadcrumbs :items="breadcrumbs" />
		</template>
		<template #right-header>
			<Button
				@click="markAllAsRead.submit"
				:loading="markAllAsRead.loading"
				v-if="activeTab === 'Unread' && unReadNotifications.data?.length > 0"
				class="bhasha-notification-mark-all"
				:aria-label="__('Mark all as read')"
			>
				<template #prefix>
					<CheckCheck class="size-4 stroke-2" />
				</template>
				{{ __('Mark all as read') }}
			</Button>
			<div
				class="bhasha-notification-tabs"
				role="group"
				:aria-label="__('Notification status')"
			>
				<button
					v-for="tab in notificationTabs"
					:key="tab.value"
					type="button"
					class="bhasha-notification-tab"
					:class="{ 'is-active': activeTab === tab.value }"
					:aria-pressed="activeTab === tab.value"
					@click="activeTab = tab.value"
				>
					<span>{{ __(tab.label) }}</span>
					<span
						class="bhasha-notification-count"
						:aria-label="`${tab.count} ${__(tab.label)}`"
					>
						{{ tab.count }}
					</span>
				</button>
			</div>
		</template>
	</LayoutHeader>
	<main class="bhasha-notifications-page">
		<div class="bhasha-notifications-list">
			<div
				v-if="notifications?.length"
				v-for="log in notifications"
				:key="log.name"
				class="bhasha-notification-card flex items-start gap-3"
				:class="{
					'is-clickable': log.link,
					'is-unread': !log.read,
					'items-center': !showDetails(log) && !isMentionOrComment(log),
				}"
				@click="navigateToPage(log)"
			>
				<div class="bhasha-notification-avatar">
					<Avatar
						:image="log.from_user_details.user_image"
						size="xl"
						:label="log.from_user_details.full_name"
					/>
					<span v-if="!log.read" class="bhasha-unread-dot">
						<span class="sr-only">{{ __('Unread') }}</span>
					</span>
				</div>
				<div class="min-w-0 w-full space-y-2.5">
					<div class="flex items-start justify-between gap-3">
						<div class="min-w-0">
							<div
								class="bhasha-notification-subject"
								:class="{ 'is-unread': !log.read }"
								v-html="log.subject"
							></div>
							<div class="bhasha-notification-time">
								{{ dayjs(log.creation).fromNow() }}
							</div>
						</div>
						<div class="shrink-0">
							<Button
								variant="ghost"
								v-if="!log.read"
								class="bhasha-mark-read-button"
								:aria-label="__('Mark as read')"
								:title="__('Mark as read')"
								@click.stop="handleMarkAsRead(log.name)"
							>
								<template #icon>
									<Check class="size-4 stroke-2" />
								</template>
							</Button>
						</div>
					</div>
					<div
						v-if="isMentionOrComment(log)"
						v-html="log.email_content"
						class="bhasha-notification-message line-clamp-3 overflow-hidden"
					></div>
					<div
						v-else-if="showDetails(log)"
						class="bhasha-notification-details flex items-stretch gap-x-2 overflow-hidden"
					>
						<iframe
							v-if="
								log.document_type == 'LMS Course' &&
								log.document_details.video_link
							"
							:src="`https://www.youtube.com/embed/${log.document_details.video_link}`"
							class="w-72"
						/>
						<video
							v-else-if="
								log.document_type == 'LMS Batch' &&
								log.document_details.video_link
							"
							:src="log.document_details.video_link"
							class="w-72"
						/>
						<div class="p-3">
							<div class="bhasha-notification-badge mb-2">
								{{
									log.document_type === 'LMS Course'
										? __('New Course')
										: __('New Batch')
								}}
							</div>
							<div class="font-semibold mb-1 text-ink-gray-9">
								{{ __(log.document_details.title) }}
							</div>
							<div class="leading-5 text-ink-gray-7">
								{{ __(log.document_details.short_introduction) }}
							</div>
							<div
								v-if="log.document_details.start_date"
								class="flex items-center gap-x-2 text-sm mt-5"
							>
								<Calendar class="size-3 stroke-1.5" />
								<span>
									{{
										dayjs(log.document_details.start_date).format('DD MMM YYYY')
									}}
								</span>
							</div>
							<div
								v-if="log.document_details.start_time"
								class="flex items-center gap-x-2 text-sm mt-2"
							>
								<Clock class="size-3 stroke-1.5" />
								<span>
									{{ formatTime(log.document_details.start_time) }}
									{{ log.document_details.timezone }}
								</span>
							</div>
							<div
								v-if="log.document_details.instructors.length > 1"
								class="space-y-2 mt-5"
							>
								<div
									v-for="instructor in log.document_details.instructors"
									class="flex items-center gap-x-2"
								>
									<Avatar
										:size="'sm'"
										:image="instructor.user_image"
										:label="instructor.full_name"
									/>
									<span class="font-medium text-sm text-ink-gray-9">
										{{ instructor.full_name }}
									</span>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
			<div v-else class="bhasha-notifications-empty">
				<div class="bhasha-notifications-empty-icon">
					<Bell class="size-6 stroke-1.5" />
				</div>
				<p class="text-lg font-semibold text-ink-gray-9 mb-2">
					{{
						activeTab === 'Unread'
							? __('No unread notifications')
							: __('No read notifications')
					}}
				</p>
				<p class="text-p-base w-full md:w-2/5 text-center text-ink-gray-7">
					{{
						activeTab === 'Unread'
							? __("You're all caught up! Check back later for updates.")
							: __('Notifications you have read will appear here.')
					}}
				</p>
			</div>
		</div>
	</main>
</template>
<script setup>
import {
	Avatar,
	Breadcrumbs,
	Button,
	createListResource,
	createResource,
	getCachedResource,
	usePageMeta,
} from 'frappe-ui'
import { sessionStore } from '../stores/session'
import { computed, inject, ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Bell, Calendar, Check, CheckCheck, Clock } from 'lucide-vue-next'
import { formatTime } from '@/utils/'
import LayoutHeader from '@/components/Layouts/LayoutHeader.vue'

const { brand } = sessionStore()
const dayjs = inject('$dayjs')
const user = inject('$user')
const socket = inject('$socket')
const activeTab = ref('Unread')
const router = useRouter()

onMounted(() => {
	if (!user.data) router.push({ name: 'Courses' })

	socket.on('publish_lms_notifications', (data) => {
		unReadNotifications.reload()
	})
})

const notifications = computed(() => {
	return activeTab.value === 'Unread'
		? unReadNotifications.data
		: readNotifications.data
})

const notificationTabs = computed(() => [
	{
		label: 'Unread',
		value: 'Unread',
		count: unReadNotifications.data?.length || 0,
	},
	{
		label: 'Read',
		value: 'Read',
		count: readNotifications.data?.length || 0,
	},
])

const unReadNotifications = createListResource({
	doctype: 'Notification Log',
	url: 'lms.lms.api.get_notifications',
	filters: {
		read: 0,
	},
	auto: user.data ? true : false,
	cache: 'Unread Notifications',
})

const readNotifications = createListResource({
	doctype: 'Notification Log',
	url: 'lms.lms.api.get_notifications',
	filters: {
		read: 1,
	},
	auto: user.data ? true : false,
	cache: 'Read Notifications',
})

const refreshSidebarCount = () => {
	getCachedResource('Unread Notifications Count')?.reload()
}

const markAsRead = createResource({
	url: 'frappe.desk.doctype.notification_log.notification_log.mark_as_read',
	makeParams(values) {
		return {
			docname: values.name,
		}
	},
	onSuccess(data) {
		unReadNotifications.reload()
		readNotifications.reload()
		refreshSidebarCount()
	},
})

const markAllAsRead = createResource({
	url: 'frappe.desk.doctype.notification_log.notification_log.mark_all_as_read',
	onSuccess(data) {
		unReadNotifications.reload()
		readNotifications.reload()
		refreshSidebarCount()
	},
})

const handleMarkAsRead = (logName) => {
	markAsRead.submit({ name: logName })
}

const navigateToPage = (log) => {
	if (!log.link) return
	if (!log.read) handleMarkAsRead(log.name)
	let link = log.link.split('/')
	if (link[2] == 'courses') {
		router.push({
			name: 'CourseDetail',
			params: { courseName: link[3] },
		})
	} else if (link.includes('batches')) {
		if (link.includes('details')) {
			router.push({
				name: 'BatchDetail',
				params: { batchName: link.pop() },
			})
		} else {
			router.push({
				name: 'Batch',
				params: { batchName: link.pop() },
			})
		}
	} else if (link.includes('assignment-submission')) {
		router.push({
			name: 'AssignmentSubmission',
			params: {
				submissionName: link[4],
				assignmentID: link[3],
			},
		})
	}
}

const isMentionOrComment = (log) => {
	if (log.type == 'Mention') {
		return true
	}
	if (log.subject.includes('mentioned you')) {
		return true
	}
	if (log.subject.includes('comment')) {
		return true
	}
	return false
}

const showDetails = (log) => {
	return (
		['LMS Course', 'LMS Batch'].includes(log.document_type) &&
		log.document_details
	)
}

onUnmounted(() => {
	socket.off('publish_lms_notifications')
})

const breadcrumbs = computed(() => {
	let crumbs = [
		{
			label: 'Notifications',
			route: {
				name: 'Notifications',
			},
		},
	]
	return crumbs
})

usePageMeta(() => {
	return {
		title: 'Notifications',
		icon: brand.favicon,
	}
})
</script>

<style scoped>
.bhasha-notifications-page {
	min-height: calc(100vh - 3.75rem);
	padding: clamp(1rem, 3vw, 2rem);
	background:
		radial-gradient(
			circle at 12% 0%,
			rgba(129, 80, 223, 0.08),
			transparent 24rem
		),
		var(--bhasha-page);
}

.bhasha-notifications-list {
	width: min(100%, 56rem);
	margin-inline: auto;
	display: flex;
	flex-direction: column;
	gap: 0.75rem;
}

.bhasha-notification-tabs {
	display: inline-flex;
	align-items: center;
	gap: 0.25rem;
	padding: 0.25rem;
	border: 1px solid var(--bhasha-border-brand);
	border-radius: 9999px;
	background: rgba(255, 255, 255, 0.86);
	box-shadow: 0 5px 16px rgba(61, 34, 111, 0.06);
}

.bhasha-notification-tab {
	display: inline-flex;
	min-height: 2rem;
	align-items: center;
	gap: 0.4rem;
	padding: 0.35rem 0.7rem;
	border-radius: 9999px;
	color: var(--bhasha-text-muted);
	font-size: 0.8125rem;
	font-weight: 650;
	line-height: 1;
	transition:
		background-color 160ms ease,
		color 160ms ease,
		box-shadow 160ms ease;
}

.bhasha-notification-tab:hover {
	background: var(--bhasha-50);
	color: var(--bhasha-700);
}

.bhasha-notification-tab.is-active {
	background: linear-gradient(135deg, var(--bhasha-600), var(--bhasha-700));
	color: #fff;
	box-shadow: 0 6px 14px rgba(101, 50, 197, 0.24);
}

.bhasha-notification-tab:focus-visible {
	outline: none;
	box-shadow: var(--bhasha-focus-ring);
}

.bhasha-notification-count {
	display: inline-grid;
	min-width: 1.25rem;
	height: 1.25rem;
	place-items: center;
	padding-inline: 0.3rem;
	border-radius: 9999px;
	background: var(--bhasha-100);
	color: var(--bhasha-700);
	font-size: 0.6875rem;
	font-variant-numeric: tabular-nums;
}

.bhasha-notification-tab.is-active .bhasha-notification-count {
	background: rgba(255, 255, 255, 0.2);
	color: #fff;
}

.bhasha-notification-card {
	position: relative;
	padding: 1rem;
	border: 1px solid var(--bhasha-border);
	border-radius: var(--bhasha-radius-card);
	background: var(--bhasha-surface);
	box-shadow: 0 5px 18px rgba(61, 34, 111, 0.045);
	transition:
		transform 160ms ease,
		border-color 160ms ease,
		box-shadow 160ms ease;
}

.bhasha-notification-card.is-unread {
	border-color: rgba(101, 50, 197, 0.22);
	background:
		linear-gradient(
			110deg,
			rgba(246, 242, 255, 0.94),
			rgba(255, 255, 255, 0.98) 48%
		),
		var(--bhasha-surface);
	box-shadow: 0 8px 22px rgba(61, 34, 111, 0.07);
}

.bhasha-notification-card.is-unread::before {
	position: absolute;
	inset-block: 1.1rem;
	inset-inline-start: -1px;
	width: 3px;
	border-radius: 9999px;
	background: linear-gradient(180deg, var(--bhasha-500), var(--bhasha-700));
	content: '';
}

.bhasha-notification-card.is-clickable {
	cursor: pointer;
}

.bhasha-notification-card.is-clickable:hover {
	transform: translateY(-1px);
	border-color: rgba(101, 50, 197, 0.3);
	box-shadow: 0 12px 28px rgba(61, 34, 111, 0.09);
}

.bhasha-notification-card:focus-visible {
	outline: none;
	box-shadow:
		var(--bhasha-focus-ring),
		0 10px 24px rgba(61, 34, 111, 0.08);
}

.bhasha-notification-avatar {
	position: relative;
	flex-shrink: 0;
}

.bhasha-unread-dot {
	position: absolute;
	inset-inline-end: -0.05rem;
	inset-block-end: 0.05rem;
	width: 0.7rem;
	height: 0.7rem;
	border: 2px solid var(--bhasha-surface);
	border-radius: 9999px;
	background: var(--bhasha-600);
	box-shadow: 0 0 0 2px var(--bhasha-100);
}

.bhasha-notification-subject {
	color: var(--bhasha-text);
	font-size: 0.9375rem;
	font-weight: 500;
	line-height: 1.5;
}

.bhasha-notification-subject.is-unread {
	color: var(--bhasha-900);
	font-weight: 700;
}

.bhasha-notification-time {
	margin-top: 0.2rem;
	color: var(--bhasha-text-muted);
	font-size: 0.75rem;
	font-weight: 550;
}

.bhasha-mark-read-button {
	color: var(--bhasha-600);
}

.bhasha-mark-read-button:hover {
	background: var(--bhasha-100);
	color: var(--bhasha-800);
}

.bhasha-notification-message,
.bhasha-notification-details {
	border: 1px solid var(--bhasha-border-brand);
	border-radius: var(--bhasha-radius-control);
	background: rgba(255, 255, 255, 0.72);
}

.bhasha-notification-message {
	padding: 0.65rem 0.8rem;
	color: var(--bhasha-text-muted);
	line-height: 1.55;
}

.bhasha-notification-badge {
	display: inline-flex;
	width: fit-content;
	padding: 0.3rem 0.65rem;
	border: 1px solid var(--bhasha-border-brand);
	border-radius: 9999px;
	background: var(--bhasha-50);
	color: var(--bhasha-700);
	font-size: 0.75rem;
	font-weight: 700;
}

.bhasha-notifications-empty {
	display: flex;
	min-height: min(28rem, calc(100vh - 9rem));
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: 3rem 1.5rem;
	border: 1px dashed rgba(101, 50, 197, 0.2);
	border-radius: var(--bhasha-radius-card);
	background: rgba(255, 255, 255, 0.72);
	text-align: center;
}

.bhasha-notifications-empty-icon {
	display: grid;
	width: 3.25rem;
	height: 3.25rem;
	place-items: center;
	margin-bottom: 1rem;
	border-radius: 1rem;
	background: var(--bhasha-100);
	color: var(--bhasha-700);
	box-shadow: 0 8px 20px rgba(61, 34, 111, 0.08);
}

@media (max-width: 639px) {
	.bhasha-notifications-page {
		padding: 0.75rem;
	}

	.bhasha-notification-card {
		padding: 0.85rem;
		border-radius: 1rem;
	}

	.bhasha-notification-mark-all {
		font-size: 0;
	}

	.bhasha-notification-mark-all :deep(svg) {
		margin: 0;
	}

	.bhasha-notification-details {
		flex-direction: column;
	}

	.bhasha-notification-details :is(iframe, video) {
		width: 100%;
		aspect-ratio: 16 / 9;
	}
}

@media (prefers-reduced-motion: reduce) {
	.bhasha-notification-card,
	.bhasha-notification-tab {
		transition: none;
	}
}
</style>
