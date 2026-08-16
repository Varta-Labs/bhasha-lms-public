<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
    <template #right-header>
      <router-link :to="certificationCoursesRoute">
        <Button variant="solid" class="bhasha-primary certified-header-cta">
          <template #prefix>
            <GraduationCap class="size-4 stroke-1.5" />
          </template>
          {{ __('Get Certified') }}
        </Button>
      </router-link>
    </template>
  </LayoutHeader>

  <main class="certified-page">
    <section class="certified-hero" aria-labelledby="certified-page-title">
      <div class="certified-hero-copy">
        <div class="certified-eyebrow">
          <BadgeCheck class="size-4 stroke-2" />
          {{ __('Verified learning, visible progress') }}
        </div>
        <h1 id="certified-page-title">
          {{ __('Meet our certified learners') }}
        </h1>
        <p>
          {{
            __(
              'Discover people who have built practical skills and earned a verified Bhasha certificate.',
            )
          }}
        </p>
        <div class="certified-hero-actions">
          <router-link
            :to="certificationCoursesRoute"
            class="certified-primary-action"
          >
            <GraduationCap class="size-5 stroke-1.75" />
            {{ __('Get Certified') }}
            <ArrowRight class="size-4 stroke-2" />
          </router-link>
          <span class="certified-hero-note">
            <Sparkles class="size-4 stroke-1.5" />
            {{ __('Learn, complete, and showcase your achievement') }}
          </span>
        </div>
      </div>

      <div class="certified-hero-stat" aria-live="polite">
        <div class="certified-hero-stat-icon">
          <UsersRound class="size-7 stroke-1.5" />
        </div>
        <div>
          <strong>{{ memberCount }}</strong>
          <span>{{ __('Certified Members') }}</span>
        </div>
        <div class="certified-hero-stat-seal" aria-hidden="true">
          <BadgeCheck class="size-5 stroke-2" />
        </div>
      </div>
    </section>

    <section class="certified-directory" aria-labelledby="directory-title">
      <div class="certified-directory-heading">
        <div>
          <span class="certified-section-kicker">{{
            __('Community directory')
          }}</span>
          <h2 id="directory-title">{{ __('Find certified learners') }}</h2>
          <p>
            {{
              __(
                'Search by name, explore a learning category, or find people certified through us.',
              )
            }}
          </p>
        </div>
        <div class="certified-result-count" aria-live="polite">
          {{ memberCount }}
          {{ memberCount === 1 ? __('member') : __('members') }}
        </div>
      </div>

      <div class="certified-filter-panel">
        <div class="certified-filter-main">
          <FormControl
            v-model="nameFilter"
            :placeholder="__('Search by name')"
            type="text"
            size="md"
            variant="outline"
            class="certified-name-search"
            @input="debouncedUpdateParticipants"
          >
            <template #prefix>
              <Search class="size-4 stroke-1.5 text-ink-gray-5" />
            </template>
            <template v-if="nameFilter" #suffix>
              <button
                type="button"
                class="certified-search-clear"
                :aria-label="__('Clear search')"
                @click="clearNameSearch"
              >
                <X class="size-3.5 stroke-2" />
              </button>
            </template>
          </FormControl>

          <Select
            v-if="categories.data?.length"
            v-model="currentCategory"
            :options="categories.data"
            :placeholder="__('All categories')"
            size="md"
            variant="outline"
            class="certified-category-filter"
            @update:modelValue="updateParticipants()"
          />
        </div>

        <div v-if="hasActiveFilters" class="certified-filter-actions">
          <button
            type="button"
            class="certified-clear-filters"
            @click="resetFilters"
          >
            <X class="size-3.5 stroke-2" />
            {{ __('Clear filters') }}
          </button>
        </div>
      </div>

      <div
        v-if="participants.list.loading"
        class="certified-grid"
        aria-hidden="true"
      >
        <div v-for="index in 8" :key="index" class="certified-card is-loading">
          <div class="certified-skeleton certified-skeleton-avatar" />
          <div class="certified-skeleton certified-skeleton-title" />
          <div class="certified-skeleton certified-skeleton-copy" />
          <div class="certified-skeleton certified-skeleton-meta" />
        </div>
      </div>

      <div v-else-if="participants.data?.length" class="certified-grid">
        <router-link
          v-for="participant in participants.data"
          :key="participant.username"
          :to="{
            name: 'ProfileAbout',
            params: { username: participant.username },
          }"
          class="certified-card"
        >
          <div class="certified-card-topline">
            <UserAvatar :user="participant" size="2xl" />
            <span
              v-if="participant.open_to"
              class="certified-availability"
              :class="{ 'is-hiring': participant.open_to === 'Hiring' }"
            >
              {{
                participant.open_to === 'Hiring'
                  ? __('Hiring')
                  : __('Open to Work')
              }}
            </span>
          </div>

          <div class="certified-card-copy">
            <h3>{{ participant.full_name }}</h3>
            <p>
              {{
                participant.headline ||
                __('Joined {0}', [dayjs(participant.creation).fromNow()])
              }}
            </p>
          </div>

          <div class="certified-card-meta">
            <div>
              <GraduationCap class="size-4 stroke-1.75" />
              <span>
                <strong>{{ participant.certificate_count }}</strong>
                {{
                  participant.certificate_count === 1
                    ? __('certificate')
                    : __('certificates')
                }}
              </span>
            </div>
            <div>
              <Calendar class="size-4 stroke-1.75" />
              <span>{{
                dayjs(participant.issue_date).format('DD MMM YYYY')
              }}</span>
            </div>
          </div>

          <div class="certified-card-footer">
            <span>{{ __('View profile') }}</span>
            <ArrowRight class="size-4 stroke-2" />
          </div>
        </router-link>
      </div>

      <div v-else class="certified-empty">
        <div class="certified-empty-icon">
          <Search v-if="hasActiveFilters" class="size-6 stroke-1.5" />
          <GraduationCap v-else class="size-6 stroke-1.5" />
        </div>
        <h3>
          {{
            hasActiveFilters
              ? __('No matching members')
              : __('No certified members yet')
          }}
        </h3>
        <p>
          {{
            hasActiveFilters
              ? __('Try another name or clear one of the active filters.')
              : __(
                  'Certified learners will appear here as they complete courses.',
                )
          }}
        </p>
        <Button v-if="hasActiveFilters" @click="resetFilters">
          {{ __('Clear filters') }}
        </Button>
        <router-link v-else :to="certificationCoursesRoute">
          <Button variant="solid" class="bhasha-primary">
            {{ __('Explore certificate courses') }}
          </Button>
        </router-link>
      </div>

      <div
        v-if="!participants.list.loading && participants.data?.length"
        class="certified-pagination"
      >
        <p>
          {{ __('Showing') }}
          <strong>{{ participants.data.length }}</strong>
          {{ __('of') }}
          <strong>{{ memberCount }}</strong>
          {{ __('members') }}
        </p>
        <Button
          v-if="participants.hasNextPage"
          class="certified-load-more"
          @click="participants.next()"
        >
          {{ __('Load more members') }}
          <template #suffix>
            <ArrowRight class="size-4 stroke-2" />
          </template>
        </Button>
      </div>
    </section>
  </main>
