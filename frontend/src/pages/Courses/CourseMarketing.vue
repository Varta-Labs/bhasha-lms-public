<template>
	<div v-if="course.data" class="guest-course">
		<section ref="heroElement" class="guest-course__hero">
			<div class="guest-course__shell guest-course__hero-grid">
				<div class="guest-course__hero-copy">
					<h1>{{ marketingTitle }}</h1>
					<p>{{ marketingIntroduction }}</p>
					<div class="guest-course__offer">
						<div class="guest-course__price-row">
							<span v-if="hasEarlyBirdOffer" class="guest-course__offer-label">{{ __('Early bird offer') }}</span>
							<strong>{{ priceLabel }}</strong>
							<s v-if="hasEarlyBirdOffer">₹2,999</s>
							<span>{{ __('Lifetime access') }}</span>
						</div>
						<a :href="signupUrl" class="guest-course__primary-action">
							{{ enrollLabel }}
						</a>
					</div>
				</div>

				<figure class="guest-course__media">
					<iframe
						v-if="landingVideoUrl"
						:src="landingVideoUrl"
						:title="__('Course introduction video')"
						allow="autoplay; fullscreen; picture-in-picture"
						allowfullscreen
					/>
					<img v-else :src="previewImage" :alt="course.data.title" />
					<a v-if="!landingVideoUrl" href="#course-curriculum" :aria-label="__('Preview the course curriculum')">
						<Play class="size-5 fill-current" />
					</a>
				</figure>
			</div>
		</section>

		<section class="guest-course__section guest-course__outcomes">
			<div class="guest-course__shell">
				<header class="guest-course__section-header">
					<span>{{ __('What speaking changes') }}</span>
					<h2>{{ outcomesTitle }}</h2>
					<p>{{ outcomesLead }}</p>
				</header>
				<div class="guest-course__outcome-grid">
					<article v-for="(outcome, index) in outcomes" :key="outcome">
						<div class="guest-course__icon-well">
							<component :is="outcomeIcons[index % outcomeIcons.length]" class="size-5" />
						</div>
						<p>{{ outcome }}</p>
					</article>
				</div>
			</div>
		</section>

		<section class="guest-course__section guest-course__story">
			<div class="guest-course__shell guest-course__story-grid">
				<figure class="guest-course__story-art">
					<img :src="communityImage" :alt="communityImageAlt" />
				</figure>
				<div>
					<span class="guest-course__kicker">{{ storyKicker }}</span>
					<h2>{{ storyTitle }}</h2>
					<p class="guest-course__story-lead">{{ storyLead }}</p>
					<ul class="guest-course__story-points">
						<li v-for="(point, index) in storyPoints" :key="point.title">
							<span>{{ String(index + 1).padStart(2, '0') }}</span>
							<div><strong>{{ point.title }}</strong><p>{{ point.copy }}</p></div>
						</li>
					</ul>
				</div>
			</div>
		</section>

		<section class="guest-course__section guest-course__method">
			<div class="guest-course__shell guest-course__story-grid guest-course__story-grid--reverse">
				<div>
					<span class="guest-course__kicker">{{ __('How you learn') }}</span>
					<h2>{{ __('Learn with a trainer—and a learner just like you.') }}</h2>
					<p class="guest-course__story-lead">{{ __('This is more than a regular recorded lesson. You watch a trainer actively teach an adult beginner, then practise alongside them as the conversation develops.') }}</p>
					<ol class="guest-course__method-steps">
						<li v-for="(step, index) in methodSteps" :key="step.title">
							<span>{{ index + 1 }}</span>
							<div><strong>{{ step.title }}</strong><p>{{ step.copy }}</p></div>
						</li>
					</ol>
					<p class="guest-course__quiet-callout">{{ __('Self-paced · Practical · Designed for adult beginners') }}</p>
				</div>
				<figure class="guest-course__story-art">
					<img :src="guidedLearningImage" :alt="guidedLearningImageAlt" />
				</figure>
			</div>
		</section>

		<section id="course-curriculum" class="guest-course__section guest-course__curriculum">
			<div class="guest-course__shell guest-course__curriculum-shell">
				<header class="guest-course__curriculum-header">
					<div>
						<span class="guest-course__kicker">{{ __('What you will learn') }}</span>
						<h2>{{ isKannadaCourse ? __('Practical Kannada for the conversations you actually have.') : __('Practical lessons for the situations that matter.') }}</h2>
						<p>{{ isKannadaCourse ? __('The same beginner curriculum used with Bhasha.io’s personal and group coaching learners.') : __('A structured path built from the live course curriculum.') }}</p>
					</div>
					<div v-if="referenceStats" class="guest-course__curriculum-badge">
						<BookOpen class="size-4" />
						{{ referenceStats }}
					</div>
				</header>
				<div class="guest-course__curriculum-panel">
					<div v-if="isKannadaCourse" class="guest-course__module-list">
						<details v-for="(module, index) in marketingModules" :key="module.title" :open="index === 0">
							<summary>
								<ChevronRight class="guest-course__module-chevron size-5" />
								<span><strong>{{ index + 1 }}. {{ module.title }}</strong><small>{{ module.lessons.length }} {{ __('lessons') }}</small></span>
							</summary>
							<ul>
								<li v-for="lesson in module.lessons" :key="lesson"><MonitorPlay class="size-4" />{{ lesson }}</li>
							</ul>
						</details>
					</div>
					<CourseOutline
						v-else
						:courseName="course.data.name"
						:showOutline="true"
						:allowEdit="false"
						:disableNavigation="true"
						:hideHeader="true"
					/>
				</div>
			</div>
		</section>

		<section class="guest-course__section guest-course__confidence">
			<div class="guest-course__shell guest-course__story-grid">
				<figure class="guest-course__story-art">
					<img :src="confidenceImage" :alt="confidenceImageAlt" />
				</figure>
				<div>
					<span class="guest-course__kicker">{{ __('Your first confident conversations') }}</span>
					<h2>{{ confidenceTitle }}</h2>
					<p class="guest-course__story-lead">{{ confidenceLead }}</p>
					<ul class="guest-course__confidence-list">
						<li v-for="item in confidenceItems" :key="item"><CheckCircle2 class="size-5" />{{ item }}</li>
					</ul>
					<div class="guest-course__credibility"><strong>{{ __('12,000+ learners') }}</strong><span>{{ __('across 20 countries have begun their language-learning journey with Bhasha.io.') }}</span></div>
				</div>
			</div>
		</section>

		<section v-if="testimonials.length" class="guest-course__section guest-course__testimonials">
			<div class="guest-course__shell">
				<header class="guest-course__section-header">
					<span>{{ __('Trusted by adult learners') }}</span>
					<h2>{{ __('Learning a new language can feel approachable.') }}</h2>
					<p>{{ testimonialsLead }}</p>
				</header>
				<div class="guest-course__testimonial-grid">
					<article v-for="testimonial in testimonials" :key="testimonial.name">
						<div class="guest-course__stars"><Star v-for="star in 5" :key="star" class="size-4 fill-current" /></div>
						<p>“{{ testimonial.quote }}”</p>
						<footer><span>{{ initials(testimonial.name) }}</span><div><strong>{{ testimonial.name }}</strong><small>{{ testimonial.role }}</small></div></footer>
					</article>
				</div>
			</div>
		</section>

		<section id="faq" class="guest-course__section guest-course__faq">
			<div class="guest-course__shell">
				<header class="guest-course__section-header"><span>{{ __('Got questions?') }}</span><h2>{{ __('Frequently asked questions') }}</h2></header>
				<div class="guest-course__faq-list">
					<details v-for="(faq, index) in faqs" :key="faq.question" :open="index === 0">
						<summary><span>{{ faq.question }}</span><strong>+</strong></summary>
						<p>{{ faq.answer }}</p>
					</details>
				</div>
			</div>
		</section>

		<footer class="guest-course__footer">
			<div class="guest-course__shell"><img :src="brandLogo" alt="bhasha.io" /><span>{{ __('Practical language learning for real conversations.') }}</span><a href="#faq">{{ __('Course Questions') }} ↑</a><a href="https://github.com/Varta-Labs/bhasha-lms-public" target="_blank" rel="noopener noreferrer">{{ __('Source code') }}</a></div>
		</footer>

		<a
			v-if="showFloatingAction"
			:href="signupUrl"
			class="guest-course__floating-action"
		>
			{{ enrollLabel }}
		</a>
	</div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { createResource } from 'frappe-ui'
