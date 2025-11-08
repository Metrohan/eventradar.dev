import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { useAuth } from '../contexts/AuthContext'
import { adminAPI } from '../services/api'
import toast from 'react-hot-toast'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'
import EventManagement from '../components/admin/EventManagement'
import AnnouncementManagement from '../components/admin/AnnouncementManagement'
import SuggestionManagement from '../components/admin/SuggestionManagement'
import EventRequestManagement from '../components/admin/EventRequestManagement'

const AdminDashboard = () => {
  const { isAuthenticated } = useAuth()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState('events')

  // Redirect if not authenticated
  if (!isAuthenticated) {
    window.location.href = '/admin/login'
    return null
  }

  // Fetch dashboard data (converted from Flask dashboard route)
  const { 
    data: eventsData, 
    isLoading: eventsLoading, 
    error: eventsError 
  } = useQuery('admin-events', () => adminAPI.getEvents())

  const { 
    data: announcementsData, 
    isLoading: announcementsLoading 
  } = useQuery('admin-announcements', () => adminAPI.getAnnouncements())

  const { 
    data: suggestionsData, 
    isLoading: suggestionsLoading 
  } = useQuery('admin-suggestions', () => adminAPI.getSuggestions())

  const { 
    data: requestsData, 
    isLoading: requestsLoading 
  } = useQuery('admin-requests', () => adminAPI.getEventRequests())

  if (eventsLoading || announcementsLoading || suggestionsLoading || requestsLoading) {
    return <LoadingSpinner message="Dashboard yükleniyor..." />
  }

  if (eventsError) {
    return <ErrorMessage message="Dashboard verileri yüklenirken hata oluştu." />
  }

  const events = eventsData?.data?.events || []
  const announcements = announcementsData?.data?.announcements || []
  const suggestions = suggestionsData?.data?.suggestions || []
  const requests = requestsData?.data?.requests || []

  const stats = {
    totalEvents: events.length,
    activeEvents: events.filter(e => e.is_active).length,
    totalAnnouncements: announcements.length,
    totalSuggestions: suggestions.length,
    totalRequests: requests.length
  }

  const tabs = [
    { id: 'events', label: 'Etkinlikler', icon: 'fas fa-calendar-alt', count: stats.totalEvents },
    { id: 'announcements', label: 'Duyurular', icon: 'fas fa-bullhorn', count: stats.totalAnnouncements },
    { id: 'suggestions', label: 'Öneriler', icon: 'fas fa-lightbulb', count: stats.totalSuggestions },
    { id: 'requests', label: 'Talepler', icon: 'fas fa-inbox', count: stats.totalRequests }
  ]

  return (
    <div className="container-fluid py-4">
      {/* Header */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="d-flex justify-content-between align-items-center">
            <h1 className="h2 mb-0">
              <i className="fas fa-tachometer-alt me-2"></i>
              Admin Dashboard
            </h1>
            <div className="text-muted">
              <i className="fas fa-clock me-1"></i>
              Son Güncelleme: {new Date().toLocaleString('tr-TR')}
            </div>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="row mb-4">
        <div className="col-md-3 mb-3">
          <div className="card bg-primary text-white">
            <div className="card-body">
              <div className="d-flex justify-content-between">
                <div>
                  <h4 className="card-title">{stats.totalEvents}</h4>
                  <p className="card-text">Toplam Etkinlik</p>
                </div>
                <i className="fas fa-calendar-alt fa-2x"></i>
              </div>
            </div>
          </div>
        </div>
        
        <div className="col-md-3 mb-3">
          <div className="card bg-success text-white">
            <div className="card-body">
              <div className="d-flex justify-content-between">
                <div>
                  <h4 className="card-title">{stats.activeEvents}</h4>
                  <p className="card-text">Aktif Etkinlik</p>
                </div>
                <i className="fas fa-check-circle fa-2x"></i>
              </div>
            </div>
          </div>
        </div>
        
        <div className="col-md-3 mb-3">
          <div className="card bg-warning text-white">
            <div className="card-body">
              <div className="d-flex justify-content-between">
                <div>
                  <h4 className="card-title">{stats.totalSuggestions}</h4>
                  <p className="card-text">Öneri/Şikayet</p>
                </div>
                <i className="fas fa-lightbulb fa-2x"></i>
              </div>
            </div>
          </div>
        </div>
        
        <div className="col-md-3 mb-3">
          <div className="card bg-info text-white">
            <div className="card-body">
              <div className="d-flex justify-content-between">
                <div>
                  <h4 className="card-title">{stats.totalRequests}</h4>
                  <p className="card-text">Etkinlik Talebi</p>
                </div>
                <i className="fas fa-inbox fa-2x"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="row mb-4">
        <div className="col-12">
          <ul className="nav nav-tabs">
            {tabs.map(tab => (
              <li className="nav-item" key={tab.id}>
                <button
                  className={`nav-link ${activeTab === tab.id ? 'active' : ''}`}
                  onClick={() => setActiveTab(tab.id)}
                >
                  <i className={`${tab.icon} me-2`}></i>
                  {tab.label}
                  <span className="badge bg-secondary ms-2">{tab.count}</span>
                </button>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Tab Content */}
      <div className="row">
        <div className="col-12">
          {activeTab === 'events' && <EventManagement events={events} />}
          {activeTab === 'announcements' && <AnnouncementManagement announcements={announcements} />}
          {activeTab === 'suggestions' && <SuggestionManagement suggestions={suggestions} />}
          {activeTab === 'requests' && <EventRequestManagement requests={requests} />}
        </div>
      </div>
    </div>
  )
}

export default AdminDashboard


