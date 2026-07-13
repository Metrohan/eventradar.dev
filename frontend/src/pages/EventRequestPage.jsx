import React, { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useMutation } from 'react-query'
import toast from 'react-hot-toast'
import { formAPI } from '../services/api'
import { getErrorMessage } from '../utils/errorMessage'

const EventRequestPage = () => {
  const [step, setStep] = useState(1)
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm()

  const submitMutation = useMutation(formAPI.submitEventRequest, {
    onSuccess: () => {
      toast.success('Etkinlik ekleme talebiniz başarıyla alındı. Teşekkür ederiz!')
      reset()
      setStep(1)
    },
    onError: error => {
      toast.error(getErrorMessage(error, 'Talebiniz gönderilirken bir hata oluştu.'))
    },
  })

  // Step 1 only renders the event_link field, so handleSubmit's validation
  // (and a native Enter-key submit) only ever checks that field. Route the
  // form's own submit through the step machine instead of hitting the API
  // with a request that's missing the step-2 fields the backend requires.
  const onSubmit = data => {
    if (step === 1) {
      setStep(2)
      return
    }
    // Optional fields left blank arrive as '' from their inputs; the backend's
    // Optional[date]/EmailStr fields reject '' as invalid rather than treating
    // it as absent, so blank optionals must be sent as undefined, not ''.
    submitMutation.mutate({
      ...data,
      event_date: data.event_date || undefined,
      event_description: data.event_description || undefined,
      contact_email: data.contact_email || undefined,
    })
  }

  return (
    <div className="container py-4">
      <div className="page-hero" style={{ textAlign: 'center' }}>
        <h1 className="page-hero-title">Etkinlik Ekleme Talebi</h1>
        <p className="page-hero-subtitle" style={{ margin: '0 auto' }}>
          Kaçırdığımız bir etkinlik mi var? Bize bildirin, en kısa sürede ekleyelim.
        </p>
      </div>

      <div className="wizard-card">
        {/* Step indicator */}
        <div className="step-indicator" role="list" aria-label="Form adımları">
          <div className="step-item" role="listitem" aria-current={step === 1 ? 'step' : undefined}>
            <div className={`step-circle ${step === 1 ? 'active' : 'done'}`}>
              {step > 1
                ? <i className="fas fa-check" style={{ fontSize: '10px' }} aria-hidden="true" />
                : '1'}
            </div>
            <span className={`step-label ${step === 1 ? 'active' : 'inactive'}`}>Link</span>
          </div>
          <div className={`step-line ${step > 1 ? 'done' : 'inactive'}`} aria-hidden="true" />
          <div className="step-item" role="listitem" aria-current={step === 2 ? 'step' : undefined}>
            <div className={`step-circle ${step === 2 ? 'active' : 'inactive'}`}>2</div>
            <span className={`step-label ${step === 2 ? 'active' : 'inactive'}`}>Detaylar</span>
          </div>
        </div>

        <form onSubmit={handleSubmit(onSubmit)}>
          {/* Step 1 */}
          {step === 1 && (
            <div>
              <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '6px' }}>
                Etkinlik Linkini Gir
              </h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '20px' }}>
                Etkinliğin bağlantısını yapıştır
              </p>
              <div style={{ marginBottom: '24px' }}>
                <label className="form-label-dark" htmlFor="event_link">
                  Etkinlik Linki <span style={{ color: 'var(--danger)' }}>*</span>
                </label>
                <input
                  id="event_link"
                  type="url"
                  className="form-field-dark"
                  placeholder="https://etkinlik.com/..."
                  {...register('event_link', {
                    required: 'Etkinlik linki gereklidir',
                    pattern: { value: /^https?:\/\/.+/, message: 'Geçerli bir URL giriniz' },
                  })}
                />
                {errors.event_link && (
                  <p className="field-error" role="alert">{errors.event_link.message}</p>
                )}
              </div>
              <button type="submit" className="gradient-btn">
                Devam <i className="fas fa-arrow-right ms-2" aria-hidden="true" />
              </button>
            </div>
          )}

          {/* Step 2 */}
          {step === 2 && (
            <div>
              <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '6px' }}>
                Etkinlik Detayları
              </h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '20px' }}>
                Başlık zorunlu, diğer alanlar isteğe bağlıdır.
              </p>

              <div style={{ marginBottom: '16px' }}>
                <label className="form-label-dark" htmlFor="event_title">
                  Etkinlik Başlığı <span style={{ color: 'var(--danger)' }}>*</span>
                </label>
                <input
                  id="event_title"
                  className="form-field-dark"
                  placeholder="Etkinlik başlığını giriniz"
                  {...register('event_title', {
                    required: 'Etkinlik başlığı gereklidir',
                    minLength: { value: 5, message: 'Başlık en az 5 karakter olmalıdır' },
                  })}
                />
                {errors.event_title && (
                  <p className="field-error" role="alert">{errors.event_title.message}</p>
                )}
              </div>

              <div style={{ marginBottom: '16px' }}>
                <label className="form-label-dark" htmlFor="event_date">Etkinlik Tarihi</label>
                <input
                  id="event_date"
                  type="date"
                  className="form-field-dark"
                  {...register('event_date')}
                />
              </div>

              <div style={{ marginBottom: '16px' }}>
                <label className="form-label-dark" htmlFor="event_description">Açıklama</label>
                <textarea
                  id="event_description"
                  className="form-field-dark"
                  rows={4}
                  placeholder="Etkinlik hakkında detaylı bilgi veriniz..."
                  {...register('event_description')}
                />
              </div>

              <div style={{ marginBottom: '24px' }}>
                <label className="form-label-dark" htmlFor="contact_email">
                  E-posta{' '}
                  <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>(isteğe bağlı)</span>
                </label>
                <input
                  id="contact_email"
                  type="email"
                  className="form-field-dark"
                  placeholder="Geri dönüş için e-posta adresiniz"
                  {...register('contact_email')}
                />
              </div>

              <div style={{ display: 'flex', gap: '12px' }}>
                <button type="button" className="ghost-btn" onClick={() => setStep(1)}>
                  <i className="fas fa-arrow-left me-2" aria-hidden="true" />Geri
                </button>
                <button
                  type="submit"
                  className="gradient-btn"
                  style={{ flex: 1 }}
                  disabled={submitMutation.isLoading}
                >
                  {submitMutation.isLoading ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true" />
                      Gönderiliyor...
                    </>
                  ) : (
                    <><i className="fas fa-paper-plane me-2" aria-hidden="true" />Talep Gönder</>
                  )}
                </button>
              </div>
            </div>
          )}
        </form>
      </div>
    </div>
  )
}

export default EventRequestPage
