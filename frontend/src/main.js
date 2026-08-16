import './index.css'
import { createApp, watch } from 'vue'
import router from './router'
import App from './App.vue'
import { createPinia } from 'pinia'
import dayjs from '@/utils/dayjs'
import { createDialog } from '@/utils/dialogs'
import translationPlugin from './translation'
import { usersStore } from './stores/user'
import { initSocket } from './socket'
import { FrappeUI, setConfig, frappeRequest, pageMetaPlugin } from 'frappe-ui'
import { telemetryPlugin } from 'frappe-ui/frappe'
import { getLmsBasePath } from '@/utils/basePath'

let pinia = createPinia()
let app = createApp(App)
setConfig('resourceFetcher', frappeRequest)

app.use(FrappeUI)
app.use(pinia)
app.use(router)
app.use(translationPlugin)
app.use(pageMetaPlugin)
app.provide('$dayjs', dayjs)
app.provide('$socket', initSocket())
app.mount('#app')

const { userResource, allUsers } = usersStore()
app.provide('$user', userResource)
app.provide('$allUsers', allUsers)

watch(userResource, () => {
	if (userResource.data) {
		app.use(telemetryPlugin, { app_name: 'lms' })
	}
})

app.config.globalProperties.$user = userResource
app.config.globalProperties.$dialog = createDialog

async function registerServiceWorker() {
	if (!('serviceWorker' in navigator)) return

	const basePath = getLmsBasePath().replace(/^\/+|\/+$/g, '')
	const scope = `/${basePath}/`

	try {
		await navigator.serviceWorker.register(`${scope}sw.js`, {
			scope,
			updateViaCache: 'none',
		})

		// Remove the old asset-scoped registration, which could never control LMS pages.
		const legacyScope = new URL(
			'/assets/lms/frontend/',
			window.location.origin
		).href
		const registrations = await navigator.serviceWorker.getRegistrations()
		await Promise.all(
			registrations
				.filter((registration) => registration.scope === legacyScope)
				.map((registration) => registration.unregister())
		)
	} catch (error) {
		console.warn('Unable to register the Bhasha service worker:', error)
	}
}

if (document.readyState === 'complete') {
	registerServiceWorker()
} else {
	window.addEventListener('load', registerServiceWorker, { once: true })
}
