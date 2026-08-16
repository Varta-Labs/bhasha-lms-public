<template>
	<div v-if="course.data" class="product-course">
		<section ref="heroElement" class="product-course__hero">
			<div class="product-course__shell product-course__hero-grid">
				<div class="product-course__hero-copy">
					<span v-if="course.data.category" class="product-course__tag"><Tag class="size-4" />{{ course.data.category }}</span>
					<h1>{{ course.data.title }}</h1>
					<p>{{ course.data.short_introduction }}</p>
					<div v-if="primaryInstructor || ratingValue" class="product-course__author-row">
						<div v-if="primaryInstructor" class="product-course__author">
							<span>{{ instructorInitials }}</span>
							<div><small>{{ __('Instructor') }}</small><strong>{{ primaryInstructor.full_name || primaryInstructor.name }}</strong></div>
						</div>
						<div v-if="ratingValue" class="product-course__rating"><Star class="size-4 fill-current" />{{ ratingValue }}<span>· {{ ratingCount }} {{ __('ratings') }}</span></div>
					</div>
					<div class="product-course__outcomes">
						<strong>{{ __('By the end of this course, you will be able to:') }}</strong>
						<ul><li v-for="outcome in heroOutcomes" :key="outcome"><span><Check class="size-3.5" /></span>{{ outcome }}</li></ul>
					</div>
				</div>
				<aside id="product-enroll" class="product-course__enrollment"><CourseCardOverlay ref="enrollmentCard" :course="course" /></aside>
			</div>
		</section>

		<div class="product-course__shell product-course__layout">
			<main class="product-course__main">
				<section id="product-about" class="product-course__section">
					<span class="product-course__kicker">{{ __('About this course') }}</span>
					<h2>{{ aboutTitle }}</h2>
					<div v-if="course.data.description" class="product-course__prose" v-html="course.data.description" />
					<p v-else class="product-course__prose">{{ aboutLead }}</p>
					<h3>{{ __('Course objectives') }}</h3>
					<ol class="product-course__objectives"><li v-for="objective in productObjectives" :key="objective"><span>{{ objective }}</span></li></ol>
					<p class="product-course__prose">{{ lessonsFormatNote }}</p>
				</section>

				<section id="product-curriculum" class="product-course__section">
					<header class="product-course__curriculum-header">
						<div><span class="product-course__kicker">{{ __('Course outline') }}</span><h2>{{ __('Course content') }}</h2></div>
						<span v-if="courseStats">{{ courseStats }}</span>
					</header>
					<div class="product-course__curriculum-tools"><button type="button" @click="toggleAllChapters">{{ allChaptersOpen ? __('Collapse all chapters') : __('Expand all chapters') }}</button></div>
					<div class="product-course__chapter-list">
						<details v-for="chapter in outline.data || []" :key="chapter.name" class="product-course__chapter" :open="expandedChapterNames.includes(chapter.name)" @toggle="syncChapter($event, chapter.name)">
							<summary>
								<span class="product-course__chapter-chevron"><ChevronRight class="size-4.5" /></span>
								<span class="product-course__chapter-copy"><strong>{{ chapter.title }}</strong><small>{{ chapterDescription(chapter.idx) }}</small></span>
								<span class="product-course__chapter-count">{{ chapter.lessons?.length || 0 }} {{ (chapter.lessons?.length || 0) === 1 ? __('lesson') : __('lessons') }}</span>
							</summary>
							<ul>
								<li v-for="lesson in chapter.lessons || []" :key="lesson.name">
									<router-link :to="lessonRoute(lesson.number)"><PlayCircle class="size-4.5" /><span>{{ lesson.title }}</span><CheckCircle2 v-if="lesson.is_complete" class="product-course__lesson-status size-4" /></router-link>
								</li>
							</ul>
						</details>
						<p v-if="outline.loading" class="product-course__outline-state">{{ __('Loading course content…') }}</p>
						<p v-else-if="!outline.data?.length" class="product-course__outline-state">{{ __('Course content will appear here as lessons are published.') }}</p>
					</div>
				</section>
			</main>

			<aside class="product-course__nav-card">
				<h2>{{ __('Course overview') }}</h2>
				<p>{{ __('Jump to the information you need or continue learning.') }}</p>
				<nav :aria-label="__('Course overview')"><a href="#product-about">{{ __('About') }}<ChevronRight class="size-4" /></a><a href="#product-curriculum">{{ __('Curriculum') }}<ChevronRight class="size-4" /></a><a href="#product-reviews">{{ __('Reviews') }}<ChevronRight class="size-4" /></a></nav>
				<a v-if="primaryActionHref" :href="primaryActionHref" class="product-course__primary-action">{{ primaryActionLabel }}</a>
				<button v-else type="button" class="product-course__primary-action" @click="enrollStudent">{{ primaryActionLabel }}</button>
			</aside>
		</div>

		<section id="product-reviews" class="product-course__reviews">
			<div class="product-course__shell">
				<span class="product-course__kicker">{{ __('Learner feedback') }}</span>
				<h2>{{ __('Reviews') }}</h2>
				<p class="product-course__review-lead">{{ reviewLead }}</p>
				<div class="product-course__reviews-grid">
					<article class="product-course__rating-card">
						<strong>{{ ratingValue || '0.0' }}</strong>
						<div><Star v-for="star in 5" :key="star" class="size-5" :class="{ 'is-filled': star <= roundedRating }" /></div>
						<p>{{ __('Based on') }} {{ ratingCount }} {{ ratingCount === 1 ? __('rating') : __('ratings') }}</p>
					</article>
					<div class="product-course__rating-breakdown">
						<div v-for="star in [5,4,3,2,1]" :key="star" class="product-course__rating-row"><span>{{ star }} {{ __('stars') }}</span><div><span :style="{ width: ratingPercent(star) + '%' }" /></div><span>{{ ratingPercent(star) }}%</span></div>
					</div>
				</div>
				<CourseReviews :courseName="course.data.name" :avg_rating="course.data.rating" :membership="course.data.membership || null" />
			</div>
		</section>

		<footer class="product-course__footer"><div class="product-course__shell"><img :src="brandLogo" alt="bhasha.io" /><span>{{ __('Practical language learning for real conversations.') }}</span><a href="https://github.com/Varta-Labs/bhasha-lms-public" target="_blank" rel="noopener noreferrer">{{ __('Source code') }}</a></div></footer>
		<a v-if="showFloatingAction && primaryActionHref" :href="primaryActionHref" class="product-course__floating-action">{{ primaryActionLabel }}</a>
		<button v-else-if="showFloatingAction" type="button" class="product-course__floating-action" @click="enrollStudent">{{ primaryActionLabel }}</button>
	</div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { createResource } from 'frappe-ui'
