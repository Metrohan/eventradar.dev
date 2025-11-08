import React from 'react'
import { useForm } from 'react-hook-form'
import { useMutation } from 'react-query'
import { adminAPI } from '../../services/api'
import toast from 'react-hot-toast'

const EventForm = ({ event, onClose, onSuccess }) => {
  const isEditing = !!event
  const { register, handleSubmit, formState: { errors } } = useForm({
    defaultValues: event ? {
      title: event.title,
      description: event.description || '',
      date: event.date ? new Date(event.date).toISOString().slice(0, 16) : '',
      location: event.location || '',
      url: event.url,
      image_url: event.image_url || '',
      source: event.source,
      is_active: event.is_active
    } : {}
  })

  // Create/Update event mutation
  const mutation = useMutation(
    (data) => isEditing ? adminAPI.updateEvent(event.id, data) : adminAPI.createEvent(data),
    {
      onSuccess: () => {
        toast.success(isEditing ? 'Etkinlik güncellendi.' : 'Etkinlik eklendi.')
        onSuccess()
      },
      onError: (error) => {
        toast.error(error.response?.data?.detail || 'İşlem sırasında hata oluştu.')
      }
    }
  )

  const onSubmit = (data) => {
    mutation.mutate(data)
  }

  return (
    <div className="modal fade show" style={{ display: 'block' }} tabIndex="-1">
      <div className="modal-dialog modal-lg">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">
              {isEditing ? 'Etkinlik Düzenle' : 'Yeni Etkinlik Ekle'}
            </h5>
            <button
              type="button"
              className="btn-close"
              onClick={onClose}
              aria-label="Close"
            ></button>
          </div>
          <div className="modal-body">
            <form onSubmit={handleSubmit(onSubmit)}>
              <div className="row">
                <div className="col-md-6 mb-3">
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

                <div className="col-md-6 mb-3">
                  <label htmlFor="source" className="form-label">
                    Kaynak <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    className={`form-control ${errors.source ? 'is-invalid' : ''}`}
                    id="source"
                    {...register('source', { required: 'Kaynak gereklidir' })}
                  />
                  {errors.source && (
                    <div className="invalid-feedback">{errors.source.message}</div>
                  )}
                </div>
              </div>

              <div className="mb-3">
                <label htmlFor="description" className="form-label">Açıklama</label>
                <textarea
                  className="form-control"
                  id="description"
                  rows="3"
                  {...register('description')}
                />
              </div>

              <div className="row">
                <div className="col-md-6 mb-3">
                  <label htmlFor="date" className="form-label">Tarih</label>
                  <input
                    type="datetime-local"
                    className="form-control"
                    id="date"
                    {...register('date')}
                  />
                </div>

                <div className="col-md-6 mb-3">
                  <label htmlFor="location" className="form-label">Konum</label>
                  <input
                    type="text"
                    className="form-control"
                    id="location"
                    {...register('location')}
                  />
                </div>
              </div>

              <div className="mb-3">
                <label htmlFor="url" className="form-label">
                  URL <span className="text-danger">*</span>
                </label>
                <input
                  type="url"
                  className={`form-control ${errors.url ? 'is-invalid' : ''}`}
                  id="url"
                  {...register('url', { 
                    required: 'URL gereklidir',
                    pattern: {
                      value: /^https?:\/\/.+/,
                      message: 'Geçerli bir URL giriniz'
                    }
                  })}
                />
                {errors.url && (
                  <div className="invalid-feedback">{errors.url.message}</div>
                )}
              </div>

              <div className="mb-3">
                <label htmlFor="image_url" className="form-label">Resim URL</label>
                <input
                  type="url"
                  className="form-control"
                  id="image_url"
                  {...register('image_url')}
                />
              </div>

              <div className="mb-3">
                <div className="form-check">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    id="is_active"
                    {...register('is_active')}
                  />
                  <label className="form-check-label" htmlFor="is_active">
                    Etkinlik aktif
                  </label>
                </div>
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
                  {isEditing ? 'Güncelleniyor...' : 'Ekleniyor...'}
                </>
              ) : (
                isEditing ? 'Güncelle' : 'Ekle'
              )}
            </button>
          </div>
        </div>
      </div>
      <div className="modal-backdrop fade show"></div>
    </div>
  )
}

export default EventForm