import {
	Award,
	BookOpen,
	CheckCircle2,
	ChevronRight,
	Languages,
	MessageCircle,
	MonitorPlay,
	Play,
	Star,
	Users,
} from 'lucide-vue-next'
import CourseOutline from '@/components/CourseOutline.vue'
import { getLmsRoute, getSignupUrl } from '@/utils/basePath'
import type { CourseDetails, OutlineChapter, Resource } from '@/types/api'

const props = defineProps<{ course: Resource<CourseDetails | null> }>()
const heroElement = ref<HTMLElement | null>(null)
const showFloatingAction = ref(false)
let pageObserver: IntersectionObserver | null = null
let heroVisible = true

const outline = createResource({
	url: 'lms.lms.utils.get_course_outline',
	makeParams() {
		return { course: props.course.data?.name, progress: false }
	},
	auto: false,
}) as Resource<OutlineChapter[] | null>

watch(
	() => props.course.data?.name,
	(courseName) => {
		if (courseName) outline.reload()
	},
	{ immediate: true },
)

const isKannadaCourse = computed(() =>
	`${props.course.data?.name || ''} ${props.course.data?.title || ''}`.toLowerCase().includes('kannada'),
)

const isHindiCourse = computed(() =>
	`${props.course.data?.name || ''} ${props.course.data?.title || ''}`.toLowerCase().includes('hindi'),
)

