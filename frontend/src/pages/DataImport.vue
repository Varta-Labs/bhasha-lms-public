<template>
	<div
		class="bhasha-data-import-page"
		:class="{ 'is-batch-import': isBatchImport }"
	>
		<DataImport
			:doctype="route.params.doctype"
			:importName="route.params.importName"
			:doctypeMap="doctypeMap"
		/>
	</div>
</template>
<script setup lang="ts">
import { usePageMeta } from 'frappe-ui'
import { DataImport } from 'frappe-ui/frappe'
import { sessionStore } from '../stores/session'
import { useRoute, useRouter } from 'vue-router'
import { computed, inject, onMounted } from 'vue'

const { brand } = sessionStore()
const route = useRoute()
const router = useRouter()
const user = inject<any>('$user')
const isBatchImport = computed(() => route.params.doctype === 'LMS Batch')

onMounted(() => {
	const canImport = isBatchImport.value
		? user.data?.is_moderator ||
			user.data?.is_instructor ||
			user.data?.is_evaluator
		: user.data?.is_moderator

	if (!canImport) {
		router.push({
			name: isBatchImport.value ? 'Batches' : 'Courses',
		})
	}
})

const doctypeMap = {
	'LMS Course': {
		title: 'Courses',
		listRoute: '/courses',
		pageRoute: `/courses/docname`,
	},
	'LMS Batch': {
		title: 'Batches',
		listRoute: '/batches',
	},
	'LMS Category': {
		title: 'Categories',
		listRoute: '/lms',
	},
}

usePageMeta(() => {
	return {
		title: isBatchImport.value ? __('Import Batches') : __('Data Import'),
		icon: brand.favicon,
	}
})
</script>

<style scoped>
.bhasha-data-import-page {
	display: flex;
	min-height: 0;
	flex: 1;
	flex-direction: column;
	background:
		radial-gradient(
			circle at 12% 0%,
			rgba(129, 80, 223, 0.075),
			transparent 24rem
		),
		var(--bhasha-page);
	color: var(--bhasha-text);
}

.bhasha-data-import-page :deep(header) {
	border-color: var(--bhasha-border-brand);
	background: rgba(255, 255, 255, 0.94);
	backdrop-filter: blur(14px);
}

.bhasha-data-import-page :deep(header + div) {
	min-height: 0;
	flex: 1;
}

.bhasha-data-import-page
	:deep(
		header + div > [class~='w-[85%]'],
		header + div > [class~='w-[90%]']:not([class~='lg:hidden'])
	) {
	width: min(calc(100% - 2rem), 52rem);
	height: auto;
	margin-block: clamp(1.5rem, 4vw, 3rem);
	padding: clamp(1.25rem, 3vw, 2rem) !important;
	border: 1px solid var(--bhasha-border-brand);
	border-radius: var(--bhasha-radius-card);
	background: rgba(255, 255, 255, 0.94);
	box-shadow: 0 14px 36px rgba(61, 34, 111, 0.07);
}

.bhasha-data-import-page
	:deep(
		header + div > [class~='w-[85%]'] [class~='lg:w-[700px]'],
		header + div > [class~='w-[90%]'] [class~='lg:w-[700px]']
	) {
	max-width: 52rem;
}

.bhasha-data-import-page :deep([class~='text-xl'][class~='font-semibold']),
.bhasha-data-import-page :deep([class~='text-lg'][class~='font-semibold']) {
	color: var(--bhasha-text);
	font-family: var(--bhasha-font-display);
	font-weight: 750;
	letter-spacing: -0.015em;
}

.bhasha-data-import-page :deep([class~='leading-5'][class*='text-ink-gray']) {
	color: var(--bhasha-text-muted);
	line-height: 1.5;
}

.bhasha-data-import-page :deep([class~='h-[300px]']) {
	border-width: 1.5px;
	border-color: rgba(101, 50, 197, 0.28);
	border-radius: 1.25rem;
	background: linear-gradient(
		rgba(246, 242, 255, 0.7),
		rgba(255, 255, 255, 0.9)
	);
}

.bhasha-data-import-page :deep([class~='h-[300px]']:hover) {
	border-color: var(--bhasha-500);
	background: var(--bhasha-50);
}

.bhasha-data-import-page
	:deep([class~='h-[300px]'] .cursor-pointer.font-semibold) {
	color: var(--bhasha-700);
	text-decoration: underline;
	text-decoration-color: var(--bhasha-300);
	text-underline-offset: 0.18rem;
}

.bhasha-data-import-page :deep(button[class~='bg-surface-gray-7']) {
	border-color: transparent !important;
	border-radius: 9999px;
	background: linear-gradient(
		135deg,
		var(--bhasha-600),
		var(--bhasha-700)
	) !important;
	color: #fff !important;
	font-weight: 700;
	box-shadow: 0 8px 20px rgba(101, 50, 197, 0.2);
}

.bhasha-data-import-page :deep(button[class~='bg-surface-gray-7']:hover) {
	background: linear-gradient(
		135deg,
		var(--bhasha-500),
		var(--bhasha-700)
	) !important;
}

.bhasha-data-import-page :deep(header [class~='bg-surface-gray-7']) {
	border-color: transparent;
	background: var(--bhasha-600) !important;
	color: #fff;
}

.bhasha-data-import-page :deep([class~='bg-surface-gray-7']) {
	background-color: var(--bhasha-600) !important;
	color: #fff;
}

.bhasha-data-import-page :deep([class~='border'][class~='rounded-md']) {
	border-color: var(--bhasha-border-brand);
}

@media (max-width: 639px) {
	.bhasha-data-import-page
		:deep(
			header + div > [class~='w-[85%]'],
			header + div > [class~='w-[90%]']:not([class~='lg:hidden'])
		) {
		width: calc(100% - 1.25rem);
		margin-block: 0.75rem 1.5rem;
		border-radius: 1rem;
	}

	.bhasha-data-import-page :deep([class~='h-[300px]']) {
		min-height: 14rem;
		height: auto;
	}
}
</style>
