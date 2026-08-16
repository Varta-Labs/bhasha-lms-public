<template>
	<NoPermission v-if="!$user.data" />
	<div v-else-if="profile.data" class="bhasha-profile-page">
		<header
			class="bhasha-product-header sticky group top-0 z-10 flex flex-col md:flex-row md:items-center justify-between border-b bg-surface-white px-3 py-2.5 sm:px-5"
		>
			<Breadcrumbs class="h-7" :items="breadcrumbs" />
			<Button v-if="isSessionUser()" class="invisible group-hover:visible">
				<template #icon>
					<RefreshCcw
						class="w-4 h-4 stroke-1.5 text-ink-gray-7"
						@click="reloadUser()"
					/>
				</template>
			</Button>
		</header>
		<div class="bhasha-profile-cover group relative h-[180px] w-full">
			<img
				v-if="profile.data.cover_image"
				:src="profile.data.cover_image"
				class="h-[180px] w-full object-cover object-center"
			/>
			<div
				v-else
				:class="{ 'bg-surface-gray-2': !profile.data.cover_image }"
				class="bhasha-profile-cover__fallback h-[180px] w-full"
			></div>
			<div
				class="absolute bottom-[30%] md:bottom-0 start-[50%] mb-4 flex -translate-x-1/2 gap-x-2 opacity-0 transition-opacity focus-within:opacity-100 group-hover:opacity-100"
				v-if="isSessionUser()"
			>
				<EditCoverImage
					@select="(imageUrl) => coverImage.submit({ url: imageUrl })"
				>
					<template v-slot="{ togglePopover }">
						<Button
							v-if="!readOnlyMode"
							variant="outline"
							@click="togglePopover()"
						>
							<template #prefix>
								<Edit class="w-4 h-4 stroke-1.5 text-ink-gray-7" />
							</template>
							{{ __('Edit') }}
						</Button>
					</template>
				</EditCoverImage>
			</div>
		</div>
		<main
			class="bhasha-profile-shell mx-auto -mt-14 max-w-4xl translate-x-0 px-5"
		>
			<section
				class="bhasha-profile-card flex flex-col md:flex-row items-center"
			>
				<div>
					<div class="relative">
						<img
							v-if="profile.data.user_image"
							:src="profile.data.user_image"
							class="bhasha-profile-avatar object-cover h-[108px] w-[108px] rounded-full border-4 border-white"
						/>
						<div
							v-else
							class="bhasha-profile-avatar flex items-center justify-center h-[108px] w-[108px] rounded-full border-4 border-white text-3xl font-semibold text-ink-gray-7"
						>
							{{ profile.data.full_name.charAt(0).toUpperCase() }}
						</div>
						<Tooltip
							v-if="profile.data.open_to"
							:text="
								profile.data.open_to === 'Work'
									? __('Open to Work')
									: __('Hiring')
							"
							placement="right"
						>
							<div
								class="absolute bottom-3 end-1 p-0.5 bg-surface-white rounded-full"
							>
								<div
									class="rounded-full w-fit"
									:class="
										profile.data.open_to === 'Work'
											? 'bg-surface-green-3'
											: 'bg-purple-500'
									"
								>
									<BadgeCheckIcon class="text-ink-white size-5" />
								</div>
							</div>
						</Tooltip>
					</div>
				</div>
				<div class="ms-6 mt-5">
					<h2 class="text-3xl font-semibold text-ink-gray-9">
						{{ profile.data.full_name }}
					</h2>
					<div class="text-base text-ink-gray-7 mt-1">
						{{ profile.data.headline }}
					</div>
					<div class="flex items-center gap-x-4 mt-2">
						<Twitter
							v-if="profile.data.twitter"
							class="size-4 text-ink-gray-5 cursor-pointer"
							@click="navigateTo(profile.data.twitter)"
						/>
						<Linkedin
							v-if="profile.data.linkedin"
							class="size-4 text-ink-gray-5 cursor-pointer"
							@click="navigateTo(profile.data.linkedin)"
						/>
						<Github
							v-if="profile.data.github"
							class="size-4 text-ink-gray-5 cursor-pointer"
							@click="navigateTo(profile.data.github)"
						/>
					</div>
				</div>
				<Button
					v-if="isSessionUser() && !readOnlyMode"
					class="bhasha-profile-edit mt-3 sm:mt-0 md:ms-auto"
					@click="editProfile()"
				>
					<template #prefix>
						<Edit class="w-4 h-4 stroke-1.5 text-ink-gray-7" />
					</template>
					{{ __('Edit Profile') }}
				</Button>
			</section>

			<div class="bhasha-profile-tabs mb-4 mt-6">
				<TabButtons
					class="inline-block"
					:buttons="getTabButtons()"
					v-model="activeTab"
				/>
			</div>
			<div class="bhasha-profile-content">
				<router-view :profile="profile" :key="profile.data?.name" />
			</div>
		</main>
	</div>
	<EditProfile
		v-model="showProfileModal"
		v-model:reloadProfile="profile"
		:profile="profile"
	/>
