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

test('event SEO omits unsupported free/availability/online claims', async ({ page }) => {
  await page.route('**/api/events/1', route => route.fulfill({ json: { ...future, location: null } }))
  await page.goto('/etkinlik/1')
  await expect(page.locator('#event-jsonld')).toBeAttached()
  const schema = await page.locator('#event-jsonld').evaluate(el => JSON.parse(el.textContent))
  expect(schema).not.toHaveProperty('isAccessibleForFree')
  expect(schema).not.toHaveProperty('offers')
  expect(schema).not.toHaveProperty('location')
  expect(schema).not.toHaveProperty('eventAttendanceMode')
})
