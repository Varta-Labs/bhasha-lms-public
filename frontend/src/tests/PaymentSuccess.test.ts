import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { enableAutoUnmount, flushPromises, mount } from '@vue/test-utils'
import { reactive } from 'vue'
import PaymentSuccess from '@/pages/PaymentSuccess.vue'

const { fetchStatus, removePurchased } = vi.hoisted(() => ({
	fetchStatus: vi.fn(),
	removePurchased: vi.fn(),
}))
vi.mock('@/stores/cart', () => ({ useCart: () => ({ removePurchased }) }))
vi.mock('@/stores/session', () => ({ sessionStore: () => ({ brand: {} }) }))
vi.mock('frappe-ui', () => ({
	usePageMeta: vi.fn(),
	createResource: (options: any) => {
		const resource = reactive({
			data: null as any,
			loading: false,
			async submit() {
				resource.loading = true
				try {
					resource.data = await fetchStatus(options.makeParams())
					options.onSuccess(resource.data)
				} catch (error) {
					options.onError(error)
					throw error
				} finally {
					resource.loading = false
				}
			},
		})
		return resource
	},
}))

enableAutoUnmount(afterEach)

const pending = { status: 'Pending', courses: [] }
const paid = {
	status: 'Paid',
	courses: [
		{ course: 'main', title: 'Main course' },
		{ course: 'addon', title: 'Addons pack' },
	],
}
const showPage = () =>
	mount(PaymentSuccess, {
		props: { type: 'order', name: 'order-reference' },
		global: {
			mocks: { __: (text: string) => text },
			stubs: { RouterLink: { template: '<a><slot /></a>' } },
		},
	})

describe('cart payment confirmation', () => {
	beforeEach(() => {
		vi.useFakeTimers()
		vi.stubGlobal('__', (text: string) => text)
		fetchStatus.mockReset().mockResolvedValue(pending)
		removePurchased.mockReset()
	})
	afterEach(() => {
		vi.clearAllTimers()
		vi.useRealTimers()
		vi.unstubAllGlobals()
	})

	it('waits for confirmation, then shows purchased courses and stops polling', async () => {
		fetchStatus.mockResolvedValueOnce(pending).mockResolvedValueOnce(paid)
		const page = showPage()
		await flushPromises()
		expect(page.text()).toContain('Confirming your payment')
		expect(page.text()).not.toContain('Payment confirmed')
		expect(removePurchased).not.toHaveBeenCalled()
		await vi.advanceTimersByTimeAsync(3000)
		expect(page.text()).toContain('Your courses are ready')
		expect(page.text()).toContain('Addons pack')
		expect(removePurchased).toHaveBeenCalledWith(['main', 'addon'])
		await vi.advanceTimersByTimeAsync(60000)
		expect(fetchStatus).toHaveBeenCalledTimes(2)
	})

	it('lets a learner restart checks after automatic polling expires', async () => {
		const page = showPage()
		await flushPromises()
		await vi.advanceTimersByTimeAsync(60000)
		expect(fetchStatus).toHaveBeenCalledTimes(20)
		expect(page.text()).toContain('Payment confirmation is taking longer')
		expect(page.text()).toContain('You do not need to pay again.')
		expect(page.text()).toContain('order-reference')
		await page.get('button').trigger('click')
		await flushPromises()
		expect(page.text()).toContain('Confirming your payment')
		fetchStatus.mockResolvedValue(paid)
		await vi.advanceTimersByTimeAsync(3000)
		expect(page.text()).toContain('Your courses are ready')
	})

	it('shows a verification error and allows a successful retry', async () => {
		fetchStatus.mockRejectedValueOnce(new Error('Verification unavailable'))
		const page = showPage()
		await flushPromises()
		expect(page.text()).toContain('Unable to check this order')
		expect(page.text()).toContain('Verification unavailable')
		expect(removePurchased).not.toHaveBeenCalled()
		fetchStatus.mockResolvedValue(paid)
		await page.get('button').trigger('click')
		await flushPromises()
		expect(page.text()).toContain('Your courses are ready')
	})

	it('clears the previous timer when the learner checks manually', async () => {
		const page = showPage()
		await flushPromises()
		await vi.advanceTimersByTimeAsync(1000)
		await page.get('button').trigger('click')
		await flushPromises()
		await vi.advanceTimersByTimeAsync(2000)
		expect(fetchStatus).toHaveBeenCalledTimes(2)
		await vi.advanceTimersByTimeAsync(1000)
		expect(fetchStatus).toHaveBeenCalledTimes(3)
	})

	it('does not schedule polling when an in-flight request finishes after leaving', async () => {
		let resolve: (value: any) => void = () => {}
		fetchStatus.mockReturnValueOnce(
			new Promise((done) => {
				resolve = done
			}),
		)
		const page = showPage()
		page.unmount()
		resolve(pending)
		await flushPromises()
		await vi.advanceTimersByTimeAsync(60000)
		expect(fetchStatus).toHaveBeenCalledTimes(1)
	})
})
