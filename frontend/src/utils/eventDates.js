// API event timestamps are naive Istanbul dates. Do not reinterpret them in
// the visitor's timezone when deciding whether their calendar day has ended.
export const istanbulDay = (now = new Date()) => new Intl.DateTimeFormat('en-CA', {
  timeZone: 'Europe/Istanbul', year: 'numeric', month: '2-digit', day: '2-digit',
}).format(now)

export const eventDay = value => value?.slice(0, 10)
export const isPastEvent = (event, now = new Date()) => Boolean(event.date && eventDay(event.date) < istanbulDay(now))
