import { test, expect } from '@playwright/test'
const ev = id => ({ id, title: `Event ${id}`, description: 'd', date: '2030-01-15T18:00:00', application_deadline: null, location: 'Online', url: 'https://example.com/e', source: 'Test', is_active: true, tags: ['hackathon'], scraped_at: '2026-01-01T00:00:00', image_url: null, thumbnail_url: null })
test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem('eventradar:lang', 'en'))
  await page.route('**/api/**', route => {
    const p = new URL(route.request().url()).pathname
    const json = p === '/api/events' ? { events: [ev(1)], total_pages: 1, total_count: 1 } : p === '/api/events/1' ? ev(1) : p === '/api/sources' ? [] : p === '/api/status' ? { active_events: 1, total_events: 1, scrapers: [] } : null
    return route.fulfill({ status: 200, json })
  })
})
const publicRoutes = ['/', '/etkinlik/1', '/bootcamp-rehberi', '/etkinlik-talep', '/oneri-sikayet', '/egitim-kaynaklari', '/status', '/takvim', '/abone-onay?token=x', '/abone-iptal?token=x', '/blog', '/hackathonlar', '/bootcamplar', '/online-etkinlikler', '/bu-haftaki-etkinlikler', '/son-basvurular', '/error/server', '/redirect', '/no-such-page']
for (const r of publicRoutes) {
  test(`route ${r} renders without page errors`, async ({ page }) => {
    const errors = []
    page.on('pageerror', e => errors.push(e.message))
    await page.goto(r)
    await expect(page.locator('#root')).not.toBeEmpty()
    await page.waitForTimeout(400)
    expect(errors).toEqual([])
  })
}
test('protected admin routes redirect to login', async ({ page }) => {
  for (const r of ['/admin/dashboard', '/admin/scrapers', '/admin/notifications', '/admin/analytics']) {
    await page.goto(r)
    await expect(page).toHaveURL(/\/admin\/login$/)
  }
})
test('search params stay in sync and client navigation works', async ({ page }) => {
  await page.goto('/?q=Event')
  await expect(page.locator('.event-card')).toHaveCount(1)
  await page.getByRole('link', { name: 'Event 1', exact: true }).click()
  await expect(page).toHaveURL(/\/etkinlik\/1$/)
  await page.goBack()
  await expect(page).toHaveURL(/\/\?q=Event$|\/$/)
  await page.goForward()
  await expect(page).toHaveURL(/\/etkinlik\/1$/)
})
