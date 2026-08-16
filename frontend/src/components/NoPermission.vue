<template>
	<AccessState
		:title="__('This page is not available')"
		:text="
			user.data
				? __(
						'Your account does not have access to this page. You can return to the course library and keep learning.',
					)
				: __(
						'Sign in to continue. If you already have an account, your learning progress will be waiting for you.',
					)
		"
		:eyebrow="user.data ? __('Access needed') : __('Welcome back')"
		:buttonLabel="user.data ? __('Explore courses') : __('Sign in')"
		:hint="__('Your account and progress are safe.')"
		@primary="handlePrimary"
	/>
</template>
<script setup>
import { inject } from 'vue'
import { usePageMeta } from 'frappe-ui'
import { sessionStore } from '../stores/session'
import { useRouter } from 'vue-router'
import AccessState from '@/components/AccessState.vue'

const user = inject('$user')
const { brand } = sessionStore()
const router = useRouter()

const redirectToLogin = () => {
	window.location.href = '/login'
}

const handlePrimary = () => {
	if (user.data) router.push({ name: 'Courses' })
	else redirectToLogin()
}

usePageMeta(() => {
	return {
		title: __('Not Permitted'),
		icon: brand.favicon,
	}
})
</script>
