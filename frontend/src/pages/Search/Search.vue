<template>
  <header
    class="bhasha-product-header sticky flex items-center justify-between top-0 z-10 border-b bg-surface-white px-3 py-2.5 sm:px-5"
  >
    <Breadcrumbs :items="[{ label: __('Search') }]" />
  </header>
  <main class="bhasha-search-page min-h-0 flex-1">
    <section class="bhasha-search-panel">
      <div class="bhasha-search-heading">
        <div>
          <h1>{{ __('Search learning content') }}</h1>
          <p>
            {{ __('Find courses, batches, and opportunities across Bhasha.') }}
          </p>
        </div>
        <div
          v-if="hasSearched && searchResults.length"
          class="bhasha-search-count"
          aria-live="polite"
        >
          {{ searchResults.length }}
          {{ searchResults.length === 1 ? __('match') : __('matches') }}
        </div>
      </div>

      <TextInput
        ref="searchInput"
        class="bhasha-search-input"
        :placeholder="__('Search for a keyword or phrase')"
        autocomplete="off"
        :model-value="query"
        @update:model-value="updateQuery"
        @keydown.enter="() => submit()"
      >
        <template #prefix>
          <Search class="size-4 stroke-1.5 text-bhasha-accent" />
        </template>
        <template #suffix>
          <div class="flex items-center">
            <button
              v-if="query"
              type="button"
              class="bhasha-search-clear"
              :aria-label="__('Clear search')"
              @click="clearSearch"
            >
              <X class="size-3.5 stroke-2" />
            </button>
          </div>
        </template>
      </TextInput>
      <div class="bhasha-search-helper" aria-live="polite">
        <template v-if="search.loading">
          <LoaderCircle class="size-3.5 animate-spin" />
          {{ __('Searching Bhasha…') }}
        </template>
        <template v-else-if="queryChanged">
          {{ searchPrompt }}
        </template>
        <template v-else-if="hasSearched && query && !searchResults.length">
          {{ __('No matches found. Try a broader keyword.') }}
        </template>
        <template v-else>
          {{ __('Enter at least 3 characters, then press Enter to search.') }}
        </template>
      </div>
    </section>

    <section class="bhasha-search-results" aria-live="polite">
      <div v-if="search.loading" class="bhasha-search-result-list">
        <div v-for="index in 3" :key="index" class="bhasha-search-skeleton">
          <div class="bhasha-search-skeleton-icon"></div>
          <div class="flex-1 space-y-3">
            <div class="h-3 w-1/4 rounded-full bg-surface-gray-3"></div>
            <div class="h-4 w-2/3 rounded-full bg-surface-gray-3"></div>
            <div class="h-3 w-full rounded-full bg-surface-gray-2"></div>
          </div>
        </div>
      </div>

      <div v-else-if="searchResults.length" class="bhasha-search-result-list">
        <button
          v-for="result in searchResults"
          :key="`${result.doctype}-${result.name}`"
          type="button"
          class="bhasha-search-result"
          @click="navigate(result)"
        >
          <div class="bhasha-search-result-icon" aria-hidden="true">
            <component
              :is="getDocTypeIcon(result.doctype)"
              class="size-5 stroke-1.5"
            />
          </div>
          <div class="min-w-0 flex-1">
            <div class="bhasha-search-result-meta">
              <span class="bhasha-search-type">
                {{ getDocTypeTitle(result.doctype) }}
              </span>
              <span v-if="getResultDate(result)" class="bhasha-search-date">
                {{ dayjs(getResultDate(result)).format('DD MMM YYYY') }}
              </span>
            </div>
            <h2 class="bhasha-search-result-title" v-html="result.title"></h2>
            <div
              class="bhasha-search-result-copy"
              v-html="result.content"
            ></div>
            <div v-if="result.author_info" class="bhasha-search-author">
              <Tooltip :text="result.author_info.full_name">
                <Avatar
                  :label="result.author_info.full_name"
                  :image="result.author_info.user_image"
                  size="sm"
                />
              </Tooltip>
              <span>{{ result.author_info.full_name }}</span>
            </div>
          </div>
          <ArrowUpRight class="bhasha-search-result-arrow size-4 stroke-1.5" />
        </button>
      </div>

      <div v-else class="bhasha-search-empty">
        <div class="bhasha-search-empty-icon">
          <component
            :is="hasSearched ? SearchX : FileSearch"
            class="size-6 stroke-1.5"
          />
        </div>
        <h2>
          {{
            hasSearched ? __('No results found') : __('Search across Bhasha')
          }}
        </h2>
        <p>
          {{
            hasSearched
              ? __(
                  'Try a different spelling or use a more general search term.',
                )
              : __(
                  'Courses, upcoming batches, and open opportunities will appear here.',
                )
          }}
        </p>
      </div>
    </section>
  </main>
