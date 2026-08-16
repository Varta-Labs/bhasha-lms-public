<template>
	<Dialog v-model="showDialog">
		<template #body-title>
			<h2 class="text-lg font-bold">{{ __('Install Bhasha') }}</h2>
		</template>
		<template #body-content>
			<p class="bhasha-install-prompt-copy">
				{{
					__(
						'Get the app on your device for easy access & a better experience!'
					)
				}}
			</p>
		</template>
		<template #actions>
			<Button
				variant="solid"
				class="bhasha-install-prompt-action w-full py-5"
				@click="install"
			>
				<template #prefix><FeatherIcon name="download" class="w-4" /></template>
				{{ __('Install') }}
			</Button>
		</template>
	</Dialog>

	<Popover :show="iosInstallMessage" placement="top-start">
		<template #body>
			<div
				class="fixed top-[20rem] translate-x-1/3 z-20 flex flex-col gap-3 rounded bg-surface-white py-5 drop-shadow-xl"
			>
				<div
					class="mb-1 flex flex-row items-center justify-between px-3 text-center"
				>
					<span class="text-base font-bold text-gray-900">
						{{ __('Install Bhasha') }}
					</span>
					<span class="inline-flex items-baseline">
						<FeatherIcon
							name="x"
							class="ms-auto h-4 w-4 text-gray-700"
							@click="iosInstallMessage = false"
						/>
					</span>
				</div>
				<div class="px-3 text-xs text-gray-800">
					<span class="flex flex-col gap-2">
						<span class="leading-5">
							{{
								__(
									'Get the app on your iPhone for easy access & a better experience'
								)
							}}
						</span>
						<span class="inline-flex items-start whitespace-nowrap">
							<span>{{ __('Tap') }}&nbsp;</span>
							<FeatherIcon name="share" class="h-4 w-4 text-blue-600" />
							<span>&nbsp;{{ __("and then 'Add to Home Screen'") }}</span>
						</span>
					</span>
				</div>
			</div>
		</template>
	</Popover>
</template>

<script setup>
import { onBeforeUnmount, ref, watch } from 'vue'
import { Button, Dialog, FeatherIcon, Popover } from 'frappe-ui'

const INSTALL_PROMPT_DISMISSED_KEY = 'learningInstallPromptDismissed'
const IOS_INSTALL_PROMPT_SHOWN_KEY = 'learningIosInstallPromptShown'
const deferredPrompt = ref(null)
const showDialog = ref(false)
const iosInstallMessage = ref(false)
const nativePromptIsOpen = ref(false)
const appWasInstalled = ref(false)

const hasDismissedInstallPrompt = () =>
	localStorage.getItem(INSTALL_PROMPT_DISMISSED_KEY) === 'true'

const rememberInstallPromptDismissal = () => {
	localStorage.setItem(INSTALL_PROMPT_DISMISSED_KEY, 'true')
}

const isIos = () => {
	const userAgent = window.navigator.userAgent.toLowerCase()
	return /iphone|ipad|ipod/.test(userAgent)
}

const isInStandaloneMode = () =>
	'standalone' in window.navigator && window.navigator.standalone

if (
	isIos() &&
	!isInStandaloneMode() &&
	!hasDismissedInstallPrompt() &&
	localStorage.getItem(IOS_INSTALL_PROMPT_SHOWN_KEY) !== 'true'
) {
	iosInstallMessage.value = true
	localStorage.setItem(IOS_INSTALL_PROMPT_SHOWN_KEY, 'true')
}

watch(showDialog, (isOpen, wasOpen) => {
	if (
		wasOpen &&
		!isOpen &&
		!nativePromptIsOpen.value &&
		!appWasInstalled.value
	) {
		rememberInstallPromptDismissal()
	}
})

watch(iosInstallMessage, (isOpen, wasOpen) => {
	if (wasOpen && !isOpen && !appWasInstalled.value) {
		rememberInstallPromptDismissal()
	}
})

const handleBeforeInstallPrompt = (e) => {
	e.preventDefault()
	if (hasDismissedInstallPrompt()) return

	deferredPrompt.value = e
	if (isIos() && !isInStandaloneMode()) iosInstallMessage.value = true
	else showDialog.value = true
}

const handleAppInstalled = () => {
	appWasInstalled.value = true
	showDialog.value = false
	iosInstallMessage.value = false
	deferredPrompt.value = null
}

window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
window.addEventListener('appinstalled', handleAppInstalled)

onBeforeUnmount(() => {
	window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
	window.removeEventListener('appinstalled', handleAppInstalled)
})

const install = async () => {
	if (!deferredPrompt.value) return

	nativePromptIsOpen.value = true

	try {
		deferredPrompt.value.prompt()
		showDialog.value = false
		const choice = await deferredPrompt.value.userChoice
		if (choice?.outcome === 'dismissed') rememberInstallPromptDismissal()
	} finally {
		deferredPrompt.value = null
		nativePromptIsOpen.value = false
	}
}
</script>

<style>
@media (max-width: 639px) {
	/* Keep the complete prompt inside the initially visible mobile viewport. */
	.dialog-overlay:has(.bhasha-install-prompt-copy) {
		overflow: hidden;
	}

	.dialog-overlay:has(.bhasha-install-prompt-copy) > div {
		height: 100dvh;
		min-height: 100dvh;
		padding-top: max(0.75rem, env(safe-area-inset-top));
		padding-bottom: max(0.75rem, env(safe-area-inset-bottom));
	}

	.dialog-content:has(.bhasha-install-prompt-copy) {
		display: flex;
		max-height: calc(
			100dvh - max(1.5rem, env(safe-area-inset-top)) -
			max(1.5rem, env(safe-area-inset-bottom))
		);
		flex-direction: column;
		margin-block: 0 !important;
		overflow: hidden;
		overscroll-behavior: contain;
	}

	.dialog-content:has(.bhasha-install-prompt-copy) > div:first-child {
		overflow-y: auto;
	}

	.dialog-content:has(.bhasha-install-prompt-copy)
		> div:last-child:not(:first-child) {
		flex: 0 0 auto;
		padding-bottom: calc(1rem + env(safe-area-inset-bottom)) !important;
	}
}
</style>
