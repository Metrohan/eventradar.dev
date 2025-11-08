import React from 'react'
import { useForm } from 'react-hook-form'
import { useMutation } from 'react-query'
import { adminAPI } from '../../services/api'
import toast from 'react-hot-toast'

const AnnouncementForm = ({ announcement, onClose, onSuccess }) => {
  const isEditing = !!announcement
  const { register, handleSubmit, formState: { errors } } = useForm({
    defaultValues: announcement ? {
      title: announcement.title,
      message: announcement.message
    } : {}
  })

  // Create announcement mutation
  const mutation = useMutation(adminAPI.createAnnouncement, {
    onSuccess: () => {
      toast.success('Duyuru eklendi.')
      onSuccess()
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'İşlem sırasında hata oluştu.')
    }
  })

  const onSubmit = (data) => {
    mutation.mutate(data)
  }

  return (
    <div className="modal fade show" style={{ display: 'block' }} tabIndex="-1">
      <div className="modal-dialog">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">Yeni Duyuru Ekle</h5>
            <button
              type="button"
              className="btn-close"
              onClick={onClose}
              aria-label="Close"
            ></button>
          </div>
          <div className="modal-body">
            <form onSubmit={handleSubmit(onSubmit)}>
              <div className="mb-3">
                <label htmlFor="title" className="form-label">
                  Başlık <span className="text-danger">*</span>
                </label>
                <input
                  type="text"
                  className={`form-control ${errors.title ? 'is-invalid' : ''}`}
                  id="title"
                  {...register('title', { required: 'Başlık gereklidir' })}
                />
                {errors.title && (
                  <div className="invalid-feedback">{errors.title.message}</div>
                )}
              </div>

              <div className="mb-3">
                <label htmlFor="message" className="form-label">
                  Mesaj <span className="text-danger">*</span>
                </label>
                <textarea
                  className={`form-control ${errors.message ? 'is-invalid' : ''}`}
                  id="message"
                  rows="4"
                  {...register('message', { required: 'Mesaj gereklidir' })}
                />
                {errors.message && (
                  <div className="invalid-feedback">{errors.message.message}</div>
                )}
              </div>
            </form>
          </div>
          <div className="modal-footer">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onClose}
            >
              İptal
            </button>
            <button
              type="button"
              className="btn btn-primary"
              onClick={handleSubmit(onSubmit)}
              disabled={mutation.isLoading}
            >
              {mutation.isLoading ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  Ekleniyor...
                </>
              ) : (
                'Ekle'
              )}
            </button>
          </div>
        </div>
      </div>
      <div className="modal-backdrop fade show"></div>
    </div>
  )
}

export default AnnouncementForm


