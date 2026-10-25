import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { enableAutoUnmount, mount } from '@vue/test-utils'
import CartBundleOffer from '@/components/CartBundleOffer.vue'

enableAutoUnmount(afterEach)
const course = {
	course: 'marathi-for-everyday-conversations',
	title: 'Marathi for Everyday Conversations',
	currency: 'INR',
	original_amount: 2499,
	amount: 2499,
	amount_formatted: '₹2,499',
}
const pack = {
	course: 'marathi-addons',
	title: 'Marathi Addons Pack',
	short_introduction:
		'101 Beginner Phrases, 202 Beginner Vocabulary, verb conjugation tables and a 450-sentence practice workbook.',
	original_amount: 1999,
	original_amount_formatted: '₹1,999',
	amount: 500,
	amount_formatted: '₹500',
	discount_amount: 1499,
	discount_amount_formatted: '₹1,499',
}
const showOffer = (selected = false) =>
	mount(CartBundleOffer, {
		props: { course, pack, selected },
		global: {
			mocks: { __: (text: string) => text },
			stubs: { RouterLink: { template: '<a><slot /></a>' } },
		},
	})

describe('checkout bundle offer', () => {
	beforeEach(() => vi.stubGlobal('__', (text: string) => text))
	afterEach(() => vi.unstubAllGlobals())

	it('shows the regular price, checkout offer and savings before selection', () => {
		const offer = showOffer()
		expect(offer.text()).toContain('₹4,999')
		expect(offer.text()).toContain('50% off')
		expect(offer.text()).toContain('Regular price ₹1,999')
		expect(offer.text()).toContain('₹500')
		expect(offer.text()).toContain('Save ₹1,499 (75% off)')
		expect(offer.get('.bundle-offer__total').text()).toContain('₹2,499')
		expect((offer.get('input').element as HTMLInputElement).checked).toBe(false)
	})

	it('lets the learner opt in and remove the pack, with the selected total', async () => {
		const offer = showOffer()
		await offer.get('input').setValue(true)
		expect(offer.emitted('toggle-pack')).toHaveLength(1)
		await offer.setProps({ selected: true })
		expect(offer.get('.bundle-offer__total').text()).toContain('₹2,999')
		await offer.get('input').setValue(false)
		expect(offer.emitted('toggle-pack')).toHaveLength(2)
		await offer.setProps({ selected: false })
		expect(offer.get('.bundle-offer__total').text()).toContain('₹2,499')
		await offer.get('button').trigger('click')
		expect(offer.emitted('remove-course')).toHaveLength(1)
	})

	it('uses actual coupon-adjusted prices and waits while refreshing', async () => {
		const offer = showOffer(true)
		await offer.setProps({
			course: { ...course, amount: 1999, amount_formatted: '₹1,999' },
			loading: true,
		})
		expect(offer.get('.bundle-offer__total').text()).toContain('₹2,499')
		expect((offer.get('input').element as HTMLInputElement).disabled).toBe(true)
	})
})
