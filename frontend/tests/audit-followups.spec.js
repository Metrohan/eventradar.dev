import { test, expect } from '@playwright/test'
test.use({ timezoneId: 'Europe/Istanbul' })

const future = { id: 1, title: 'Future event', url: 'https://example.com/event', source: 'Test', date: '2030-01-15T15:00:00', application_deadline: null, is_active: true, tags: [] }
const past = { ...future, id: 2, title: 'Past event', date: '2020-01-15T15:00:00', is_active: false }

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem('eventradar:lang', 'en'))
  await page.route('**/api/**', route => {
    const url = new URL(route.request().url())
    const path = url.pathname
    const json = path === '/api/events' ? { events: url.searchParams.get('active_only') === 'false' ? [future, past] : [future], total_count: 1, total_pages: 1 }
      : path === '/api/admin/events' ? { events: [future], total_count: 1 }
        : path === '/api/sources' ? [] : null
    return route.fulfill({ json })
  })
})

test('history toggle retrieves past events under its own query', async ({ page }) => {
  await page.goto('/')
  await expect(page.locator('.event-card')).toHaveCount(1)
  await page.locator('input[type="checkbox"]').first().check()
  await expect(page.getByText('Past event', { exact: true })).toBeVisible()
  await page.locator('input[type="checkbox"]').first().uncheck()
  await expect(page.getByText('Past event', { exact: true })).toHaveCount(0)
})

test('denied storage reads and writes preserve public rendering', async ({ page }) => {
  await page.addInitScript(() => {
    Storage.prototype.getItem = () => { throw new DOMException('Storage denied', 'SecurityError') }
    Storage.prototype.setItem = () => { throw new DOMException('Storage denied', 'SecurityError') }
    Storage.prototype.removeItem = () => { throw new DOMException('Storage denied', 'SecurityError') }
  })
  await page.goto('/')
  await expect(page.locator('.event-card')).toHaveCount(1)
  await page.locator('.favorite-button').click()
  await expect(page.locator('.favorite-button')).toHaveClass(/active/)
})

test('admin editor preserves wall-clock time and serializes blank dates as null', async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem('admin_token', 'synthetic-test-token'))
  await page.goto('/admin/dashboard')
  await page.getByTitle('Düzenle', { exact: true }).first().click()
  await expect(page.locator('#date')).toHaveValue('2030-01-15T15:00')
  await page.locator('#date').fill('')
  const requestPromise = page.waitForRequest(request => request.method() === 'PUT' && request.url().includes('/api/admin/events/'))
  await page.getByRole('button', { name: /Güncelle|Kaydet/ }).last().click()
  const payload = (await requestPromise).postDataJSON()
  expect(payload.date).toBeNull()
  expect(payload.application_deadline).toBeNull()
})

test('event SEO omits unsupported free/availability claims', async ({ page }) => {
  await page.route('**/api/events/1', route => route.fulfill({ json: { ...future, location: 'Istanbul' } }))
  await page.goto('/etkinlik/1')
  await expect(page.locator('#event-jsonld')).toBeAttached()
  const schema = await page.locator('#event-jsonld').evaluate(el => JSON.parse(el.textContent))
  expect(schema).not.toHaveProperty('isAccessibleForFree')
  expect(schema).not.toHaveProperty('offers')
  expect(schema.location).toMatchObject({ '@type': 'Place', name: 'Istanbul' })
})

async function eventSchema(page, overrides) {
  await page.route('**/api/events/1', route => route.fulfill({ json: { ...future, ...overrides } }))
  await page.goto('/etkinlik/1')
  await expect(page.locator('#event-jsonld')).toBeAttached()
  return page.locator('#event-jsonld').evaluate(el => JSON.parse(el.textContent))
}

