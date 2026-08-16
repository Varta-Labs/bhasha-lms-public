<template>
	<section class="course-settings-section space-y-5 border-t pt-6">
		<div class="course-settings-section__heading">
			<div class="course-settings-section__icon">
				<LayoutTemplate class="size-5 stroke-[1.7]" />
			</div>
			<div>
				<h3>{{ __('Course overview') }}</h3>
				<p>
					{{
						__('Give learners a clear picture of what they will experience.')
					}}
				</p>
			</div>
		</div>
		<FormControl
			v-model="doc.video_link"
			:label="__('Embed (preview video)')"
			:description="__('Supports YouTube and Vimeo.')"
			:placeholder="__('e.g. https://www.youtube.com/video')"
			variant="outline"
			@input="markDirty()"
		/>
		<div class="space-y-1.5">
			<FormLabel
				:label="__('Course Description')"
				:id="descriptionId"
				:required="true"
			/>
			<div
				class="rounded-t-lg rounded-b-md outline-none transition-[box-shadow] duration-150 ease-[cubic-bezier(0.23,1,0.32,1)] focus-within:ring-2 ring-outline-gray-3"
			>
				<TextEditor
					:id="descriptionId"
					:content="doc.description"
					@change="
						(val) => {
							doc.description = val
							markDirty()
						}
					"
					:editable="true"
					:fixedMenu="true"
					editorClass="prose-sm max-w-none border-b border-x border-outline-gray-2 hover:border-outline-gray-3 hover:shadow-sm focus-within:border-outline-gray-4 focus-within:shadow-sm rounded-b-md py-1 px-2 min-h-[7rem] transition-colors"
				/>
			</div>
		</div>
		<MultiLink
			v-model="relatedCourses"
			doctype="LMS Course"
			:filters="{ name: ['!=', resource.doc?.name] }"
			:label="__('Related Courses')"
			:placeholder="__('Select related courses')"
			variant="outline"
			:onCreate="goToCreateCourse"
			@update:modelValue="markDirty()"
		/>
	</section>

	<section class="course-settings-section space-y-5 border-t pt-6">
		<div class="course-settings-section__heading">
			<div class="course-settings-section__icon">
				<SearchCheck class="size-5 stroke-[1.7]" />
			</div>
			<div>
				<h3>{{ __('Search appearance') }}</h3>
				<div class="mt-1 text-p-sm text-ink-gray-6">
					{{
						__(
							'These tags help search engines describe and rank your course in results.',
						)
					}}
				</div>
			</div>
		</div>
		<FormControl
			v-model="meta.description"
			:label="__('Meta description')"
			type="textarea"
			:rows="4"
			:placeholder="__('A short summary of the course for search results.')"
			variant="outline"
			@input="markDirty()"
		/>
		<FormControl
			v-model="meta.keywords"
			:label="__('Meta keywords')"
			type="textarea"
			:rows="4"
			:placeholder="__('Comma separated keywords for SEO')"
			variant="outline"
			@input="markDirty()"
		/>
	</section>
</template>

<script setup lang="ts">
import { TextEditor, FormControl, FormLabel } from 'frappe-ui'
import { computed, inject, useId } from 'vue'
import { useRouter } from 'vue-router'
import MultiLink from '@/components/Controls/MultiLink.vue'
import type { CourseFormContext } from '@/types/api'
import { LayoutTemplate, SearchCheck } from 'lucide-vue-next'

const { resource, relatedCourses, meta, markDirty } =
	inject<CourseFormContext>('courseForm')!
const router = useRouter()
const doc = computed(() => resource.doc)
const descriptionId = useId()

function goToCreateCourse(close: () => void) {
	close()
	router.push({ name: 'Courses', query: { newCourse: '1' } })
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

.course-settings-section__heading p,
.course-settings-section__heading .text-p-sm {
	color: #7c7c7c;
	font-size: 0.75rem;
	line-height: 1.5;
}
</style>
