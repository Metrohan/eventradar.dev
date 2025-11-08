import React, { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useMutation } from 'react-query'
import toast from 'react-hot-toast'
import { formAPI } from '../services/api'

const SuggestionPage = () => {
  const { register, handleSubmit, formState: { errors }, reset } = useForm()

  // Submit suggestion mutation (converted from Flask route /suggestions/oneri_sikayet)
  const submitMutation = useMutation(formAPI.submitSuggestion, {
    onSuccess: () => {
      toast.success('Öneri/Şikayetiniz başarıyla gönderildi.')
      reset()
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Gönderilirken bir hata oluştu.')
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
            <div className="card-header bg-success text-white">
              <h3 className="card-title mb-0">
                <i className="fas fa-lightbulb me-2"></i>
                Öneri / Şikayet
              </h3>
            </div>
            <div className="card-body">
              <p className="text-muted mb-4">
                TechEventRadar'ı daha iyi hale getirmek için önerilerinizi ve şikayetlerinizi 
                bizimle paylaşın. Geri bildirimleriniz bizim için çok değerli!
              </p>

              <form onSubmit={handleSubmit(onSubmit)}>
                {/* Request Type */}
                <div className="mb-3">
                  <label htmlFor="suggestion_type" className="form-label">
                    Talep Türü <span className="text-danger">*</span>
                  </label>
                  <select
                    className={`form-select ${errors.suggestion_type ? 'is-invalid' : ''}`}
                    id="suggestion_type"
                    {...register('suggestion_type', {
                      required: 'Talep türü seçilmelidir'
                    })}
                  >
                    <option value="">Seçiniz...</option>
                    <option value="öneri">Öneri</option>
                    <option value="şikayet">Şikayet</option>
                    <option value="hata_bildirimi">Hata Bildirimi</option>
                    <option value="diğer">Diğer</option>
                  </select>
                  {errors.suggestion_type && (
                    <div className="invalid-feedback">
                      {errors.suggestion_type.message}
                    </div>
                  )}
                </div>

                {/* Suggestion Title */}
                <div className="mb-3">
                  <label htmlFor="suggestion_title" className="form-label">
                    Başlık <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    className={`form-control ${errors.suggestion_title ? 'is-invalid' : ''}`}
                    id="suggestion_title"
                    placeholder="Öneri/şikayet başlığını giriniz"
                    {...register('suggestion_title', {
                      required: 'Başlık gereklidir',
                      minLength: {
                        value: 5,
                        message: 'Başlık en az 5 karakter olmalıdır'
                      }
                    })}
                  />
                  {errors.suggestion_title && (
                    <div className="invalid-feedback">
                      {errors.suggestion_title.message}
                    </div>
                  )}
                </div>

                {/* Suggestion Text */}
                <div className="mb-4">
                  <label htmlFor="suggestion_text" className="form-label">
                    Açıklama <span className="text-danger">*</span>
                  </label>
                  <textarea
                    className={`form-control ${errors.suggestion_text ? 'is-invalid' : ''}`}
                    id="suggestion_text"
                    rows="5"
                    placeholder="Öneri/şikayetinizi detaylı olarak açıklayınız..."
                    {...register('suggestion_text', {
                      required: 'Açıklama gereklidir',
                      minLength: {
                        value: 10,
                        message: 'Açıklama en az 10 karakter olmalıdır'
                      }
                    })}
                  />
                  {errors.suggestion_text && (
                    <div className="invalid-feedback">
                      {errors.suggestion_text.message}
                    </div>
                  )}
                </div>

                {/* Submit Button */}
                <div className="d-grid">
                  <button
                    type="submit"
                    className="btn btn-success btn-lg"
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
                        Gönder
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

export default SuggestionPage


