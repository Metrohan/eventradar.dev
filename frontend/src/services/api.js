import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('admin_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('admin_token')
      // Dispatch custom event instead of full page reload
      window.dispatchEvent(new CustomEvent('auth:logout'))
    }
    return Promise.reject(error)
  }
)

// Public API endpoints (converted from Flask routes)
export const publicAPI = {
  // Get all events (converted from /events)
  getEvents: (activeOnly = true, page = 1, pageSize = 200) =>
    api.get(`/events?active_only=${activeOnly}&page=${page}&page_size=${pageSize}`),

  // Canonical event-source catalog
  getSources: () =>
    api.get('/sources'),

  getBlogPosts: () =>
    api.get('/blog'),
  getBlogPost: (slug) =>
    api.get(`/blog/${encodeURIComponent(slug)}`),

  // Get single event by id
  getEventById: (id) =>
    api.get(`/events/${id}`),

  // Get all announcements (converted from /api/announcements)
  getAnnouncements: () =>
    api.get('/announcements'),

  // Get latest announcement
  getLatestAnnouncement: () =>
    api.get('/announcements/latest'),

  // Platform status
  getStatus: () =>
    api.get('/status'),

  // Email subscription (double opt-in)
  subscribeEmail: (email) =>
    api.post('/subscribe', { email }),
  confirmSubscription: (token) =>
    api.get(`/subscribe/confirm?token=${encodeURIComponent(token)}`),
  unsubscribe: (token) =>
    api.get(`/subscribe/unsubscribe?token=${encodeURIComponent(token)}`),

  // Browser push
  getVapidPublicKey: () =>
    api.get('/push/vapid-public-key'),
  pushSubscribe: (subscription) =>
    api.post('/push/subscribe', subscription),
  pushUnsubscribe: (endpoint) =>
    api.post('/push/unsubscribe', { endpoint }),
}

// Admin API endpoints (converted from Flask admin routes)
export const adminAPI = {
  // Authentication (converted from /admin/admin)
  login: (credentials) =>
    api.post('/admin/login', credentials),

  // Event management (converted from /events/* routes)
  getEvents: () =>
    api.get('/admin/events'),

  createEvent: (eventData) =>
    api.post('/admin/events', eventData),

  updateEvent: (eventId, eventData) =>
    api.put(`/admin/events/${eventId}`, eventData),

  deleteEvent: (eventId) =>
    api.delete(`/admin/events/${eventId}`),

  // Announcement management (converted from /announcements/* routes)
  getAnnouncements: () =>
    api.get('/admin/announcements'),

  createAnnouncement: (announcementData) =>
    api.post('/admin/announcements', announcementData),

  deleteAnnouncement: (announcementId) =>
    api.delete(`/admin/announcements/${announcementId}`),

  // Suggestion management (converted from /suggestions/* routes)
  getSuggestions: () =>
    api.get('/admin/suggestions'),

  deleteSuggestion: (suggestionId) =>
    api.delete(`/admin/suggestions/${suggestionId}`),

  // Event request management (converted from /events/requests)
  getEventRequests: () =>
    api.get('/admin/event-requests'),

  deleteEventRequest: (requestId) =>
    api.delete(`/admin/event-requests/${requestId}`),

  // Scraper Control
  getScraperlogs: (limit = 50) =>
    api.get(`/admin/scrapers/logs?limit=${limit}`),

  getScraperStatus: () =>
    api.get('/admin/scrapers/status'),

  triggerScraper: (source) =>
    api.post(`/admin/scrapers/trigger?source=${source}`),

  // Notification Management
  getNotificationStats: () =>
    api.get('/admin/notifications/stats'),

  getSubscribers: () =>
    api.get('/admin/notifications/subscribers'),

  broadcastMessage: (data) =>
    api.post('/admin/notifications/broadcast', data),

  // Analytics
  getTrafficStats: (days = 30) =>
    api.get(`/admin/analytics/traffic?days=${days}`),

  getDataQuality: () =>
    api.get('/admin/quality'),
}

// Form submission endpoints (converted from Flask form routes)
export const formAPI = {
  // Submit event request (converted from /requests/etkinlik-talep)
  submitEventRequest: (requestData) =>
    api.post('/event-requests', requestData),

  // Submit suggestion (converted from /suggestions/oneri_sikayet)
  submitSuggestion: (suggestionData) =>
    api.post('/suggestions', suggestionData),
}

export default api


