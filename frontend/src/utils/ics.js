const DEFAULT_DURATION_HOURS = 2

const escapeICSText = (text) =>
  String(text || '')
    .replace(/\\/g, '\\\\')
    .replace(/;/g, '\\;')
    .replace(/,/g, '\\,')
    .replace(/\n/g, '\\n')

const toICSDate = (date) => {
  const pad = (n) => String(n).padStart(2, '0')
  return (
    `${date.getUTCFullYear()}${pad(date.getUTCMonth() + 1)}${pad(date.getUTCDate())}` +
    `T${pad(date.getUTCHours())}${pad(date.getUTCMinutes())}${pad(date.getUTCSeconds())}Z`
  )
}

export const generateICSContent = (event, detailUrl) => {
  if (!event?.date) return null

  const start = new Date(event.date)
  if (Number.isNaN(start.getTime())) return null

  const end = new Date(start.getTime() + DEFAULT_DURATION_HOURS * 60 * 60 * 1000)
  const now = new Date()

  const lines = [
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    'PRODID:-//EventRadar//eventradar.dev//TR',
    'CALSCALE:GREGORIAN',
    'BEGIN:VEVENT',
    `UID:event-${event.id}@eventradar.dev`,
    `DTSTAMP:${toICSDate(now)}`,
    `DTSTART:${toICSDate(start)}`,
    `DTEND:${toICSDate(end)}`,
    `SUMMARY:${escapeICSText(event.title)}`,
    `DESCRIPTION:${escapeICSText(event.description || '')}`,
    `LOCATION:${escapeICSText(event.location || '')}`,
    `URL:${escapeICSText(detailUrl || event.url || '')}`,
    'END:VEVENT',
    'END:VCALENDAR',
  ]

  return lines.join('\r\n')
}

export const downloadICS = (event, detailUrl) => {
  const content = generateICSContent(event, detailUrl)
  if (!content) return false

  const blob = new Blob([content], { type: 'text/calendar;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${(event.title || 'etkinlik').slice(0, 60).replace(/[^\w\s-]/g, '')}.ics`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  return true
}