</template>

<script setup>
import {
  Breadcrumbs,
  Button,
  call,
  createListResource,
  FormControl,
  usePageMeta,
} from 'frappe-ui'
import Select from '@/components/Controls/Select.vue'
import { computed, inject, onMounted, ref } from 'vue'
import {
  ArrowRight,
  BadgeCheck,
  Calendar,
  GraduationCap,
  Search,
  Sparkles,
  UsersRound,
  X,
} from 'lucide-vue-next'
import { useDebounceFn } from '@vueuse/core'
import { sessionStore } from '../stores/session'
import { useRouter } from 'vue-router'
import UserAvatar from '@/components/UserAvatar.vue'
import LayoutHeader from '@/components/Layouts/LayoutHeader.vue'

const filters = ref({})
const currentCategory = ref(null)
const nameFilter = ref('')
const { brand } = sessionStore()
const memberCount = ref(0)
const dayjs = inject('$dayjs')
const user = inject('$user')
const router = useRouter()
const certificationCoursesRoute = {
  name: 'Courses',
  query: { certification: true },
}

onMounted(() => {
  if (!user.data) {
    router.push({ name: 'Courses' })
    return
  }
  setFiltersFromQuery()
  updateParticipants()
})

const participants = createListResource({
  doctype: 'LMS Certificate',
  url: 'lms.lms.api.get_certified_participants',
  start: 0,
  pageLength: 40,
  cache: ['certified_participants'],
})

