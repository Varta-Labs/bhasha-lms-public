import { beforeEach, describe, expect, it } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { nextTick } from 'vue'
import { useCart } from '@/stores/cart'

describe('course cart persistence', () => {
	beforeEach(() => {
		localStorage.clear()
		document.cookie = 'user_id=Guest; path=/'
		setActivePinia(createPinia())
	})
	it('deduplicates courses and persists removals', async () => {
		const cart = useCart()
		cart.add('main')
		cart.add('main')
		cart.add('pack')
		expect(cart.count).toBe(2)
		cart.remove('pack')
		await nextTick()
		expect(JSON.parse(localStorage.getItem('bhasha-cart:Guest')!)).toEqual([
			'main',
		])
	})
	it('carries a guest selection through signup without mixing other accounts', () => {
		localStorage.setItem('bhasha-cart:Guest', JSON.stringify(['main', 'pack']))
		localStorage.setItem(
			'bhasha-cart:other@example.com',
			JSON.stringify(['other']),
		)
		document.cookie = 'user_id=learner@example.com; path=/'
		expect(useCart().courses).toEqual(['main', 'pack'])
		expect(localStorage.getItem('bhasha-cart:Guest')).toBeNull()
	})
	it('removes only the purchased courses after confirmation', () => {
		const cart = useCart()
		cart.add('main')
		cart.add('pack')
		cart.add('later')
		cart.removePurchased(['main', 'pack'])
		expect(cart.courses).toEqual(['later'])
	})
})
