<template>
	<router-link
		:to="{ name: 'Cart' }"
		class="inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-semibold text-ink-gray-9 hover:bg-surface-gray-2"
		:aria-label="`Cart (${cart.count})`"
	>
		<ShoppingCart class="size-4" />
		<span
			>{{ __('Cart') }}<span v-if="cart.count"> ({{ cart.count }})</span></span
		>
	</router-link>
</template>
<script setup lang="ts">
import { ShoppingCart } from 'lucide-vue-next'
import { useCart } from '@/stores/cart'
const cart = useCart()
</script>
