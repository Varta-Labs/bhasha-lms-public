<template>
	<SkeletonLoader v-if="!course.data" variant="course-page" />
	<div v-else class="course-landing min-w-0 overflow-x-clip bg-surface-white dark:bg-ink-gray-9">
		<!-- Band 1: HERO SECTION -->
		<section class="course-hero">
			<div class="course-shell course-hero-grid items-center py-12 lg:py-20">
				<div class="min-w-0 space-y-6">
					<div class="course-eyebrow">
						<Sparkles class="size-4 text-bhasha-purple animate-pulse" />
						<span class="font-bold tracking-wide uppercase">{{ heroEyebrow }}</span>
					</div>
					<h1 class="course-title text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight leading-tight text-ink-gray-9 dark:text-white">
						{{ heroTitle }}
					</h1>
					<p v-if="heroIntroduction" class="course-introduction text-lg sm:text-xl text-ink-gray-7 dark:text-ink-gray-3 leading-relaxed max-w-2xl">
						{{ heroIntroduction }}
					</p>
					
					<!-- Trust Highlights Strip in Hero -->
					<div class="flex flex-wrap items-center gap-3 py-2">
						<div v-for="badge in trustBadgesList" :key="badge" class="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-bhasha-purple/10 dark:bg-bhasha-purple/20 border border-bhasha-purple/25 text-bhasha-purple dark:text-[#A292FF] text-sm font-semibold shadow-sm">
							<CheckCircle2 class="size-4 stroke-[2.5] shrink-0" />
							<span>{{ badge }}</span>
						</div>
					</div>

					<!-- Hero CTA Block -->
					<div class="flex flex-wrap items-center gap-4 pt-2">
						<a class="course-button course-button-primary shadow-xl shadow-bhasha-purple/30 hover:scale-[1.02] active:scale-[0.98] transition-all" href="#course-content">
							{{ __('View Curriculum') }}
						</a>
						<a class="course-button course-button-secondary bg-white/90 dark:bg-ink-gray-8 hover:bg-surface-gray-2 transition-colors" href="#faq-section">
							{{ __('Read FAQs') }}
						</a>
					</div>

					<!-- Hero Meta Stats -->
					<div class="flex flex-wrap items-center gap-4 pt-4 border-t border-outline-gray-2/80 text-sm font-medium text-ink-gray-7 dark:text-ink-gray-4">
						<div class="flex items-center gap-1.5 bg-white/80 dark:bg-ink-gray-8 px-3.5 py-1.5 rounded-full border border-purple-200/50 dark:border-purple-900/30 shadow-2xs">
							<Star class="size-4 text-amber-500 fill-amber-500" />
							<span class="font-bold text-ink-gray-9 dark:text-white">{{ formatRating(course.data.rating || 0) }}</span>
							<span class="text-ink-gray-5">({{ formatAmount(course.data.rating_count || 0) }} {{ __('reviews') }})</span>
						</div>
						<div class="flex items-center gap-1.5 bg-white/80 dark:bg-ink-gray-8 px-3.5 py-1.5 rounded-full border border-purple-200/50 dark:border-purple-900/30 shadow-2xs">
							<Users class="size-4 text-bhasha-purple stroke-2" />
							<span class="font-bold text-ink-gray-9 dark:text-white">{{ formatAmount(course.data.enrollments || 0) }}</span>
							<span class="text-ink-gray-5">{{ __('active learners') }}</span>
						</div>
					</div>
				</div>
				<!-- Right Side of Hero: Media Box + Enrollment Card Overlay -->
				<div class="min-w-0 lg:ps-6">
					<CourseCardOverlay :course="course" />
				</div>
			</div>
		</section>

		<!-- Band 2: KEY HIGHLIGHTS / FEATURES STRIP (Full Width Horizontal Band) -->
		<section v-if="featuresList.length" class="w-full bg-surface-gray-2 dark:bg-ink-gray-8/80 border-y border-outline-gray-2 py-14 sm:py-20">
			<div class="course-shell">
				<div class="text-center max-w-2xl mx-auto mb-12">
					<div class="section-kicker text-bhasha-purple font-bold tracking-widest uppercase text-xs mb-2">{{ __('Why Choose This Course') }}</div>
					<h2 class="text-2xl sm:text-3xl font-black tracking-tight text-ink-gray-9 dark:text-white">{{ __('Everything you need to succeed') }}</h2>
				</div>
				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
					<div v-for="(feature, idx) in featuresList" :key="feature.title" class="bg-white dark:bg-ink-gray-9 p-6 sm:p-8 rounded-2xl border border-outline-gray-2/80 shadow-sm hover:shadow-md transition-all flex flex-col justify-between group">
						<div>
							<div class="size-12 rounded-xl bg-bhasha-purple/10 dark:bg-bhasha-purple/20 flex items-center justify-center text-bhasha-purple mb-5 group-hover:scale-110 transition-transform">
								<component :is="getFeatureIcon(idx)" class="size-6 stroke-[2]" />
							</div>
							<h3 class="font-bold text-lg text-ink-gray-9 dark:text-white mb-2">{{ feature.title }}</h3>
							<p class="text-sm text-ink-gray-6 dark:text-ink-gray-4 leading-relaxed">{{ feature.copy }}</p>
						</div>
					</div>
				</div>
			</div>
		</section>

		<!-- Band 3: ABOUT THE COURSE & TARGET AUDIENCE (Full Width Horizontal Band) -->
		<section class="w-full bg-white dark:bg-ink-gray-9 py-16 sm:py-24">
			<div class="course-shell grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-start">
				<!-- Left Column: Detailed Course Narrative -->
				<div class="lg:col-span-7 space-y-6">
					<div class="section-kicker text-bhasha-purple font-bold tracking-widest uppercase text-xs">{{ __('About the course') }}</div>
					<h2 class="text-3xl sm:text-4xl font-black tracking-tight text-ink-gray-9 dark:text-white leading-tight">
						{{ isKannadaShowcase ? __('For learners who want usable Kannada, not just vocabulary lists.') : (course.data.title || __('Designed for practical mastery.')) }}
					</h2>
					
					<div v-if="isKannadaShowcase" class="space-y-4 text-base sm:text-lg text-ink-gray-7 dark:text-ink-gray-3 leading-relaxed">
						<p>
							{{ __('Traditional language classes focus heavily on script and formal grammar that native speakers rarely use in casual settings. This course bridges that gap by putting daily spoken fluency first.') }}
						</p>
						<p>
							{{ __('You will practice real-life sentence structures, polite cues, listening recognition, and regional expressions needed when interacting with auto drivers, colleagues, neighbors, and shopkeepers across Karnataka.') }}
						</p>
						<div class="p-6 sm:p-8 rounded-3xl bg-bhasha-purple/[0.04] dark:bg-bhasha-purple/[0.1] border border-bhasha-purple/20 my-6 shadow-2xs">
							<h4 class="font-bold text-lg text-ink-gray-9 dark:text-white mb-3 flex items-center gap-2">
								<Sparkles class="size-5 text-bhasha-purple" />
								<span>{{ __('The 3-Step Practical Method') }}</span>
							</h4>
							<ul class="space-y-3 text-sm sm:text-base text-ink-gray-7 dark:text-ink-gray-3">
								<li class="flex items-start gap-3">
									<CheckCircle2 class="size-5 text-bhasha-purple shrink-0 mt-0.5" />
									<span><strong>{{ __('Listen & Absorb:') }}</strong> {{ __('Understand sentence melody and key vocabulary.') }}</span>
								</li>
								<li class="flex items-start gap-3">
									<CheckCircle2 class="size-5 text-bhasha-purple shrink-0 mt-0.5" />
									<span><strong>{{ __('Guided Roleplay:') }}</strong> {{ __('Simulate authentic everyday scenarios.') }}</span>
								</li>
								<li class="flex items-start gap-3">
									<CheckCircle2 class="size-5 text-bhasha-purple shrink-0 mt-0.5" />
									<span><strong>{{ __('Active Repetition:') }}</strong> {{ __('Lock in muscle memory with interactive prompts.') }}</span>
								</li>
							</ul>
						</div>
					</div>
					<div
						v-else-if="course.data.description"
						v-html="course.data.description"
						class="ProseMirror prose max-w-none text-ink-gray-7 dark:text-ink-gray-3 prose-headings:text-ink-gray-9 dark:prose-headings:text-white prose-a:text-bhasha-purple"
					/>
					<p v-else-if="heroIntroduction" class="text-base sm:text-lg text-ink-gray-7 dark:text-ink-gray-3 leading-relaxed">
						{{ heroIntroduction }}
					</p>
				</div>

				<!-- Right Column: Who is this course for? (Target Audience Box) -->
				<div class="lg:col-span-5 bg-gradient-to-br from-purple-50/50 via-white to-purple-50/30 dark:from-[#16161e] dark:to-[#1a1824] p-8 sm:p-10 rounded-3xl border border-purple-200/60 dark:border-purple-900/40 sticky top-24 shadow-lg">
					<div class="flex items-center gap-4 mb-6">
						<div class="size-12 rounded-xl bg-bhasha-purple/10 dark:bg-bhasha-purple/20 text-bhasha-purple flex items-center justify-center font-bold shadow-xs shrink-0">
							<Users class="size-6 stroke-2" />
						</div>
						<div>
							<h3 class="text-xl font-bold text-ink-gray-9 dark:text-white flex items-center gap-2.5">
								<span>{{ __('Who is this course for?') }}</span>
							</h3>
							<p class="text-xs font-semibold text-ink-gray-5 dark:text-ink-gray-4 uppercase tracking-wider mt-1">
								{{ __('Target learner profile') }}
							</p>
						</div>
					</div>
					<ul class="space-y-4">
						<li v-for="(audience, i) in targetAudienceList" :key="i" class="flex items-start gap-3.5 pb-4 border-b border-purple-100 dark:border-purple-900/30 last:border-0 last:pb-0">
							<div class="size-6 rounded-full bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0 mt-0.5 font-bold text-sm">
								✓
							</div>
							<div>
								<h4 class="font-bold text-sm text-ink-gray-9 dark:text-white">{{ audience.title }}</h4>
								<p class="text-xs text-ink-gray-6 dark:text-ink-gray-4 mt-0.5 leading-relaxed">{{ audience.desc }}</p>
							</div>
						</li>
					</ul>
				</div>
			</div>
		</section>

		<!-- Band 4: WHAT YOU WILL ACCOMPLISH / LEARNING OUTCOMES (Full Width Horizontal Band) -->
		<section v-if="outcomesList.length || highlightsList.length" class="w-full bg-[#F8F6FF] dark:bg-ink-gray-8 py-16 sm:py-24 border-y border-bhasha-purple/15">
			<div class="course-shell">
				<div class="text-center max-w-3xl mx-auto mb-14">
					<div class="section-kicker text-bhasha-purple font-bold tracking-widest uppercase text-xs mb-2">{{ __('Learning Outcomes') }}</div>
					<h2 class="text-3xl sm:text-4xl font-black tracking-tight text-ink-gray-9 dark:text-white">{{ __('What you will accomplish') }}</h2>
					<p class="text-sm sm:text-base text-ink-gray-6 dark:text-ink-gray-4 mt-3">{{ __('By the end of this structured program, you will have mastered these practical competencies.') }}</p>
				</div>

				<div v-if="outcomesList.length" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 lg:gap-6 mb-12">
					<div v-for="(outcome, idx) in outcomesList" :key="typeof outcome === 'string' ? outcome : outcome.title" class="bg-white dark:bg-ink-gray-9 p-6 rounded-2xl border border-purple-200/50 dark:border-purple-900/30 shadow-sm flex items-start gap-4 hover:border-bhasha-purple/50 transition-colors group">
						<div class="size-10 rounded-xl bg-bhasha-purple/10 text-bhasha-purple flex items-center justify-center shrink-0 shadow-2xs group-hover:scale-110 transition-transform">
							<component :is="getOutcomeIcon(idx)" class="size-5 stroke-[2]" />
						</div>
						<div class="text-sm sm:text-base font-medium text-ink-gray-8 dark:text-ink-gray-2 leading-relaxed pt-0.5">
							{{ typeof outcome === 'string' ? outcome : (outcome.copy || outcome.title) }}
						</div>
					</div>
				</div>

				<div v-if="highlightsList.length" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 pt-8 border-t border-bhasha-purple/15">
					<div v-for="highlight in highlightsList" :key="highlight.title" class="bg-white/90 dark:bg-ink-gray-9/90 p-6 rounded-2xl border border-outline-gray-2 flex flex-col justify-between shadow-2xs">
						<div class="size-10 rounded-xl bg-bhasha-purple/10 text-bhasha-purple flex items-center justify-center mb-4">
							<component :is="highlight.icon || BookOpen" class="size-5 stroke-1.5" />
						</div>
						<div>
							<h4 class="font-bold text-ink-gray-9 dark:text-white">{{ highlight.title }}</h4>
							<p class="text-xs text-ink-gray-6 dark:text-ink-gray-4 mt-1 leading-relaxed">{{ highlight.copy }}</p>
						</div>
					</div>
				</div>
			</div>
		</section>

		<!-- Band 5: CURRICULUM OVERVIEW (Full Width Horizontal Band) -->
		<section id="course-content" class="w-full bg-white dark:bg-ink-gray-9 py-16 sm:py-24">
			<div class="course-shell max-w-5xl mx-auto">
				<div class="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-10 pb-6 border-b border-purple-100 dark:border-purple-900/30">
					<div>
						<div class="section-kicker text-bhasha-purple font-bold tracking-widest uppercase text-xs mb-1">{{ __('Curriculum') }}</div>
						<h2 class="text-3xl sm:text-4xl font-black tracking-tight text-ink-gray-9 dark:text-white">{{ courseContentTitle }}</h2>
					</div>
					<div class="flex items-center gap-2 px-4 py-2 rounded-full bg-purple-50 dark:bg-purple-900/30 text-sm font-bold text-bhasha-purple border border-purple-200/50 dark:border-purple-800/40">
						<BookOpen class="size-4.5 stroke-2 text-bhasha-purple" />
						<span>{{ outlineStats }}</span>
					</div>
				</div>

				<div class="bg-gradient-to-br from-purple-50/30 via-white to-purple-50/15 dark:from-[#15151c] dark:via-[#191824] dark:to-[#15151c] rounded-3xl border border-purple-200/60 dark:border-purple-900/40 p-5 sm:p-8 shadow-lg">
					<SkeletonLoader v-if="outline.loading && !outline.data" variant="list" :count="6" />
					<div v-else-if="!hasCourseContent" class="flex flex-col items-center justify-center py-16 text-center">
						<BookOpen class="size-12 text-purple-400 mb-3 stroke-1.5" />
						<span class="text-base font-semibold text-ink-gray-9 dark:text-white">{{ __('Syllabus modules are currently being finalized.') }}</span>
						<span class="text-xs text-ink-gray-5 mt-1">{{ __('Check back soon for the complete chapter breakdown.') }}</span>
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

		<!-- Band 6: MEET YOUR COACH / INSTRUCTORS BAND (Full Width Horizontal Band) -->
		<!-- Band 6: WHY SELF-PACED LEARNING WORKS (Full Width Horizontal Band) -->
		<section class="w-full bg-gradient-to-b from-purple-50/20 via-white to-purple-50/40 dark:from-[#15151c] dark:via-[#181822] dark:to-[#15151c] py-16 sm:py-24 border-t border-purple-100 dark:border-purple-900/30">
			<div class="course-shell max-w-5xl mx-auto">
				<div class="text-center max-w-2xl mx-auto mb-12">
					<div class="section-kicker text-bhasha-purple font-bold tracking-widest uppercase text-xs mb-2">{{ __('Self-Paced Learning') }}</div>
					<h2 class="text-3xl sm:text-4xl font-black tracking-tight text-ink-gray-9 dark:text-white">{{ __('Master skills on your schedule, at your own speed') }}</h2>
					<p class="text-sm sm:text-base text-ink-gray-6 dark:text-ink-gray-4 mt-3">
						{{ __('Designed for busy routines. Access lessons anytime without waiting for live cohorts or schedules.') }}
					</p>
				</div>

				<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
					<div class="bg-white dark:bg-ink-gray-9 p-8 rounded-2xl border border-purple-200/60 dark:border-purple-900/40 shadow-sm flex flex-col justify-between">
						<div>
							<div class="size-12 rounded-xl bg-bhasha-purple/10 dark:bg-bhasha-purple/20 text-bhasha-purple flex items-center justify-center mb-5">
								<MonitorPlay class="size-6 stroke-[2]" />
							</div>
							<h3 class="font-bold text-lg text-ink-gray-9 dark:text-white mb-2">{{ __('Instant & Lifetime Access') }}</h3>
							<p class="text-sm text-ink-gray-6 dark:text-ink-gray-4 leading-relaxed">
								{{ __('Start immediately upon enrollment. Revisit video lessons and audio practice materials as often as you like.') }}
							</p>
						</div>
					</div>
					<div class="bg-white dark:bg-ink-gray-9 p-8 rounded-2xl border border-purple-200/60 dark:border-purple-900/40 shadow-sm flex flex-col justify-between">
						<div>
							<div class="size-12 rounded-xl bg-bhasha-purple/10 dark:bg-bhasha-purple/20 text-bhasha-purple flex items-center justify-center mb-5">
								<Languages class="size-6 stroke-[2]" />
							</div>
							<h3 class="font-bold text-lg text-ink-gray-9 dark:text-white mb-2">{{ __('Active Voice Practice') }}</h3>
							<p class="text-sm text-ink-gray-6 dark:text-ink-gray-4 leading-relaxed">
								{{ __('Practice everyday sentences using structured prompts designed to build spoken confidence naturally.') }}
							</p>
						</div>
					</div>
					<div class="bg-white dark:bg-ink-gray-9 p-8 rounded-2xl border border-purple-200/60 dark:border-purple-900/40 shadow-sm flex flex-col justify-between">
						<div>
							<div class="size-12 rounded-xl bg-bhasha-purple/10 dark:bg-bhasha-purple/20 text-bhasha-purple flex items-center justify-center mb-5">
								<Award class="size-6 stroke-[2]" />
							</div>
							<h3 class="font-bold text-lg text-ink-gray-9 dark:text-white mb-2">{{ __('Structured Checkpoints') }}</h3>
							<p class="text-sm text-ink-gray-6 dark:text-ink-gray-4 leading-relaxed">
								{{ __('Track clear milestones lesson by lesson and earn your verifiable certificate upon completing the program.') }}
							</p>
						</div>
					</div>
				</div>
			</div>
		</section>

		<!-- Band 7: CERTIFICATION BAND (Full Width Horizontal Band) -->
		<section v-if="isKannadaShowcase || course.data.enable_certification" class="w-full bg-gradient-to-r from-[#6C5CE7] to-[#4A38C2] text-white py-16 sm:py-20 relative overflow-hidden">
			<div class="absolute -right-20 -bottom-20 size-80 rounded-full bg-white/10 blur-3xl pointer-events-none" />
			<div class="course-shell flex flex-col md:flex-row items-center justify-between gap-8 relative z-10">
				<div class="space-y-3 text-center md:text-left max-w-2xl">
					<div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/20 text-xs font-bold uppercase tracking-wider">
						<Award class="size-4" />
						<span>{{ __('Verified Achievement') }}</span>
					</div>
					<h2 class="text-3xl sm:text-4xl font-black tracking-tight">{{ __('Earn Your Verified Certificate') }}</h2>
					<p class="text-white/90 text-base sm:text-lg leading-relaxed">
						{{ __('Demonstrate your language competency upon completion. Download or share directly on LinkedIn and your professional resume.') }}
					</p>
				</div>
				<div class="shrink-0">
					<a v-if="!user?.data" :href="signupUrl" class="inline-flex items-center justify-center px-8 py-4 rounded-2xl bg-white !text-[#4A38C2] hover:!text-[#36279E] dark:bg-white dark:!text-[#4A38C2] font-black text-base shadow-2xl hover:bg-purple-50 hover:scale-105 active:scale-95 transition-all">
						{{ __('Sign up and Enroll') }}
					</a>
					<router-link
						v-else
						:to="{
							name: 'Billing',
							params: { type: 'course', name: course.data.name },
						}"
						class="inline-flex items-center justify-center px-8 py-4 rounded-2xl bg-white !text-[#4A38C2] hover:!text-[#36279E] dark:bg-white dark:!text-[#4A38C2] font-black text-base shadow-2xl hover:bg-purple-50 hover:scale-105 active:scale-95 transition-all"
					>
						{{ __('Sign up and Enroll') }}
					</router-link>
				</div>
			</div>
		</section>

		<!-- Band 8: TESTIMONIALS BAND (Full Width Horizontal Band) -->
		<section v-if="testimonialsList.length" class="w-full bg-white dark:bg-ink-gray-9 py-16 sm:py-24">
			<div class="course-shell">
				<div class="text-center max-w-2xl mx-auto mb-14">
					<div class="section-kicker text-bhasha-purple font-bold tracking-widest uppercase text-xs mb-2">{{ __('Learner Stories') }}</div>
					<h2 class="text-3xl sm:text-4xl font-black tracking-tight text-ink-gray-9 dark:text-white">{{ __('See what our students say') }}</h2>
				</div>
				<div class="grid grid-cols-1 md:grid-cols-3 gap-8">
					<article v-for="(testimonial, i) in testimonialsList" :key="i" class="bg-gradient-to-br from-purple-50/40 via-white to-purple-50/20 dark:from-[#16161e] dark:to-[#1a1824] p-8 rounded-3xl border border-purple-200/50 dark:border-purple-900/30 flex flex-col justify-between space-y-6 shadow-md hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
						<div>
							<div class="flex items-center gap-1 text-amber-500 mb-4">
								<Star v-for="s in 5" :key="s" class="size-4 fill-current" />
							</div>
							<p class="text-base text-ink-gray-8 dark:text-ink-gray-2 leading-relaxed italic">“{{ testimonial.quote }}”</p>
						</div>
						<div class="flex items-center gap-3 pt-4 border-t border-purple-100 dark:border-purple-900/30">
							<div class="size-11 rounded-full bg-bhasha-purple/10 text-bhasha-purple flex items-center justify-center font-bold text-sm">
								{{ testimonial.name.split(' ').map((n: string) => n[0]).join('').slice(0, 2) }}
							</div>
							<div>
								<strong class="block font-bold text-sm text-ink-gray-9 dark:text-white">{{ testimonial.name }}</strong>
								<span class="text-xs text-ink-gray-5">{{ testimonial.role }}</span>
							</div>
						</div>
					</article>
				</div>
			</div>
		</section>

		<!-- Band 9: FREQUENTLY ASKED QUESTIONS (Full Width Horizontal Band) -->
		<section v-if="faqsList.length" id="faq-section" class="w-full bg-[#F9F8FD] dark:bg-[#14141a] py-16 sm:py-24 border-t border-purple-100 dark:border-purple-900/30">
			<div class="course-shell max-w-4xl mx-auto">
				<div class="text-center max-w-2xl mx-auto mb-14">
					<div class="section-kicker text-bhasha-purple font-bold tracking-widest uppercase text-xs mb-2">{{ __('Got Questions?') }}</div>
					<h2 class="text-3xl sm:text-4xl font-black tracking-tight text-ink-gray-9 dark:text-white">{{ __('Frequently Asked Questions') }}</h2>
				</div>
				<div class="space-y-4">
					<details
						v-for="(faq, index) in faqsList"
						:key="faq.question"
						:open="index === 0"
						class="group bg-white dark:bg-ink-gray-9 rounded-2xl border border-purple-200/50 dark:border-purple-900/30 p-6 transition-all duration-300 open:shadow-lg open:border-bhasha-purple/50"
					>
						<summary class="flex items-center justify-between font-bold text-base sm:text-lg text-ink-gray-9 dark:text-white cursor-pointer select-none list-none">
							<span>{{ faq.question }}</span>
							<span class="size-8 rounded-full bg-purple-50 dark:bg-purple-900/30 flex items-center justify-center text-bhasha-purple font-bold group-open:rotate-45 transition-transform">+</span>
						</summary>
						<p class="mt-4 pt-4 border-t border-purple-100 dark:border-purple-900/30 text-sm sm:text-base text-ink-gray-7 dark:text-ink-gray-3 leading-relaxed">
							{{ faq.answer }}
						</p>
					</details>
				</div>
			</div>
		</section>

		<!-- Band 10: COURSE REVIEWS & RELATED COURSES -->
		<section class="w-full bg-white dark:bg-ink-gray-9 py-16 sm:py-20 border-t border-outline-gray-2">
			<div class="course-shell space-y-16">
				<CourseReviews
					:courseName="course.data.name"
					:avg_rating="course.data.rating"
					:membership="course.data.membership || null"
				/>
				<RelatedCourses :courseName="course.data.name" />
			</div>
		</section>
	</div>
