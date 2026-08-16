<template>
	<details :open="defaultOpen" class="bhasha-collapsible group">
		<summary class="flex items-center justify-between cursor-pointer p-5">
			<div
				class="flex items-center gap-2 text-base font-semibold text-ink-gray-9"
			>
				<ChevronDown
					class="size-4 stroke-1.5 -rotate-90 transition-transform duration-200 group-open:rotate-0"
				/>
				<span>{{ __(label) }}</span>
			</div>
			<div class="flex items-center gap-1" @click.stop>
				<slot name="actions" />
			</div>
		</summary>
		<div class="py-3.5 px-5">
			<slot />
		</div>
	</details>
</template>

<script setup>
import { ChevronDown } from 'lucide-vue-next'

defineProps({
	label: { type: String, default: '' },
	defaultOpen: { type: Boolean, default: true },
})
</script>

<style scoped>
summary {
	list-style: none;
}
summary::-webkit-details-marker {
	display: none;
}

.bhasha-collapsible {
	margin: 0.75rem;
	border: 1px solid #e8e3ed;
	border-radius: 1rem;
	background: rgba(255, 255, 255, 0.82);
	box-shadow: 0 5px 18px rgba(44, 31, 69, 0.035);
}

.bhasha-collapsible summary {
	padding: 1rem;
}

.bhasha-collapsible[open] summary {
	border-bottom: 1px solid #eeeaf1;
	background: rgba(108, 92, 231, 0.045);
}

.bhasha-collapsible > div:last-child {
	padding: 1rem;
}
</style>
