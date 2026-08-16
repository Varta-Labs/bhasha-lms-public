<template>
	<div class="billing-page">
		<div class="billing-page__rings" aria-hidden="true" />
		<header class="billing-header">
			<div aria-label="Bhasha" class="billing-logo">
				<LMSLogo class="h-8 !max-h-none" />
			</div>
			<div class="billing-secure-pill">
				<LockKeyhole class="size-3.5 stroke-2" />
				{{ __('Secure checkout') }}
			</div>
		</header>

		<main
			v-if="access.data?.access && orderSummary.data"
			class="billing-layout"
		>
			<section class="billing-form-card">
				<a :href="backLink" class="billing-back-link">
					<ChevronLeft class="size-4 stroke-2" />
					{{
						__('Back to {0}').format(
							type == 'course' ? __('course') : __('batch'),
						)
					}}
				</a>
				<div class="billing-heading">
					<div class="billing-step">{{ __('Step 1 of 2') }}</div>
					<h1>{{ __('Complete your details') }}</h1>
					<p>
						{{
							__(
								'We use this information for your receipt and payment confirmation.',
							)
						}}
					</p>
				</div>

				<div class="billing-fields">
					<FormControl
						:label="__('Full name')"
						v-model="billingDetails.billing_name"
						:placeholder="__('Name on your receipt')"
						required
					/>
					<FormControl
						:label="__('Phone number')"
						v-model="billingDetails.phone"
						:placeholder="__('Payment contact number')"
						required
					/>
					<FormControl
						:label="__('City')"
						v-model="billingDetails.city"
						:placeholder="__('Your city')"
						required
					/>
					<Link
						class="billing-country-control"
						doctype="Country"
						:value="billingDetails.country"
						@change="changeCurrency"
						:label="__('Country')"
						:placeholder="__('Select country')"
						required
					/>
				</div>

				<div class="billing-primary-action">
					<Button
						variant="solid"
						size="md"
						:loading="paymentLink.loading"
						@click="generatePaymentLink()"
					>
						<template #prefix>
							<LockKeyhole v-if="!isZeroAmount" class="size-4 stroke-2" />
							<Sparkles v-else class="size-4 stroke-2" />
						</template>
						{{
							isZeroAmount ? __('Enroll for Free') : __('Proceed to Payment')
						}}
					</Button>
				</div>
				<div class="billing-trust-row">
					<ShieldCheck class="size-4 shrink-0 stroke-[1.7]" />
					<span>{{
						__(
							'Your details are encrypted and only used to process this enrollment.',
						)
					}}</span>
				</div>
			</section>

			<aside class="billing-summary-card">
				<div class="billing-summary-card__header">
					<div class="billing-summary-icon">
						<ReceiptText class="size-5 stroke-[1.7]" />
					</div>
					<div>
						<div class="billing-summary-kicker">{{ __('Order summary') }}</div>
						<div class="billing-summary-title">
							{{ orderSummary.data.title }}
						</div>
					</div>
				</div>
				<div class="billing-summary-lines">
					<div
						v-if="
							orderSummary.data.gst_applied || orderSummary.data.discount_amount
						"
						class="billing-summary-line"
					>
						<span>{{ __('Original amount') }}</span>
						<strong>
							{{ orderSummary.data.original_amount_formatted }}
						</strong>
					</div>
					<div
						v-if="orderSummary.data.discount_amount"
						class="billing-summary-line is-discount"
					>
						<span>{{ __('Discount') }}</span>
						<strong>- {{ orderSummary.data.discount_amount_formatted }}</strong>
					</div>
					<div
						v-if="orderSummary.data.gst_applied"
						class="billing-summary-line"
					>
						<span>{{ __('GST') }}</span>
						<strong>
							{{ orderSummary.data.gst_amount_formatted }}
						</strong>
					</div>
					<div class="billing-summary-total">
						<span>{{ __('Total') }}</span>
						<strong>
							{{ orderSummary.data.total_amount_formatted }}
						</strong>
					</div>
				</div>
				<div class="billing-summary-note">
					<ShieldCheck class="size-4 shrink-0 stroke-[1.8]" />
					{{
						isZeroAmount
							? __('No payment is required for this enrollment.')
							: __('You will review the payment before it is confirmed.')
					}}
				</div>
			</aside>
		</main>
		<div v-else-if="access.data?.message" class="billing-state-wrap">
			<NotPermitted
				:text="access.data.message"
				title="Checkout is not available"
				eyebrow="Action unavailable"
				:buttonLabel="type == 'course' ? 'View course' : 'View batch'"
				:buttonLink="backLink"
			/>
		</div>
		<div v-else-if="!user.data?.name" class="billing-state-wrap">
			<NotPermitted
				text="Please login to access this page."
				title="Sign in to continue"
				eyebrow="Secure checkout"
				buttonLabel="Sign up"
				:buttonLink="signupUrl"
			/>
		</div>
		<div v-else class="billing-loading" role="status">
			<LoaderCircle class="size-6 animate-spin stroke-2" />
			<span>{{ __('Preparing your secure checkout…') }}</span>
		</div>
	</div>
