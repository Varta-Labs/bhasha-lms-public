<template>
	<section class="bundle-offer">
		<header class="bundle-offer__header">
			<div class="bundle-offer__course-row">
				<router-link
					:to="{ name: 'CourseDetail', params: { courseName: course.course } }"
					class="bundle-offer__thumbnail"
					:aria-label="course.title"
				>
					<img v-if="course.image" :src="course.image" alt="" loading="lazy" />
					<BookOpen v-else class="size-8" aria-hidden="true" />
				</router-link>
				<div class="bundle-offer__course-copy">
					<p class="bundle-offer__eyebrow">{{ __('Your video course') }}</p>
					<router-link
						:to="{
							name: 'CourseDetail',
							params: { courseName: course.course },
						}"
						class="bundle-offer__course"
						>{{ course.title }}</router-link
					>
					<div class="bundle-offer__course-price">
						<strong>{{ course.amount_formatted }}</strong>
						<template
							v-if="
								course.currency === 'INR' && course.original_amount === 2499
							"
						>
							<s>₹4,999</s><span>{{ __('50% off') }}</span>
						</template>
					</div>
					<button
						type="button"
						class="bundle-offer__remove"
						@click="$emit('remove-course')"
					>
						{{ __('Remove course') }}
					</button>
				</div>
			</div>
			<span class="bundle-offer__badge">{{ __('Bundle offer') }}</span>
		</header>
		<div class="bundle-offer__pack">
			<div class="bundle-offer__pack-heading">
				<router-link
					:to="{ name: 'CourseDetail', params: { courseName: pack.course } }"
					class="bundle-offer__thumbnail"
					:aria-label="pack.title"
				>
					<img v-if="pack.image" :src="pack.image" alt="" loading="lazy" />
					<BookOpen v-else class="size-6" aria-hidden="true" />
				</router-link>
				<div>
					<h2>{{ __('Complete your learning with the Add-ons Pack') }}</h2>
					<router-link
						:to="{ name: 'CourseDetail', params: { courseName: pack.course } }"
						class="bundle-offer__pack-title"
						>{{ pack.title }}</router-link
					>
				</div>
			</div>
			<p class="bundle-offer__description">{{ pack.short_introduction }}</p>
			<p v-if="pack.discount_amount" class="bundle-offer__regular">
				{{ __('Regular price') }} <s>{{ pack.original_amount_formatted }}</s>
			</p>
			<strong class="bundle-offer__price">{{ pack.amount_formatted }}</strong>
			<p v-if="pack.discount_amount" class="bundle-offer__saving">
				{{ __('Save') }} {{ pack.discount_amount_formatted }} ({{
					discountPercent
				}}% {{ __('off') }})
			</p>
			<label class="bundle-offer__toggle">
				<input
					type="checkbox"
					:checked="selected"
					:disabled="loading"
					@change="$emit('toggle-pack')"
				/>
				<span>{{ __('Add the Add-ons Pack to my course') }}</span>
			</label>
		</div>
		<footer class="bundle-offer__total" aria-live="polite">
			<span>{{ __('Course total') }}</span>
			<strong>{{ total }}</strong>
			<small>{{ __('Before any applicable tax') }}</small>
		</footer>
	</section>
</template>

<script setup>
import { computed } from 'vue'
import { BookOpen } from 'lucide-vue-next'

const props = defineProps({
	course: { type: Object, required: true },
	pack: { type: Object, required: true },
	selected: Boolean,
	loading: Boolean,
})
defineEmits(['toggle-pack', 'remove-course'])
const discountPercent = computed(() =>
	Math.round((props.pack.discount_amount / props.pack.original_amount) * 100),
)
const total = computed(() =>
	new Intl.NumberFormat('en-IN', {
		style: 'currency',
		currency: props.course.currency,
		maximumFractionDigits: 2,
		minimumFractionDigits: 0,
	}).format(props.course.amount + (props.selected ? props.pack.amount : 0)),
)
</script>

