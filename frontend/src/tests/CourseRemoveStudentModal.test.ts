import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { enableAutoUnmount, flushPromises, mount } from '@vue/test-utils'
import CourseRemoveStudentModal from '@/pages/Courses/CourseRemoveStudentModal.vue'

const { call, toast } = vi.hoisted(() => ({
	call: vi.fn(),
	toast: { success: vi.fn(), error: vi.fn() },
}))
vi.mock('frappe-ui', () => ({
	call,
	toast,
	Dialog: {
		template:
			'<div><slot name="body-content" /><slot name="actions" :close="close" /></div>',
		methods: { close() {} },
	},
	Button: {
		emits: ['click'],
		template: '<button @click="$emit(\'click\')"><slot /></button>',
	},
	FormControl: {
		props: ['modelValue', 'type', 'label'],
		emits: ['update:modelValue'],
		template: `<label>{{ label }}<input v-if="type == 'checkbox'" type="checkbox" :checked="modelValue" @change="$emit('update:modelValue', $event.target.checked)" />
			<input v-else :value="modelValue" @input="$emit('update:modelValue', $event.target.value)" /></label>`,
	},
}))

enableAutoUnmount(afterEach)

const format = function (this: string, ...values: unknown[]) {
	return this.replace(/{(\d+)}/g, (_, index) => String(values[Number(index)]))
}

const showModal = () =>
	mount(CourseRemoveStudentModal, {
		props: {
			modelValue: true,
			course: { data: { name: 'hindi', title: 'Hindi for Beginners' } },
			student: { name: 'enr-1', member: 'learner@example.com', member_name: 'Asha' },
		},
		global: { mocks: { __: (text: string) => text } },
	})

const removeButton = (modal: ReturnType<typeof showModal>) =>
	modal.findAll('button').find((button) => button.text() == 'Remove student')!

describe('removing a student from a course', () => {
	beforeEach(() => {
		vi.stubGlobal('__', (text: string) => text)
		Object.defineProperty(String.prototype, 'format', { value: format, configurable: true })
		call.mockReset().mockResolvedValue({ refunded: false })
		toast.success.mockReset()
		toast.error.mockReset()
	})
	afterEach(() => {
		vi.unstubAllGlobals()
	})

	it('removes without recording a refund by default', async () => {
		const modal = showModal()
		expect(modal.text()).toContain('Asha will lose access to Hindi for Beginners')
		expect(
			(modal.find('input[type="checkbox"]').element as HTMLInputElement).checked,
		).toBe(false)
		expect(modal.text()).not.toContain('Razorpay refund ID')
		await removeButton(modal).trigger('click')
		await flushPromises()
		expect(call).toHaveBeenCalledWith('lms.lms.cart.remove_course_enrollment', {
			enrollment: 'enr-1',
			refunded: 0,
			refund_reference: null,
		})
		expect(modal.emitted('removed')).toHaveLength(1)
		expect(toast.success).toHaveBeenCalledWith('Student removed from course')
	})

	it('records a refund with its Razorpay reference when ticked', async () => {
		call.mockResolvedValueOnce({ refunded: true })
		const modal = showModal()
		await modal.find('input[type="checkbox"]').setValue(true)
		await modal.findAll('input')[1].setValue('rfnd_123')
		await removeButton(modal).trigger('click')
		await flushPromises()
		expect(call).toHaveBeenCalledWith('lms.lms.cart.remove_course_enrollment', {
			enrollment: 'enr-1',
			refunded: 1,
			refund_reference: 'rfnd_123',
		})
		expect(toast.success).toHaveBeenCalledWith('Student removed and refund recorded')
	})

	it('keeps the dialog open and shows the server error', async () => {
		call.mockRejectedValueOnce({ messages: ['No paid, unrefunded purchase'] })
		vi.spyOn(console, 'error').mockImplementation(() => {})
		const modal = showModal()
		await modal.find('input[type="checkbox"]').setValue(true)
		await removeButton(modal).trigger('click')
		await flushPromises()
		expect(toast.error).toHaveBeenCalledWith('No paid, unrefunded purchase')
		expect(modal.emitted('removed')).toBeUndefined()
	})
})
