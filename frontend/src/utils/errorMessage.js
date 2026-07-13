// FastAPI returns `detail` as a plain string for most errors, but as an array
// of {loc, msg, type} objects for 422 validation errors. Rendering that array
// directly in a toast crashes React ("objects are not valid as a child"), so
// every error path must go through here instead of reading `detail` raw.
export const getErrorMessage = (error, fallback) => {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string' && detail.trim()) return detail
  if (Array.isArray(detail) && detail.length) {
    return detail.map(item => item?.msg || String(item)).join(', ')
  }
  return fallback
}
