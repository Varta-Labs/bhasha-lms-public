<template>
	<div class="cart-page">
		<div class="cart-page__rings" aria-hidden="true"></div>
		<header class="cart-header">
			<router-link :to="{ name: 'Courses' }" class="cart-logo"
				><LMSLogo class="h-8 !max-h-none"
			/></router-link>
			<CartLink class="cart-header-link" />
		</header>
		<main class="cart-main">
			<router-link :to="{ name: 'Courses' }" class="cart-back-link">
				<ChevronLeft class="size-4 stroke-2" aria-hidden="true" />
				{{ __('Continue browsing') }}
			</router-link>
			<h1 class="cart-title">
				{{ __('Your cart') }}
			</h1>
			<p class="cart-intro">
				{{
					__(
						'Choose your courses and practice packs. Your savings are applied automatically.',
					)
				}}
			</p>
			<div v-if="summary.loading && !summary.data" role="status">
				{{ __('Loading your cart…') }}
			</div>
			<div v-else-if="error" class="cart-card cart-message" role="alert">
				<p>{{ error }}</p>
				<Button class="cart-primary mt-4" @click="retryWithoutCoupon">{{
					__('Try again without coupon')
				}}</Button>
				<div
					v-for="course in cart.courses"
					:key="course"
					class="mt-4 flex justify-between gap-4"
				>
					<span>{{ course }}</span
					><Button
						class="cart-remove"
						variant="ghost"
						@click="cart.remove(course)"
						>{{ __('Remove') }}</Button
					>
				</div>
			</div>
			<div v-else-if="summary.data" class="cart-layout">
				<div class="cart-items">
					<p
						v-if="ownedNotice"
						class="rounded-xl bg-green-50 p-4 text-sm text-green-800"
						role="status"
					>
						{{ __('Courses you already own were removed from your cart.') }}
					</p>
					<div
						v-for="item in summary.data.items"
						:key="item.course"
						class="cart-card cart-item"
					>
						<router-link
							:to="{
								name: 'CourseDetail',
								params: { courseName: item.course },
							}"
							class="cart-thumbnail"
							:class="{ 'cart-thumbnail--placeholder': !item.image }"
							:aria-label="item.title"
						>
							<img v-if="item.image" :src="item.image" alt="" loading="lazy" />
							<BookOpen v-else class="size-8" aria-hidden="true" />
						</router-link>
						<div class="cart-item-content">
							<router-link
								:to="{
									name: 'CourseDetail',
									params: { courseName: item.course },
								}"
								class="cart-item-title"
								>{{ item.title }}</router-link
							>
							<p class="cart-item-intro">
								{{ item.short_introduction }}
							</p>
							<p
								v-if="item.discount_amount"
								class="mt-3 text-sm font-medium text-green-700"
							>
								{{ summary.data.discount_label }}:
								{{ item.discount_amount_formatted }}
							</p>
							<Button
								class="cart-remove mt-3"
								variant="ghost"
								@click="cart.remove(item.course)"
								>{{ __('Remove') }}</Button
							>
						</div>
						<div class="cart-item-price">
							<s
								v-if="item.discount_amount"
								class="block text-sm text-ink-gray-5"
								>{{ item.original_amount_formatted }}</s
							><strong>{{ item.amount_formatted }}</strong>
						</div>
					</div>
					<div
						v-for="item in summary.data.unavailable_courses"
						:key="item.course"
						class="cart-card cart-message"
					>
						<p>{{ item.title }} — {{ __('Currently unavailable') }}</p>
						<Button
							class="cart-remove mt-3"
							variant="ghost"
							@click="cart.remove(item.course)"
							>{{ __('Remove') }}</Button
						>
					</div>
					<div
						v-if="
							!summary.data.items.length &&
							!summary.data.unavailable_courses.length
						"
						class="cart-card cart-message"
					>
						<h2 class="text-lg font-semibold">
							{{ __('Your cart is empty') }}
						</h2>
						<p class="mt-2 text-ink-gray-6">
							{{ __('Explore a language course to get started.') }}
						</p>
						<router-link :to="{ name: 'Courses' }"
							><Button class="cart-primary mt-5" variant="solid">{{
								__('Browse courses')
							}}</Button></router-link
						>
					</div>
					<section
						v-if="summary.data.suggestions.length"
						class="cart-card cart-suggestions"
					>
						<h2 class="text-lg font-semibold text-ink-gray-9">
							{{ __('Complete your learning with a practice pack') }}
						</h2>
						<div
							v-for="item in summary.data.suggestions"
							:key="item.course"
							class="mt-4"
						>
							<router-link
								:to="{
									name: 'CourseDetail',
									params: { courseName: item.course },
								}"
								class="font-semibold"
								>{{ item.title }}</router-link
							>
							<p class="cart-item-intro">
								{{ item.short_introduction }}
							</p>
							<p class="my-3 text-sm">
								{{ item.amount_formatted
								}}<span
									v-if="item.discount_amount"
									class="ml-2 font-medium text-green-700"
									>{{ __('Save') }} {{ item.discount_amount_formatted }}</span
								>
							</p>
							<Button
								class="cart-primary"
								variant="solid"
								@click="cart.add(item.course)"
								>{{ __('Add practice pack') }}</Button
							>
						</div>
					</section>
				</div>
				<aside v-if="summary.data.items.length" class="cart-card cart-summary">
					<div class="cart-summary-header">
						<div class="cart-summary-icon">
							<ReceiptText class="size-5" aria-hidden="true" />
						</div>
						<h2>{{ __('Order summary') }}</h2>
					</div>
					<div class="cart-summary-body">
						<div class="cart-summary-lines">
							<div class="cart-summary-line">
								<span>{{ __('Amount') }}</span
								><strong>{{ summary.data.original_amount_formatted }}</strong>
							</div>
							<div
								v-if="summary.data.discount_amount"
								class="cart-summary-line is-discount"
							>
								<span>{{ summary.data.discount_label }}</span
								><strong>− {{ summary.data.discount_amount_formatted }}</strong>
							</div>
							<div v-if="summary.data.gst_applied" class="cart-summary-line">
								<span>{{ __('GST') }}</span
								><strong>{{ summary.data.gst_amount_formatted }}</strong>
							</div>
							<div class="cart-summary-total">
								<span>{{ __('Total') }}</span
								><strong>{{ summary.data.total_amount_formatted }}</strong>
							</div>
						</div>
						<p class="cart-summary-note">
							{{
								__('Final currency and taxes depend on your billing country.')
							}}
						</p>
						<div class="mt-6 flex items-end gap-2">
							<FormControl
								v-model="couponInput"
								:label="__('Coupon code')"
								class="min-w-0 flex-1"
							/><Button
								class="cart-secondary"
								@click="cart.couponCode = couponInput.trim()"
								>{{ __('Apply') }}</Button
							>
						</div>
						<Button
							v-if="cart.couponCode"
							class="cart-remove mt-2"
							variant="ghost"
							@click="removeCoupon"
							>{{ __('Remove coupon') }}</Button
						>
						<p class="mt-2 text-xs text-ink-gray-5">
							{{
								__(
									'We apply the better discount: your coupon or bundle savings.',
								)
							}}
						</p>
						<Button
							class="cart-primary cart-checkout"
							variant="solid"
							:disabled="
								summary.loading || !!summary.data.unavailable_courses.length
							"
							@click="checkout"
							>{{ __('Continue to checkout') }}</Button
						>
					</div>
				</aside>
			</div>
		</main>
	</div>