const hasEarlyBirdOffer = computed(() =>
	Boolean(props.course.data?.paid_course && (isKannadaCourse.value || isHindiCourse.value)),
)

const courseLanguage = computed(() => {
	const category = props.course.data?.category?.trim()
	if (category && category.toLowerCase() !== 'languages') return category
	const title = props.course.data?.title?.trim() || ''
	return title.replace(/\s+(?:video\s+)?course$/i, '').trim() || __('the language')
})

const storyKicker = computed(() => __('Why {0} matters').format(courseLanguage.value))
const communityImageAlt = computed(() =>
	isKannadaCourse.value
		? __('Three adults sharing a friendly conversation in a Bengaluru apartment community')
		: __('Adults sharing a friendly conversation while practising {0}').format(courseLanguage.value),
)
const guidedLearningImageAlt = computed(() =>
	__('An adult learner practising {0} with a trainer through a guided video lesson').format(courseLanguage.value),
)
const confidenceImageAlt = computed(() =>
	__('A learner confidently using {0} in an everyday conversation').format(courseLanguage.value),
)
const confidenceTitle = computed(() =>
	__('Move from recognising words to replying in {0}.').format(courseLanguage.value),
)
const confidenceLead = computed(() =>
	__('By the end of the course, you will have a practical foundation for simple, everyday spoken {0}.').format(courseLanguage.value),
)
const testimonialsLead = computed(() =>
	__('Hear from learners who have studied {0} with Bhasha.io.').format(courseLanguage.value),
)

const marketingTitle = computed(() =>
	isKannadaCourse.value || isHindiCourse.value
		? __('Start Speaking {0} for Everyday Conversations').format(courseLanguage.value)
		: props.course.data?.title || '',
)

const marketingIntroduction = computed(() =>
	isKannadaCourse.value || isHindiCourse.value
		? __('Learn practical {0} to communicate more comfortably at work, while travelling, and in everyday situations through a structured, beginner-friendly course you can complete at your own pace.').format(courseLanguage.value)
		: props.course.data?.short_introduction || __('A practical, guided course designed to help you build useful skills with confidence.'),
)

const storyTitle = computed(() =>
	isKannadaCourse.value
		? __('Karnataka feels more like home when you can join the conversation.')
		: __('Turn structured learning into skills you can use every day.'),
)

const storyLead = computed(() =>
	isKannadaCourse.value
		? __('Whether you are working here, building a life here, or simply trying to feel more connected, a few spoken sentences can make a meaningful difference.')
		: props.course.data?.short_introduction || __('A practical course can turn unfamiliar situations into moments of real confidence.'),
)

const outcomesTitle = computed(() =>
	isKannadaCourse.value
		? __('Participate instead of staying silent.')
		: __('Move from understanding to confident action.'),
)

const outcomesLead = computed(() =>
	isKannadaCourse.value
		? __('Even simple Kannada can help you build trust, show respect, and feel more connected.')
		: __('Each lesson is designed around practical progress you can recognise and use.'),
)

const priceLabel = computed(() => {
	if (!props.course.data?.paid_course) return __('Free')
	return props.course.data.price || (props.course.data.course_price ? `₹${props.course.data.course_price}` : __('Paid course'))
})

const enrollLabel = computed(() =>
	`${__('Sign up and Enroll for')} ${priceLabel.value}`,
)