const getMemberCount = () => {
  call('lms.lms.api.get_count_of_certified_members', {
    filters: filters.value,
  }).then((data) => {
    memberCount.value = data
  })
}

const categories = createListResource({
  doctype: 'LMS Certificate',
  url: 'lms.lms.api.get_certification_categories',
  cache: ['certification_categories'],
  auto: user.data ? true : false,
  transform(data) {
    return [{ label: __('All categories'), value: null }, ...data]
  },
})

const updateParticipants = () => {
  updateFilters()
  getMemberCount()
  setQueryParams()

  participants.update({
    filters: filters.value,
    start: 0,
  })
  participants.reload()
}

const debouncedUpdateParticipants = useDebounceFn(updateParticipants, 300)

const updateFilters = () => {
  filters.value = {
    ...(currentCategory.value && {
      category: currentCategory.value,
    }),
    ...(nameFilter.value.trim() && {
      member_name: ['like', '%' + nameFilter.value.trim() + '%'],
    }),
  }
}

const setQueryParams = () => {
  let queries = new URLSearchParams(location.search)
  queries.delete('open-to-work')
  queries.delete('hiring')
  let filterKeys = {
    category: currentCategory.value,
    name: nameFilter.value.trim(),
  }

  Object.keys(filterKeys).forEach((key) => {
    if (hasValue(filterKeys[key])) {
      queries.set(key, filterKeys[key])
    } else {
      queries.delete(key)
    }
  })
  const queryString = queries.size > 0 ? '?' + queries.toString() : ''
  history.replaceState({}, '', location.pathname + queryString)
}

const hasValue = (value) => {
  if (typeof value === 'string') return value.trim() !== ''
  return value === true
}

const setFiltersFromQuery = () => {
  let queries = new URLSearchParams(location.search)
  nameFilter.value = queries.get('name') || ''
  currentCategory.value = queries.get('category') || null
}

const clearNameSearch = () => {
  nameFilter.value = ''
  updateParticipants()
}

const resetFilters = () => {
  nameFilter.value = ''
  currentCategory.value = null
  updateParticipants()
}

const hasActiveFilters = computed(
  () => Boolean(nameFilter.value.trim()) || Boolean(currentCategory.value),
)

const breadcrumbs = computed(() => [
  {
    label: __('Certified Members'),
    route: { name: 'CertifiedParticipants' },
  },
])

usePageMeta(() => {
  return {
    title: __('Certified Members'),
    icon: brand.favicon,
  }
})
</script>

<style scoped>
.certified-page {
  min-height: 100%;
  flex: 1;
  overflow-y: auto;
  background: var(--bhasha-page);
  color: var(--bhasha-text);
}

.certified-hero,
.certified-directory {
  width: min(100%, 80rem);
  margin-inline: auto;
  padding-inline: clamp(1rem, 4vw, 2.5rem);
}