</template>
<script setup>
import { ref, watch } from 'vue'
import { Button, FormControl, createResource, usePageMeta } from 'frappe-ui'
import { useRouter } from 'vue-router'
import { BookOpen, ChevronLeft, ReceiptText } from 'lucide-vue-next'
import LMSLogo from '@/components/Icons/LMSLogo.vue'
import CartLink from '@/components/CartLink.vue'
import { useCart } from '@/stores/cart'
const cart = useCart()
const router = useRouter()
const error = ref('')
const ownedNotice = ref(false)
const couponInput = ref(cart.couponCode)
const summary = createResource({
	url: 'lms.lms.cart.get_cart_summary',
	makeParams: () => ({
		courses: cart.courses,
		coupon_code: cart.couponCode || null,
	}),
	onSuccess(data) {
		error.value = ''
		if (data.owned_courses.length) {
			ownedNotice.value = true
			data.owned_courses.forEach((item) => cart.remove(item.course))
		}
	},
	onError(err) {
		error.value = err.messages?.[0] || err.message || String(err)
	},
})
function retryWithoutCoupon() {
	cart.couponCode = ''
	refresh()
}
function removeCoupon() {
	cart.couponCode = ''
	couponInput.value = ''
}
function refresh() {
	summary.submit()
}
watch(() => [cart.courses.join('|'), cart.couponCode], refresh, {
	immediate: true,
})
function checkout() {
	router.push({ name: 'Billing', params: { type: 'cart', name: 'current' } })
}
usePageMeta({ title: __('Your cart') })
</script>