<style scoped>
.bundle-offer {
	overflow: hidden;
	padding: clamp(1.25rem, 3vw, 2rem);
	border: 1px solid rgba(108, 92, 231, 0.22);
	border-radius: 1.5rem;
	background: rgba(255, 255, 255, 0.96);
	box-shadow: 0 18px 48px -28px rgba(74, 47, 25, 0.3);
	color: #171717;
}
.bundle-offer__header {
	display: flex;
	justify-content: space-between;
	align-items: flex-start;
	gap: 1rem;
	padding-bottom: 1.5rem;
}
.bundle-offer__course-row {
	display: grid;
	grid-template-columns: 8rem minmax(0, 1fr);
	align-items: start;
	gap: 1rem;
	min-width: 0;
	width: 100%;
}
.bundle-offer__course-copy {
	min-width: 0;
}
.bundle-offer__thumbnail {
	display: grid;
	place-items: center;
	overflow: hidden;
	aspect-ratio: 16 / 9;
	border-radius: 0.75rem;
	background: #f0edff;
	color: #6c5ce7;
}
.bundle-offer__thumbnail img {
	display: block;
	width: 100%;
	height: auto;
}
.bundle-offer__pack-heading {
	display: grid;
	grid-template-columns: 6rem minmax(0, 1fr);
	align-items: start;
	gap: 1rem;
}
.bundle-offer__eyebrow {
	margin-bottom: 0.5rem;
	color: #625d68;
	font-size: 0.75rem;
	font-weight: 700;
	letter-spacing: 0.06em;
	text-transform: uppercase;
}
.bundle-offer__course {
	font-weight: 700;
	line-height: 1.5;
}
.bundle-offer__course-price {
	display: flex;
	align-items: baseline;
	flex-wrap: wrap;
	gap: 0.6rem;
	margin-top: 0.5rem;
}
.bundle-offer__course-price strong {
	font-size: 1.75rem;
	letter-spacing: -0.03em;
}
.bundle-offer__course-price s,
.bundle-offer__regular {
	color: #625d68;
	font-size: 0.875rem;
}
.bundle-offer__course-price span {
	color: #4a38c2;
	font-size: 0.75rem;
	font-weight: 700;
}
.bundle-offer__badge {
	flex-shrink: 0;
	padding: 0.4rem 0.75rem;
	border-radius: 9999px;
	background: #f0edff;
	color: #4a38c2;
	font-size: 0.75rem;
	font-weight: 800;
}
.bundle-offer__remove {
	margin-top: 0.75rem;
	color: #625d68;
	font-size: 0.75rem;
	text-decoration: underline;
	text-underline-offset: 0.2rem;
}
.bundle-offer__pack {
	padding-block: 1.5rem;
	border-block: 1px solid #ede9f2;
}
.bundle-offer__pack h2 {
	margin-bottom: 0.75rem;
	font-family: var(--bhasha-font-display);
	font-size: 1.25rem;
	font-weight: 800;
	line-height: 1.4;
}
.bundle-offer__pack-title {
	color: #4a38c2;
	font-size: 0.875rem;
	font-weight: 700;
}
.bundle-offer__description {
	margin-top: 0.5rem;
	color: #625d68;
	font-size: 0.875rem;
	line-height: 1.7;
}
.bundle-offer__regular {
	margin-top: 1.25rem;
}
.bundle-offer__price {
	display: block;
	margin-top: 0.5rem;
	font-size: 2.25rem;
	font-weight: 800;
	letter-spacing: -0.03em;
}
.bundle-offer__saving {
	margin-top: 0.5rem;
	color: #4a38c2;
	font-size: 0.9375rem;
	font-weight: 700;
}
.bundle-offer__toggle {
	display: flex;
	align-items: center;
	gap: 0.75rem;
	margin-top: 1.5rem;
	cursor: pointer;
	font-size: 0.9375rem;
	font-weight: 600;
	line-height: 1.5;
}
.bundle-offer__toggle input {
	flex: none;
	width: 1.4rem;
	height: 1.4rem;
	min-height: 0;
	accent-color: #6c5ce7;
	cursor: pointer;
}
.bundle-offer__toggle input:disabled {
	cursor: wait;
}
.bundle-offer__total {
	display: flex;
	align-items: baseline;
	justify-content: space-between;
	gap: 0.5rem 1rem;
	flex-wrap: wrap;
	padding-top: 1.5rem;
	font-weight: 800;
}
.bundle-offer__total strong {
	font-size: 1.75rem;
	letter-spacing: -0.03em;
}
.bundle-offer__total small {
	width: 100%;
	color: #625d68;
	font-size: 0.75rem;
	font-weight: 400;
}
.bundle-offer a:hover,
.bundle-offer__remove:hover {
	color: #4a38c2;
}
.bundle-offer a:focus-visible,
.bundle-offer button:focus-visible,
.bundle-offer input:focus-visible {
	outline: 3px solid rgba(108, 92, 231, 0.45);
	outline-offset: 4px;
}
@media (max-width: 479px) {
	.bundle-offer__course-row {
		grid-template-columns: minmax(0, 1fr);
	}
	.bundle-offer__course-copy {
		overflow-wrap: anywhere;
	}
	.bundle-offer__header {
		flex-direction: column-reverse;
	}
}
</style>