</template>
<script setup>
import {
	Button,
	createResource,
	FormControl,
	usePageMeta,
	toast,
} from 'frappe-ui'
import { reactive, inject, onMounted, computed } from 'vue'
import { sessionStore } from '../stores/session'
import Link from '@/components/Controls/Link.vue'
import LMSLogo from '@/components/Icons/LMSLogo.vue'
import NotPermitted from '@/components/NotPermitted.vue'
import { useTelemetry } from 'frappe-ui/frappe'
import { getLmsRoute, getSignupUrl } from '@/utils/basePath'
import {
	ChevronLeft,
	LoaderCircle,
	LockKeyhole,
	ReceiptText,
	ShieldCheck,
	Sparkles,
} from 'lucide-vue-next'

const user = inject('$user')
const { brand } = sessionStore()
const { capture } = useTelemetry()

onMounted(() => {
	const script = document.createElement('script')
	script.src = `https://checkout.razorpay.com/v1/checkout.js`
	document.body.appendChild(script)
	if (user.data?.name) {
		access.submit()
	} else {
		window.location.replace(signupUrl.value)
	}
})

const props = defineProps({
	type: {
		type: String,
		required: true,
	},
	name: {
		type: String,
		required: true,
	},
})

const signupUrl = computed(() =>
	getSignupUrl(getLmsRoute(`billing/${props.type}/${props.name}`)),
)

const backLink = computed(() =>
	props.type == 'course'
		? getLmsRoute(`courses/${props.name}`)
		: getLmsRoute(`batches/${props.name}`),
)

const access = createResource({
	url: 'lms.lms.api.validate_billing_access',
	params: {
		billing_type: props.type,
		name: props.name,
	},
	onSuccess(data) {
		setBillingDetails(data.address)
		orderSummary.submit()
	},
})

const orderSummary = createResource({
	url: 'lms.lms.utils.get_order_summary',
	makeParams(values) {
		return {
			doctype: props.type == 'batch' ? 'LMS Batch' : 'LMS Course',
			docname: props.name,
			country: billingDetails.country,
		}
	},
	onError(err) {
		showError(err)
	},
})

const billingDetails = reactive({})

const setBillingDetails = (data) => {
	billingDetails.billing_name = data?.billing_name || user.data?.full_name || ''
	billingDetails.phone = data?.phone || ''
	billingDetails.city = data?.city || ''
	billingDetails.country = data?.country || ''
}

const paymentLink = createResource({
	url: 'lms.lms.payments.get_payment_link',
	makeParams(values) {
		let data = {
			doctype: props.type == 'batch' ? 'LMS Batch' : 'LMS Course',
			docname: props.name,
			address: billingDetails,
			payment_for_certificate: props.type == 'certificate',
			country: billingDetails.country,
		}
		return data
	},
})

const generatePaymentLink = () => {
	paymentLink.submit(
		{},
		{
			validate() {
				return validateBillingDetails()
			},
			onSuccess(data) {
				capture('checkout_initiated', { type: props.type })
				window.location.href = data
			},
			onError(err) {
				toast.error(err.messages?.[0] || err)
			},
		},
	)
}

const validateBillingDetails = () => {
	const fields = {
		billing_name: __('Full name'),
		phone: __('Phone number'),
		city: __('City'),
		country: __('Country'),
	}
	for (const [field, label] of Object.entries(fields)) {
		if (!billingDetails[field])
			return __('Please enter a valid {0}').format(label)
	}
}

const showError = (err) => {
	toast.error(err.messages?.[0] || err)
}

const changeCurrency = (country) => {
	billingDetails.country = country
	orderSummary.reload()
}

