import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { reactive } from 'vue'

vi.mock('frappe-ui', async () => {
  const { reactive } = await import('vue')
  const cache = new Map()
  return {
    createResource: (options: any) => {
      const key = options.cache && JSON.stringify(options.cache)
      if (key && cache.has(key)) return cache.get(key)
      const resource = reactive({
        data: null,
        loading: false,
        error: null,
        reload: async () => {
          const params = options.makeParams()
          resource.data = [
            {
              name: `${params.course}-chapter`,
              title: `${params.course} curriculum`,
              idx: 1,
              lessons: [],
            },
          ] as any
          options.onSuccess?.(resource.data)
        },
      })
      if (key) cache.set(key, resource)
      return resource
    },
  }
})
vi.mock('@/stores/cart', () => ({ useCart: () => ({ add: vi.fn() }) }))
vi.mock('vue-router', () => ({ useRouter: () => ({ push: vi.fn() }) }))
vi.mock('@/components/CourseCardOverlay.vue', () => ({
  default: { template: '<div />' },
}))
vi.mock('@/components/CourseReviews.vue', () => ({
  default: { template: '<div />' },
}))

import CourseProductOverview from '@/pages/Courses/CourseProductOverview.vue'

describe('course overview curriculum isolation', () => {
  beforeEach(() => {
    vi.stubGlobal('__', (text: string) =>
      /\{\d+\}/.test(text)
        ? {
            format: (...args: string[]) =>
              text.replace(/\{(\d+)\}/g, (_, i) => args[i]),
          }
        : text,
    )
  })
  it('loads each course even when overview mounts before its course data resolves', async () => {
    for (const name of [
      'kannada-addons',
      'hindi-for-everyday-conversations',
      'tamil-addons',
    ]) {
      const course = reactive({ data: null as any })
      const wrapper = mount(CourseProductOverview, {
        props: { course: course as any },
        global: {
          mocks: { __: (globalThis as any).__ },
          stubs: { RouterLink: true },
        },
      })
      course.data = {
        name,
        title: name,
        membership: { progress: 0 },
        instructors: [],
      }
      await flushPromises()
      expect(wrapper.text()).toContain(`${name} curriculum`)
      if (name !== 'kannada-addons')
        expect(wrapper.text()).not.toContain('kannada-addons curriculum')
      wrapper.unmount()
    }
  })
})