</template>
<script setup lang="ts">
import {
  Avatar,
  Breadcrumbs,
  createResource,
  debounce,
  TextInput,
  Tooltip,
  usePageMeta,
} from 'frappe-ui'
import { computed, inject, onMounted, ref, watch } from 'vue'
import {
  ArrowUpRight,
  BookOpen,
  BriefcaseBusiness,
  FileSearch,
  LoaderCircle,
  Search,
  SearchX,
  UsersRound,
  X,
} from 'lucide-vue-next'
import { sessionStore } from '@/stores/session'
import { useRouter, useRoute } from 'vue-router'

const query = ref('')
const searchInput = ref<HTMLInputElement | null>(null)
const searchResults = ref<Array<any>>([])
const { brand } = sessionStore()
const router = useRouter()
const route = useRoute()
const queryChanged = ref(false)
const hasSearched = ref(false)
const dayjs = inject<any>('$dayjs')

onMounted(() => {
  if (router.currentRoute.value.query.q) {
    query.value = router.currentRoute.value.query.q as string
    submit()
  }
})

const updateQuery = (value: string) => {
  query.value = value
  router.replace({ query: value ? { q: value } : {} })
}

const submit = debounce(() => {
  if (query.value.length > 2) {
    queryChanged.value = false
    search.reload()
  }
}, 500)

const search = createResource({
  url: 'lms.command_palette.search_sqlite',
  makeParams: () => ({
    query: query.value,
  }),
  onSuccess() {
    hasSearched.value = true
    generateSearchResults()
  },
})

const searchPrompt = computed(() => {
  if (query.value.length < 3) {
    const remaining = 3 - query.value.length
    return remaining === 1
      ? __('Type 1 more character to search.')
      : __('Type {0} more characters to search.').format(remaining)
  }
  return __('Press Enter to search.')
})

const generateSearchResults = () => {
  searchResults.value = []
  if (search.data) {
    queryChanged.value = false
    search.data.forEach((group: any) => {
      group.items.forEach((item: any) => {
        searchResults.value.push(item)
      })
    })
    sortResults()
  }
}

const sortResults = () => {
  searchResults.value.sort((a, b) => {
    const dateA = new Date(
      a.published_on || a.start_date || a.creation || a.modified,
    ).getTime()
    const dateB = new Date(
      b.published_on || b.start_date || b.creation || b.modified,
    ).getTime()
    return dateB - dateA
  })
}

const navigate = (result: any) => {
  if (result.doctype == 'LMS Course') {
    router.push({
      name: 'CourseDetail',
      params: {
        courseName: result.name,
      },
    })
  } else if (result.doctype == 'LMS Batch') {
    router.push({
      name: 'BatchDetail',
      params: {
        batchName: result.name,
      },
    })
  } else if (result.doctype == 'Job Opportunity') {
    router.push({
      name: 'JobDetail',
      params: {
        job: result.name,
      },
    })
  }
}

watch(query, () => {
  if (query.value && query.value != search.params?.query) {
    queryChanged.value = true
  } else if (!query.value) {
    queryChanged.value = false
    hasSearched.value = false
    searchResults.value = []
  }
})

watch(
  () => route.query.q,
  (newQ) => {
    if (newQ && newQ !== query.value) {
      query.value = newQ as string
      submit()
    }
  },
)

const getDocTypeTitle = (doctype: string) => {
  if (doctype === 'LMS Course') {
    return __('Course')
  } else if (doctype === 'LMS Batch') {
    return __('Batch')
  } else if (doctype === 'Job Opportunity') {
    return __('Job')
  } else {
    return doctype
  }
}

const getDocTypeIcon = (doctype: string) => {
  if (doctype === 'LMS Course') return BookOpen
  if (doctype === 'LMS Batch') return UsersRound
  if (doctype === 'Job Opportunity') return BriefcaseBusiness
  return FileSearch
}

const getResultDate = (result: any) =>
  result.published_on ||
  result.start_date ||
  result.creation ||
  result.modified ||
  null

const clearSearch = () => {
  query.value = ''
  updateQuery('')
}

usePageMeta(() => {
  return {
    title: __('Search'),
    icon: brand.favicon,
  }
})
</script>

<style scoped>
.bhasha-search-page {
  padding: clamp(1rem, 2.5vw, 1.75rem) clamp(0.75rem, 3vw, 2rem) 3rem;
  background:
    radial-gradient(
      circle at 10% 0%,
      rgba(129, 80, 223, 0.075),
      transparent 23rem
    ),
    var(--bhasha-page);
}

.bhasha-search-panel,
.bhasha-search-results {
  width: min(100%, 64rem);
  margin-inline: auto;
}

