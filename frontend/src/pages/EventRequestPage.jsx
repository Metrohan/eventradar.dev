import React, { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { useMutation } from 'react-query'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'
import { formAPI } from '../services/api'
import { getErrorMessage } from '../utils/errorMessage'
import { setPageSEO } from '../utils/seo'

const EventRequestPage = () => {
  const { t, i18n } = useTranslation()
  const [step, setStep] = useState(1)

  useEffect(() => {
    setPageSEO({
      title: 'Etkinlik Ekleme Talebi | TechEventRadar',
      tabTitle: `${t('eventRequest.pageTitle')} | TechEventRadar`,
      description: 'Kaçırdığımız bir hackathon, bootcamp veya kariyer etkinliği mi var? TechEventRadar\'a ekleyelim.',
      path: '/etkinlik-talep',
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [i18n.language])
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm()

  const submitMutation = useMutation(formAPI.submitEventRequest, {
    onSuccess: () => {
      toast.success(t('eventRequest.toastSuccess'))
      reset()
      setStep(1)
    },
    onError: error => {
      toast.error(getErrorMessage(error, t('eventRequest.toastErrorFallback')))
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
        <h1 className="page-hero-title">{t('eventRequest.pageTitle')}</h1>
        <p className="page-hero-subtitle" style={{ margin: '0 auto' }}>
          {t('eventRequest.pageSubtitle')}
        </p>
      </div>

      <div className="wizard-card">
        {/* Step indicator */}
        <div className="step-indicator" role="list" aria-label={t('eventRequest.stepsAriaLabel')}>
          <div className="step-item" role="listitem" aria-current={step === 1 ? 'step' : undefined}>
            <div className={`step-circle ${step === 1 ? 'active' : 'done'}`}>
              {step > 1
                ? <i className="fas fa-check" style={{ fontSize: '10px' }} aria-hidden="true" />
                : '1'}
            </div>
            <span className={`step-label ${step === 1 ? 'active' : 'inactive'}`}>{t('eventRequest.stepLink')}</span>
          </div>
          <div className={`step-line ${step > 1 ? 'done' : 'inactive'}`} aria-hidden="true" />
          <div className="step-item" role="listitem" aria-current={step === 2 ? 'step' : undefined}>
            <div className={`step-circle ${step === 2 ? 'active' : 'inactive'}`}>2</div>
            <span className={`step-label ${step === 2 ? 'active' : 'inactive'}`}>{t('eventRequest.stepDetails')}</span>
          </div>
        </div>

        <form onSubmit={handleSubmit(onSubmit)}>
          {/* Step 1 */}
          {step === 1 && (
            <div>
              <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '6px' }}>
                {t('eventRequest.step1Heading')}
              </h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '20px' }}>
                {t('eventRequest.step1Subtitle')}
              </p>
              <div style={{ marginBottom: '24px' }}>
                <label className="form-label-dark" htmlFor="event_link">
                  {t('eventRequest.linkLabel')} <span style={{ color: 'var(--danger)' }}>*</span>
                </label>
                <input
                  id="event_link"
                  type="url"
                  className="form-field-dark"
                  placeholder="https://etkinlik.com/..."
                  {...register('event_link', {
                    required: t('eventRequest.linkRequired'),
                    pattern: { value: /^https?:\/\/.+/, message: t('eventRequest.linkInvalid') },
                  })}
                />
                {errors.event_link && (
                  <p className="field-error" role="alert">{errors.event_link.message}</p>
                )}
              </div>
              <button type="submit" className="gradient-btn">
                {t('eventRequest.continueButton')} <i className="fas fa-arrow-right ms-2" aria-hidden="true" />
              </button>
            </div>
          )}

          {/* Step 2 */}
          {step === 2 && (
            <div>
              <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '6px' }}>
                {t('eventRequest.step2Heading')}
              </h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '20px' }}>
                {t('eventRequest.step2Subtitle')}
              </p>

              <div style={{ marginBottom: '16px' }}>
                <label className="form-label-dark" htmlFor="event_title">
                  {t('eventRequest.titleLabel')} <span style={{ color: 'var(--danger)' }}>*</span>
                </label>
                <input
                  id="event_title"
                  className="form-field-dark"
                  placeholder={t('eventRequest.titlePlaceholder')}
                  {...register('event_title', {
                    required: t('eventRequest.titleRequired'),
                    minLength: { value: 5, message: t('eventRequest.titleMinLength') },
                  })}
                />
                {errors.event_title && (
                  <p className="field-error" role="alert">{errors.event_title.message}</p>
                )}
              </div>

              <div style={{ marginBottom: '16px' }}>
                <label className="form-label-dark" htmlFor="event_date">{t('eventRequest.dateLabel')}</label>
                <input
                  id="event_date"
                  type="date"
                  className="form-field-dark"
                  {...register('event_date')}
                />
              </div>

              <div style={{ marginBottom: '16px' }}>
                <label className="form-label-dark" htmlFor="event_description">{t('eventRequest.descLabel')}</label>
                <textarea
                  id="event_description"
                  className="form-field-dark"
                  rows={4}
                  placeholder={t('eventRequest.descPlaceholder')}
                  {...register('event_description')}
                />
              </div>

              <div style={{ marginBottom: '24px' }}>
                <label className="form-label-dark" htmlFor="contact_email">
                  {t('eventRequest.emailLabel')}{' '}
                  <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>({t('eventRequest.emailOptional')})</span>
                </label>
                <input
                  id="contact_email"
                  type="email"
                  className="form-field-dark"
                  placeholder={t('eventRequest.emailPlaceholder')}
                  {...register('contact_email')}
                />
              </div>

              <div style={{ display: 'flex', gap: '12px' }}>
                <button type="button" className="ghost-btn" onClick={() => setStep(1)}>
                  <i className="fas fa-arrow-left me-2" aria-hidden="true" />{t('eventRequest.backButton')}
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
                      {t('eventRequest.submitting')}
                    </>
                  ) : (
                    <><i className="fas fa-paper-plane me-2" aria-hidden="true" />{t('eventRequest.submitButton')}</>
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