test('in-person event with a known city gets a postal address', async ({ page }) => {
  const schema = await eventSchema(page, { location: 'Kadıköy', city: 'İstanbul', attendance: 'in_person' })
  expect(schema.eventAttendanceMode).toMatch(/OfflineEventAttendanceMode$/)
  expect(schema.location).toEqual({
    '@type': 'Place',
    name: 'Kadıköy',
    address: { '@type': 'PostalAddress', addressLocality: 'İstanbul', addressCountry: 'TR' },
  })
})

test('hybrid event is mixed, with a place and a virtual location', async ({ page }) => {
  const schema = await eventSchema(page, { location: 'Hibrit ( Istanbul & Zoom )', city: 'İstanbul', attendance: 'hybrid' })
  expect(schema.eventAttendanceMode).toMatch(/MixedEventAttendanceMode$/)
  expect(schema.location.map(l => l['@type'])).toEqual(['Place', 'VirtualLocation'])
})

test('event not yet refreshed (no structured fields) keeps the old markup', async ({ page }) => {
  const schema = await eventSchema(page, { location: 'Istanbul' })
  expect(schema.eventAttendanceMode).toMatch(/OfflineEventAttendanceMode$/)
  expect(schema.location).toEqual({ '@type': 'Place', name: 'Istanbul', address: 'Istanbul' })
})

test('admin analytics lists the AI assistants that sent visitors', async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem('admin_token', 'synthetic-test-token'))
  const stats = (ai) => ({ daily_traffic: [], today_visitors: 1, total_visitors: 5, top_pages: [], ai_referrals: ai })
  await page.route('**/api/admin/analytics/traffic*', route => route.fulfill({
    json: stats({ total: 3, by_source: [{ source: 'chatgpt', count: 2 }, { source: 'claude', count: 1 }], top_pages: [{ path: '/events/a', count: 2 }] }),
  }))
  await page.goto('/admin/analytics')
  const card = page.getByTestId('ai-referrals')
  await expect(card.getByRole('cell', { name: 'chatgpt', exact: true })).toBeVisible()
  await expect(card.getByRole('cell', { name: 'claude', exact: true })).toBeVisible()
  await expect(card.getByText('/events/a')).toBeVisible()
})

test('admin analytics says so when no assistant has sent anyone yet', async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem('admin_token', 'synthetic-test-token'))
  await page.route('**/api/admin/analytics/traffic*', route => route.fulfill({
    json: { daily_traffic: [], today_visitors: 0, total_visitors: 0, top_pages: [], ai_referrals: { total: 0, by_source: [], top_pages: [] } },
  }))
  await page.goto('/admin/analytics')
  await expect(page.getByTestId('ai-referrals').getByText('Henüz yönlendirme yok.')).toBeVisible()
})

test('tech-related filter narrows the list; with it off every event is shown', async ({ page }) => {
  const events = [
    { ...future, id: 11, title: 'Python Atölyesi', topic: 'technical' },
    { ...future, id: 12, title: 'Engineering Career Summit', topic: 'adjacent' },
    { ...future, id: 13, title: 'Talent Summit', topic: 'general' },
  ]
  await page.route('**/api/events?*', route => route.fulfill({ json: { events, total_count: 3, total_pages: 1 } }))
  await page.goto('/')
  await expect(page.locator('.event-card')).toHaveCount(3)
  await page.getByText('Tech related', { exact: true }).click()
  await expect(page.locator('.event-card')).toHaveCount(2)
  await expect(page.getByText('Talent Summit', { exact: true })).toHaveCount(0)
  await expect(page).toHaveURL(/tech=1/)
  await page.getByText('Tech related', { exact: true }).click()
  await expect(page.locator('.event-card')).toHaveCount(3)
})

test('event without a location gets no Event JSON-LD (Google requires one)', async ({ page }) => {
  await page.route('**/api/events/1', route => route.fulfill({ json: { ...future, location: null } }))
  await page.goto('/etkinlik/1')
  // The breadcrumb is injected by the same effect, so once it exists the Event
  // markup has had its chance to appear.
  await expect(page.locator('#breadcrumb-jsonld')).toBeAttached()
  await expect(page.locator('#event-jsonld')).toHaveCount(0)
})
