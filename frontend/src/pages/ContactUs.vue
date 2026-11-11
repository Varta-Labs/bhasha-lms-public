<template>
	<LegalPage :title="__('Contact Us')" updated="11 November 2026">
		<template #intro>
			<p>
				Bhasha is operated by Varta Labs Private Limited. Reach us using the
				details below.
			</p>
		</template>

		<section id="details">
			<h2>Varta Labs Private Limited</h2>
			<dl>
				<dt>Address</dt>
				<dd>
					<address>DNO-145/118, BLDG East End B Main, 9th Block Jayanagar, Bengaluru, Karnataka 560069, India</address>
				</dd>
				<dt>Email</dt>
				<dd><a href="mailto:hello@bhasha.io">hello@bhasha.io</a></dd>
				<dt>Phone</dt>
				<dd><a href="tel:+918884842224">+91 88848 42224</a></dd>
				<dt>Support hours</dt>
				<dd>Monday–Friday, 10:00–18:00 IST</dd>
			</dl>
		</section>
	</LegalPage>
</template>

<script setup lang="ts">
import LegalPage from '@/components/LegalPage.vue'
</script>
