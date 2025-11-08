import React, { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useMutation } from 'react-query'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { formAPI } from '../services/api'

const EventRequestPage = () => {
  const navigate = useNavigate()
  const { register, handleSubmit, formState: { errors }, reset } = useForm()

  // Submit event request mutation (converted from Flask route /requests/etkinlik-talep)
  const submitMutation = useMutation(formAPI.submitEventRequest, {
    onSuccess: () => {
      toast.success('Etkinlik ekleme talebiniz başarıyla alındı. Teşekkür ederiz!')
      reset()
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Talebiniz gönderilirken bir hata oluştu.')
    }
  })

  const onSubmit = (data) => {
    submitMutation.mutate(data)
  }

  return (
    <div className="container py-5">
      <div className="row justify-content-center">
        <div className="col-md-8 col-lg-6">
          <div className="card shadow">
            <div className="card-header bg-primary text-white">
              <h3 className="card-title mb-0">
                <i className="fas fa-plus-circle me-2"></i>
                Etkinlik Ekleme Talebi
              </h3>
            </div>
            <div className="card-body">
              <p className="text-muted mb-4">
                Kaçırdığımız bir teknoloji etkinliği mi var? Aşağıdaki formu doldurarak 
                bize bildirin. Talebinizi değerlendirip en kısa sürede ekleyeceğiz.
              </p>

              <form onSubmit={handleSubmit(onSubmit)}>
                {/* Event Link */}
                <div className="mb-3">
                  <label htmlFor="event_link" className="form-label">
                    Etkinlik Linki <span className="text-danger">*</span>
                  </label>
                  <input
                    type="url"
                    className={`form-control ${errors.event_link ? 'is-invalid' : ''}`}
                    id="event_link"
                    placeholder="https://example.com/event"
                    {...register('event_link', {
                      required: 'Etkinlik linki gereklidir',
                      pattern: {
                        value: /^https?:\/\/.+/,
                        message: 'Geçerli bir URL giriniz'
                      }
                    })}
                  />
                  {errors.event_link && (
                    <div className="invalid-feedback">
                      {errors.event_link.message}
                    </div>
                  )}
                </div>

                {/* Event Title */}
                <div className="mb-3">
                  <label htmlFor="event_title" className="form-label">
                    Etkinlik Başlığı <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    className={`form-control ${errors.event_title ? 'is-invalid' : ''}`}
                    id="event_title"
                    placeholder="Etkinlik başlığını giriniz"
                    {...register('event_title', {
                      required: 'Etkinlik başlığı gereklidir',
                      minLength: {
                        value: 5,
                        message: 'Başlık en az 5 karakter olmalıdır'
                      }
                    })}
                  />
                  {errors.event_title && (
                    <div className="invalid-feedback">
                      {errors.event_title.message}
                    </div>
                  )}
                </div>

                {/* Event Date */}
                <div className="mb-3">
                  <label htmlFor="event_date" className="form-label">
                    Etkinlik Tarihi
                  </label>
                  <input
                    type="date"
                    className="form-control"
                    id="event_date"
                    {...register('event_date')}
                  />
                </div>

                {/* Event Description */}
                <div className="mb-4">
                  <label htmlFor="event_description" className="form-label">
                    Etkinlik Açıklaması
                  </label>
                  <textarea
                    className="form-control"
                    id="event_description"
                    rows="4"
                    placeholder="Etkinlik hakkında detaylı bilgi veriniz..."
                    {...register('event_description')}
                  />
                </div>

                {/* Submit Button */}
                <div className="d-grid">
                  <button
                    type="submit"
                    className="btn btn-primary btn-lg"
                    disabled={submitMutation.isLoading}
                  >
                    {submitMutation.isLoading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                        Gönderiliyor...
                      </>
                    ) : (
                      <>
                        <i className="fas fa-paper-plane me-2"></i>
                        Talep Gönder
                      </>
                    )}
                  </button>
                </div>
              </form>

              <div className="mt-4 text-center">
                <a href="/" className="btn btn-outline-secondary">
                  <i className="fas fa-arrow-left me-2"></i>
                  Ana Sayfaya Dön
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default EventRequestPage


