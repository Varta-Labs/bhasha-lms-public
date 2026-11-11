<template>
	<nav class="legal-links" :class="{ 'legal-links--subtle': subtle }" :aria-label="__('Policies')">
		<router-link v-for="link in links" :key="link.name" :to="{ name: link.name }">{{
			__(link.label)
		}}</router-link>
	</nav>
</template>

<script setup lang="ts">
defineProps<{ subtle?: boolean }>()

const links = [
	{ name: 'TermsAndConditions', label: 'Terms & Conditions' },
	{ name: 'RefundPolicy', label: 'Refund Policy' },
	{ name: 'ShippingPolicy', label: 'Shipping & Delivery' },
	{ name: 'PrivacyPolicy', label: 'Privacy Policy' },
	{ name: 'ContactUs', label: 'Contact Us' },
]
</script>

<style scoped>
.legal-links { display:flex; flex-wrap:wrap; gap:.35rem 1rem; }
.legal-links a { color:#4a38c2; font-weight:700; }
.legal-links a:hover { text-decoration:underline; text-underline-offset:3px; }
.legal-links--subtle { gap:.15rem .75rem; font-size:.6875rem; line-height:1.4; }
.legal-links--subtle a { color:inherit; font-weight:500; }
</style>
