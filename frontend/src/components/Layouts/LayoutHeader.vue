<template>
	<SkeletonLoader v-if="isLoading" variant="header" />
	<header
		v-else
		:class="[
			'bhasha-product-header sticky top-0 z-10 flex items-center justify-between border-b bg-surface-white px-3 py-2.5 sm:px-5',
			variant === 'marketing' && 'course-marketing-header',
		]"
	>
		<div class="flex items-center gap-2">
			<slot name="left-header" />
		</div>
		<div class="flex items-center gap-2">
			<slot name="right-header" />
		</div>
	</header>
</template>

<script setup lang="ts">
import SkeletonLoader from '@/components/SkeletonLoader.vue'

withDefaults(defineProps<{ isLoading?: boolean; variant?: 'product' | 'marketing' }>(), {
	isLoading: false,
	variant: 'product',
})
</script>
