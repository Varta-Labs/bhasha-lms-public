<template>
	<Dialog
		v-model="show"
		:options="{
			title: __('Remove from course'),
			size: 'lg',
		}"
	>
		<template #body-content>
			<div class="space-y-4 text-base text-ink-gray-7">
				<p>
					{{
						__('{0} will lose access to {1} straight away.').format(
							student.member_name || student.member,
							course.data?.title,
						)
					}}
				</p>
				<FormControl
					type="checkbox"
					:label="__('Record a refund')"
					v-model="refunded"
				/>
				<template v-if="refunded">
					<p class="text-sm text-ink-gray-5">
						{{
							__(
								'Issue the refund in Razorpay first. Recording it here stops their original payment from unlocking this course again.',
							)
						}}
					</p>
					<FormControl
						:label="__('Razorpay refund ID (optional)')"
						placeholder="rfnd_..."
						v-model="refundReference"
					/>
				</template>
			</div>
		</template>
		<template #actions="{ close }">
			<div class="flex justify-end gap-2">
				<Button @click="close">{{ __('Cancel') }}</Button>
				<Button
					variant="solid"
					theme="red"
					:loading="removing"
					@click="removeStudent(close)"
				>
					{{ __('Remove student') }}
				</Button>
			</div>
		</template>
	</Dialog>
</template>
<script setup lang="ts">
import { Button, call, Dialog, FormControl, toast } from 'frappe-ui'
import { ref } from 'vue'

const show = defineModel<boolean>({ required: true, default: false })
const emit = defineEmits<{ removed: [] }>()

const props = defineProps<{
	course: any
	student: any
}>()

const refunded = ref<boolean>(false)
const refundReference = ref<string>('')
const removing = ref<boolean>(false)

const removeStudent = (close: () => void) => {
	if (removing.value) return
	removing.value = true
	const withRefund = refunded.value
	call('lms.lms.cart.remove_course_enrollment', {
		enrollment: props.student.name,
		refunded: withRefund ? 1 : 0,
		refund_reference: withRefund ? refundReference.value : null,
	})
		.then(() => {
			toast.success(
				withRefund
					? __('Student removed and refund recorded')
					: __('Student removed from course'),
			)
			emit('removed')
			close()
		})
		.catch((err: any) => {
			toast.error(__(err.messages?.[0] || err))
			console.error(err)
		})
		.finally(() => {
			removing.value = false
		})
}
</script>