</template>

<script setup lang="ts">
import { computed, inject, watch, watchEffect } from 'vue'
import { createResource } from 'frappe-ui'
import {
	Award,
	BookOpen,
	CheckCircle2,
	Files,
	Languages,
	MonitorPlay,
	Sparkles,
	Star,
	Users,
} from 'lucide-vue-next'
import { formatAmount, formatRating } from '@/utils/'
import type { SessionUser } from '@/types/api'
import CourseCardOverlay from '@/components/CourseCardOverlay.vue'
import CourseOutline from '@/components/CourseOutline.vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import CourseReviews from '@/components/CourseReviews.vue'
import CourseInstructors from '@/components/CourseInstructors.vue'
import CourseCreatorCard from '@/components/CourseCreatorCard.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import RelatedCourses from '@/components/RelatedCourses.vue'
import { getLmsRoute, getSignupUrl } from '@/utils/basePath'
import type { CourseDetails, OutlineChapter, Resource } from '@/types/api'

const props = defineProps<{
	course: Resource<CourseDetails | null>
}>()

const user = inject<SessionUser>('$user')

const signupUrl = computed(() =>
	getSignupUrl(getLmsRoute(`billing/course/${props.course.data?.name || ''}`)),
)

const isKannadaShowcase = computed(
	() => props.course.data?.name === 'kannada-for-everyday-conversations',
)

