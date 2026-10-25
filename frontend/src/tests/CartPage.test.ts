import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { enableAutoUnmount, flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { reactive } from 'vue'
import { useCart } from '@/stores/cart'
import Cart from '@/pages/Cart.vue'

const { fetchSummary } = vi.hoisted(() => ({ fetchSummary: vi.fn() }))
vi.mock('frappe-ui', () => ({
	usePageMeta: vi.fn(),
	Button: { template: '<button><slot /></button>' },
	FormControl: { template: '<input />' },
	createResource: (options: any) => {
		const resource = reactive({
			data: null as any,
			loading: false,
			async submit() {
				resource.loading = true
				resource.data = await fetchSummary(options.makeParams())
				options.onSuccess(resource.data)
				resource.loading = false
			},
		})
		return resource
	},
}))
vi.mock('vue-router', () => ({ useRouter: () => ({ push: vi.fn() }) }))
vi.mock('@/components/CartLink.vue', () => ({
	default: { template: '<span />' },
}))

enableAutoUnmount(afterEach)
const video = {
	course: 'marathi-for-everyday-conversations',
	title: 'Marathi video course',
	currency: 'INR',
	amount: 2499,
	original_amount: 2499,
	amount_formatted: '₹2,499',
}
const pack = {
	course: 'marathi-addons',
	title: 'Marathi Addons Pack',
	addon_for_course: video.course,
	currency: 'INR',
	amount: 500,
	original_amount: 1999,
	amount_formatted: '₹500',
	original_amount_formatted: '₹1,999',
	discount_amount: 1499,
	discount_amount_formatted: '₹1,499',
}
const summary = (items: any[], suggestions: any[] = []) => ({
	items,
	suggestions,
	owned_courses: [],
	unavailable_courses: [],
})
const showCart = () =>
	mount(Cart, {
		global: {
			mocks: { __: (text: string) => text },
			stubs: { RouterLink: { template: '<a><slot /></a>' } },
		},
	})

describe('cart bundle selection', () => {
	beforeEach(() => {
		localStorage.clear()
		document.cookie = 'user_id=Guest; path=/'
		setActivePinia(createPinia())
		vi.stubGlobal('__', (text: string) => text)
		fetchSummary.mockReset()
	})
	afterEach(() => vi.unstubAllGlobals())

	it('keeps the offer in one card when adding and removing the matching pack', async () => {
		fetchSummary
			.mockResolvedValueOnce(summary([video], [pack]))
			.mockResolvedValueOnce(summary([video, pack]))
			.mockResolvedValueOnce(summary([video], [pack]))
		const cart = useCart()
		cart.add(video.course)
		const page = showCart()
		await flushPromises()
		expect(page.findAll('.bundle-offer')).toHaveLength(1)
		expect(page.findAll('.cart-item')).toHaveLength(0)
		await page.get('input[type="checkbox"]').setValue(true)
		await flushPromises()
		expect(cart.courses).toEqual([video.course, pack.course])
		expect(page.findAll('.bundle-offer')).toHaveLength(1)
		expect(page.findAll('.cart-item')).toHaveLength(0)
		expect(page.get('.bundle-offer__total').text()).toContain('₹2,999')
		await page.get('input[type="checkbox"]').setValue(false)
		await flushPromises()
		expect(cart.courses).toEqual([video.course])
		expect(page.get('.bundle-offer__total').text()).toContain('₹2,499')
	})

	it('shows a standalone pack at its normal price after removing the video course', async () => {
		const standalone = {
			...pack,
			amount: 1999,
			amount_formatted: '₹1,999',
			discount_amount: 0,
		}
		fetchSummary
			.mockResolvedValueOnce(summary([video, pack]))
			.mockResolvedValueOnce(summary([standalone]))
		const cart = useCart()
		cart.add(video.course)
		cart.add(pack.course)
		const page = showCart()
		await flushPromises()
		await page.get('.bundle-offer__remove').trigger('click')
		await flushPromises()
		expect(cart.courses).toEqual([pack.course])
		expect(page.findAll('.bundle-offer')).toHaveLength(0)
		expect(page.findAll('.cart-item')).toHaveLength(1)
		expect(page.get('.cart-item-price').text()).toBe('₹1,999')
	})
})
