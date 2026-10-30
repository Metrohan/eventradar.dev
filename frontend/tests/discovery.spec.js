import { test, expect } from '@playwright/test'

test.skip(!process.env.SSR_EVENT_SLUG, 'Run scripts/check_discovery_browser.py for isolated real-backend SSR checks')
const slug = process.env.SSR_EVENT_SLUG

test('event and collections work without JavaScript', async ({ browser }) => {
  const context = await browser.newContext({ javaScriptEnabled: false })
  const page = await context.newPage()
  await page.goto(`${process.env.PLAYWRIGHT_BASE_URL}/events/${slug}`)
  await expect(page.locator('h1')).toHaveText('İstanbul Python Atölyesi')
  await expect(page.locator('main')).toContainText('<script>evil()</script>')
  await expect(page.locator('link[rel="canonical"]')).toHaveAttribute('href', `https://eventradar.dev/events/${slug}`)
  await page.getByRole('link', { name: 'Şehirler', exact: true }).click()
  await page.getByRole('link', { name: 'İstanbul', exact: true }).click()
  await expect(page.getByRole('link', { name: 'İstanbul Python Atölyesi' })).toHaveAttribute('href', `/events/${slug}`)
  await context.close()
})

test('homepage click opens a real server-rendered event document', async ({ page }) => {
  await page.goto('/')
  await page.getByRole('link', { name: 'İstanbul Python Atölyesi', exact: true }).click()
  await expect(page).toHaveURL(new RegExp(`/events/${slug}$`))
  await expect(page.locator('h1')).toHaveText('İstanbul Python Atölyesi')
  await page.goBack()
  await expect(page.locator('.event-card')).toHaveCount(1)
})

test('missing and manually hidden events return real 404', async ({ request }) => {
  for (const path of ['/events/no-such-event', '/events/hidden-test-event']) {
    const response = await request.get(path)
    expect(response.status()).toBe(404)
    expect(await response.text()).toContain('noindex, follow')
  }
})