const previewImage = computed(() =>
	props.course.data?.image || `${import.meta.env.BASE_URL}kannada-course-hero-v1.png`,
)
const landingVideoUrl = computed(() => {
	const link = props.course.data?.video_link
	if (!link) return ''
	return link.startsWith('http') ? link : `https://www.youtube.com/embed/${link}`
})
const brandLogo = `${import.meta.env.BASE_URL}bhasha-logo-text-transparent.png`
const communityImage = `${import.meta.env.BASE_URL}course-marketing/community-connection.jpg`
const guidedLearningImage = `${import.meta.env.BASE_URL}course-marketing/guided-learning.jpg`
const confidenceImage = `${import.meta.env.BASE_URL}course-marketing/everyday-confidence.jpg`

const signupUrl = computed(() =>
	getSignupUrl(getLmsRoute(`billing/course/${props.course.data?.name || ''}`)),
)

const outcomes = computed<string[]>(() => {
	const configured = props.course.data?.learning_outcomes
	if (configured?.length) return configured.slice(0, 6)
	if (isKannadaCourse.value) {
		return [
			__('Greet neighbours and take part in everyday community conversations.'),
			__('Join simple workplace exchanges instead of waiting on the sidelines.'),
			__('Ask and answer common questions in clear, simple Kannada.'),
			__('Recognise familiar words and understand common spoken phrases.'),
			__('Respond with simple sentences when it is your turn to speak.'),
			__('Connect with the language, culture, and people of the place you live in.'),
		]
	}
	return [
		__('Understand the essential ideas with a clear, guided learning path.'),
		__('Practise new skills through examples grounded in real situations.'),
		__('Build confidence through active repetition and useful checkpoints.'),
		__('Return to lessons whenever you need a quick, focused refresher.'),
		__('Track your progress as you complete each part of the course.'),
		__('Finish with a practical foundation you can keep building on.'),
	]
})

const courseStats = computed(() => {
	const chapterCount = props.course.data?.chapters?.length || 0
	const lessonCount = props.course.data?.lessons || 0
	const parts = []
	if (chapterCount) parts.push(`${chapterCount} ${chapterCount === 1 ? __('module') : __('modules')}`)
	if (lessonCount) parts.push(`${lessonCount} ${lessonCount === 1 ? __('lesson') : __('lessons')}`)
	return parts.join(' · ')
})

const referenceStats = computed(() => {
	if (!isKannadaCourse.value) return courseStats.value
	if (!outline.data?.length) return courseStats.value
	const moduleCount = marketingModules.value.length
	const lessonCount = marketingModules.value.reduce(
		(total, module) => total + module.lessons.length,
		0,
	)
	return `${moduleCount} ${moduleCount === 1 ? __('module') : __('modules')} · ${lessonCount} ${lessonCount === 1 ? __('lesson') : __('lessons')}`
})

const storyPoints = [
	{ title: __('Build trust'), copy: __('Meet everyday interactions with warmth and effort.') },
	{ title: __('Take part'), copy: __('Join the conversation instead of staying silent.') },
	{ title: __('Show respect'), copy: __('Connect with the language, culture, and people around you.') },
]

const methodSteps = computed(() => [
	{ title: __('Watch the trainer teach'), copy: __('New {0} words and phrases are introduced in context.').format(courseLanguage.value) },
	{ title: __('Practise with the learner'), copy: __('Pause, repeat aloud, and learn as the learner improves.') },
	{ title: __('Understand how it is used'), copy: __('Hear pronunciation corrections, usage notes, and conversations built step by step.') },
])

const marketingModules = computed(() => {
	if (!outline.data?.length) return []
	return outline.data.map((module) => ({
		title: module.title,
		lessons: (module.lessons || []).map((lesson) => lesson.title),
	}))
})

const confidenceItems = computed(() => [
	__('Introduce yourself in simple {0}').format(courseLanguage.value),
	__('Ask and answer common questions'),
	__('Understand familiar spoken phrases'),
	__('Build clear, simple {0} sentences').format(courseLanguage.value),
])

const testimonials = computed(() =>
	props.course.data?.testimonials?.length ? props.course.data.testimonials : [],
)