<style scoped>
.cart-page {
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
.cart-page__rings {
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
.cart-header,
.cart-main {
	position: relative;
	z-index: 1;
	width: min(100%, 70rem);
	margin-inline: auto;
}
.cart-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: clamp(2rem, 5vw, 4rem);
}
.cart-logo {
	display: inline-flex;
	padding: 0.35rem;
	border-radius: 0.75rem;
}
.cart-back-link {
	display: inline-flex;
	align-items: center;
	gap: 0.25rem;
	color: #625d68;
	font-size: 0.8125rem;
	font-weight: 700;
}
.cart-header :deep(.cart-header-link) {
	padding: 0.5rem 0.8rem;
	border: 1px solid rgba(108, 92, 231, 0.24);
	border-radius: 9999px;
	background: rgba(255, 255, 255, 0.76);
	color: #4a38c2;
	font-size: 0.75rem;
	font-weight: 800;
	backdrop-filter: blur(8px);
}
.cart-logo:focus-visible,
.cart-back-link:focus-visible,
.cart-thumbnail:focus-visible {
	outline: 3px solid rgba(108, 92, 231, 0.25);
	outline-offset: 3px;
}
.cart-back-link:hover,
.cart-item-title:hover {
	color: #4a38c2;
}
.cart-title {
	margin: 1rem 0 0.75rem;
	color: #171717;
	font-family: var(--bhasha-font-display);
	font-size: clamp(2rem, 5vw, 2.75rem);
	font-weight: 800;
	letter-spacing: -0.035em;
	line-height: 1.12;
}
.cart-intro {
	margin-bottom: 2rem;
	color: #625d68;
	font-size: 0.95rem;
	line-height: 1.6;
}
.cart-layout {
	display: grid;
	grid-template-columns: minmax(0, 1.3fr) minmax(19rem, 0.7fr);
	gap: clamp(1.25rem, 3vw, 2rem);
	align-items: start;
}
.cart-items {
	display: grid;
	gap: 1.25rem;
	min-width: 0;
}
.cart-card {
	border: 1px solid rgba(108, 92, 231, 0.18);
	border-radius: 1.5rem;
	background: rgba(255, 255, 255, 0.94);
	backdrop-filter: blur(16px);
	box-shadow: 0 18px 48px -28px rgba(74, 47, 25, 0.3);
}
.cart-item {
	display: grid;
	grid-template-columns: 10rem minmax(0, 1fr);
	gap: 1rem 1.25rem;
	padding: 1.5rem;
}
.cart-thumbnail {
	display: block;
	grid-row: span 2;
	align-self: start;
	overflow: hidden;
	border-radius: 0.8rem;
	color: #6c5ce7;
}
.cart-thumbnail--placeholder {
	display: grid;
	aspect-ratio: 16 / 9;
	place-items: center;
	background: #f0edff;
}
.cart-thumbnail img {
	display: block;
	width: 100%;
	height: auto;
}
.cart-item-content {
	min-width: 0;
}
.cart-item-title {
	color: #171717;
	font-family: var(--bhasha-font-display);
	font-size: 1rem;
	font-weight: 700;
	line-height: 1.45;
	overflow-wrap: anywhere;
}
.cart-item-intro {
	margin-top: 0.5rem;
	color: #625d68;
	font-size: 0.875rem;
	line-height: 1.6;
	overflow-wrap: anywhere;
}
.cart-item-price {
	grid-column: 2;
	display: flex;
	flex-wrap: wrap;
	align-items: baseline;
	gap: 0.5rem;
	color: #171717;
	font-size: 1rem;
}
.cart-item-price strong {
	white-space: nowrap;
}
.cart-message,
.cart-suggestions {
	padding: 1.5rem;
}
.cart-suggestions {
	background: linear-gradient(135deg, #f0edff, #fff);
}
.cart-summary {
	position: sticky;
	top: 1.5rem;
	overflow: hidden;
	min-width: 0;
}
.cart-summary-header {
	display: flex;
	align-items: center;
	gap: 0.85rem;
	padding: 1.5rem;
	border-bottom: 1px solid #ede9f2;
	background: linear-gradient(
		135deg,
		rgba(108, 92, 231, 0.09),
		rgba(255, 255, 255, 0.5)
	);
}
.cart-summary-header h2 {
	color: #171717;
	font-family: var(--bhasha-font-display);
	font-size: 1.05rem;
	font-weight: 700;
	line-height: 1.35;
}
.cart-summary-icon {
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
.cart-summary-body {
	padding: 1.5rem;
}
.cart-summary-line,
.cart-summary-total {
	display: flex;
	align-items: baseline;
	justify-content: space-between;
	gap: 1rem;
}
.cart-summary-line {
	padding-block: 0.55rem;
	color: #625d68;
	font-size: 0.875rem;
}
.cart-summary-line strong {
	color: #383838;
	font-weight: 700;
	white-space: nowrap;
}
.cart-summary-line.is-discount strong {
	color: #059669;
}
.cart-summary-total {
	margin-top: 1rem;
	padding-top: 1.25rem;
	border-top: 1px solid #e2e2e2;
	color: #171717;
	font-weight: 800;
}
.cart-summary-total strong {
	font-family: var(--bhasha-font-display);
	font-size: 1.65rem;
	letter-spacing: -0.03em;
	white-space: nowrap;
}
.cart-summary-note {
	margin-top: 1rem;
	padding: 0.85rem;
	border-radius: 0.8rem;
	background: #f8f6ff;
	color: #625d68;
	font-size: 0.75rem;
	line-height: 1.5;
}
.cart-page :deep(button.cart-primary) {
	min-height: 3.25rem;
	padding-inline: 1.5rem;
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
.cart-page :deep(button.cart-primary:hover:not(:disabled)) {
	transform: translateY(-1px);
	box-shadow: 0 18px 32px -8px rgba(108, 92, 231, 0.5);
}
.cart-page :deep(button.cart-primary:disabled) {
	opacity: 0.5;
	box-shadow: none;
}
.cart-page :deep(button.cart-secondary) {
	min-height: 2.5rem;
	padding-inline: 1rem;
	border: 1px solid rgba(108, 92, 231, 0.3);
	border-radius: 9999px;
	background: #f8f6ff;
	color: #4a38c2;
	font-weight: 700;
}
.cart-page :deep(button.cart-remove) {
	border-radius: 9999px;
	color: #625d68;
	font-weight: 700;
}
.cart-page :deep(button.cart-remove:hover) {
	background: #f0edff;
	color: #4a38c2;
}
.cart-page :deep(.cart-checkout) {
	width: 100%;
	margin-top: 1.5rem;
}
.cart-page :deep(input) {
	min-height: 2.5rem;
	border: 1px solid #d9d2ed;
	border-radius: 0.75rem;
	background: #fbfaff;
}
@media (max-width: 799px) {
	.cart-layout {
		grid-template-columns: minmax(0, 1fr);
	}
	.cart-summary {
		position: static;
	}
}
@media (max-width: 639px) {
	.cart-page {
		padding-inline: 0.85rem;
	}
	.cart-item {
		grid-template-columns: minmax(0, 1fr);
		padding: 1.25rem;
		gap: 1rem;
	}
	.cart-thumbnail {
		grid-row: auto;
		width: 100%;
	}
	.cart-item-price {
		grid-column: 1;
		padding-top: 1rem;
		border-top: 1px solid #ede9f2;
	}
	.cart-message,
	.cart-suggestions,
	.cart-summary-header,
	.cart-summary-body {
		padding: 1.25rem;
	}
}
</style>