import { Check, CheckCircle2, ChevronRight, PlayCircle, Star, Tag } from 'lucide-vue-next'
import CourseCardOverlay from '@/components/CourseCardOverlay.vue'
import CourseReviews from '@/components/CourseReviews.vue'
import { getLmsRoute } from '@/utils/basePath'
import type { CourseDetails, OutlineChapter, Resource } from '@/types/api'

const props = defineProps<{ course: Resource<CourseDetails | null> }>()
const heroElement = ref<HTMLElement | null>(null)
const enrollmentCard = ref<{ enrollStudent: () => void } | null>(null)
const showFloatingAction = ref(false)
const expandedChapterNames = ref<string[]>([])
let pageObserver: IntersectionObserver | null = null
let heroVisible = true

const outline = createResource({
	url: 'lms.lms.utils.get_course_outline',
	cache: ['product_course_outline', props.course.data?.name],
	makeParams() { return { course: props.course.data?.name, progress: true } },
	auto: true,
	onSuccess(data: OutlineChapter[]) { if (data?.length && !expandedChapterNames.value.length) expandedChapterNames.value = [data[0].name] },
}) as Resource<OutlineChapter[] | null>

watch(() => props.course.data?.name, () => outline.reload())

const primaryInstructor = computed(() => props.course.data?.instructors?.[0])
const numericRating = computed(() => { const value = Number.parseFloat(props.course.data?.rating || ''); return Number.isFinite(value) ? value : 0 })
const ratingValue = computed(() => numericRating.value > 0 ? numericRating.value.toFixed(1) : '')
const ratingCount = computed(() => props.course.data?.rating_count || 0)
const roundedRating = computed(() => Math.round(numericRating.value))
const instructorInitials = computed(() => { const name = primaryInstructor.value?.full_name || primaryInstructor.value?.name || ''; return name.split(/\s+/).filter(Boolean).map((part) => part[0]).join('').slice(0, 2).toUpperCase() })
const isKannadaCourse = computed(() => `${props.course.data?.name || ''} ${props.course.data?.title || ''}`.toLowerCase().includes('kannada'))
const heroOutcomes = computed<string[]>(() => {
	const configured = props.course.data?.learning_outcomes
	if (configured?.length) return configured.slice(0, 3)
	return isKannadaCourse.value
		? [__('Use simple Kannada confidently in everyday conversations.'), __('Recognise common sentence patterns and natural pronunciation.'), __('Ask questions and respond naturally in routine situations.')]
		: [__('Understand the essential concepts and how they fit together.'), __('Apply what you learn through guided, practical examples.'), __('Build a foundation you can use with confidence.')]
})
const aboutTitle = computed(() => isKannadaCourse.value ? __('Build practical speaking confidence for life in Karnataka.') : __('Build a practical foundation you can use.'))
const aboutLead = computed(() => isKannadaCourse.value ? __('This course is designed for adults who want to learn practical spoken Kannada and take part more confidently in everyday life across Karnataka.') : props.course.data?.short_introduction || '')
const productObjectives = computed(() => {
	const configured = props.course.data?.learning_outcomes
	if (configured?.length) return configured.slice(0, 5)
	return isKannadaCourse.value
		? [__('Understand the sounds and sentence patterns used in everyday Kannada.'), __('Introduce yourself and ask common questions with confidence.'), __('Handle routine conversations at work, while travelling, and while shopping.'), __('Improve listening, pronunciation, and natural speaking rhythm.'), __('Build simple Kannada sentences for real conversations.')]
		: [__('Understand the key concepts and principles in this course.'), __('Identify where and when to apply each core skill.'), __('Learn through guided examples and practical exercises.'), __('Build an effective practice routine of your own.'), __('Use your new foundation confidently in real situations.')]
})
const lessonsFormatNote = computed(() => isKannadaCourse.value ? __('Lessons combine clear explanations with guided audio and video practice wherever it adds value, making pronunciation and learning straightforward from the start.') : __('Lessons combine clear information and instructions with guided media wherever it adds value, making setup and learning straightforward from the start.'))
const courseStats = computed(() => {
	const chapters = outline.data?.length || props.course.data?.chapters?.length || 0
	const lessons = outline.data?.reduce((total, chapter) => total + (chapter.lessons?.length || 0), 0) || props.course.data?.lessons || 0
	const parts = []; if (chapters) parts.push(`${chapters} ${chapters === 1 ? __('chapter') : __('chapters')}`); if (lessons) parts.push(`${lessons} ${lessons === 1 ? __('lesson') : __('lessons')}`); return parts.join(' · ')
})
const allChaptersOpen = computed(() => Boolean(outline.data?.length) && expandedChapterNames.value.length === outline.data?.length)
const primaryActionLabel = computed(() => {
	if (props.course.data?.membership) return __('Continue Learning')
	const price = props.course.data?.paid_course
		? props.course.data.price || __('Paid course')
		: __('Free')
	return `${__('Enroll for')} ${price}`
})
const primaryActionHref = computed(() => {
	if (props.course.data?.membership) {
		return getLmsRoute(`courses/${props.course.data.name}/learn/${props.course.data.current_lesson || '1-1'}`)
	}
	return props.course.data?.paid_course
		? getLmsRoute(`billing/course/${props.course.data.name}`)
		: null
})
const brandLogo = `${import.meta.env.BASE_URL}bhasha-logo-text-transparent.png`
const reviewLead = computed(() => ratingCount.value ? `${__('This course currently has')} ${ratingCount.value} ${ratingCount.value === 1 ? __('rating') : __('ratings')}.` : __('Be the first learner to share feedback on this course.'))