const defaultFaqs = computed(() => [
	{ question: __('What will I be able to do after this course?'), answer: __('You will have a practical foundation for introducing yourself, asking and answering common questions, understanding familiar phrases, and speaking in simple {0} sentences.').format(courseLanguage.value) },
	{ question: __('How is the course taught?'), answer: __('You watch a trainer teach an adult learner on screen. The learner practises, the trainer corrects pronunciation and explains usage, and you pause and practise along with them.') },
	{ question: __('Is this a live course?'), answer: __('No. It is a self-paced course you can access online. Pause, repeat, practise aloud, and move through the lessons on your own schedule.') },
	{ question: __('Do I need to know {0} grammar or script?').format(courseLanguage.value), answer: __('No. The course is made for adult beginners and focuses on practical spoken {0}—not a heavy grammar-first or textbook-first approach.').format(courseLanguage.value) },
	{ question: __('How do I get access after payment?'), answer: __('Enroll or create your account, complete payment through the LMS billing page, and your course access will be activated automatically.') },
])

const faqs = computed(() =>
	props.course.data?.faqs?.length ? props.course.data.faqs : defaultFaqs.value,
)

function initials(name: string) {
	return name.split(/\s+/).filter(Boolean).map((part) => part[0]).join('').slice(0, 2).toUpperCase()
}

const outcomeIcons = [CheckCircle2, Languages, MessageCircle, MonitorPlay, Users, Award]

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
.guest-course {
	--guest-brand: #6c5ce7;
	--guest-brand-deep: #4a38c2;
	--guest-brand-soft: rgba(108, 92, 231, 0.1);
	--guest-brand-border: rgba(108, 92, 231, 0.25);
	--guest-ink: #171717;
	--guest-body: #525252;
	--guest-muted: #7c7c7c;
	--guest-line: #e2e2e2;
	min-width: 0;
	color: var(--guest-body);
	background: #fff;
	font-family: var(--bhasha-font-sans);
}

