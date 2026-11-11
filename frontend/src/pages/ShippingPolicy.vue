<template>
	<LegalPage :title="__('Shipping & Delivery Policy')" updated="11 November 2026">
		<template #intro>
			<p>
				Bhasha sells <strong>digital courses only</strong>. No physical goods
				are shipped.
			</p>
		</template>

		<section id="delivery">
			<h2>Delivery</h2>
			<p>Once your payment is successfully captured, the purchased courses are added to your account immediately. You can open them from <strong>My courses</strong> on the <router-link :to="{ name: 'Courses' }">Courses</router-link> page at learn.bhasha.io.</p>
		</section>

		<section id="delays">
			<h2>Delays</h2>
			<p>If a course does not appear within 30 minutes of a successful payment, refresh the page or sign out and back in. If it is still missing, email <a href="mailto:hello@bhasha.io">hello@bhasha.io</a> with your order ID and we will resolve it within 1 working day.</p>
		</section>

		<section id="requirements">
			<h2>Requirements</h2>
			<p>You need an internet connection and an up-to-date web browser to access courses.</p>
		</section>
	</LegalPage>
</template>

<script setup lang="ts">
import LegalPage from '@/components/LegalPage.vue'
</script>