const kannadaSeoTitle = 'Start Speaking Kannada for Everyday Conversations'
const kannadaSeoDescription =
	'Learn practical Kannada to communicate more comfortably at work, while travelling, and in everyday situations through a structured, beginner-friendly course you can complete at your own pace.'

const heroEyebrow = computed(() => {
	if (props.course.data?.eyebrow_text) return props.course.data.eyebrow_text
	if (isKannadaShowcase.value) return __('Online Kannada course')
	return __('Learn at your pace')
})

const heroTitle = computed(() =>
	isKannadaShowcase.value ? __(kannadaSeoTitle) : props.course.data?.title,
)

const heroIntroduction = computed(() => {
	if (isKannadaShowcase.value) {
		return __(kannadaSeoDescription)
	}
	return props.course.data?.short_introduction || ''
})

const courseContentTitle = computed(() =>
	isKannadaShowcase.value
		? __('A clear path from basics to conversation.')
		: __('Course content'),
)

const trustBadgesList = computed<string[]>(() => {
	if (props.course.data?.trust_badges) {
		return props.course.data.trust_badges.split(',').map((s: string) => s.trim()).filter(Boolean)
	}
	if (isKannadaShowcase.value) {
		return [__('1:1 personal coaching'), __('Native language coaches'), __('Course certificate')]
	}
	return [__('1:1 personal coaching'), __('Native language coaches'), __('Course certificate')]
})