.bhasha-search-panel {
  padding: clamp(1rem, 2.5vw, 1.5rem);
  border: 1px solid var(--bhasha-border-brand);
  border-radius: var(--bhasha-radius-card);
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 10px 30px rgba(61, 34, 111, 0.055);
}

.bhasha-search-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.1rem;
}

.bhasha-search-heading h1 {
  color: var(--bhasha-text);
  font-family: var(--bhasha-font-display);
  font-size: 1.35rem;
  font-weight: 750;
  letter-spacing: -0.025em;
  line-height: 1.3;
}

.bhasha-search-heading p {
  max-width: 58ch;
  margin-top: 0.25rem;
  color: var(--bhasha-text-muted);
  font-size: 0.8125rem;
  line-height: 1.55;
}

.bhasha-search-count,
.bhasha-search-type {
  display: inline-flex;
  align-items: center;
  border: 1px solid var(--bhasha-border-brand);
  border-radius: 9999px;
  background: var(--bhasha-50);
  color: var(--bhasha-700);
  font-size: 0.75rem;
  font-weight: 650;
}

.bhasha-search-count {
  flex-shrink: 0;
  padding: 0.35rem 0.65rem;
  font-variant-numeric: tabular-nums;
}

.bhasha-search-input :deep(input) {
  min-height: 2.75rem;
  border-color: var(--bhasha-border);
  border-radius: var(--bhasha-radius-control);
  background: var(--bhasha-surface);
  font-size: 0.9375rem;
  transition:
    border-color 160ms ease,
    box-shadow 160ms ease;
}

.bhasha-search-input :deep(input:hover) {
  border-color: var(--bhasha-200);
}

.bhasha-search-input :deep(input:focus) {
  border-color: var(--bhasha-400);
  box-shadow: var(--bhasha-focus-ring);
}

.bhasha-search-clear {
  display: grid;
  width: 1.5rem;
  height: 1.5rem;
  place-items: center;
  border-radius: 9999px;
  color: var(--bhasha-text-muted);
}

.bhasha-search-clear:hover {
  background: var(--bhasha-100);
  color: var(--bhasha-700);
}

.bhasha-search-clear:focus-visible {
  outline: none;
  box-shadow: var(--bhasha-focus-ring);
}

.bhasha-search-helper {
  display: flex;
  min-height: 1.25rem;
  align-items: center;
  gap: 0.35rem;
  margin-top: 0.55rem;
  color: var(--bhasha-text-muted);
  font-size: 0.75rem;
  line-height: 1.4;
}

.bhasha-search-results {
  margin-top: 1rem;
}

.bhasha-search-result-list {
  display: grid;
  gap: 0.75rem;
}

.bhasha-search-result,
.bhasha-search-skeleton {
  display: flex;
  width: 100%;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.15rem;
  border: 1px solid var(--bhasha-border);
  border-radius: 1rem;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 6px 20px rgba(35, 24, 61, 0.045);
  text-align: start;
}

.bhasha-search-result {
  cursor: pointer;
  transition:
    transform 180ms ease,
    border-color 180ms ease,
    box-shadow 180ms ease;
}

.bhasha-search-result:hover {
  transform: translateY(-2px);
  border-color: var(--bhasha-200);
  box-shadow: 0 14px 32px rgba(73, 38, 135, 0.1);
}

.bhasha-search-result:focus-visible {
  outline: none;
  border-color: var(--bhasha-300);
  box-shadow: var(--bhasha-focus-ring);
}

.bhasha-search-result-icon,
.bhasha-search-skeleton-icon {
  display: grid;
  width: 2.75rem;
  height: 2.75rem;
  flex: 0 0 2.75rem;
  place-items: center;
  border-radius: 0.85rem;
  background: linear-gradient(135deg, var(--bhasha-100), var(--bhasha-50));
  color: var(--bhasha-700);
}

