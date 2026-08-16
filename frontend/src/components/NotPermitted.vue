<template>
	<AccessState
		:title="title"
		:text="text"
		:buttonLabel="buttonLabel"
		:eyebrow="eyebrow"
		:hint="hint"
		@primary="redirect"
	/>
</template>
<script setup>
import AccessState from '@/components/AccessState.vue'

const props = defineProps({
	title: {
		type: String,
		default: 'Not Permitted',
	},
	text: {
		type: String,
		default: 'You are not permitted to access this page.',
	},
	buttonLabel: {
		type: String,
		default: 'Login',
	},
	buttonLink: {
		type: String,
		default: '/login',
	},
	eyebrow: {
		type: String,
		default: 'Action unavailable',
	},
	hint: {
		type: String,
		default: 'Your account and progress are safe.',
	},
})

const redirect = () => {
	window.location.href = props.buttonLink
}
</script>
