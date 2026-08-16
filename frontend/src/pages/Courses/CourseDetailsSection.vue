<template>
	<section class="course-settings-section space-y-5">
		<div class="course-settings-section__heading">
			<div class="course-settings-section__icon">
				<BookOpenText class="size-5 stroke-[1.7]" />
			</div>
			<div>
				<h3>{{ __('Course details') }}</h3>
				<p>
					{{
						__('The essentials learners see when they discover this course.')
					}}
				</p>
			</div>
		</div>
		<div class="course-settings-fields grid grid-cols-2 gap-5">
			<FormControl
				v-model="doc.title"
				:label="__('Title')"
				:required="true"
				variant="outline"
				@input="markDirty()"
			/>
			<Link
				v-model="doc.category"
				doctype="LMS Category"
				:label="__('Category')"
				:placeholder="__('Select category')"
				:inlineCreate="true"
				inlineCreatePlaceholder="Category name"
				:onCreate="createCategory"
				variant="outline"
				@update:modelValue="markDirty()"
			/>
			<CourseInstructorsField />
			<div class="space-y-1.5">
				<FormLabel :label="__('Tags')" />
				<MultiSelect
					v-model="tagsArray"
					:options="tagOptions"
					:placeholder="__('Add tag')"
					variant="outline"
					class="w-full justify-between"
					@update:query="tagQuery = $event"
				>
					<template #trigger="{ open, toggleOpen, selectedOptions }">
						<button
							type="button"
							:class="[
								'relative inline-flex w-full min-h-7 items-center gap-2 rounded border border-outline-gray-2 bg-surface-white px-2 text-left text-base text-ink-gray-8 outline-none transition-colors hover:border-outline-gray-3 hover:shadow-sm focus:border-outline-gray-4 focus:shadow-sm focus-visible:ring-2 ring-outline-gray-3',
								open && 'border-outline-gray-4 shadow-sm ring-2',
							]"
							@click="toggleOpen"
						>
							<Tag class="size-4 shrink-0 stroke-1.5 text-ink-gray-5" />
							<span
								class="min-w-0 flex-1 truncate"
								:class="!selectedOptions.length && 'text-ink-gray-4'"
							>
								<template v-if="tagsArray.length">{{
									tagsSelectedLabels
								}}</template>
								<template v-else>{{ __('Add tag') }}</template>
							</span>
							<ChevronDown
								class="size-4 shrink-0 text-ink-gray-4 transition-transform duration-200"
								:class="open && 'rotate-180'"
							/>
						</button>
					</template>
				</MultiSelect>
			</div>
			<FormControl
				v-model="doc.short_introduction"
				type="textarea"
				:rows="3"
				:label="__('Short description')"
				:placeholder="__('Type something')"
				:required="true"
				variant="outline"
				class="col-span-2"
				@change="markDirty()"
			/>
		</div>
		<CourseThumbnailField />
	</section>
</template>

<script setup lang="ts">
import { FormControl, FormLabel, MultiSelect } from 'frappe-ui'
import { BookOpenText, ChevronDown, Tag } from 'lucide-vue-next'
import { computed, inject, ref } from 'vue'
import { createLMSCategory } from '@/utils'
import Link from '@/components/Controls/Link.vue'
import CourseInstructorsField from '@/pages/Courses/CourseInstructorsField.vue'
import CourseThumbnailField from '@/pages/Courses/CourseThumbnailField.vue'
import type { CourseFormContext } from '@/types/api'

interface TagOption {
	label: string
	value: string
}

const { resource, markDirty } = inject<CourseFormContext>('courseForm')!

const doc = computed(() => resource.doc)

const parsedTags = computed<string[]>(() => {
	const tags = resource.doc?.tags
	return tags ? tags.split(', ').filter(Boolean) : []
})

const tagsArray = computed<string[]>({
	get: () => parsedTags.value,
	set: (vals: string[]) => {
		if (!resource.doc) return
		resource.doc.tags = vals.join(', ')
		markDirty()
	},
})

const tagQuery = ref<string>('')
const tagOptions = computed<TagOption[]>(() => {
	const selected: TagOption[] = parsedTags.value.map((t) => ({
		label: t,
		value: t,
	}))
	const q = tagQuery.value.trim()
	if (q && !parsedTags.value.includes(q)) {
		return [...selected, { label: `${__('Create')} "${q}"`, value: q }]
	}
	return selected
})

const tagsSelectedLabels = computed<string>(() => tagsArray.value.join(', '))

function createCategory(name: string, done?: () => void) {
	if (!name) return
	createLMSCategory(name).then((categoryName: string | undefined) => {
		if (!categoryName || !resource.doc) return
		resource.doc.category = categoryName
		done?.()
		markDirty()
	})
}
</script>

<style scoped>
.course-settings-section__heading {
	display: flex;
	align-items: center;
	gap: 0.85rem;
}

.course-settings-section__icon {
	display: grid;
	width: 2.75rem;
	height: 2.75rem;
	flex: none;
	place-items: center;
	border-radius: 0.8rem;
	background: rgba(108, 92, 231, 0.1);
	color: #6c5ce7;
}

.course-settings-section__heading h3 {
	color: #27222e;
	font-family: var(--bhasha-font-display);
	font-size: 1.1rem;
	font-weight: 700;
}

.course-settings-section__heading p {
	margin-top: 0.15rem;
	color: #7c7c7c;
	font-size: 0.75rem;
	line-height: 1.5;
}

@media (max-width: 639px) {
	.course-settings-fields {
		grid-template-columns: minmax(0, 1fr);
	}

	.course-settings-fields > :deep(.col-span-2) {
		grid-column: auto;
	}
}
</style>