.bhasha-search-skeleton-icon {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.bhasha-search-result-meta {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.45rem;
}

.bhasha-search-type {
  padding: 0.22rem 0.5rem;
  font-size: 0.6875rem;
}

.bhasha-search-date {
  color: var(--bhasha-text-muted);
  font-size: 0.75rem;
  font-variant-numeric: tabular-nums;
}

.bhasha-search-result-title {
  color: var(--bhasha-text);
  font-family: var(--bhasha-font-display);
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  line-height: 1.4;
}

.bhasha-search-result-copy {
  display: -webkit-box;
  margin-top: 0.3rem;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  color: var(--bhasha-text-muted);
  font-size: 0.8125rem;
  line-height: 1.6;
}

.bhasha-search-result-title :deep(mark),
.bhasha-search-result-copy :deep(mark),
.bhasha-search-result-title :deep(b),
.bhasha-search-result-copy :deep(b) {
  border-radius: 0.2rem;
  background: var(--bhasha-100);
  color: var(--bhasha-800);
  font-weight: 700;
}

.bhasha-search-author {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  margin-top: 0.7rem;
  color: var(--bhasha-text-muted);
  font-size: 0.75rem;
  font-weight: 550;
}

.bhasha-search-result-arrow {
  flex-shrink: 0;
  margin-top: 0.2rem;
  color: var(--bhasha-400);
  transition:
    transform 180ms ease,
    color 180ms ease;
}

.bhasha-search-result:hover .bhasha-search-result-arrow {
  transform: translate(2px, -2px);
  color: var(--bhasha-700);
}

.bhasha-search-empty {
  display: flex;
  min-height: min(24rem, calc(100vh - 17rem));
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1.5rem;
  border: 1px dashed rgba(101, 50, 197, 0.22);
  border-radius: var(--bhasha-radius-card);
  background: rgba(255, 255, 255, 0.72);
  text-align: center;
}

.bhasha-search-empty-icon {
  display: grid;
  width: 3.25rem;
  height: 3.25rem;
  place-items: center;
  margin-bottom: 1rem;
  border-radius: 1rem;
  background: var(--bhasha-100);
  color: var(--bhasha-700);
}

.bhasha-search-empty h2 {
  color: var(--bhasha-text);
  font-size: 1.125rem;
  font-weight: 700;
}

.bhasha-search-empty p {
  max-width: 34rem;
  margin-top: 0.35rem;
  color: var(--bhasha-text-muted);
  font-size: 0.875rem;
  line-height: 1.55;
}

:global(html[data-theme='dark'] .bhasha-search-page) {
  background: var(--surface-white);
}

:global(html[data-theme='dark'] .bhasha-search-panel),
:global(html[data-theme='dark'] .bhasha-search-result),
:global(html[data-theme='dark'] .bhasha-search-skeleton),
:global(html[data-theme='dark'] .bhasha-search-empty) {
  border-color: rgba(199, 174, 255, 0.16);
  background: var(--surface-white);
  box-shadow: none;
}

:global(html[data-theme='dark'] .bhasha-search-input input),
:global(html[data-theme='dark'] .bhasha-search-type),
:global(html[data-theme='dark'] .bhasha-search-result-icon),
:global(html[data-theme='dark'] .bhasha-search-empty-icon) {
  border-color: rgba(199, 174, 255, 0.16);
  background: rgba(129, 80, 223, 0.12);
}

:global(html[data-theme='dark'] .bhasha-search-heading h1),
:global(html[data-theme='dark'] .bhasha-search-result-title),
:global(html[data-theme='dark'] .bhasha-search-empty h2) {
  color: var(--ink-gray-9);
}

:global(html[data-theme='dark'] .bhasha-search-heading p),
:global(html[data-theme='dark'] .bhasha-search-helper),
:global(html[data-theme='dark'] .bhasha-search-date),
:global(html[data-theme='dark'] .bhasha-search-result-copy),
:global(html[data-theme='dark'] .bhasha-search-author),
:global(html[data-theme='dark'] .bhasha-search-empty p) {
  color: var(--ink-gray-6);
}

:global(html[data-theme='dark'] .bhasha-search-count),
:global(html[data-theme='dark'] .bhasha-search-type),
:global(html[data-theme='dark'] .bhasha-search-result-icon),
:global(html[data-theme='dark'] .bhasha-search-empty-icon) {
  color: var(--bhasha-200);
}

:global(html[data-theme='dark'] .bhasha-search-result-title mark),
:global(html[data-theme='dark'] .bhasha-search-result-copy mark),
:global(html[data-theme='dark'] .bhasha-search-result-title b),
:global(html[data-theme='dark'] .bhasha-search-result-copy b) {
  background: rgba(129, 80, 223, 0.2);
  color: var(--bhasha-200);
}

@media (max-width: 639px) {
  .bhasha-search-page {
    padding: 0.75rem 0.75rem 2rem;
  }

  .bhasha-search-panel {
    padding: 1rem;
    border-radius: 1rem;
  }

  .bhasha-search-heading p {
    display: none;
  }

  .bhasha-search-result,
  .bhasha-search-skeleton {
    gap: 0.75rem;
    padding: 1rem;
  }

  .bhasha-search-result-icon,
  .bhasha-search-skeleton-icon {
    width: 2.4rem;
    height: 2.4rem;
    flex-basis: 2.4rem;
  }

  .bhasha-search-result-arrow {
    display: none;
  }
}

@media (prefers-reduced-motion: reduce) {
  .bhasha-search-result,
  .bhasha-search-result-arrow,
  .bhasha-search-skeleton-icon {
    animation: none;
    transition: none;
  }
}
</style>