.certified-hero {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) minmax(16rem, 0.7fr);
  align-items: center;
  gap: clamp(2rem, 6vw, 5rem);
  width: 100%;
  max-width: none;
  padding-block: clamp(3.5rem, 7vw, 6rem);
  padding-inline: max(1rem, calc((100vw - 80rem) / 2 + 2.5rem));
  overflow: hidden;
  border-bottom: 1px solid rgba(113, 91, 61, 0.12);
  background:
    radial-gradient(
      circle at 18% 8%,
      rgba(255, 255, 255, 0.72),
      transparent 34%
    ),
    radial-gradient(
      circle at 82% 76%,
      rgba(210, 189, 153, 0.18),
      transparent 36%
    ),
    linear-gradient(135deg, #f7f2e8 0%, #f3ecdf 58%, #f8f4eb 100%);
}

.certified-hero::before {
  position: absolute;
  top: -15rem;
  right: -9rem;
  width: 34rem;
  height: 34rem;
  border: 1px solid rgba(113, 91, 61, 0.11);
  border-radius: 50%;
  box-shadow:
    0 0 0 4rem rgba(113, 91, 61, 0.04),
    0 0 0 8rem rgba(113, 91, 61, 0.025);
  content: '';
  pointer-events: none;
}

.certified-hero::after {
  position: absolute;
  bottom: -2rem;
  left: 3%;
  width: 18rem;
  height: 10rem;
  background-image: radial-gradient(
    rgba(113, 91, 61, 0.16) 1px,
    transparent 1px
  );
  background-size: 16px 16px;
  content: '';
  mask-image: linear-gradient(to top right, black, transparent 72%);
  pointer-events: none;
}

.certified-hero-copy,
.certified-hero-stat {
  position: relative;
  z-index: 1;
}

.certified-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
  padding: 0.45rem 0.8rem;
  border: 1px solid rgba(108, 92, 231, 0.25);
  border-radius: 9999px;
  background: rgba(255, 255, 255, 0.72);
  color: #4a38c2;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  backdrop-filter: blur(8px);
}

.certified-hero h1 {
  max-width: 13ch;
  color: #171717;
  font-family: var(--bhasha-font-display);
  font-size: clamp(2.25rem, 4.2vw, 3.5rem);
  font-weight: 800;
  letter-spacing: -0.03em;
  line-height: 1.1;
}

.certified-hero-copy > p {
  max-width: 38rem;
  margin-top: 1.25rem;
  color: #525252;
  font-size: clamp(1rem, 1.5vw, 1.15rem);
  line-height: 1.65;
}

.certified-hero-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem 1.25rem;
  margin-top: 2rem;
}

.certified-primary-action {
  display: inline-flex;
  min-height: 3.25rem;
  align-items: center;
  justify-content: center;
  gap: 0.65rem;
  padding: 0.9rem 1.35rem;
  border-radius: 9999px;
  background: linear-gradient(135deg, #6c5ce7, #4a38c2);
  color: #fff;
  box-shadow: 0 14px 28px -8px rgba(108, 92, 231, 0.45);
  font-size: 0.95rem;
  font-weight: 800;
  transition:
    transform 180ms ease,
    box-shadow 180ms ease;
}

.certified-primary-action:hover {
  transform: translateY(-1px);
  box-shadow: 0 18px 32px -8px rgba(108, 92, 231, 0.52);
  color: #fff;
  text-decoration: none;
}

.certified-primary-action:focus-visible,
.certified-card:focus-visible,
.certified-clear-filters:focus-visible,
.certified-search-clear:focus-visible {
  outline: 3px solid rgba(108, 92, 231, 0.3);
  outline-offset: 3px;
}

.certified-hero-note {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  max-width: 18rem;
  color: #715b3d;
  font-size: 0.8125rem;
  font-weight: 600;
  line-height: 1.45;
}

.certified-hero-stat {
  display: flex;
  min-height: 11rem;
  align-items: center;
  gap: 1rem;
  padding: 1.75rem;
  border: 1px solid rgba(108, 92, 231, 0.2);
  border-radius: 1.5rem;
  background: rgba(255, 255, 255, 0.86);
  box-shadow: 0 26px 56px -32px rgba(74, 47, 25, 0.4);
  backdrop-filter: blur(12px);
}

.certified-hero-stat-icon {
  display: flex;
  width: 3.5rem;
  height: 3.5rem;
  flex: 0 0 auto;
  align-items: center;
  justify-content: center;
  border-radius: 1rem;
  background: rgba(108, 92, 231, 0.1);
  color: #6c5ce7;
}

.certified-hero-stat strong,
.certified-hero-stat span {
  display: block;
}

.certified-hero-stat strong {
  color: #171717;
  font-family: var(--bhasha-font-display);
  font-size: clamp(2.5rem, 4vw, 3rem);
  font-weight: 800;
  letter-spacing: -0.04em;
  line-height: 1;
}

.certified-hero-stat span {
  margin-top: 0.4rem;
  color: #525252;
  font-size: 0.875rem;
  font-weight: 600;
}

.certified-hero-stat-seal {
  position: absolute;
  top: 1rem;
  right: 1rem;
  display: flex;
  width: 2rem;
  height: 2rem;
  align-items: center;
  justify-content: center;
  border-radius: 9999px;
  background: rgba(5, 150, 105, 0.12);
  color: #059669;
}

.certified-directory {
  padding-block: clamp(4rem, 7vw, 6rem);
}

.certified-directory-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 2rem;
}

