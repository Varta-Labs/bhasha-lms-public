<template>
	<div class="min-h-screen bg-[#f7f2e8] px-4 py-6 sm:px-8">
		<header class="mx-auto mb-10 flex max-w-5xl items-center justify-between">
			<router-link :to="{ name: 'Courses' }"
				><LMSLogo class="h-8 !max-h-none"
			/></router-link>
			<CartLink />
		</header>
		<main class="mx-auto max-w-5xl">
			<router-link :to="{ name: 'Courses' }" class="text-sm text-ink-gray-6">{{
				__('Continue browsing')
			}}</router-link>
			<h1 class="mb-2 mt-4 text-3xl font-bold text-ink-gray-9">
				{{ __('Your cart') }}
			</h1>
			<p class="mb-8 text-ink-gray-6">
				{{
					__(
						'Choose your courses and practice packs. Your savings are applied automatically.',
					)
				}}
			</p>
			<div v-if="summary.loading && !summary.data" role="status">
				{{ __('Loading your cart…') }}
			</div>
			<div v-else-if="error" class="rounded-2xl bg-white p-6" role="alert">
				<p>{{ error }}</p>
				<Button class="mt-4" @click="retryWithoutCoupon">{{
					__('Try again without coupon')
				}}</Button>
				<div
					v-for="course in cart.courses"
					:key="course"
					class="mt-4 flex justify-between gap-4"
				>
					<span>{{ course }}</span
					><Button @click="cart.remove(course)">{{ __('Remove') }}</Button>
				</div>
			</div>
			<div v-else-if="summary.data" class="grid gap-6 lg:grid-cols-[1fr_340px]">
				<div class="space-y-5">
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
						class="flex items-start justify-between gap-4 rounded-2xl bg-white p-6 shadow-sm"
					>
						<div class="min-w-0">
							<router-link
								:to="{
									name: 'CourseDetail',
									params: { courseName: item.course },
								}"
								class="font-semibold text-ink-gray-9"
								>{{ item.title }}</router-link
							>
							<p class="mt-2 text-sm text-ink-gray-6">
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
								class="mt-3"
								variant="ghost"
								@click="cart.remove(item.course)"
								>{{ __('Remove') }}</Button
							>
						</div>
						<div class="shrink-0 text-right">
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
						class="rounded-2xl bg-white p-6"
					>
						<p>{{ item.title }} — {{ __('Currently unavailable') }}</p>
						<Button class="mt-3" @click="cart.remove(item.course)">{{
							__('Remove')
						}}</Button>
					</div>
					<div
						v-if="
							!summary.data.items.length &&
							!summary.data.unavailable_courses.length
						"
						class="rounded-2xl bg-white p-8"
					>
						<h2 class="text-lg font-semibold">
							{{ __('Your cart is empty') }}
						</h2>
						<p class="mt-2 text-ink-gray-6">
							{{ __('Explore a language course to get started.') }}
						</p>
						<router-link :to="{ name: 'Courses' }"
							><Button class="mt-5" variant="solid">{{
								__('Browse courses')
							}}</Button></router-link
						>
					</div>
					<section
						v-if="summary.data.suggestions.length"
						class="rounded-2xl border border-purple-200 bg-purple-50 p-6"
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
							<p class="mt-2 text-sm text-ink-gray-6">
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
							<Button variant="solid" @click="cart.add(item.course)">{{
								__('Add practice pack')
							}}</Button>
						</div>
					</section>
				</div>
				<aside
					v-if="summary.data.items.length"
					class="h-fit rounded-2xl bg-white p-6 shadow-sm"
				>
					<h2 class="mb-5 text-lg font-semibold">{{ __('Order summary') }}</h2>
					<div class="space-y-4 text-sm">
						<div class="flex justify-between">
							<span>{{ __('Original amount') }}</span
							><strong>{{ summary.data.original_amount_formatted }}</strong>
						</div>
						<div
							v-if="summary.data.discount_amount"
							class="flex justify-between text-green-700"
						>
							<span>{{ summary.data.discount_label }}</span
							><strong>− {{ summary.data.discount_amount_formatted }}</strong>
						</div>
						<div v-if="summary.data.gst_applied" class="flex justify-between">
							<span>{{ __('GST') }}</span
							><strong>{{ summary.data.gst_amount_formatted }}</strong>
						</div>
						<div class="flex justify-between border-t pt-4 text-lg">
							<span>{{ __('Total') }}</span
							><strong>{{ summary.data.total_amount_formatted }}</strong>
						</div>
					</div>
					<p class="mt-3 text-xs text-ink-gray-5">
						{{ __('Final currency and taxes depend on your billing country.') }}
					</p>
					<div class="mt-6 flex items-end gap-2">
						<FormControl
							v-model="couponInput"
							:label="__('Coupon code')"
							class="min-w-0 flex-1"
						/><Button @click="cart.couponCode = couponInput.trim()">{{
							__('Apply')
						}}</Button>
					</div>
					<Button
						v-if="cart.couponCode"
						class="mt-2"
						variant="ghost"
						@click="removeCoupon"
						>{{ __('Remove coupon') }}</Button
					>
					<p class="mt-2 text-xs text-ink-gray-5">
						{{
							__('We apply the better discount: your coupon or bundle savings.')
						}}
					</p>
					<Button
						class="mt-6 w-full"
						variant="solid"
						:disabled="
							summary.loading || !!summary.data.unavailable_courses.length
						"
						@click="checkout"
						>{{ __('Continue to checkout') }}</Button
					>
					<p class="mt-3 text-xs text-ink-gray-5">
						{{ __('One payment unlocks all courses in this order.') }}
					</p>
				</aside>
			</div>
		</main>
	</div>
</template>
<script setup>
import { ref, watch } from 'vue'
import { Button, FormControl, createResource, usePageMeta } from 'frappe-ui'
import { useRouter } from 'vue-router'
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