const featuresList = computed(() => {
	if (props.course.data?.course_highlights?.length) {
		return props.course.data.course_highlights
	}
	if (isKannadaShowcase.value) return kannadaFeatures
	return [
		{ title: __('Live sessions'), copy: __('Personal coaching with guided practice') },
		{ title: __('Structured path'), copy: __('Beginner-friendly lessons and exercises') },
		{ title: __('Study material'), copy: __('Downloadable notes and revision prompts') },
		{ title: __('Flexible access'), copy: __('Learn online from mobile or desktop') },
		{ title: __('Speaking focus'), copy: __('Roleplays for daily conversations') },
		{ title: __('Certificate'), copy: __('Complete the course and show progress') },
	]
})

const outcomesList = computed<string[]>(() => {
	if (props.course.data?.learning_outcomes?.length) {
		return props.course.data.learning_outcomes
	}
	if (isKannadaShowcase.value) return kannadaOutcomes
	return [
		__('Build practical confidence with structured lessons and real-world examples.'),
		__('Master key concepts through guided exercises and active repetition.'),
		__('Understand core workflows and apply them in daily scenarios.'),
		__('Earn a verifiable certificate of completion to showcase your achievement.'),
		__('Solve common problems quickly using practical frameworks and templates.'),
		__('Build a strong portfolio of real-world skills to accelerate your goals.'),
	]
})

