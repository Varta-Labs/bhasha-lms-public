<template>
	<div class="bhasha-metric-card">
		<div class="bhasha-metric-card__topline">
			<div class="bhasha-metric-card__icon" v-if="$slots.prefix">
				<slot name="prefix" />
			</div>
			<slot name="suffix" />
		</div>
		<div class="bhasha-metric-card__label">
			{{ __(title) }}
		</div>
		<div class="bhasha-metric-card__value">
			{{ value }}
		</div>
	</div>
</template>
<script setup lang="ts">
const props = defineProps<{
	title: string
	value: number | string
}>()
</script>

<style scoped>
.bhasha-metric-card {
	position: relative;
	overflow: hidden;
	min-width: 0;
	padding: 1.25rem;
	border: 1px solid rgba(108, 92, 231, 0.16);
	border-radius: 1.25rem;
	background: linear-gradient(145deg, #fff, #fbfaff);
	box-shadow: 0 10px 28px rgba(44, 31, 69, 0.055);
}

.bhasha-metric-card::after {
	position: absolute;
	top: -2.25rem;
	right: -2.25rem;
	width: 6rem;
	aspect-ratio: 1;
	border-radius: 50%;
	background: rgba(108, 92, 231, 0.06);
	content: '';
	pointer-events: none;
}

.bhasha-metric-card__topline {
	position: relative;
	z-index: 1;
	display: flex;
	min-height: 2.25rem;
	align-items: center;
	justify-content: space-between;
}

.bhasha-metric-card__icon {
	display: grid;
	width: 2.25rem;
	height: 2.25rem;
	place-items: center;
	border-radius: 0.7rem;
	background: rgba(108, 92, 231, 0.1);
	color: #6c5ce7;
}

.bhasha-metric-card__label {
	position: relative;
	z-index: 1;
	margin-top: 1rem;
	color: #7c7c7c;
	font-size: 0.75rem;
	font-weight: 700;
	letter-spacing: 0.03em;
}

.bhasha-metric-card__value {
	position: relative;
	z-index: 1;
	margin-top: 0.3rem;
	color: #171717;
	font-family: var(--bhasha-font-display);
	font-size: clamp(1.6rem, 3vw, 2rem);
	font-weight: 800;
	letter-spacing: -0.035em;
	line-height: 1.15;
}
</style>
