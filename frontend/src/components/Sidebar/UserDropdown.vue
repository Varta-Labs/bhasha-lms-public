<template>
	<div class="bhasha-sidebar-brand p-2">
		<Dropdown :options="userDropdownOptions">
			<template v-slot="{ open, close }">
				<button
					class="bhasha-sidebar-brand-button flex h-12 items-center py-2 duration-300 ease-in-out"
					:class="
						isCollapsed
							? 'px-0 w-auto'
							: open
							? 'is-open px-2 w-auto'
							: 'px-2 w-auto'
					"
				>
					<LMSLogo :compact="isCollapsed" class="h-7 sm:h-8 w-auto flex-shrink-0" />
				</button>
			</template>
		</Dropdown>
	</div>
	<SettingsModal
		v-if="userResource.data?.is_moderator"
		v-model="showSettingsModal"
	/>
</template>

<script setup>
import { sessionStore } from '@/stores/session'
import { call, Dropdown, toast } from 'frappe-ui'
import { useRouter } from 'vue-router'
import { usersStore } from '@/stores/user'
import { useSettings } from '@/stores/settings'
import { markRaw, watch, ref, computed } from 'vue'
import { createDialog } from '@/utils/dialogs'
import Configuration from '@/components/Sidebar/Configuration.vue'
import LMSLogo from '@/components/Icons/LMSLogo.vue'
import SettingsModal from '@/components/Settings/Settings.vue'
import {
	LogIn,
	LogOut,
	User,
	Settings,
	Trash2,
} from 'lucide-vue-next'

const router = useRouter()
const { logout } = sessionStore()
let { userResource } = usersStore()
const settingsStore = useSettings()
let { isLoggedIn } = sessionStore()
const showSettingsModal = ref(false)
const $dialog = createDialog

const props = defineProps({
	isCollapsed: {
		type: Boolean,
		default: false,
	},
})

watch(
	() => settingsStore.isSettingsOpen,
	(value) => {
		showSettingsModal.value = value
	}
)

const userDropdownOptions = computed(() => {
	return [
		{
			group: '',
			items: [
				{
					icon: User,
					label: 'My Profile',
					onClick: () => {
						router.push(`/user/${userResource.data?.username}`)
					},
					condition: () => {
						return isLoggedIn
					},
				},
				{
					icon: Settings,
					label: 'Settings',
					onClick: () => {
						settingsStore.isSettingsOpen = true
					},
					condition: () => {
						return userResource.data?.is_moderator
					},
				},
				{
					component: markRaw(Configuration),
					condition: () => {
						return userResource.data?.is_moderator
					},
				},
				{
					label: 'Clear Demo Data',
					icon: Trash2,
					onClick: () => {
						clearDemoDataConfirmation()
					},
					condition: () => {
						return (
							userResource.data?.is_moderator &&
							settingsStore.settings.data?.demo_data_present
						)
					},
				},
				{
					icon: LogOut,
					label: 'Log out',
					onClick: () => {
						logout.submit().then(() => {
							isLoggedIn = false
						})
					},
					condition: () => {
						return isLoggedIn
					},
				},
				{
					icon: LogIn,
					label: 'Log in',
					onClick: () => {
						window.location.href = '/login'
					},
					condition: () => {
						return !isLoggedIn
					},
				},
			],
		},
	]
})

const clearDemoDataConfirmation = () => {
	$dialog({
		title: __('Confirm clearing demo data?'),
		message: __(
			'Are you sure you want to clear the demo data? This would delete the demo course along with all its associated data. This action cannot be undone.'
		),
		actions: [
			{
				label: __('Confirm'),
				theme: 'red',
				variant: 'solid',
				onClick(close) {
					clearDemoData()
					close()
				},
			},
		],
	})
}

const clearDemoData = () => {
	call('lms.lms.api.clear_demo_data')
		.then(() => {
			window.location.href = '/lms'
			toast.success(__('Demo data cleared successfully'))
		})
		.catch((error) => {
			toast.error(__(error.message || 'Error clearing demo data'))
			console.error('Error clearing demo data:', error)
		})
}
</script>