const highlightsList = computed(() => {
	// If outcomesList is being shown, we keep highlightsList empty to avoid duplicate cards in the Learning Outcomes band
	if (outcomesList.value.length) return []
	if (isKannadaShowcase.value) return kannadaHighlights
	return [
		{ icon: Languages, title: __('Core Foundations'), copy: __('Learn essential rules, concepts, and structures from step one.') },
		{ icon: Files, title: __('Practical Examples'), copy: __('Practise real-world applications and solidify understanding.') },
		{ icon: MonitorPlay, title: __('Guided Learning'), copy: __('Follow step-by-step guidance designed for steady progress.') },
		{ icon: BookOpen, title: __('Revision & Mastery'), copy: __('Reinforce skills with prompts, exercises, and feedback.') },
	]
})

const targetAudienceList = computed(() => {
	if (isKannadaShowcase.value) {
		return [
			{ title: __('New Residents & Relocators'), desc: __('Professionals moving to Karnataka who want smooth daily communication.') },
			{ title: __('Working Professionals'), desc: __('IT, healthcare, and retail staff needing polite Kannada for workplace interactions.') },
			{ title: __('Language & Culture Enthusiasts'), desc: __('Learners looking to appreciate movies, literature, and local traditions.') },
			{ title: __('Everyday Conversationalists'), desc: __('Anyone who wants to chat naturally with drivers, vendors, and neighbors without hesitation.') },
		]
	}
	return [
		{ title: __('Beginner Learners'), desc: __('Those starting from scratch looking for clear, structured step-by-step guidance.') },
		{ title: __('Intermediate Practitioners'), desc: __('Learners who want to refine their fluency and eliminate common mistakes.') },
		{ title: __('Career-Oriented Professionals'), desc: __('Individuals seeking verifiable skills to enhance workplace opportunities.') },
	]
})