</template>
<script setup>
import {
	Breadcrumbs,
	Button,
	call,
	createResource,
	TabButtons,
	Tooltip,
	toast,
	usePageMeta,
} from 'frappe-ui'
import { computed, inject, watch, ref, onMounted, watchEffect } from 'vue'
import { sessionStore } from '@/stores/session'
import {
	BadgeCheckIcon,
	Edit,
	Github,
	Linkedin,
	RefreshCcw,
	Twitter,
} from 'lucide-vue-next'
import { useRoute, useRouter } from 'vue-router'
import { convertToTitleCase } from '@/utils'
import UserAvatar from '@/components/UserAvatar.vue'
import NoPermission from '@/components/NoPermission.vue'
import EditProfile from '@/components/Modals/EditProfile.vue'
import EditCoverImage from '@/components/Modals/EditCoverImage.vue'

const { user, brand } = sessionStore()
const $user = inject('$user')
const route = useRoute()
const router = useRouter()
const activeTab = ref('')
const showProfileModal = ref(false)
const readOnlyMode = window.read_only_mode

const props = defineProps({
	username: {
		type: String,
		required: true,
	},
})

onMounted(() => {
	if ($user.data) profile.reload()
	setActiveTab()
})

const profile = createResource({
	url: 'lms.lms.api.get_profile_details',
	makeParams() {
		return {
			username: props.username,
		}
	},
})

const coverImage = createResource({
	url: 'frappe.client.set_value',
	makeParams(values) {
		return {
			doctype: 'User',
			name: profile.data?.name,
			fieldname: 'cover_image',
			value: values.url,
		}
	},
	onSuccess() {
		profile.reload()
	},
})

const setActiveTab = () => {
	let fragments = route.path.split('/')
	let sections = ['certificates', 'roles', 'slots', 'schedule']
	sections.forEach((section) => {
		if (fragments.includes(section)) {
			activeTab.value = convertToTitleCase(section)
		}
	})
	if (!activeTab.value) activeTab.value = 'About'
}

watchEffect(() => {
	if (activeTab.value) {
		let route = {
			About: { name: 'ProfileAbout' },
			Certificates: { name: 'ProfileCertificates' },
			Roles: { name: 'ProfileRoles' },
			Slots: { name: 'ProfileEvaluator' },
			Schedule: { name: 'ProfileEvaluationSchedule' },
		}[activeTab.value]
		router.push(route)
	}
})

watch(
	() => props.username,
	() => {
		profile.reload()
	},
)

const editProfile = () => {
	showProfileModal.value = true
}

const isSessionUser = () => {
	return $user.data?.name === profile.data?.name
}

const currentUserHasHigherAccess = () => {
	return $user.data?.is_evaluator || $user.data?.is_moderator
}

const isEvaluatorOrModerator = () => {
	return (
		profile.data?.roles?.includes('Batch Evaluator') ||
		profile.data?.roles?.includes('Moderator')
	)
}