.guest-course__shell { width: min(100%, 1180px); margin-inline: auto; padding-inline: clamp(1.5rem, 4vw, 2.5rem); }
.guest-course__hero { position: relative; overflow: hidden; padding-block: clamp(3rem, 6vw, 4.5rem); isolation: isolate; background: radial-gradient(circle at 18% 8%, rgba(255,255,255,.72), transparent 34%), radial-gradient(circle at 82% 76%, rgba(210,189,153,.18), transparent 36%), linear-gradient(135deg,#f7f2e8,#f3ecdf 58%,#f8f4eb); }
.guest-course__hero::before { position: absolute; z-index: -1; top: -20rem; right: -14rem; width: 42rem; height: 42rem; border-radius: 50%; opacity: .45; background: repeating-radial-gradient(circle,transparent 0 35px,rgba(113,91,61,.13) 36px 37px,transparent 38px 70px); content: ''; }
.guest-course__hero::after { position: absolute; z-index: -1; left: max(1.25rem,calc((100vw - 1180px)/2 - 3rem)); bottom: 1.5rem; width: 9.5rem; height: 5.75rem; opacity: .4; background-image: radial-gradient(circle,rgba(113,91,61,.28) 1.25px,transparent 1.5px); background-size: 16px 16px; mask-image: linear-gradient(115deg,#000,transparent 84%); content: ''; }
.guest-course__hero-grid { display: grid; align-items: start; gap: 2.5rem; }
.guest-course__hero-copy h1, .guest-course h2, .guest-course h3 { color: var(--guest-ink); font-family: var(--bhasha-font-display); }
.guest-course__hero-copy h1 { max-width: 34rem; font-size: clamp(2.25rem,4.2vw,3.5rem); font-weight: 800; line-height: 1.1; letter-spacing: -.035em; text-wrap: balance; }
.guest-course__hero-copy > p { max-width: 34rem; margin-top: 1.5rem; font-size: clamp(1.0625rem,1.5vw,1.2rem); line-height: 1.65; }
.guest-course__offer { margin-top: 2rem; }
.guest-course__price-row { display: flex; flex-wrap: wrap; align-items: center; gap: .6rem 1rem; margin-bottom: 1.25rem; }
.guest-course__offer-label { flex-basis: 100%; color: var(--guest-brand-deep)!important; font-size: .75rem!important; font-weight: 800!important; letter-spacing: .1em; text-transform: uppercase; }
.guest-course__price-row strong { color: var(--guest-ink); font-family: var(--bhasha-font-display); font-size: clamp(2.5rem,4vw,3rem); line-height: 1; letter-spacing: -.04em; }
.guest-course__price-row s { color: var(--guest-muted); font-family: var(--bhasha-font-display); font-size: 1.25rem; font-weight: 700; }
.guest-course__price-row span { color: var(--guest-muted); font-size: .875rem; font-weight: 600; }
.guest-course__primary-action, .guest-course__floating-action { display: inline-flex; min-height: 3.25rem; align-items: center; justify-content: center; padding: .875rem 1.5rem; border-radius: 9999px; background: linear-gradient(135deg,var(--guest-brand),var(--guest-brand-deep)); color: #fff; font-size: .9375rem; font-weight: 800; box-shadow: 0 14px 28px -8px rgba(108,92,231,.4); transition: transform .18s ease,filter .18s ease; }
.guest-course__primary-action:hover, .guest-course__floating-action:hover { filter: brightness(1.06); transform: translateY(-1px); }
.guest-course__media { position: relative; overflow: hidden; width: 100%; margin: 0; aspect-ratio: 16/10; border: 1px solid rgba(84,64,39,.12); border-radius: clamp(24px,3vw,28px); background: var(--guest-brand-deep); box-shadow: 0 26px 56px -32px rgba(74,47,25,.4); }
.guest-course__media img { width: 100%; height: 100%; object-fit: cover; }
.guest-course__media iframe { width: 100%; height: 100%; border: 0; }
.guest-course__media > a { position: absolute; bottom: 1.5rem; left: 1.5rem; display: inline-flex; width: 3.5rem; height: 3.5rem; align-items: center; justify-content: center; border: 6px solid rgba(255,255,255,.94); border-radius: 50%; background: var(--guest-brand); color: #fff; }
.guest-course__section { padding-block: clamp(4rem,8vw,6rem); }
.guest-course__section-header { max-width: 42rem; margin: 0 auto 3rem; text-align: center; }
.guest-course__section-header > span, .guest-course__kicker { display: block; margin-bottom: .75rem; color: var(--guest-brand); font-size: .75rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }
.guest-course__section-header h2, .guest-course__story h2, .guest-course__curriculum h2 { font-size: clamp(1.75rem,2.5vw,2.5rem); font-weight: 800; line-height: 1.2; letter-spacing: -.025em; text-wrap: balance; }
.guest-course__section-header p { max-width: 38rem; margin: .75rem auto 0; line-height: 1.6; }
.guest-course__outcomes { background: #f8f6ff; }
.guest-course__outcome-grid { display: grid; gap: 1.25rem; }
.guest-course__outcome-grid article { padding: 2rem; border: 1px solid #ededed; border-radius: 1.25rem; background: #fff; box-shadow: 0 1px 2px rgba(0,0,0,.06); }
.guest-course__outcome-grid article { display: flex; align-items: flex-start; gap: 1rem; }
.guest-course__outcome-grid p { line-height: 1.55; }
.guest-course__icon-well { display: inline-flex; width: 3rem; height: 3rem; flex: 0 0 auto; align-items: center; justify-content: center; border-radius: .75rem; background: var(--guest-brand-soft); color: var(--guest-brand); }
.guest-course__story-grid { display: grid; align-items: center; gap: clamp(2.5rem,6vw,5rem); }
.guest-course__story-art { overflow: hidden; aspect-ratio: 4/3; border-radius: 1.75rem; background: #f3ecdf; box-shadow: 0 20px 45px -28px rgba(74,47,25,.4); }
.guest-course__story-art img { width: 100%; height: 100%; object-fit: cover; }
.guest-course__story-lead, .guest-course__prose { margin-top: 1.25rem; font-size: 1.0625rem; line-height: 1.7; }
.guest-course__prose :deep(p + p) { margin-top: 1rem; }
.guest-course__story-points, .guest-course__method-steps { display:grid; gap:1.25rem; margin-top:2rem; padding:0; list-style:none; }
.guest-course__story-points li, .guest-course__method-steps li { display:grid; grid-template-columns:2.5rem minmax(0,1fr); align-items:start; gap:1rem; }
.guest-course__story-points li > span, .guest-course__method-steps li > span { display:inline-flex; width:2.5rem; height:2.5rem; align-items:center; justify-content:center; border-radius:.75rem; background:var(--guest-brand-soft); color:var(--guest-brand-deep); font-size:.75rem; font-weight:800; }
.guest-course__story-points strong, .guest-course__method-steps strong { display:block; color:var(--guest-ink); font-family:var(--bhasha-font-display); font-size:1rem; }
.guest-course__story-points p, .guest-course__method-steps p { margin-top:.25rem; font-size:.9rem; line-height:1.55; }
.guest-course__method { background: #f3f3f3; }
.guest-course__quiet-callout { display:inline-flex; margin-top:1.75rem; padding:.65rem 1rem; border:1px solid var(--guest-brand-border); border-radius:9999px; background:rgba(255,255,255,.72); color:var(--guest-brand-deep); font-size:.8125rem; font-weight:700; }
.guest-course__curriculum-header { display: flex; flex-wrap: wrap; align-items: flex-end; justify-content: space-between; gap: 1.5rem; margin-bottom: 2.5rem; padding-bottom: 1.5rem; border-bottom: 1px solid #f3e8ff; }
.guest-course__curriculum-header p { max-width:38rem; margin-top:.75rem; line-height:1.6; }
.guest-course__curriculum-badge { display: inline-flex; align-items: center; gap: .5rem; padding: .5rem 1rem; border: 1px solid var(--guest-brand-border); border-radius: 9999px; background: var(--guest-brand-soft); color: var(--guest-brand-deep); font-size: .875rem; font-weight: 700; }
.guest-course__curriculum-panel { max-width: 52rem; margin-inline: auto; padding: clamp(1.25rem,4vw,2rem); border: 1px solid rgba(196,181,253,.6); border-radius: 1.75rem; background: linear-gradient(145deg,rgba(248,246,255,.5),#fff,rgba(248,246,255,.25)); box-shadow: 0 8px 24px -6px rgba(0,0,0,.08); }
.guest-course__module-list { display:grid; gap:.625rem; }
.guest-course__module-list details { overflow:hidden; border:1px solid var(--guest-line); border-radius:1.25rem; background:#fff; transition:border-color .18s ease,box-shadow .18s ease; }
.guest-course__module-list details[open] { border-color:var(--guest-brand-border); box-shadow:0 8px 24px -6px rgba(0,0,0,.08); }
.guest-course__module-list summary { display:grid; grid-template-columns:2.5rem minmax(0,1fr); align-items:center; gap:.875rem; min-height:4.5rem; padding:.875rem 1.125rem; cursor:pointer; list-style:none; }
.guest-course__module-list summary::-webkit-details-marker { display:none; }
.guest-course__module-list summary:hover { background:#f8f6ff; }
.guest-course__module-chevron { padding:.45rem; border-radius:.7rem; background:var(--guest-brand-soft); color:var(--guest-brand); transition:transform .18s ease; }
.guest-course__module-list details[open] .guest-course__module-chevron { transform:rotate(90deg); }
.guest-course__module-list summary span { display:flex; min-width:0; align-items:center; justify-content:space-between; gap:1rem; }
.guest-course__module-list summary strong { color:var(--guest-ink); font-family:var(--bhasha-font-display); font-size:1rem; }
.guest-course__module-list summary small { flex:0 0 auto; padding:.3rem .6rem; border-radius:9999px; background:#f3f3f3; color:var(--guest-muted); font-size:.72rem; font-weight:700; }
.guest-course__module-list ul { margin:0; padding:0 1.125rem 1rem 4.5rem; list-style:none; }
.guest-course__module-list li { display:flex; min-height:2.75rem; align-items:center; gap:.75rem; border-top:1px solid #ededed; color:var(--guest-body); font-size:.875rem; }
.guest-course__module-list li svg { flex:0 0 auto; color:var(--guest-brand); }
.guest-course__confidence { background:#fff; }
.guest-course__confidence-list { display:grid; gap:.875rem; margin-top:1.75rem; padding:0; list-style:none; }
.guest-course__confidence-list li { display:flex; align-items:center; gap:.75rem; color:var(--guest-ink); font-weight:650; }
.guest-course__confidence-list svg { flex:0 0 auto; color:var(--guest-brand); }
.guest-course__credibility { display:grid; gap:.25rem; margin-top:2rem; padding:1.25rem; border-left:3px solid var(--guest-brand); border-radius:0 1rem 1rem 0; background:#f8f6ff; }
.guest-course__credibility strong { color:var(--guest-brand-deep); font-family:var(--bhasha-font-display); font-size:1.125rem; }
.guest-course__credibility span { font-size:.875rem; line-height:1.55; }
.guest-course__testimonials { background:#f9f8fd; }
.guest-course__testimonial-grid { display:grid; gap:1.25rem; }
.guest-course__testimonial-grid article { display:flex; min-width:0; flex-direction:column; padding:1.75rem; border:1px solid var(--guest-brand-border); border-radius:1.5rem; background:#fff; box-shadow:0 1px 2px rgba(0,0,0,.06); }
.guest-course__stars { display:flex; gap:.2rem; color:#f59e0b; }
.guest-course__testimonial-grid article > p { flex:1; margin-top:1.25rem; color:var(--guest-ink); font-size:1rem; line-height:1.65; }
.guest-course__testimonial-grid footer { display:flex; align-items:center; gap:.75rem; margin-top:1.5rem; padding-top:1.25rem; border-top:1px solid #ededed; }
.guest-course__testimonial-grid footer > span { display:inline-flex; width:2.5rem; height:2.5rem; align-items:center; justify-content:center; border-radius:50%; background:var(--guest-brand-soft); color:var(--guest-brand-deep); font-size:.75rem; font-weight:800; }
.guest-course__testimonial-grid footer div { display:grid; gap:.1rem; }
.guest-course__testimonial-grid footer strong { color:var(--guest-ink); font-size:.875rem; }
.guest-course__testimonial-grid footer small { color:var(--guest-muted); font-size:.75rem; }
.guest-course__faq-list { max-width:52rem; margin-inline:auto; }
.guest-course__faq-list details { border-bottom:1px solid var(--guest-line); }
.guest-course__faq-list summary { display:flex; min-height:4.5rem; align-items:center; justify-content:space-between; gap:1rem; cursor:pointer; list-style:none; color:var(--guest-ink); font-family:var(--bhasha-font-display); font-weight:700; }
.guest-course__faq-list summary::-webkit-details-marker { display:none; }
.guest-course__faq-list summary strong { color:var(--guest-brand); font-size:1.5rem; font-weight:500; transition:transform .18s ease; }
.guest-course__faq-list details[open] summary strong { transform:rotate(45deg); }
.guest-course__faq-list details p { max-width:46rem; padding:0 2rem 1.5rem 0; line-height:1.7; }
.guest-course__footer { border-top:1px solid var(--guest-line); background:#fff; }
.guest-course__footer .guest-course__shell { display:flex; min-height:6rem; align-items:center; justify-content:space-between; gap:1.5rem; color:var(--guest-muted); font-size:.8125rem; }
.guest-course__footer img { width:8.5rem; height:auto; }
.guest-course__footer a { color:var(--guest-brand-deep); font-weight:700; }
.guest-course__floating-action { position: fixed; right: 1.5rem; bottom: calc(1.5rem + env(safe-area-inset-bottom)); z-index: 50; }

@media (min-width: 768px) { .guest-course__outcome-grid { grid-template-columns: repeat(2,minmax(0,1fr)); } .guest-course__story-grid { grid-template-columns: minmax(0,1fr) minmax(0,1fr); } .guest-course__story-grid--reverse > :first-child { order:1; } .guest-course__testimonial-grid { grid-template-columns:repeat(3,minmax(0,1fr)); } }
@media (min-width: 1024px) { .guest-course__hero-grid { grid-template-columns: minmax(0,.9fr) minmax(0,1.4fr); gap: 3.5rem; } .guest-course__hero-copy h1 { font-size:clamp(2.5rem,3.2vw,3rem); line-height:1.08; } .guest-course__outcome-grid { grid-template-columns: repeat(3,minmax(0,1fr)); } }
@media (max-width: 639px) { .guest-course { padding-bottom:calc(7.25rem + env(safe-area-inset-bottom)); } .guest-course__shell { padding-inline: 1rem; } .guest-course__hero::before { opacity: .3; } .guest-course__primary-action { width: 100%; } .guest-course__module-list summary { grid-template-columns:2.25rem minmax(0,1fr); padding-inline:.75rem; } .guest-course__module-list summary span { align-items:flex-start; flex-direction:column; gap:.35rem; } .guest-course__module-list ul { padding-left:3.75rem; } .guest-course__footer .guest-course__shell { align-items:flex-start; flex-direction:column; justify-content:center; padding-block:1.5rem; } .guest-course__floating-action { right: 1rem; bottom: calc(1rem + env(safe-area-inset-bottom)); left: 1rem; } }
@media (prefers-reduced-motion: reduce) { .guest-course *, .guest-course *::before, .guest-course *::after { scroll-behavior: auto !important; transition-duration: .01ms !important; } }
</style>