.certified-section-kicker {
  color: #6c5ce7;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.certified-directory-heading h2 {
  margin-top: 0.6rem;
  color: var(--bhasha-text);
  font-family: var(--bhasha-font-display);
  font-size: clamp(1.75rem, 2.5vw, 2.5rem);
  font-weight: 800;
  letter-spacing: -0.025em;
  line-height: 1.2;
}

.certified-directory-heading p {
  max-width: 40rem;
  margin-top: 0.75rem;
  color: var(--bhasha-text-muted);
  line-height: 1.6;
}

.certified-result-count {
  flex: 0 0 auto;
  padding: 0.55rem 0.85rem;
  border: 1px solid var(--bhasha-border-brand);
  border-radius: 9999px;
  background: var(--bhasha-50);
  color: var(--bhasha-700);
  font-size: 0.8125rem;
  font-weight: 700;
}

.certified-filter-panel {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 2rem;
  padding: 1rem;
  border: 1px solid var(--bhasha-border);
  border-radius: 1.25rem;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 8px 24px rgba(35, 24, 61, 0.05);
}

.certified-filter-main,
.certified-filter-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.certified-filter-main {
  min-width: 0;
  flex: 1;
}

.certified-name-search {
  width: min(100%, 20rem);
}

.certified-category-filter {
  width: 12rem;
  flex: 0 0 auto;
}

.certified-search-clear {
  display: inline-flex;
  width: 1.5rem;
  height: 1.5rem;
  align-items: center;
  justify-content: center;
  border-radius: 9999px;
  color: var(--bhasha-text-muted);
}

.certified-search-clear:hover {
  background: var(--bhasha-100);
  color: var(--bhasha-700);
}

.certified-clear-filters {
  display: inline-flex;
  min-height: 2.5rem;
  flex: 0 0 auto;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  padding: 0.65rem 0.8rem;
  border-radius: 9999px;
  font-size: 0.8125rem;
  font-weight: 700;
  transition: all 160ms ease;
}

.certified-clear-filters {
  color: var(--bhasha-600);
}

.certified-clear-filters:hover {
  background: var(--bhasha-50);
  color: var(--bhasha-800);
}

.certified-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1.25rem;
  margin-top: 2rem;
}

.certified-card {
  display: flex;
  min-width: 0;
  min-height: 18.5rem;
  flex-direction: column;
  padding: 1.35rem;
  border: 1px solid var(--bhasha-border);
  border-radius: var(--bhasha-radius-card);
  background: var(--bhasha-surface);
  box-shadow: 0 8px 24px rgba(35, 24, 61, 0.055);
  transition:
    transform 180ms ease,
    border-color 180ms ease,
    box-shadow 180ms ease;
}

