<template>
	<img
		:src="compact ? squareUrl : logoUrl"
		alt="bhasha.io"
		:class="['object-contain max-h-8 w-auto transition-all duration-200', compact ? 'rounded-lg overflow-hidden shadow-2xs' : '']"
	/>
</template>

<script setup>
defineProps({
	compact: {
		type: Boolean,
		default: false,
	},
})
const logoUrl = `${import.meta.env.BASE_URL}bhasha-logo-text-transparent.png`
const squareUrl = `${import.meta.env.BASE_URL}bhasha-logo-v4-square.png`
</script>
