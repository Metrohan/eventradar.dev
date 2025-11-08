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
      window.location.href = '/admin/login'
    }
    return Promise.reject(error)
  }
)

// Public API endpoints (converted from Flask routes)
export const publicAPI = {
  // Get all events (converted from /events)
  getEvents: (activeOnly = true) => 
    api.get(`/events?active_only=${activeOnly}`),
  
  // Get all announcements (converted from /api/announcements)
  getAnnouncements: () => 
    api.get('/announcements'),
  
  // Get latest announcement
  getLatestAnnouncement: () => 
    api.get('/announcements/latest'),
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
}

// Form submission endpoints (converted from Flask form routes)
export const formAPI = {
  // Submit event request (converted from /requests/etkinlik-talep)
  submitEventRequest: (requestData) => 
    api.post('/admin/event-requests', requestData),
  
  // Submit suggestion (converted from /suggestions/oneri_sikayet)
  submitSuggestion: (suggestionData) => 
    api.post('/admin/suggestions', suggestionData),
}

export default api