function getFeatureIcon(idx: number) {
	const icons = [MonitorPlay, BookOpen, CheckCircle2, Award, Files, Languages]
	return icons[idx % icons.length] || BookOpen
}

function getOutcomeIcon(idx: number) {
	const icons = [CheckCircle2, Languages, MonitorPlay, BookOpen, Sparkles, Award]
	return icons[idx % icons.length] || CheckCircle2
}

const testimonialsList = computed(() => {
	if (props.course.data?.testimonials?.length) {
		return props.course.data.testimonials
	}
	return []
})

const faqsList = computed(() => {
	if (props.course.data?.faqs?.length) {
		return props.course.data.faqs
	}
	if (isKannadaShowcase.value) return kannadaFaqs
	return [
		{
			question: __('Who is this course structured for?'),
			answer: __('This course is designed for both beginners and intermediate learners who want a structured, practical path to mastery with guided exercises.'),
		},
		{
			question: __('How do I access course materials and live sessions?'),
			answer: __('Once you enroll, you gain immediate access to all lesson chapters, study notes, and video modules directly from your dashboard.'),
		},
		{
			question: __('How does enrollment and payment work?'),
			answer: __('Click the enrollment button on this page, log into your account, and follow the simple checkout process to unlock immediate access.'),
		},
		{
			question: __('Will I receive a certificate when I finish?'),
			answer: __('Yes! Once you complete all lessons and required exercises, you can download your verifiable course certificate directly from the platform.'),
		},
	]
})

