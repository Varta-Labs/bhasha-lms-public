<template>
	<main class="bhasha-access-state">
		<div class="bhasha-access-state__decoration" aria-hidden="true" />
		<section class="bhasha-access-state__card" role="status">
			<div class="bhasha-access-state__icon" aria-hidden="true">
				<component :is="icon" class="size-7 stroke-[1.7]" />
			</div>
			<p class="bhasha-access-state__eyebrow">{{ __(eyebrow) }}</p>
			<h1>{{ __(title) }}</h1>
			<p class="bhasha-access-state__copy">{{ __(text) }}</p>
			<div class="bhasha-access-state__actions">
				<div class="bhasha-access-state__primary">
					<Button variant="solid" @click="$emit('primary')">
						<template #prefix>
							<ArrowRight class="size-4 stroke-2" />
						</template>
						{{ __(buttonLabel) }}
					</Button>
				</div>
				<div v-if="secondaryLabel" class="bhasha-access-state__secondary">
					<Button variant="outline" @click="$emit('secondary')">
						{{ __(secondaryLabel) }}
					</Button>
				</div>
			</div>
			<p v-if="hint" class="bhasha-access-state__hint">
				<ShieldCheck class="size-4 shrink-0 stroke-[1.7]" />
				{{ __(hint) }}
			</p>
		</section>
	</main>
</template>

<script setup lang="ts">
import { Button } from 'frappe-ui'
import { ArrowRight, LockKeyhole, ShieldCheck } from 'lucide-vue-next'
import type { Component } from 'vue'

withDefaults(
	defineProps<{
		title?: string
		text?: string
		eyebrow?: string
		buttonLabel?: string
		secondaryLabel?: string
		hint?: string
		icon?: Component
	}>(),
	{
		title: 'This page is not available',
		text: 'You do not have access to this page right now.',
		eyebrow: 'Access needed',
		buttonLabel: 'Explore courses',
		secondaryLabel: '',
		hint: '',
		icon: () => LockKeyhole,
	},
)

defineEmits<{
	primary: []
	secondary: []
}>()
</script>

<style scoped>
.bhasha-access-state {
	position: relative;
	display: grid;
	min-height: 100%;
	place-items: center;
	overflow: hidden;
	padding: clamp(2rem, 7vw, 6rem) 1.25rem;
	background:
		radial-gradient(
			circle at 14% 8%,
			rgba(255, 255, 255, 0.85),
			transparent 30%
		),
		radial-gradient(
			circle at 84% 80%,
			rgba(210, 189, 153, 0.2),
			transparent 34%
		),
		linear-gradient(135deg, #f7f2e8, #f3ecdf 58%, #f8f4eb);
}

.bhasha-access-state__decoration {
	position: absolute;
	top: -11rem;
	right: -8rem;
	width: 30rem;
	aspect-ratio: 1;
	border: 1px solid rgba(113, 91, 61, 0.13);
	border-radius: 50%;
	box-shadow:
		0 0 0 4.5rem rgba(113, 91, 61, 0.045),
		0 0 0 9rem rgba(113, 91, 61, 0.03);
	pointer-events: none;
}

.bhasha-access-state__card {
	position: relative;
	z-index: 1;
	width: min(100%, 36rem);
	padding: clamp(2rem, 5vw, 3.25rem);
	border: 1px solid rgba(108, 92, 231, 0.2);
	border-radius: 2rem;
	background: rgba(255, 255, 255, 0.92);
	box-shadow: 0 24px 60px -20px rgba(74, 47, 25, 0.28);
	text-align: center;
	backdrop-filter: blur(16px);
}

.bhasha-access-state__icon {
	display: grid;
	width: 3.75rem;
	height: 3.75rem;
	margin: 0 auto 1.25rem;
	place-items: center;
	border: 1px solid rgba(108, 92, 231, 0.25);
	border-radius: 1rem;
	background: rgba(108, 92, 231, 0.1);
	color: #6c5ce7;
}

.bhasha-access-state__eyebrow {
	color: #4a38c2;
	font-size: 0.75rem;
	font-weight: 800;
	letter-spacing: 0.12em;
	text-transform: uppercase;
}

h1 {
	margin-top: 0.65rem;
	color: #171717;
	font-family: var(--bhasha-font-display);
	font-size: clamp(1.85rem, 5vw, 2.5rem);
	font-weight: 800;
	letter-spacing: -0.03em;
	line-height: 1.15;
}

.bhasha-access-state__copy {
	max-width: 29rem;
	margin: 1rem auto 0;
	color: #625d68;
	font-size: 1rem;
	line-height: 1.65;
}

.bhasha-access-state__actions {
	display: flex;
	justify-content: center;
	gap: 0.75rem;
	margin-top: 1.75rem;
}

.bhasha-access-state__primary :deep(button),
.bhasha-access-state__secondary :deep(button) {
	min-height: 3rem;
	padding-inline: 1.25rem !important;
	border-radius: 9999px !important;
	font-weight: 800 !important;
}

.bhasha-access-state__primary :deep(button) {
	border-color: transparent !important;
	background: linear-gradient(135deg, #6c5ce7, #4a38c2) !important;
	color: white !important;
	box-shadow: 0 14px 28px -8px rgba(108, 92, 231, 0.42);
}

.bhasha-access-state__secondary :deep(button) {
	border-color: rgba(108, 92, 231, 0.25) !important;
	background: white !important;
	color: #4a38c2 !important;
}

.bhasha-access-state__hint {
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
	.bhasha-access-state__card {
		border-radius: 1.5rem;
	}

	.bhasha-access-state__actions {
		flex-direction: column;
	}

	.bhasha-access-state__primary,
	.bhasha-access-state__secondary,
	.bhasha-access-state__primary :deep(button),
	.bhasha-access-state__secondary :deep(button) {
		width: 100%;
	}
}
</style>
