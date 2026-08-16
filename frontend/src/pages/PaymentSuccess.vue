<template>
	<div class="payment-success-page">
		<div class="payment-success-page__rings" aria-hidden="true" />
		<header class="payment-success-header">
			<LMSLogo class="h-8 !max-h-none" />
			<div class="payment-success-secure">
				<ShieldCheck class="size-3.5 stroke-2" />
				{{ __('Payment confirmed') }}
			</div>
		</header>

		<main class="payment-success-card">
			<div class="payment-success-icon" aria-hidden="true">
				<Check class="size-8 stroke-[2.2]" />
			</div>
			<div class="payment-success-eyebrow">{{ successEyebrow }}</div>
			<h1>{{ successTitle }}</h1>
			<p>{{ successMessage }}</p>

			<div class="payment-success-detail">
				<BookOpen v-if="type !== 'batch'" class="size-5 stroke-[1.7]" />
				<Users v-else class="size-5 stroke-[1.7]" />
				<div>
					<strong>{{ accessLabel }}</strong>
					<span>{{ __('Available now in your learning account') }}</span>
				</div>
			</div>

			<a :href="destination" class="payment-success-action">
				{{ actionLabel }}
				<ArrowRight class="size-4 stroke-2" />
			</a>
			<div class="payment-success-hint">
				<ReceiptText class="size-4 shrink-0 stroke-[1.7]" />
				{{
					__(
						'A payment receipt will be available with your transaction details.',
					)
				}}
			</div>
		</main>
	</div>
</template>

<script setup>
import { usePageMeta } from 'frappe-ui'
import {
	ArrowRight,
	BookOpen,
	Check,
	ReceiptText,
	ShieldCheck,
	Users,
} from 'lucide-vue-next'
import { computed } from 'vue'
import LMSLogo from '@/components/Icons/LMSLogo.vue'
import { sessionStore } from '@/stores/session'
import { getLmsRoute } from '@/utils/basePath'

const props = defineProps({
	type: { type: String, required: true },
	name: { type: String, required: true },
})

const { brand } = sessionStore()
const destination = computed(() =>
	props.type === 'course'
		? getLmsRoute(`courses/${props.name}`)
		: props.type === 'certificate'
			? getLmsRoute(`courses/${props.name}/certification`)
			: getLmsRoute(`batches/${props.name}`),
)
const accessLabel = computed(() =>
	props.type === 'batch'
		? __('Batch access')
		: props.type === 'certificate'
			? __('Certification access')
			: __('Course access'),
)
const actionLabel = computed(() =>
	props.type === 'batch'
		? __('View batch')
		: props.type === 'certificate'
			? __('Continue certification')
			: __('Start learning'),
)
const successEyebrow = computed(() =>
	props.type === 'certificate' ? __('Payment complete') : __('Enrollment complete'),
)
const successTitle = computed(() =>
	props.type === 'certificate' ? __('Certification unlocked') : __('You are all set'),
)
const successMessage = computed(() =>
	props.type === 'certificate'
		? __('Your payment was confirmed and certification access is ready.')
		: __('Your payment was confirmed and access has been added to your account.'),
)

usePageMeta(() => ({
	title: __('Payment successful'),
	icon: brand.favicon,
}))
</script>

<style scoped>
.payment-success-page {
	position: relative;
	display: flex;
	min-height: 100vh;
	overflow: hidden;
	flex-direction: column;
	padding: 1.5rem clamp(1rem, 4vw, 2.5rem) 4rem;
	background:
		radial-gradient(
			circle at 16% 4%,
			rgba(255, 255, 255, 0.82),
			transparent 28%
		),
		radial-gradient(
			circle at 86% 74%,
			rgba(210, 189, 153, 0.2),
			transparent 34%
		),
		linear-gradient(135deg, #f7f2e8, #f3ecdf 58%, #f8f4eb);
}

.payment-success-page__rings {
	position: absolute;
	top: -13rem;
	right: -10rem;
	width: 34rem;
	aspect-ratio: 1;
	border: 1px solid rgba(113, 91, 61, 0.12);
	border-radius: 50%;
	box-shadow:
		0 0 0 5rem rgba(113, 91, 61, 0.04),
		0 0 0 10rem rgba(113, 91, 61, 0.025);
}

.payment-success-header,
.payment-success-card {
	position: relative;
	z-index: 1;
	width: min(100%, 48rem);
	margin-inline: auto;
}

.payment-success-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: clamp(2rem, 6vw, 4.5rem);
}

