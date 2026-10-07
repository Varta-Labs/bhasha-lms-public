import { afterEach, describe, expect, it } from 'vitest'
import { getLmsRoute, getSignupUrl } from '@/utils/basePath'

afterEach(() => {
	delete (window as any).lms_path
})

describe('authentication return URLs', () => {
	it('returns to the LMS root from a nested login URL', () => {
		const signup = new URL(getSignupUrl(), 'https://learn.bhasha.io')
		const destination = signup.searchParams.get('redirect-to')!
		expect(new URL(destination, 'https://learn.bhasha.io/login').pathname).toBe(
			'/lms',
		)
		expect(signup.hash).toBe('#signup')
	})

	it('preserves checkout paths and query parameters through signup', () => {
		const destination = getLmsRoute('billing/cart/current?coupon=LEARN&lang=hi')
		const signup = new URL(getSignupUrl(destination), 'https://learn.bhasha.io')
		expect(signup.searchParams.get('redirect-to')).toBe(destination)
	})

	it('uses the configured LMS path for the default return destination', () => {
		;(window as any).lms_path = 'learn'
		const signup = new URL(getSignupUrl(), 'https://learn.bhasha.io')
		expect(signup.searchParams.get('redirect-to')).toBe('/learn')
	})
})