function lessonRoute(number: string) { const [chapterNumber, lessonNumber] = number.split('-'); return { name: 'Lesson', params: { courseName: props.course.data?.name, chapterNumber, lessonNumber } } }
function chapterDescription(index: number) { return `${__('Chapter')} ${index} · ${__('Guided lessons and practice')}` }
function toggleAllChapters() { expandedChapterNames.value = allChaptersOpen.value ? [] : (outline.data || []).map((chapter) => chapter.name) }
function syncChapter(event: Event, name: string) { const open = (event.currentTarget as HTMLDetailsElement).open; const names = new Set(expandedChapterNames.value); open ? names.add(name) : names.delete(name); expandedChapterNames.value = [...names] }
function ratingPercent(star: number) { return ratingCount.value > 0 && star === roundedRating.value ? 100 : 0 }
function enrollStudent() { enrollmentCard.value?.enrollStudent() }

watch(heroElement, (hero) => {
	pageObserver?.disconnect()
	if (!hero || !('IntersectionObserver' in window)) return
	heroVisible = true
	showFloatingAction.value = false
	pageObserver = new IntersectionObserver((entries) => {
		for (const entry of entries) {
			if (entry.target === hero) heroVisible = entry.isIntersecting
		}
		showFloatingAction.value = !heroVisible
	}, { threshold: 0 })
	pageObserver.observe(hero)
}, { flush: 'post' })
onBeforeUnmount(() => pageObserver?.disconnect())
</script>