.payment-success-secure {
	display: inline-flex;
	align-items: center;
	gap: 0.4rem;
	padding: 0.5rem 0.8rem;
	border: 1px solid rgba(5, 150, 105, 0.22);
	border-radius: 9999px;
	background: rgba(255, 255, 255, 0.78);
	color: #047857;
	font-size: 0.75rem;
	font-weight: 800;
}

.payment-success-card {
	padding: clamp(2rem, 6vw, 4rem);
	border: 1px solid rgba(108, 92, 231, 0.2);
	border-radius: 2rem;
	background: rgba(255, 255, 255, 0.94);
	box-shadow: 0 28px 64px -26px rgba(74, 47, 25, 0.32);
	text-align: center;
	backdrop-filter: blur(16px);
}

.payment-success-icon {
	display: grid;
	width: 4.25rem;
	height: 4.25rem;
	margin: 0 auto 1.25rem;
	place-items: center;
	border: 1px solid rgba(5, 150, 105, 0.24);
	border-radius: 1.25rem;
	background: rgba(16, 185, 129, 0.12);
	color: #059669;
	box-shadow: 0 12px 24px rgba(5, 150, 105, 0.12);
}

.payment-success-eyebrow {
	color: #4a38c2;
	font-size: 0.75rem;
	font-weight: 800;
	letter-spacing: 0.12em;
	text-transform: uppercase;
}

.payment-success-card h1 {
	margin-top: 0.65rem;
	color: #171717;
	font-family: var(--bhasha-font-display);
	font-size: clamp(2rem, 6vw, 3rem);
	font-weight: 800;
	letter-spacing: -0.04em;
	line-height: 1.1;
}

.payment-success-card > p {
	max-width: 34rem;
	margin: 1rem auto 0;
	color: #625d68;
	font-size: 1rem;
	line-height: 1.65;
}

.payment-success-detail {
	display: flex;
	max-width: 27rem;
	align-items: center;
	gap: 0.85rem;
	margin: 1.75rem auto 0;
	padding: 1rem;
	border: 1px solid rgba(108, 92, 231, 0.15);
	border-radius: 1rem;
	background: #f8f6ff;
	color: #6c5ce7;
	text-align: left;
}

.payment-success-detail div {
	display: flex;
	flex-direction: column;
}

.payment-success-detail strong {
	color: #383838;
	font-size: 0.875rem;
}

.payment-success-detail span {
	margin-top: 0.15rem;
	color: #7c7c7c;
	font-size: 0.75rem;
}

.payment-success-action {
	display: inline-flex;
	min-height: 3.25rem;
	align-items: center;
	justify-content: center;
	gap: 0.5rem;
	margin-top: 1.75rem;
	padding: 0.9rem 1.5rem;
	border-radius: 9999px;
	background: linear-gradient(135deg, #6c5ce7, #4a38c2);
	color: #fff;
	font-weight: 800;
	box-shadow: 0 14px 28px -8px rgba(108, 92, 231, 0.45);
	transition:
		transform 160ms ease,
		box-shadow 160ms ease;
}

.payment-success-action:hover {
	transform: translateY(-1px);
	color: #fff;
	text-decoration: none;
	box-shadow: 0 18px 32px -8px rgba(108, 92, 231, 0.5);
}

.payment-success-hint {
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 0.45rem;
	margin-top: 1.5rem;
	color: #7c7c7c;
	font-size: 0.75rem;
	font-weight: 600;
}

@media (max-width: 639px) {
	.payment-success-card {
		border-radius: 1.5rem;
	}

	.payment-success-action {
		width: 100%;
	}
}
</style>
