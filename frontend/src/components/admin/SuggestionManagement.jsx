import React from 'react'
import { useMutation, useQueryClient } from 'react-query'
import { adminAPI } from '../../services/api'
import toast from 'react-hot-toast'
import { format } from 'date-fns'
import { tr } from 'date-fns/locale'

const SuggestionManagement = ({ suggestions }) => {
  const queryClient = useQueryClient()

  // Delete suggestion mutation
  const deleteMutation = useMutation(adminAPI.deleteSuggestion, {
    onSuccess: () => {
      queryClient.invalidateQueries('admin-suggestions')
      toast.success('Öneri silindi.')
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Öneri silinirken hata oluştu.')
    }
  })

  const handleDelete = (suggestionId) => {
    if (window.confirm('Bu öneriyi silmek istediğinizden emin misiniz?')) {
      deleteMutation.mutate(suggestionId)
    }
  }

  const formatDate = (dateString) => {
    try {
      return format(new Date(dateString), 'dd MMMM yyyy, HH:mm', { locale: tr })
    } catch {
      return 'Geçersiz tarih'
    }
  }

  const getTypeColor = (type) => {
    switch (type) {
      case 'öneri': return 'bg-success'
      case 'şikayet': return 'bg-danger'
      case 'hata_bildirimi': return 'bg-warning'
      default: return 'bg-secondary'
    }
  }

  return (
    <div>
      {/* Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h3 className="h4 mb-0">Öneri/Şikayet Yönetimi</h3>
        <div className="text-muted">
          <i className="fas fa-info-circle me-1"></i>
          Toplam {suggestions.length} öneri/şikayet
        </div>
      </div>

      {/* Suggestions List */}
      <div className="card">
        <div className="card-body">
          {suggestions.length === 0 ? (
            <div className="text-center py-4">
              <i className="fas fa-lightbulb fa-3x text-muted mb-3"></i>
              <h5 className="text-muted">Henüz öneri/şikayet bulunmuyor</h5>
              <p className="text-muted">Kullanıcılardan gelen öneri ve şikayetler burada görünecek.</p>
            </div>
          ) : (
            <div className="row">
              {suggestions.map((suggestion) => (
                <div key={suggestion.id} className="col-md-6 mb-4">
                  <div className="card h-100">
                    <div className="card-header d-flex justify-content-between align-items-center">
                      <span className={`badge ${getTypeColor(suggestion.suggestion_type)}`}>
                        {suggestion.suggestion_type}
                      </span>
                      <small className="text-muted">
                        {formatDate(suggestion.created_at)}
                      </small>
                    </div>
                    <div className="card-body">
                      <h6 className="card-title">{suggestion.suggestion_title}</h6>
                      <p className="card-text text-muted">
                        {suggestion.suggestion_text}
                      </p>
                    </div>
                    <div className="card-footer">
                      <button
                        className="btn btn-outline-danger btn-sm"
                        onClick={() => handleDelete(suggestion.id)}
                      >
                        <i className="fas fa-trash me-1"></i>
                        Sil
                      </button>
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

export default SuggestionManagement


