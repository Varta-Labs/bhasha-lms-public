<template>
	<button
		v-if="link && !link.onlyMobile"
		class="bhasha-sidebar-link flex h-9 w-full cursor-pointer items-center text-ink-gray-8 duration-200 ease-in-out focus:outline-none focus:transition-none"
		:class="isActive ? 'bhasha-sidebar-active' : ''"
		@click="handleClick"
	>
		<div
			class="flex items-center w-full duration-300 ease-in-out group"
			:class="isCollapsed ? 'relative p-1' : 'px-2 py-1'"
		>
			<Tooltip :text="__(link.label)" placement="right">
				<slot name="icon">
					<span class="grid h-5 w-6 flex-shrink-0 place-items-center">
						<component
							:is="icons[link.icon]"
							class="h-4 w-4 stroke-1.5"
							:class="isActive ? 'text-bhasha-accent' : 'text-ink-gray-8'"
						/>
					</span>
				</slot>
			</Tooltip>
			<span
				class="flex-shrink-0 text-sm duration-300 ease-in-out"
				:class="
					isCollapsed
						? 'ms-0 w-0 overflow-hidden opacity-0'
						: 'ms-2 w-auto opacity-100'
				"
			>
				{{ __(link.label) }}
			</span>
			<span
				v-if="link.count && !isCollapsed"
				class="!ms-auto block text-xs text-ink-gray-5"
				:class="
					isCollapsed && link.count > 9
						? 'absolute top-[2px] end-0 bg-surface-white'
						: ''
				"
			>
				{{ link.count }}
			</span>
			<div
				v-if="showControls && !isCollapsed"
				class="flex items-center gap-x-2 !ms-auto block text-xs text-ink-gray-5 group-hover:visible invisible"
			>
				<component
					:is="icons['Edit']"
					class="h-3 w-3 stroke-1.5 text-ink-gray-7"
					@click.stop="openModal(link)"
				/>
				<component
					:is="icons['X']"
					class="h-3 w-3 stroke-1.5 text-ink-gray-7"
					@click.stop="deletePage(link)"
				/>
			</div>
		</div>
	</button>
	<ContactUsEmail v-model="showContactForm" />
</template>
<script setup>
import { Tooltip } from 'frappe-ui'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import ContactUsEmail from '@/components/ContactUsEmail.vue'
import * as icons from 'lucide-vue-next'

const router = useRouter()
const emit = defineEmits(['openModal', 'deletePage'])
const showContactForm = ref(false)

const props = defineProps({
	link: {
		type: Object,
		required: true,
	},
	isCollapsed: {
		type: Boolean,
		default: false,
	},
	showControls: {
		type: Boolean,
		default: false,
	},
	activeTab: {
		type: String,
		default: '',
	},
})

function handleClick() {
	if (router.hasRoute(props.link.to)) {
		router.push({ name: props.link.to })
	} else if (props.link.to?.includes('@')) {
		showContactForm.value = true
	} else if (props.link.to) {
		if (props.link.to.startsWith('http')) {
			window.open(props.link.to, '_blank')
			return
		}
		window.location.href = `/${props.link.to}`
	}
}

const isActive = computed(() => {
	const currentRouteName = router.currentRoute.value.name
	return (
		props.link?.to === currentRouteName ||
		props.link?.activeFor?.includes(currentRouteName) ||
		(props.activeTab && props.link?.label?.includes(props.activeTab))
	)
})

const openModal = (link) => {
	emit('openModal', link)
}

const deletePage = (link) => {
	emit('deletePage', link)
}
</script>
