import React from 'react'
import { useMutation, useQueryClient } from 'react-query'
import { adminAPI } from '../../services/api'
import toast from 'react-hot-toast'
import { format } from 'date-fns'
import { tr } from 'date-fns/locale'

const EventRequestManagement = ({ requests }) => {
  const queryClient = useQueryClient()

  // Delete request mutation
  const deleteMutation = useMutation(adminAPI.deleteEventRequest, {
    onSuccess: () => {
      queryClient.invalidateQueries('admin-requests')
      toast.success('Talep silindi.')
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Talep silinirken hata oluştu.')
    }
  })

  const handleDelete = (requestId) => {
    if (window.confirm('Bu talebi silmek istediğinizden emin misiniz?')) {
      deleteMutation.mutate(requestId)
    }
  }

  const formatDate = (dateString) => {
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
        <h3 className="h4 mb-0">Etkinlik Talebi Yönetimi</h3>
        <div className="text-muted">
          <i className="fas fa-info-circle me-1"></i>
          Toplam {requests.length} talep
        </div>
      </div>

      {/* Requests List */}
      <div className="card">
        <div className="card-body">
          {requests.length === 0 ? (
            <div className="text-center py-4">
              <i className="fas fa-inbox fa-3x text-muted mb-3"></i>
              <h5 className="text-muted">Henüz etkinlik talebi bulunmuyor</h5>
              <p className="text-muted">Kullanıcılardan gelen etkinlik talepleri burada görünecek.</p>
            </div>
          ) : (
            <div className="row">
              {requests.map((request) => (
                <div key={request.id} className="col-md-6 mb-4">
                  <div className="card h-100">
                    <div className="card-header d-flex justify-content-between align-items-center">
                      <span className="badge bg-primary">Etkinlik Talebi</span>
                      <small className="text-muted">
                        {formatDate(request.created_at)}
                      </small>
                    </div>
                    <div className="card-body">
                      <h6 className="card-title">{request.event_title}</h6>
                      {request.event_description && (
                        <p className="card-text text-muted">
                          {request.event_description}
                        </p>
                      )}
                      <div className="mb-2">
                        <strong>Etkinlik Linki:</strong>
                        <br />
                        <a 
                          href={request.event_link} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-primary"
                        >
                          {request.event_link}
                        </a>
                      </div>
                      {request.event_date && (
                        <div className="mb-2">
                          <strong>Tarih:</strong> {formatDate(request.event_date)}
                        </div>
                      )}
                    </div>
                    <div className="card-footer">
                      <div className="btn-group btn-group-sm">
                        <a
                          href={request.event_link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="btn btn-outline-primary"
                        >
                          <i className="fas fa-external-link-alt me-1"></i>
                          Etkinliği Görüntüle
                        </a>
                        <button
                          className="btn btn-outline-danger"
                          onClick={() => handleDelete(request.id)}
                        >
                          <i className="fas fa-trash me-1"></i>
                          Sil
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default EventRequestManagement


