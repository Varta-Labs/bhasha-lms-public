<template>
	<LegalPage :title="__('Cancellation & Refund Policy')" updated="11 November 2026">
		<template #intro>
			<p>
				This policy explains when and how you can get a refund for courses and
				Addons Packs purchased on learn.bhasha.io from Varta Labs Private
				Limited.
			</p>
		</template>

		<section id="eligibility">
			<h2>Refund eligibility</h2>
			<p>You may request a full refund within <strong>7 days</strong> of purchase, provided you have completed less than <strong>20%</strong> of the course’s lessons. This applies per course or Addons Pack in an order. If you purchased a bundle, the refund applies to the whole bundle.</p>
		</section>

		<section id="not-eligible">
			<h2>Not eligible</h2>
			<ul>
				<li>Requests made more than 7 days after purchase, or after completing 20% or more of the course’s lessons.</li>
				<li>Courses purchased with a 100% coupon or received free of charge.</li>
				<li>Accounts suspended for breaching our <router-link :to="{ name: 'TermsAndConditions' }">Terms &amp; Conditions</router-link>.</li>
			</ul>
		</section>

		<section id="request">
			<h2>How to request a refund</h2>
			<p>Email <a href="mailto:hello@bhasha.io?subject=Refund%20request">hello@bhasha.io</a> from your account email with your order ID (or the payment ID from your Razorpay receipt) and the reason for your request. We will respond within 2 working days.</p>
		</section>

		<section id="processing">
			<h2>Processing</h2>
			<p>Approved refunds are issued to your original payment method within <strong>5–7 working days</strong>. Your bank may take additional time to reflect the credit. Access to refunded courses is removed.</p>
		</section>

		<section id="failed-payments">
			<h2>Failed or duplicate payments</h2>
			<p>If money was deducted but your enrollment was not confirmed, the amount is normally reversed automatically by your bank within 5–7 working days. If you were charged twice for the same order, email us and we will refund the duplicate payment in full.</p>
		</section>

		<section id="cancellation">
			<h2>Cancellation</h2>
			<p>Courses are one-time purchases, not subscriptions, so there is nothing to cancel after purchase. You may cancel a pending order at any time before completing payment.</p>
		</section>
	</LegalPage>
</template>

<script setup lang="ts">
import LegalPage from '@/components/LegalPage.vue'
</script>