const isZeroAmount = computed(() => {
	return orderSummary.data && parseFloat(orderSummary.data.total_amount) <= 0
})

usePageMeta(() => {
	return {
		title: __('Billing Details'),
		icon: brand.favicon,
	}
})
</script>

<style scoped>
.billing-page {
	position: relative;
	min-height: 100vh;
	overflow: hidden;
	padding: 1.5rem clamp(1rem, 4vw, 2.5rem) 4rem;
	background:
		radial-gradient(
			circle at 16% 4%,
			rgba(255, 255, 255, 0.8),
			transparent 28%
		),
		radial-gradient(
			circle at 86% 74%,
			rgba(210, 189, 153, 0.2),
			transparent 34%
		),
		linear-gradient(135deg, #f7f2e8, #f3ecdf 58%, #f8f4eb);
}

.billing-page__rings {
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
	pointer-events: none;
}

.billing-header,
.billing-layout {
	position: relative;
	z-index: 1;
	width: min(100%, 70rem);
	margin-inline: auto;
}

.billing-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: clamp(2rem, 5vw, 4rem);
}

.billing-logo {
	display: inline-flex;
	padding: 0.35rem;
	border-radius: 0.75rem;
}

.billing-logo:focus-visible,
.billing-back-link:focus-visible {
	outline: 3px solid rgba(108, 92, 231, 0.25);
	outline-offset: 3px;
}

.billing-secure-pill {
	display: inline-flex;
	align-items: center;
	gap: 0.4rem;
	padding: 0.5rem 0.8rem;
	border: 1px solid rgba(108, 92, 231, 0.24);
	border-radius: 9999px;
	background: rgba(255, 255, 255, 0.76);
	color: #4a38c2;
	font-size: 0.75rem;
	font-weight: 800;
	backdrop-filter: blur(8px);
}

.billing-layout {
	display: grid;
	grid-template-columns: minmax(0, 1.3fr) minmax(19rem, 0.7fr);
	align-items: start;
	gap: clamp(1.25rem, 3vw, 2rem);
}

.billing-form-card,
.billing-summary-card {
	border: 1px solid rgba(108, 92, 231, 0.18);
	background: rgba(255, 255, 255, 0.94);
	backdrop-filter: blur(16px);
}

.billing-form-card {
	padding: clamp(1.5rem, 4vw, 3rem);
	border-radius: 2rem;
	box-shadow: 0 28px 64px -28px rgba(74, 47, 25, 0.3);
}

.billing-back-link {
	display: inline-flex;
	align-items: center;
	gap: 0.25rem;
	color: #625d68;
	font-size: 0.8125rem;
	font-weight: 700;
	transition: color 160ms ease;
}

.billing-back-link:hover {
	color: #4a38c2;
}

.billing-heading {
	margin-top: 2rem;
}

.billing-step,
.billing-summary-kicker {
	color: #4a38c2;
	font-size: 0.75rem;
	font-weight: 800;
	letter-spacing: 0.11em;
	text-transform: uppercase;
}

.billing-heading h1 {
	margin-top: 0.65rem;
	color: #171717;
	font-family: var(--bhasha-font-display);
	font-size: clamp(2rem, 5vw, 2.75rem);
	font-weight: 800;
	letter-spacing: -0.035em;
	line-height: 1.12;
}

.billing-heading p {
	max-width: 34rem;
	margin-top: 0.75rem;
	color: #625d68;
	font-size: 0.95rem;
	line-height: 1.6;
}

.billing-fields {
	display: grid;
	grid-template-columns: repeat(2, minmax(0, 1fr));
	gap: 1.25rem;
	margin-top: 2rem;
}

.billing-country-control :deep([data-slot='trigger']) {
	overflow: visible;
	border-color: #e4dfeb !important;
	border-radius: 0.75rem !important;
	background: #fff !important;
	box-shadow: none !important;
}

.billing-country-control :deep([data-slot='trigger']:focus-within),
.billing-country-control :deep([data-slot='trigger'][data-state='open']) {
	border-color: #8150df !important;
	box-shadow: 0 0 0 3px rgba(129, 80, 223, 0.14) !important;
}

