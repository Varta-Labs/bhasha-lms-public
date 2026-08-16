<template>
	<Dialog
		v-model="show"
		:options="{
			title: props.page ? __('Edit sidebar page') : __('Add a page to More'),
			size: 'lg',
			actions: [
				{
					label: props.page ? __('Save page') : __('Add to sidebar'),
					variant: 'solid',
					disabled: !page.webpage,
					onClick: (close) => {
						addWebPage(close)
					},
				},
			],
		}"
	>
		<template #body-content>
			<div class="bhasha-form-intro">
				<div class="bhasha-form-intro__icon">
					<PanelLeftDashed class="size-5 stroke-[1.7]" />
				</div>
				<div>
					<h4>{{ __('Create a useful shortcut') }}</h4>
					<p>
						{{
							__(
								'Choose a published page and an icon. It will appear inside the More section for everyone who can access it.',
							)
						}}
					</p>
				</div>
			</div>
			<div class="bhasha-form-stack text-base">
				<Link
					v-model="page.webpage"
					doctype="Web Page"
					:label="__('Web Page')"
					:placeholder="__('Choose a published page')"
					:filters="{
						published: 1,
					}"
				/>
				<IconPicker v-model="page.icon" :label="__('Icon')" />
			</div>
		</template>
	</Dialog>
</template>
<script setup>
import { Dialog, createResource, toast } from 'frappe-ui'
import Link from '@/components/Controls/Link.vue'
import { reactive, watch } from 'vue'
import IconPicker from '@/components/Controls/IconPicker.vue'
import { PanelLeftDashed } from 'lucide-vue-next'

const sidebar = defineModel('reloadSidebar')
const show = defineModel()
const page = reactive({
	icon: '',
	webpage: '',
})

const props = defineProps({
	page: {
		type: Object,
		default: null,
	},
})

const webPage = createResource({
	url: 'lms.lms.api.update_sidebar_item',
	makeParams(values) {
		return {
			webpage: page.webpage,
			icon: page.icon,
		}
	},
})

watch(
	() => props.page,
	(newPage) => {
		if (newPage) {
			page.icon = newPage.icon
			page.webpage = newPage.web_page
		}
	},
	{ immediate: true },
)

const addWebPage = (close) => {
	webPage.submit(
		{},
		{
			onSuccess() {
				sidebar.value.reload()
				close()
				toast.success(
					props.page
						? __('Sidebar page updated')
						: __('Web page added to sidebar'),
				)
			},
			onError(err) {
				toast.error(err.message[0] || err)
				close()
			},
		},
	)
}
</script>