const getTabButtons = () => {
	let buttons = [
		{ label: __('About'), value: 'About' },
		{ label: __('Certificates'), value: 'Certificates' },
	]
	if ($user.data?.is_moderator) {
		buttons.push({ label: __('Roles'), value: 'Roles' })
	}

	if (currentUserHasHigherAccess() && isEvaluatorOrModerator()) {
		buttons.push({ label: __('Slots'), value: 'Slots' })
		buttons.push({ label: __('Schedule'), value: 'Schedule' })
	}
	return buttons
}

const reloadUser = () => {
	call('frappe.sessions.clear')
		.then(() => {
			$user.reload().then(() => {
				profile.reload()
				toast.success(__('Session refreshed successfully'))
			})
		})
		.catch((err) => {
			toast.error(__('Failed to refresh session'))
			console.error(err)
		})
}

const navigateTo = (url) => {
	window.open(url, '_blank')
}

const breadcrumbs = computed(() => {
	let crumbs = [
		{
			label: __('People'),
		},
		{
			label: profile.data?.full_name,
			route: {
				name: 'Profile',
				params: {
					username: user.doc?.username,
				},
			},
		},
	]
	return crumbs
})

usePageMeta(() => {
	return {
		title: profile.data?.full_name,
		icon: brand.favicon,
	}
})
</script>

<style scoped>
.bhasha-profile-page {
	min-height: 100%;
	padding-bottom: 4rem;
	background:
		radial-gradient(
			circle at 88% 12%,
			rgba(108, 92, 231, 0.07),
			transparent 26rem
		),
		var(--bhasha-page);
}

.bhasha-profile-cover {
	overflow: hidden;
	background: #f7f2e8;
}

.bhasha-profile-cover::after {
	position: absolute;
	inset: 0;
	background: linear-gradient(180deg, transparent 45%, rgba(74, 47, 25, 0.13));
	content: '';
	pointer-events: none;
}

.bhasha-profile-cover__fallback {
	background:
		radial-gradient(
			circle at 20% 10%,
			rgba(255, 255, 255, 0.78),
			transparent 32%
		),
		radial-gradient(
			circle at 82% 72%,
			rgba(210, 189, 153, 0.2),
			transparent 34%
		),
		linear-gradient(135deg, #f7f2e8, #f3ecdf 58%, #f8f4eb) !important;
}

.bhasha-profile-shell {
	position: relative;
	z-index: 1;
}

.bhasha-profile-card,
.bhasha-profile-content {
	border: 1px solid rgba(108, 92, 231, 0.16);
	background: rgba(255, 255, 255, 0.96);
	box-shadow: 0 20px 48px -24px rgba(74, 47, 25, 0.28);
}

.bhasha-profile-card {
	min-height: 10.5rem;
	padding: 1.5rem;
	border-radius: 1.5rem;
}

.bhasha-profile-avatar {
	background: #f8f6ff;
	box-shadow: 0 8px 24px rgba(74, 56, 194, 0.13);
}

.bhasha-profile-edit {
	min-height: 2.75rem;
	padding-inline: 1rem !important;
	border: 1px solid rgba(108, 92, 231, 0.22) !important;
	border-radius: 9999px !important;
	background: #fff !important;
	color: #4a38c2 !important;
	font-weight: 700 !important;
}

.bhasha-profile-tabs {
	display: flex;
	justify-content: center;
}

.bhasha-profile-tabs :deep([role='tablist']) {
	padding: 0.3rem;
	border: 1px solid rgba(108, 92, 231, 0.16);
	border-radius: 9999px;
	background: #fff;
	box-shadow: 0 8px 22px rgba(74, 56, 194, 0.06);
}

.bhasha-profile-content {
	min-height: 15rem;
	padding: clamp(1.25rem, 4vw, 2.25rem);
	border-radius: 1.5rem;
}

@media (max-width: 767px) {
	.bhasha-profile-card {
		text-align: center;
	}

	.bhasha-profile-card > div:nth-child(2) {
		margin-inline-start: 0;
	}
}
</style>
