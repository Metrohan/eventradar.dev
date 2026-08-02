// Hydration regression tests for the prerender PoC (docs/adr/0006-prerender-poc.md).
//
// Runs against an already-built + prerendered dist/ (npm run build && npm
// run prerender), served by `vite preview` (see playwright.config.js).
// The API is mocked here for determinism — these tests care whether
// filter/search/favorite interactions work correctly *after hydration*,
// not what data happened to be baked into the prerendered snapshot at
// build time.
import { test, expect } from '@playwright/test'

const FIXTURE_EVENTS = [
  {
    id: 101,
    title: 'React Istanbul Meetup',
    description: 'Frontend topluluk bulusmasi',
    date: '2027-01-15T18:00:00',
    application_deadline: null,
    location: 'İstanbul',
    url: 'https://example.com/react-istanbul',
    image_url: null,
    thumbnail_url: null,
    source: 'Kodluyoruz',
    is_active: true,
    scraped_at: '2027-01-01T00:00:00',
    tags: [],
  },
  {
    id: 102,
    title: 'Ankara Data Bootcamp',
    description: 'Veri bilimi bootcampi',
    date: '2027-02-01T09:00:00',
    application_deadline: null,
    location: 'Ankara',
    url: 'https://example.com/ankara-data',
    image_url: null,
    thumbnail_url: null,
    source: 'Patika',
    is_active: true,
    scraped_at: '2027-01-01T00:00:00',
    tags: [],
  },
]

async function mockApi(page) {
  await page.route('**/api/events**', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        events: FIXTURE_EVENTS,
        total_count: FIXTURE_EVENTS.length,
        page: 1,
        page_size: 200,
        total_pages: 1,
      }),
    }),
  )
  // /api/sources returns a plain array of source objects (not wrapped),
  // consumed by both the source filter dropdown and Footer.jsx.
  await page.route('**/api/sources**', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        { key: 'kodluyoruz', name: 'Kodluyoruz', website: 'https://www.kodluyoruz.org', mode: 'static', enabled: true },
        { key: 'patika', name: 'Patika', website: 'https://www.patika.dev', mode: 'static', enabled: true },
      ]),
    }),
  )
  await page.route('**/api/announcements/latest**', (route) =>
    route.fulfill({ status: 404, contentType: 'application/json', body: '{}' }),
  )
}

test.beforeEach(async ({ page }) => {
  // Each Playwright test gets a fresh browser context, so localStorage
  // already starts empty — no explicit clearing needed (and clearing via
  // addInitScript would also wipe it on the reload in the favorites test,
  // defeating the point of that test).
  await mockApi(page)
})

test('prerendered homepage renders event cards after hydration', async ({ page }) => {
  await page.goto('/')
  await expect(page.locator('.event-card')).toHaveCount(FIXTURE_EVENTS.length)
  await expect(page.getByText('React Istanbul Meetup')).toBeVisible()
  await expect(page.getByText('Ankara Data Bootcamp')).toBeVisible()
});

test('search filters the list after hydration', async ({ page }) => {
  await page.goto('/')
  await expect(page.locator('.event-card')).toHaveCount(2)

  await page.locator('.hero-search-input').fill('Ankara')

  await expect(page.locator('.event-card')).toHaveCount(1)
  await expect(page.getByText('Ankara Data Bootcamp')).toBeVisible()
  await expect(page.getByText('React Istanbul Meetup')).toHaveCount(0)
});

test('source filter narrows the list after hydration', async ({ page }) => {
  await page.goto('/')
  await expect(page.locator('.event-card')).toHaveCount(2)

  await page.getByLabel('Platform seçin').selectOption('Patika')

  await expect(page.locator('.event-card')).toHaveCount(1)
  await expect(page.getByText('Ankara Data Bootcamp')).toBeVisible()
});

test('favorite toggle works after hydration and persists across reload', async ({ page }) => {
  await page.goto('/')
  await expect(page.locator('.event-card')).toHaveCount(2)

  const firstFavoriteButton = page.locator('.favorite-button').first()
  await expect(firstFavoriteButton).not.toHaveClass(/active/)

  await firstFavoriteButton.click()
  await expect(firstFavoriteButton).toHaveClass(/active/)

  const stored = await page.evaluate(() =>
    JSON.parse(localStorage.getItem('eventradar:favorites') || '[]'),
  )
  expect(stored).toContain('101')

  // Reload to prove the favorite survives a fresh hydration pass, not just
  // in-memory state from the click.
  await page.reload()
  await expect(page.locator('.event-card')).toHaveCount(2)
  await expect(page.locator('.favorite-button').first()).toHaveClass(/active/)
});

test('language toggle switches UI text and persists across reload', async ({ page }) => {
  await page.goto('/')
  await expect(page.locator('.event-card')).toHaveCount(2)

  // Explicitly clear localStorage first so this test doesn't depend on
  // whatever language a previous test run left behind, and don't assert
  // which language that leaves as the "default" — verified directly (see
  // frontend/tests/hydration.spec.js commit notes) that this sandbox's
  // headless Chromium reports navigator.language as 'en-US' consistently,
  // so with localStorage empty, src/i18n/index.js's detectedLanguage
  // resolves to 'en' (not the 'tr' fallbackLng one might expect at a
  // glance) and main.jsx applies it right after hydration. That's an
  // environment property, not an app guarantee worth pinning a test to —
  // this test only checks that toggling flips the label and persists.
  await page.evaluate(() => localStorage.removeItem('eventradar:lang'))
  await page.reload()
  await expect(page.locator('.event-card')).toHaveCount(2)

  const languageToggle = page.locator('header button', { hasText: /^(TR|EN)$/ })
  await expect(languageToggle).toBeVisible()

  // Assert real page content switches too, not just the toggle's own label —
  // a toggle that flips its own text while the rest of the page silently
  // stays in the old language would not be caught by label-only assertions.
  // The header's "Durum"/"Status" nav link (nav.status) is always visible
  // regardless of viewport/scroll state and isn't dynamic API data, so it's
  // a reliable, unambiguous stand-in for "did the page actually translate".
  const statusLink = page.getByRole('link', { name: /^(Durum|Status)$/ })
  const initialStatusText = await statusLink.textContent()
  expect(['Durum', 'Status']).toContain(initialStatusText)

  const initialLabel = await languageToggle.textContent()
  await languageToggle.click()

  const newLabel = await languageToggle.textContent()
  expect(newLabel).not.toBe(initialLabel)

  // The nav link must flip to the OTHER language, not just re-render.
  const expectedStatusText = initialStatusText === 'Durum' ? 'Status' : 'Durum'
  await expect(statusLink).toHaveText(expectedStatusText)

  const storedLang = await page.evaluate(() => localStorage.getItem('eventradar:lang'))
  expect(['tr', 'en']).toContain(storedLang)

  await page.reload()
  await expect(page.locator('.event-card')).toHaveCount(2)
  const persistedLabel = await page.locator('header button', { hasText: /^(TR|EN)$/ }).textContent()
  expect(persistedLabel).toBe(newLabel)
})