.certified-card:hover {
  transform: translateY(-2px);
  border-color: var(--bhasha-200);
  box-shadow: 0 16px 36px rgba(73, 38, 135, 0.12);
  text-decoration: none;
}

.certified-card-topline {
  display: flex;
  min-height: 3.5rem;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
}

.certified-card-topline :deep(.avatar) {
  border: 3px solid #fff;
  box-shadow:
    0 0 0 1px var(--bhasha-200),
    0 6px 16px rgba(73, 38, 135, 0.12);
}

.certified-availability {
  display: inline-flex;
  align-items: center;
  padding: 0.35rem 0.6rem;
  border: 1px solid rgba(5, 150, 105, 0.2);
  border-radius: 9999px;
  background: rgba(16, 185, 129, 0.1);
  color: #047857;
  font-size: 0.7rem;
  font-weight: 700;
  line-height: 1;
}

.certified-availability.is-hiring {
  border-color: var(--bhasha-border-brand);
  background: var(--bhasha-50);
  color: var(--bhasha-700);
}

.certified-card-copy {
  margin-top: 1.2rem;
}

.certified-card-copy h3 {
  overflow: hidden;
  color: var(--bhasha-text);
  font-family: var(--bhasha-font-display);
  font-size: 1.125rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  line-height: 1.3;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: color 180ms ease;
}

.certified-card:hover h3 {
  color: var(--bhasha-700);
}

.certified-card-copy p {
  display: -webkit-box;
  min-height: 2.7rem;
  margin-top: 0.35rem;
  overflow: hidden;
  color: var(--bhasha-text-muted);
  font-size: 0.8125rem;
  line-height: 1.55;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.certified-card-meta {
  display: grid;
  gap: 0.6rem;
  margin-top: 1.25rem;
  padding-block: 1rem;
  border-block: 1px solid var(--bhasha-border);
  color: var(--bhasha-text-muted);
  font-size: 0.78rem;
}

.certified-card-meta > div {
  display: flex;
  align-items: center;
  gap: 0.55rem;
}

.certified-card-meta svg {
  flex: 0 0 auto;
  color: var(--bhasha-600);
}

.certified-card-meta strong {
  color: var(--bhasha-text);
  font-weight: 700;
}

.certified-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: auto;
  padding-top: 1rem;
  color: var(--bhasha-600);
  font-size: 0.8125rem;
  font-weight: 700;
}

.certified-card-footer svg {
  transition: transform 180ms ease;
}

.certified-card:hover .certified-card-footer svg {
  transform: translateX(3px);
}

.certified-card.is-loading {
  pointer-events: none;
}

.certified-skeleton {
  border-radius: 9999px;
  background: linear-gradient(
    90deg,
    var(--bhasha-50),
    var(--bhasha-100),
    var(--bhasha-50)
  );
  background-size: 220% 100%;
  animation: certified-shimmer 1.5s ease-in-out infinite;
}

.certified-skeleton-avatar {
  width: 3.5rem;
  height: 3.5rem;
}

.certified-skeleton-title {
  width: 62%;
  height: 1rem;
  margin-top: 1.4rem;
}

.certified-skeleton-copy {
  width: 88%;
  height: 0.75rem;
  margin-top: 0.75rem;
}

.certified-skeleton-meta {
  width: 74%;
  height: 0.75rem;
  margin-top: 2.5rem;
}

@keyframes certified-shimmer {
  to {
    background-position: -220% 0;
  }
}

.certified-empty {
  display: flex;
  min-height: 19rem;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  margin-top: 2rem;
  padding: 2.5rem 1.5rem;
  border: 1px dashed var(--bhasha-200);
  border-radius: 1.5rem;
  background: linear-gradient(135deg, var(--bhasha-50), #fff);
  text-align: center;
}

.certified-empty-icon {
  display: flex;
  width: 3.5rem;
  height: 3.5rem;
  align-items: center;
  justify-content: center;
  border-radius: 1rem;
  background: var(--bhasha-100);
  color: var(--bhasha-600);
}

.certified-empty h3 {
  margin-top: 1rem;
  color: var(--bhasha-text);
  font-family: var(--bhasha-font-display);
  font-size: 1.25rem;
  font-weight: 700;
}

.certified-empty p {
  max-width: 28rem;
  margin: 0.5rem 0 1.25rem;
  color: var(--bhasha-text-muted);
  line-height: 1.55;
}

.certified-pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--bhasha-border);
}

