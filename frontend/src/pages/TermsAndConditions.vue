<template>
	<LegalPage
		:title="__('Terms & Conditions')"
		updated="11 November 2026"
		:contents="contents"
	>
		<template #intro>
			<p>
				These Terms govern your use of learn.bhasha.io (“Bhasha”, “we”, “us” or
				“our”), operated by Varta Labs Private Limited, DNO-145/118, BLDG East
				End B Main, 9th Block Jayanagar, Bengaluru, Karnataka 560069, India. By
				creating an account or purchasing a course, you agree to these Terms.
			</p>
		</template>

		<section id="eligibility">
			<h2>1. Eligibility</h2>
			<p>Our courses are designed for adult learners. A person under 18 may use Bhasha only with the consent and supervision of a parent or legal guardian.</p>
		</section>

		<section id="account">
			<h2>2. Your account</h2>
			<p>You are responsible for keeping your login details confidential and for all activity under your account. Accounts are personal and may not be shared, transferred or resold.</p>
		</section>

		<section id="access">
			<h2>3. Courses and access</h2>
			<p>When you purchase a course or Addons Pack, you receive a personal, non-transferable licence to access its content for your own learning. Unless a course page states otherwise, access does not expire while Bhasha continues to offer the course. If we retire a course, we will give you at least 30 days’ notice to complete it.</p>
		</section>

		<section id="pricing">
			<h2>4. Prices and payment</h2>
			<p>Prices are shown before checkout in the currency for your billing country. GST is added where applicable, and coupons and bundle discounts are applied before tax. Payments are processed securely by <a href="https://razorpay.com/" target="_blank" rel="noopener noreferrer">Razorpay</a>. Your enrollment is confirmed only after the payment is successfully captured.</p>
		</section>

		<section id="use">
			<h2>5. Acceptable use</h2>
			<p>You may not copy, download (except where we allow it), record, redistribute, resell or publicly share course content, attempt to bypass access controls, or use the platform for any unlawful purpose. We may suspend accounts that breach these Terms.</p>
		</section>

		<section id="ip">
			<h2>6. Intellectual property</h2>
			<p>All course videos, text, audio, slides and materials are owned by Varta Labs Private Limited or its licensors.</p>
		</section>

		<section id="refunds">
			<h2>7. Refunds</h2>
			<p>Refunds are governed by our <router-link :to="{ name: 'RefundPolicy' }">Cancellation &amp; Refund Policy</router-link>.</p>
		</section>

		<section id="availability">
			<h2>8. Availability</h2>
			<p>We aim to keep the platform available but do not guarantee uninterrupted access. Some videos are delivered through third parties such as Vimeo or YouTube.</p>
		</section>

		<section id="liability">
			<h2>9. Limitation of liability</h2>
			<p>To the maximum extent permitted by law, our total liability for any claim is limited to the amount you paid for the course concerned.</p>
		</section>

		<section id="changes">
			<h2>10. Changes</h2>
			<p>We may update these Terms. Material changes will be posted here with a new “Last updated” date, and continued use of Bhasha means you accept the updated Terms.</p>
		</section>

		<section id="law">
			<h2>11. Governing law</h2>
			<p>These Terms are governed by the laws of India. The courts of Bengaluru, Karnataka have exclusive jurisdiction.</p>
		</section>

		<section id="contact">
			<h2>12. Contact</h2>
			<p>For questions about these Terms, email <a href="mailto:hello@bhasha.io">hello@bhasha.io</a> or see our <router-link :to="{ name: 'ContactUs' }">Contact Us</router-link> page.</p>
		</section>
	</LegalPage>
</template>

<script setup lang="ts">
import LegalPage from '@/components/LegalPage.vue'

const contents = [
	{ id: 'eligibility', label: '1. Eligibility' },
	{ id: 'account', label: '2. Your account' },
	{ id: 'access', label: '3. Courses and access' },
	{ id: 'pricing', label: '4. Prices and payment' },
	{ id: 'use', label: '5. Acceptable use' },
	{ id: 'ip', label: '6. Intellectual property' },
	{ id: 'refunds', label: '7. Refunds' },
	{ id: 'availability', label: '8. Availability' },
	{ id: 'liability', label: '9. Limitation of liability' },
	{ id: 'changes', label: '10. Changes' },
	{ id: 'law', label: '11. Governing law' },
	{ id: 'contact', label: '12. Contact' },
]
</script>
