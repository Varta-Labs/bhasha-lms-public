<template>
	<div class="legal-page">
		<header class="legal-page__header">
			<div class="legal-page__shell legal-page__header-inner">
				<router-link :to="{ name: 'Courses' }" aria-label="Bhasha.io courses">
					<LMSLogo class="legal-page__logo" />
				</router-link>
				<router-link :to="{ name: 'Courses' }" class="legal-page__back">
					<ArrowLeft class="size-4" />
					{{ __('Back to Courses') }}
				</router-link>
			</div>
		</header>

		<main class="legal-page__shell legal-page__content">
			<div class="legal-page__intro">
				<span>{{ __('Bhasha Learning Management System') }}</span>
				<h1>{{ title }}</h1>
				<p class="legal-page__updated">
					{{ __('Last updated: {0}').format(updated) }}
				</p>
				<slot name="intro" />
			</div>

			<nav
				v-if="contents?.length"
				class="legal-page__contents"
				:aria-label="__('{0} contents').format(title)"
			>
				<strong>{{ __('On this page') }}</strong>
				<a v-for="item in contents" :key="item.id" :href="`#${item.id}`">{{
					item.label
				}}</a>
			</nav>

			<div class="legal-page__sections">
				<slot />
			</div>
		</main>

		<footer class="legal-page__footer">
			<div class="legal-page__shell legal-page__footer-inner">
				<span>{{ __('© Varta Labs Private Limited') }}</span>
				<LegalLinks />
			</div>
		</footer>
	</div>
</template>

<script setup lang="ts">
import { usePageMeta } from 'frappe-ui'
import { ArrowLeft } from 'lucide-vue-next'
import LMSLogo from '@/components/Icons/LMSLogo.vue'
import LegalLinks from '@/components/LegalLinks.vue'

const props = defineProps<{
	title: string
	updated: string
	contents?: { id: string; label: string }[]
}>()

usePageMeta(() => ({ title: props.title }))
</script>

<style>
.legal-page { min-height:100%; background:linear-gradient(180deg,#f8f6ff 0,#fff 20rem); color:#3f3f46; font-family:var(--bhasha-font-sans); }
.legal-page__shell { width:min(100%,960px); margin-inline:auto; padding-inline:clamp(1rem,4vw,2.5rem); }
.legal-page__header { position:sticky; z-index:10; top:0; border-bottom:1px solid rgba(108,92,231,.14); background:rgba(255,255,255,.92); backdrop-filter:blur(14px); }
.legal-page__header-inner { display:flex; min-height:4.5rem; align-items:center; justify-content:space-between; gap:1rem; }
.legal-page__logo { height:2rem; }
.legal-page__back { display:inline-flex; align-items:center; gap:.45rem; padding:.55rem .85rem; border-radius:9999px; color:#4a38c2; font-size:.875rem; font-weight:700; }
.legal-page__back:hover { background:rgba(108,92,231,.09); }
.legal-page__content { padding-block:clamp(3rem,7vw,5.5rem); }
.legal-page__intro { max-width:760px; }
.legal-page__intro > span { color:#6c5ce7; font-size:.75rem; font-weight:800; letter-spacing:.12em; text-transform:uppercase; }
.legal-page__intro h1 { margin-top:.7rem; color:#18181b; font-family:var(--bhasha-font-display); font-size:clamp(2.5rem,6vw,4.5rem); font-weight:800; line-height:1.05; letter-spacing:-.045em; overflow-wrap:break-word; }
.legal-page__updated { margin-top:1rem!important; color:#71717a; font-size:.875rem; font-weight:650; }
.legal-page__intro p:not(.legal-page__updated) { margin-top:1.5rem; color:#52525b; font-size:1.0625rem; line-height:1.75; }
.legal-page__contents { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:.45rem 1.5rem; margin-top:2.5rem; padding:1.5rem; border:1px solid rgba(108,92,231,.18); border-radius:1.25rem; background:rgba(255,255,255,.85); box-shadow:0 18px 45px -35px rgba(61,34,111,.45); }
.legal-page__contents strong { grid-column:1/-1; margin-bottom:.35rem; color:#18181b; font-family:var(--bhasha-font-display); }
.legal-page__contents a { color:#5b4acb; font-size:.875rem; line-height:1.5; }
.legal-page__contents a:hover,.legal-page__sections a { text-decoration:underline; text-underline-offset:3px; }
.legal-page__sections { margin-top:3.5rem; }
.legal-page__sections section { scroll-margin-top:6rem; padding-block:2rem; border-top:1px solid #e4e4e7; }
.legal-page__sections h2 { color:#18181b; font-family:var(--bhasha-font-display); font-size:clamp(1.35rem,2.5vw,1.7rem); font-weight:800; letter-spacing:-.02em; }
.legal-page__sections p,.legal-page__sections li { line-height:1.75; }
.legal-page__sections p { margin-top:1rem; }
.legal-page__sections address { margin-top:.75rem; line-height:1.75; font-style:normal; }
.legal-page__sections ul { display:grid; gap:.75rem; margin-top:1rem; padding-left:1.25rem; list-style:disc; }
.legal-page__sections dl { display:grid; grid-template-columns:max-content minmax(0,1fr); gap:.75rem 1.5rem; margin-top:1.25rem; line-height:1.75; }
.legal-page__sections dt { color:#27272a; font-weight:700; }
.legal-page__sections dd { margin:0; overflow-wrap:anywhere; }
.legal-page__sections strong { color:#27272a; }
.legal-page__sections a { color:#4a38c2; font-weight:700; }
.legal-page__footer { border-top:1px solid #e4e4e7; background:#fff; }
.legal-page__footer-inner { display:flex; min-height:5rem; align-items:center; justify-content:space-between; gap:1rem 1.5rem; color:#71717a; font-size:.8125rem; }
@media (max-width:639px) { .legal-page__contents { grid-template-columns:1fr; }.legal-page__contents strong { grid-column:auto; }.legal-page__back { padding-inline:.65rem; }.legal-page__sections section { padding-block:1.5rem; }.legal-page__sections dl { grid-template-columns:1fr; gap:.15rem; }.legal-page__sections dd { margin-bottom:.6rem; }.legal-page__footer-inner { align-items:flex-start; flex-direction:column; justify-content:center; padding-block:1.5rem; } }
</style>