watchEffect(() => {
	if (typeof document === 'undefined' || !props.course.data) return

	const title = isKannadaShowcase.value ? kannadaSeoTitle : props.course.data.title
	const desc = isKannadaShowcase.value
		? kannadaSeoDescription
		: (props.course.data.short_introduction || props.course.data.description || '').replace(/<[^>]*>?/gm, '').slice(0, 300)

	document.title = `${title} | Bhasha.io`
	upsertMeta('description', desc)
	upsertMeta('og:title', `${title} | Bhasha.io`, 'property')
	upsertMeta('og:description', desc, 'property')
	upsertMeta('twitter:card', 'summary_large_image')
})

function upsertMeta(name: string, content: string, key = 'name') {
	let element = document.head.querySelector<HTMLMetaElement>(
		`meta[${key}="${name}"]`,
	)
	if (!element) {
		element = document.createElement('meta')
		element.setAttribute(key, name)
		document.head.appendChild(element)
	}
	element.setAttribute('content', content)
}

const kannadaFeatures = [
	{
		title: __('Live sessions'),
		copy: __('Personal coaching with guided practice'),
	},
	{
		title: __('Structured path'),
		copy: __('Beginner-friendly lessons and exercises'),
	},
	{
		title: __('Study material'),
		copy: __('Downloadable notes and revision prompts'),
	},
	{
		title: __('Flexible access'),
		copy: __('Learn online from mobile or desktop'),
	},
	{
		title: __('Speaking focus'),
		copy: __('Roleplays for daily conversations'),
	},
	{
		title: __('Certificate'),
		copy: __('Complete the course and show progress'),
	},
]