.billing-country-control :deep([data-slot='input']),
.billing-country-control :deep([data-slot='input']:focus),
.billing-country-control :deep([data-slot='input']:focus-visible) {
	min-width: 0;
	min-height: 0 !important;
	padding: 0 !important;
	border: 0 !important;
	border-radius: 0 !important;
	background: transparent !important;
	box-shadow: none !important;
	outline: 0 !important;
	line-height: 1.5rem;
}

.billing-primary-action {
	margin-top: 2rem;
}

.billing-primary-action :deep(button) {
	width: 100%;
	min-height: 3.25rem;
	border-color: transparent !important;
	border-radius: 9999px !important;
	background: linear-gradient(135deg, #6c5ce7, #4a38c2) !important;
	color: white !important;
	font-weight: 800 !important;
	box-shadow: 0 14px 28px -8px rgba(108, 92, 231, 0.45);
	transition:
		transform 160ms ease,
		box-shadow 160ms ease;
}

.billing-primary-action :deep(button:hover) {
	transform: translateY(-1px);
	box-shadow: 0 18px 32px -8px rgba(108, 92, 231, 0.5);
}

.billing-trust-row,
.billing-summary-note {
	display: flex;
	align-items: flex-start;
	gap: 0.5rem;
	color: #7c7c7c;
	font-size: 0.75rem;
	font-weight: 600;
	line-height: 1.5;
}

.billing-trust-row {
	justify-content: center;
	margin-top: 1rem;
}

.billing-summary-card {
	position: sticky;
	top: 1.5rem;
	overflow: hidden;
	border-radius: 1.5rem;
	box-shadow: 0 18px 48px -28px rgba(74, 47, 25, 0.3);
}

.billing-summary-card__header {
	display: flex;
	align-items: flex-start;
	gap: 0.85rem;
	padding: 1.5rem;
	border-bottom: 1px solid #ede9f2;
	background: linear-gradient(
		135deg,
		rgba(108, 92, 231, 0.09),
		rgba(255, 255, 255, 0.5)
	);
}

.billing-summary-icon {
	display: grid;
	width: 2.75rem;
	height: 2.75rem;
	flex: none;
	place-items: center;
	border-radius: 0.8rem;
	background: white;
	color: #6c5ce7;
	box-shadow: 0 5px 14px rgba(74, 56, 194, 0.1);
}

.billing-summary-title {
	margin-top: 0.35rem;
	color: #171717;
	font-family: var(--bhasha-font-display);
	font-size: 1.05rem;
	font-weight: 700;
	line-height: 1.35;
}

.billing-summary-lines {
	padding: 1.5rem;
}

.billing-summary-line,
.billing-summary-total {
	display: flex;
	align-items: baseline;
	justify-content: space-between;
	gap: 1rem;
}

.billing-summary-line {
	padding-block: 0.55rem;
	color: #625d68;
	font-size: 0.875rem;
}

.billing-summary-line strong {
	color: #383838;
	font-weight: 700;
}

.billing-summary-line.is-discount strong {
	color: #059669;
}

.billing-summary-total {
	margin-top: 1rem;
	padding-top: 1.25rem;
	border-top: 1px solid #e2e2e2;
	color: #171717;
	font-weight: 800;
}

.billing-summary-total strong {
	font-family: var(--bhasha-font-display);
	font-size: 1.65rem;
	letter-spacing: -0.03em;
}

.billing-summary-note {
	margin: 0 1.5rem 1.5rem;
	padding: 0.85rem;
	border-radius: 0.8rem;
	background: #f8f6ff;
	color: #625d68;
}

.billing-state-wrap {
	position: relative;
	z-index: 1;
	width: min(100%, 70rem);
	min-height: 65vh;
	margin-inline: auto;
	border-radius: 2rem;
	overflow: hidden;
}

.billing-loading {
	position: relative;
	z-index: 1;
	display: flex;
	min-height: 55vh;
	align-items: center;
	justify-content: center;
	gap: 0.75rem;
	color: #4a38c2;
	font-weight: 700;
}

@media (max-width: 799px) {
	.billing-layout {
		grid-template-columns: minmax(0, 1fr);
	}

	.billing-summary-card {
		position: static;
		grid-row: 1;
	}
}

@media (max-width: 639px) {
	.billing-page {
		padding-inline: 0.85rem;
	}

	.billing-fields {
		grid-template-columns: minmax(0, 1fr);
	}

	.billing-form-card {
		border-radius: 1.5rem;
	}

	.billing-secure-pill {
		padding-inline: 0.65rem;
	}
}
</style>