.certified-pagination p {
  color: var(--bhasha-text-muted);
  font-size: 0.8125rem;
}

.certified-pagination strong {
  color: var(--bhasha-text);
  font-weight: 700;
}

.certified-load-more {
  border-color: var(--bhasha-border-brand) !important;
  border-radius: 9999px !important;
  background: #fff !important;
  color: var(--bhasha-700) !important;
}

:global(html[data-theme='dark']) .certified-page {
  background: var(--surface-white);
}

:global(html[data-theme='dark']) .certified-hero {
  border-bottom-color: rgba(199, 174, 255, 0.14);
  background:
    radial-gradient(
      circle at 18% 8%,
      rgba(129, 80, 223, 0.17),
      transparent 34%
    ),
    radial-gradient(
      circle at 82% 76%,
      rgba(255, 128, 55, 0.05),
      transparent 36%
    ),
    var(--surface-white);
}

:global(html[data-theme='dark']) .certified-hero h1,
:global(html[data-theme='dark']) .certified-hero-stat strong {
  color: var(--ink-gray-9);
}

:global(html[data-theme='dark']) .certified-hero-copy > p,
:global(html[data-theme='dark']) .certified-hero-stat span,
:global(html[data-theme='dark']) .certified-hero-note {
  color: var(--ink-gray-6);
}

:global(html[data-theme='dark']) .certified-eyebrow,
:global(html[data-theme='dark']) .certified-hero-stat,
:global(html[data-theme='dark']) .certified-filter-panel,
:global(html[data-theme='dark']) .certified-card {
  border-color: rgba(199, 174, 255, 0.16);
  background: rgba(129, 80, 223, 0.08);
}

@media (max-width: 1100px) {
  .certified-filter-panel {
    align-items: stretch;
    flex-direction: column;
  }

  .certified-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 820px) {
  .certified-hero {
    grid-template-columns: minmax(0, 1fr);
    padding-inline: clamp(1.25rem, 5vw, 2.5rem);
  }

  .certified-hero-stat {
    max-width: 26rem;
  }

  .certified-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 639px) {
  .certified-header-cta {
    padding-inline: 0.65rem !important;
  }

  .certified-hero {
    padding-block: 3.5rem;
  }

  .certified-hero::before {
    top: -20rem;
    right: -18rem;
    opacity: 0.55;
  }

  .certified-hero::after {
    opacity: 0.55;
  }

  .certified-hero h1 {
    max-width: 15ch;
  }

  .certified-hero-actions,
  .certified-directory-heading,
  .certified-filter-main,
  .certified-filter-actions,
  .certified-pagination {
    align-items: stretch;
    flex-direction: column;
  }

  .certified-primary-action {
    width: 100%;
  }

  .certified-hero-stat {
    min-height: 9rem;
    padding: 1.25rem;
  }

  .certified-result-count {
    align-self: flex-start;
  }

  .certified-filter-panel {
    padding: 0.85rem;
  }

  .certified-name-search,
  .certified-category-filter {
    width: 100%;
  }

  .certified-clear-filters {
    width: 100%;
  }

  .certified-grid {
    grid-template-columns: minmax(0, 1fr);
    gap: 1rem;
  }

  .certified-card {
    min-height: 17.5rem;
  }

  .certified-load-more {
    width: 100%;
  }
}

@media (prefers-reduced-motion: reduce) {
  .certified-primary-action,
  .certified-card,
  .certified-card-footer svg {
    transition: none;
  }

  .certified-skeleton {
    animation: none;
  }
}
</style>
