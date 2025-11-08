import React, { useState } from 'react'
import { useMutation, useQueryClient } from 'react-query'
import { adminAPI } from '../../services/api'
import toast from 'react-hot-toast'
import AnnouncementForm from './AnnouncementForm'
import { format } from 'date-fns'
import { tr } from 'date-fns/locale'

const AnnouncementManagement = ({ announcements }) => {
  const queryClient = useQueryClient()
  const [editingAnnouncement, setEditingAnnouncement] = useState(null)
  const [showForm, setShowForm] = useState(false)

  // Delete announcement mutation
  const deleteMutation = useMutation(adminAPI.deleteAnnouncement, {
    onSuccess: () => {
      queryClient.invalidateQueries('admin-announcements')
      toast.success('Duyuru silindi.')
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Duyuru silinirken hata oluştu.')
    }
  })

  const handleDelete = (announcementId) => {
    if (window.confirm('Bu duyuruyu silmek istediğinizden emin misiniz?')) {
      deleteMutation.mutate(announcementId)
    }
  }

  const handleEdit = (announcement) => {
    setEditingAnnouncement(announcement)
    setShowForm(true)
  }

  const handleFormClose = () => {
    setShowForm(false)
    setEditingAnnouncement(null)
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
        <h3 className="h4 mb-0">Duyuru Yönetimi</h3>
        <button
          className="btn btn-primary"
          onClick={() => setShowForm(true)}
        >
          <i className="fas fa-plus me-2"></i>
          Yeni Duyuru
        </button>
      </div>

      {/* Announcements Table */}
      <div className="card">
        <div className="card-body">
          {announcements.length === 0 ? (
            <div className="text-center py-4">
              <i className="fas fa-bullhorn fa-3x text-muted mb-3"></i>
              <h5 className="text-muted">Henüz duyuru bulunmuyor</h5>
              <p className="text-muted">İlk duyuruyu eklemek için yukarıdaki butona tıklayın.</p>
            </div>
          ) : (
            <div className="table-responsive">
              <table className="table table-hover">
                <thead>
                  <tr>
                    <th>Başlık</th>
                    <th>Mesaj</th>
                    <th>Oluşturulma Tarihi</th>
                    <th>İşlemler</th>
                  </tr>
                </thead>
                <tbody>
                  {announcements.map((announcement) => (
                    <tr key={announcement.id}>
                      <td>
                        <strong>{announcement.title}</strong>
                      </td>
                      <td>
                        <div className="text-muted">
                          {announcement.message.length > 100 
                            ? `${announcement.message.substring(0, 100)}...`
                            : announcement.message
                          }
                        </div>
                      </td>
                      <td>{formatDate(announcement.created_at)}</td>
                      <td>
                        <div className="btn-group btn-group-sm">
                          <button
                            className="btn btn-outline-danger"
                            onClick={() => handleDelete(announcement.id)}
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

      {/* Announcement Form Modal */}
      {showForm && (
        <AnnouncementForm
          announcement={editingAnnouncement}
          onClose={handleFormClose}
          onSuccess={() => {
            queryClient.invalidateQueries('admin-announcements')
            handleFormClose()
          }}
        />
      )}
    </div>
  )
}

export default AnnouncementManagement