<style scoped>
.product-course { --product-brand:#6c5ce7; --product-brand-deep:#4a38c2; --product-brand-soft:rgba(108,92,231,.1); --product-border:rgba(108,92,231,.25); --product-ink:#171717; --product-body:#525252; --product-muted:#7c7c7c; --product-line:#e2e2e2; min-width:0; color:var(--product-body); background:#fff; font-family:var(--bhasha-font-sans); }
.product-course__shell { width:min(100%,1180px); margin-inline:auto; padding-inline:clamp(1rem,3vw,2.5rem); }
.product-course__hero { position:relative; overflow:hidden; padding-block:clamp(2.25rem,5vw,4.5rem); isolation:isolate; background:radial-gradient(circle at 18% 8%,rgba(255,255,255,.72),transparent 34%),radial-gradient(circle at 82% 76%,rgba(210,189,153,.18),transparent 36%),linear-gradient(135deg,#f7f2e8,#f3ecdf 58%,#f8f4eb); }
.product-course__hero::before { position:absolute; z-index:-1; top:-22rem; right:-15rem; width:44rem; height:44rem; border-radius:50%; opacity:.45; background:repeating-radial-gradient(circle,transparent 0 35px,rgba(113,91,61,.13) 36px 37px,transparent 38px 70px); content:''; }
.product-course__hero-grid { display:grid; align-items:start; gap:2.5rem; }
.product-course__hero-copy h1,.product-course h2,.product-course h3 { color:var(--product-ink); font-family:var(--bhasha-font-display); }
.product-course__tag { display:inline-flex; align-items:center; gap:.45rem; padding:.45rem .875rem; border:1px solid var(--product-border); border-radius:9999px; background:rgba(255,255,255,.68); color:var(--product-brand-deep); font-size:.75rem; font-weight:700; letter-spacing:.1em; text-transform:uppercase; }
.product-course__hero-copy h1 { max-width:48rem; margin-top:1.25rem; font-size:clamp(2.25rem,4.2vw,3.5rem); font-weight:800; line-height:1.08; letter-spacing:-.035em; text-wrap:balance; }
.product-course__hero-copy > p { max-width:42rem; margin-top:1.125rem; font-size:clamp(1.0625rem,1.5vw,1.1875rem); line-height:1.6; }
.product-course__author-row { display:flex; flex-wrap:wrap; align-items:center; gap:1rem; margin-top:1.5rem; }
.product-course__author { display:flex; align-items:center; gap:.75rem; }
.product-course__author > span { display:inline-flex; width:2.75rem; height:2.75rem; align-items:center; justify-content:center; border:1px solid var(--product-border); border-radius:50%; background:var(--product-brand-soft); color:var(--product-brand-deep); font-size:.8125rem; font-weight:800; }
.product-course__author div { display:grid; gap:.1rem; }.product-course__author small { color:var(--product-muted); font-size:.75rem; font-weight:600; }.product-course__author strong { color:var(--product-ink); font-size:.9375rem; }
.product-course__rating { display:inline-flex; align-items:center; gap:.4rem; padding-left:1.25rem; border-left:1px solid rgba(113,91,61,.2); color:#f59e0b; font-size:.875rem; font-weight:800; }.product-course__rating span { color:var(--product-body); }
.product-course__outcomes { max-width:40rem; margin-top:1.75rem; padding-top:1.375rem; border-top:1px solid rgba(113,91,61,.18); }.product-course__outcomes > strong { display:block; margin-bottom:.75rem; color:var(--product-ink); font-family:var(--bhasha-font-display); font-size:.9375rem; }.product-course__outcomes ul { display:grid; gap:.625rem; }.product-course__outcomes li { display:flex; align-items:center; gap:.7rem; color:#383838; font-size:.875rem; font-weight:600; line-height:1.45; }.product-course__outcomes li span { display:inline-flex; width:1.5rem; height:1.5rem; flex:0 0 auto; align-items:center; justify-content:center; border:1px solid var(--product-border); border-radius:.5rem; background:var(--product-brand-soft); color:var(--product-brand-deep); }
.product-course__enrollment { min-width:0; scroll-margin-top:8rem; }.product-course__enrollment :deep(.course-enrollment-card) { width:100%; border-color:var(--product-border); border-radius:1.5rem; box-shadow:0 24px 50px -12px rgba(108,92,231,.22),0 8px 24px -6px rgba(0,0,0,.08); }.product-course__enrollment :deep(.bhasha-primary) { min-height:3.25rem; border-radius:9999px; background:linear-gradient(135deg,var(--product-brand),var(--product-brand-deep)); font-weight:800; }
.product-course__layout { display:grid; gap:3rem; padding-block:clamp(3.5rem,7vw,6rem); }.product-course__main { min-width:0; }.product-course__section { scroll-margin-top:8rem; }.product-course__section + .product-course__section { margin-top:5rem; }.product-course__kicker { display:block; margin-bottom:.75rem; color:var(--product-brand); font-size:.75rem; font-weight:700; letter-spacing:.12em; text-transform:uppercase; }.product-course__section h2,.product-course__reviews h2 { font-size:clamp(1.75rem,2.5vw,2.5rem); font-weight:800; line-height:1.2; letter-spacing:-.025em; }.product-course__section h3 { margin-top:2.25rem; font-size:1.5rem; font-weight:800; }.product-course__prose { margin-top:1.25rem; font-size:1rem; line-height:1.7; }.product-course__prose :deep(p + p) { margin-top:1.25rem; }
.product-course__objectives { display:grid; gap:.875rem; margin:1.75rem 0; padding:0; list-style:none; counter-reset:objective; }.product-course__objectives li { display:grid; grid-template-columns:2.25rem minmax(0,1fr); align-items:start; gap:.875rem; counter-increment:objective; color:#383838; }.product-course__objectives li::before { display:inline-flex; width:2.25rem; height:2.25rem; align-items:center; justify-content:center; border-radius:.75rem; background:var(--product-brand-soft); color:var(--product-brand-deep); content:counter(objective); font-size:.75rem; font-weight:800; }.product-course__objectives span { padding-top:.35rem; line-height:1.55; }
.product-course__curriculum-header { display:flex; flex-wrap:wrap; align-items:flex-end; justify-content:space-between; gap:1.5rem; margin-bottom:1rem; padding-bottom:1.5rem; border-bottom:1px solid #ededed; }.product-course__curriculum-header > span { padding:.45rem .875rem; border:1px solid var(--product-border); border-radius:9999px; background:var(--product-brand-soft); color:var(--product-brand-deep); font-size:.8125rem; font-weight:700; }.product-course__curriculum-tools { display:flex; justify-content:flex-end; margin-bottom:.75rem; }.product-course__curriculum-tools button { min-height:2.75rem; padding:.5rem .75rem; border:0; border-radius:9999px; background:transparent; color:var(--product-brand-deep); font-weight:700; }.product-course__curriculum-tools button:hover { background:var(--product-brand-soft); }
.product-course__chapter-list { display:grid; gap:.625rem; }.product-course__chapter { overflow:hidden; border:1px solid var(--product-line); border-radius:1.25rem; background:#fff; transition:border-color .18s ease,box-shadow .18s ease; }.product-course__chapter[open] { border-color:var(--product-border); box-shadow:0 8px 24px -6px rgba(0,0,0,.08); }.product-course__chapter summary { display:grid; grid-template-columns:2.25rem minmax(0,1fr) auto; align-items:center; gap:.875rem; min-height:4.5rem; padding:.875rem 1.125rem; cursor:pointer; list-style:none; }.product-course__chapter summary::-webkit-details-marker { display:none; }.product-course__chapter summary:hover { background:#f8f6ff; }.product-course__chapter-chevron { display:inline-flex; width:2.25rem; height:2.25rem; align-items:center; justify-content:center; border-radius:.75rem; background:var(--product-brand-soft); color:var(--product-brand); transition:transform .18s ease; }.product-course__chapter[open] .product-course__chapter-chevron { transform:rotate(90deg); }.product-course__chapter-copy { min-width:0; }.product-course__chapter-copy strong { display:block; color:var(--product-ink); font-family:var(--bhasha-font-display); font-size:1.0625rem; line-height:1.3; }.product-course__chapter-copy small { display:block; overflow:hidden; margin-top:.2rem; color:var(--product-muted); font-size:.8125rem; text-overflow:ellipsis; white-space:nowrap; }.product-course__chapter-count { padding:.3rem .625rem; border-radius:9999px; background:#f3f3f3; color:var(--product-muted); font-size:.75rem; font-weight:650; white-space:nowrap; }.product-course__chapter[open] .product-course__chapter-count { background:var(--product-brand-soft); color:var(--product-brand-deep); }.product-course__chapter ul { margin:0; padding:0 1.125rem 1rem 4.25rem; list-style:none; }.product-course__chapter li { border-top:1px solid #ededed; }.product-course__chapter li a { display:flex; min-height:2.75rem; align-items:center; gap:.75rem; padding:.5rem .75rem; color:var(--product-body); font-size:.875rem; }.product-course__chapter li a:hover { color:var(--product-brand-deep); background:#f8f6ff; }.product-course__chapter li svg { flex:0 0 auto; color:var(--product-brand); }.product-course__lesson-status { margin-left:auto; color:#059669!important; }.product-course__outline-state { padding:2rem; border:1px solid var(--product-line); border-radius:1.25rem; text-align:center; }
.product-course__nav-card { align-self:start; padding:1.5rem; border:1px solid var(--product-border); border-radius:1.25rem; background:linear-gradient(145deg,#f8f6ff,#fff); }.product-course__nav-card h2 { font-size:1.125rem; font-weight:800; }.product-course__nav-card > p { margin-top:.5rem; font-size:.8125rem; line-height:1.55; }.product-course__nav-card nav { display:grid; gap:.25rem; margin:1.25rem 0 1.5rem; }.product-course__nav-card nav a { display:flex; min-height:2.75rem; align-items:center; justify-content:space-between; gap:.65rem; padding:.5rem .75rem; border-radius:.75rem; color:#383838; font-size:.875rem; font-weight:700; }.product-course__nav-card nav a:hover { background:var(--product-brand-soft); color:var(--product-brand-deep); }.product-course__nav-card nav svg { color:var(--product-brand); }
.product-course__primary-action,.product-course__floating-action { display:inline-flex; min-height:3.25rem; align-items:center; justify-content:center; padding:.875rem 1.5rem; border:0; border-radius:9999px; background:linear-gradient(135deg,var(--product-brand),var(--product-brand-deep)); color:#fff; cursor:pointer; font-size:.9375rem; font-weight:800; box-shadow:0 14px 28px -8px rgba(108,92,231,.4); }.product-course__primary-action { width:100%; }
.product-course__reviews { scroll-margin-top:8rem; padding-block:5rem; border-top:1px solid #ededed; background:#f9f8fd; }.product-course__review-lead { max-width:40rem; margin-top:.75rem; line-height:1.6; }.product-course__reviews-grid { display:grid; gap:2rem; margin-top:2.25rem; }.product-course__rating-card,.product-course__rating-breakdown { padding:2rem; border:1px solid var(--product-border); border-radius:1.5rem; background:#fff; }.product-course__rating-card > strong { color:var(--product-ink); font-family:var(--bhasha-font-display); font-size:3rem; line-height:1; }.product-course__rating-card > div { display:flex; gap:.25rem; margin:.875rem 0 .5rem; color:#d4d4d4; }.product-course__rating-card .is-filled { color:#f59e0b; fill:currentColor; }.product-course__rating-card p { color:var(--product-muted); font-size:.875rem; }.product-course__rating-breakdown { display:grid; align-content:center; }.product-course__rating-row { display:grid; grid-template-columns:3.25rem minmax(0,1fr) 2.6rem; align-items:center; gap:.75rem; min-height:2.25rem; font-size:.8125rem; font-weight:650; }.product-course__rating-row > div { overflow:hidden; height:.45rem; border-radius:9999px; background:#f3f3f3; }.product-course__rating-row > div span { display:block; height:100%; border-radius:inherit; background:linear-gradient(90deg,var(--product-brand),var(--product-brand-deep)); }.product-course__rating-row > span:last-child { color:var(--product-muted); text-align:right; }
.product-course__reviews :deep(> .mt-12) { margin-top:3rem; }.product-course__footer { border-top:1px solid var(--product-line); }.product-course__footer .product-course__shell { display:flex; min-height:6rem; align-items:center; justify-content:space-between; gap:1.5rem; color:var(--product-muted); font-size:.8125rem; }.product-course__footer img { width:8.5rem; height:auto; }.product-course__floating-action { position:fixed; right:1rem; bottom:calc(4.75rem + env(safe-area-inset-bottom)); left:1rem; z-index:50; }
@media (min-width:760px) { .product-course__reviews-grid { grid-template-columns:.8fr 1.2fr; } }
@media (min-width:960px) { .product-course__hero-grid { grid-template-columns:minmax(0,1fr) 360px; gap:4rem; }.product-course__layout { grid-template-columns:minmax(0,1fr) 260px; gap:4.5rem; }.product-course__nav-card { position:sticky; top:9rem; }.product-course__floating-action { right:1.5rem; bottom:calc(1.5rem + env(safe-area-inset-bottom)); left:auto; } }
@media (max-width:639px) { .product-course { padding-bottom:calc(11rem + env(safe-area-inset-bottom)); }.product-course__shell { padding-inline:1rem; }.product-course__rating { width:100%; padding-top:.75rem; padding-left:0; border-top:1px solid rgba(113,91,61,.2); border-left:0; }.product-course__chapter summary { grid-template-columns:2.25rem minmax(0,1fr); padding-inline:.75rem; }.product-course__chapter-count { grid-column:2; justify-self:start; }.product-course__chapter ul { padding-left:3.5rem; }.product-course__footer .product-course__shell { align-items:flex-start; flex-direction:column; justify-content:center; padding-block:1.5rem; } }
@media (prefers-reduced-motion:reduce) { .product-course *,.product-course *::before,.product-course *::after { scroll-behavior:auto!important; transition-duration:.01ms!important; } }
</style>
