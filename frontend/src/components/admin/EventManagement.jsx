import React, { useState } from 'react'
import { useMutation, useQueryClient } from 'react-query'
import { adminAPI } from '../../services/api'
import toast from 'react-hot-toast'
import EventForm from './EventForm'
import { format } from 'date-fns'
import { tr } from 'date-fns/locale'

const EventManagement = ({ events }) => {
  const queryClient = useQueryClient()
  const [editingEvent, setEditingEvent] = useState(null)
  const [showForm, setShowForm] = useState(false)

  // Delete event mutation
  const deleteMutation = useMutation(adminAPI.deleteEvent, {
    onSuccess: () => {
      queryClient.invalidateQueries('admin-events')
      toast.success('Etkinlik silindi.')
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Etkinlik silinirken hata oluştu.')
    }
  })

  const handleDelete = (eventId) => {
    if (window.confirm('Bu etkinliği silmek istediğinizden emin misiniz?')) {
      deleteMutation.mutate(eventId)
    }
  }

  const handleEdit = (event) => {
    setEditingEvent(event)
    setShowForm(true)
  }

  const handleFormClose = () => {
    setShowForm(false)
    setEditingEvent(null)
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Tarih belirtilmemiş'
    try {
      return format(new Date(dateString), 'dd MMMM yyyy, HH:mm', { locale: tr })
    } catch {
      return 'Geçersiz tarih'
    }
  }

  return (
    <div>
      {/* Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h3 className="h4 mb-0">Etkinlik Yönetimi</h3>
        <button
          className="btn btn-primary"
          onClick={() => setShowForm(true)}
        >
          <i className="fas fa-plus me-2"></i>
          Yeni Etkinlik
        </button>
      </div>

      {/* Events Table */}
      <div className="card">
        <div className="card-body">
          {events.length === 0 ? (
            <div className="text-center py-4">
              <i className="fas fa-calendar-times fa-3x text-muted mb-3"></i>
              <h5 className="text-muted">Henüz etkinlik bulunmuyor</h5>
              <p className="text-muted">İlk etkinliği eklemek için yukarıdaki butona tıklayın.</p>
            </div>
          ) : (
            <div className="table-responsive">
              <table className="table table-hover">
                <thead>
                  <tr>
                    <th>Başlık</th>
                    <th>Tarih</th>
                    <th>Konum</th>
                    <th>Kaynak</th>
                    <th>Durum</th>
                    <th>İşlemler</th>
                  </tr>
                </thead>
                <tbody>
                  {events.map((event) => (
                    <tr key={event.id}>
                      <td>
                        <div>
                          <strong>{event.title}</strong>
                          {event.description && (
                            <div className="text-muted small">
                              {event.description.substring(0, 100)}...
                            </div>
                          )}
                        </div>
                      </td>
                      <td>{formatDate(event.date)}</td>
                      <td>{event.location || '-'}</td>
                      <td>
                        <span className="badge bg-secondary">{event.source}</span>
                      </td>
                      <td>
                        <span className={`badge ${event.is_active ? 'bg-success' : 'bg-danger'}`}>
                          {event.is_active ? 'Açık' : 'Kapalı'}
                        </span>
                      </td>
                      <td>
                        <div className="btn-group btn-group-sm">
                          <button
                            className="btn btn-outline-primary"
                            onClick={() => handleEdit(event)}
                            title="Düzenle"
                          >
                            <i className="fas fa-edit"></i>
                          </button>
                          <button
                            className="btn btn-outline-danger"
                            onClick={() => handleDelete(event.id)}
                            title="Sil"
                          >
                            <i className="fas fa-trash"></i>
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Event Form Modal */}
      {showForm && (
        <EventForm
          event={editingEvent}
          onClose={handleFormClose}
          onSuccess={() => {
            queryClient.invalidateQueries('admin-events')
            handleFormClose()
          }}
        />
      )}
    </div>
  )
}

export default EventManagement


