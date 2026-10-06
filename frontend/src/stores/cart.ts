import { defineStore } from 'pinia'
import { computed, ref, watch } from 'vue'

function read(key: string): string[] {
	try {
		const value = JSON.parse(localStorage.getItem(key) || '[]')
		return Array.isArray(value)
			? [...new Set(value.filter((v) => typeof v === 'string'))].slice(0, 20)
			: []
	} catch {
		return []
	}
}

export const useCart = defineStore('course-cart', () => {
	const cookieUser = new URLSearchParams(
		document.cookie.split('; ').join('&'),
	).get('user_id')
	const member = cookieUser && cookieUser !== 'Guest' ? cookieUser : 'Guest'
	const key = `bhasha-cart:${member}`
	const guestKey = 'bhasha-cart:Guest'
	const courses = ref(read(key))
	// Carry the guest selection through signup without mixing different accounts.
	if (member !== 'Guest') {
		courses.value = [...new Set([...courses.value, ...read(guestKey)])].slice(
			0,
			20,
		)
		localStorage.removeItem(guestKey)
	}
	const couponCode = ref(localStorage.getItem(`${key}:coupon`) || '')
	watch(courses, (value) => localStorage.setItem(key, JSON.stringify(value)), {
		deep: true,
		immediate: true,
	})
	watch(couponCode, (value) => localStorage.setItem(`${key}:coupon`, value))
	const count = computed(() => courses.value.length)
	function add(course: string) {
		if (!courses.value.includes(course) && count.value < 20)
			courses.value.push(course)
	}
	function remove(course: string) {
		courses.value = courses.value.filter((c) => c !== course)
	}
	function removePurchased(purchased: string[]) {
		courses.value = courses.value.filter((c) => !purchased.includes(c))
		couponCode.value = ''
	}
	return { courses, couponCode, count, add, remove, removePurchased }
})