const kannadaOutcomes = [
	__('Introduce yourself and hold simple Kannada conversations with confidence.'),
	__('Understand common sentence patterns used in everyday speech.'),
	__('Ask questions, express needs, and respond naturally in routine situations.'),
	__('Build listening confidence through native pronunciation and repetition.'),
	__(
		'Use practical vocabulary for work, travel, shopping, food, and social settings.',
	),
	__('Navigate Karnataka confidently and connect naturally with local culture.'),
]

const kannadaHighlights = [
	{
		icon: Languages,
		title: __('Kannada foundations'),
		copy: __('Learn sounds, pronunciation, greetings, and simple sentence forms.'),
	},
	{
		icon: Files,
		title: __('Daily conversations'),
		copy: __('Practise home, work, food, directions, transport, and questions.'),
	},
	{
		icon: MonitorPlay,
		title: __('Native listening'),
		copy: __('Use guided repetition and examples to recognise natural speech.'),
	},
	{
		icon: BookOpen,
		title: __('Confident speaking'),
		copy: __('Use roleplays, correction, and revision to speak more naturally.'),
	},
]

const kannadaFaqs = [
	{
		question: __('Will I be able to speak Kannada fluently after this course?'),
		answer: __(
			'You will build practical speaking confidence for common situations. Fluency depends on practice, but the course gives you a structured base and live correction.',
		),
	},
	{
		question: __('Is this course beginner friendly?'),
		answer: __(
			'Yes. It starts with pronunciation, basic phrases, and simple sentence patterns.',
		),
	},
	{
		question: __('How does payment work?'),
		answer: __(
			'Click the enrolment button, log in or create an account, and you will be taken directly to the LMS billing page for payment.',
		),
	},
	{
		question: __('What happens after payment?'),
		answer: __(
			'The LMS marks your payment and gives your account access to the course automatically.',
		),
	},
]

const isCourseInstructor = computed<boolean>(() =>
	(props.course.data?.instructors || []).some(
		(i) => i.name === user?.data?.name,
	),
)

const isCourseAdmin = computed<boolean>(
	() => Boolean(user?.data?.is_moderator) || isCourseInstructor.value,
)

const outline = createResource({
	url: 'lms.lms.utils.get_course_outline',
	cache: ['course_outline', props.course.data?.name],
	makeParams() {
		return { course: props.course.data?.name, progress: false }
	},
	auto: false,
}) as Resource<OutlineChapter[]>

watch(
	() => props.course.data?.name,
	(courseName) => {
		if (courseName) outline.reload()
	},
	{ immediate: true },
)

const outlineStats = computed(() => {
	const chapters = outline.data || []
	const lessonCount = chapters.reduce(
		(acc, c) => acc + (c.lessons?.length || 0),
		0,
	)
	const parts: string[] = []
	if (chapters.length) {
		parts.push(
			`${chapters.length} ${
				chapters.length === 1 ? __('section') : __('sections')
			}`,
		)
	}
	if (lessonCount) {
		parts.push(
			`${lessonCount} ${lessonCount === 1 ? __('lesson') : __('lessons')}`,
		)
	}
	return parts.join(' · ')
})

const hasCourseContent = computed(() => {
	const chapters = outline.data || []
	const lessonCount = chapters.reduce(
		(acc, c) => acc + (c.lessons?.length || 0),
		0,
	)
	return chapters.length > 0 && lessonCount > 0
})
</script>
