import { defineStore } from 'pinia'
import { createResource } from 'frappe-ui'
import { usersStore } from './user'
import { computed, reactive, ref } from 'vue'
import { getLmsRoute } from '@/utils/basePath'

export const sessionStore = defineStore('lms-session', () => {
	let { userResource } = usersStore()
	const brand = reactive({
		name: 'Bhasha',
		logo: '/assets/lms/frontend/bhasha-logo-text-transparent.png',
		favicon: '/assets/lms/frontend/favicon.png',
	})

	function sessionUser() {
		let cookies = new URLSearchParams(document.cookie.split('; ').join('&'))
		let _sessionUser = cookies.get('user_id')
		if (_sessionUser === 'Guest') {
			_sessionUser = null
		} else {
			userResource.reload()
		}
		return _sessionUser
	}

	let user = ref(sessionUser())
	const isLoggedIn = computed(() => !!user.value)

	const logout = createResource({
		url: 'logout',
		onSuccess() {
			userResource.reset()
			user.value = null
			window.location.assign(getLmsRoute('courses'))
		},
	})

	const branding = createResource({
		url: 'lms.lms.api.get_branding',
		cache: 'brand',
		auto: true,
		onSuccess(data) {
			brand.name = 'Bhasha'
			brand.logo = '/assets/lms/frontend/bhasha-logo-text-transparent.png'
			brand.favicon = '/assets/lms/frontend/favicon.png'
		},
	})

	return {
		user,
		isLoggedIn,
		logout,
		brand,
		branding,
	}
})
