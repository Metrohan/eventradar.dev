import React, { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { useMutation } from 'react-query'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'
import { formAPI } from '../services/api'
import { getErrorMessage } from '../utils/errorMessage'
import { setPageSEO } from '../utils/seo'

// value: sent to backend as free-text suggestion_type, stays fixed regardless
// of UI language; labelKey: i18n key for the button's translated display text.
const TYPES = [
  { value: 'öneri',          labelKey: 'suggestion.types.suggestion',  emoji: '💡', color: '#6366f1', bg: 'rgba(99,102,241,0.15)',  border: 'rgba(99,102,241,0.4)'  },
  { value: 'hata_bildirimi', labelKey: 'suggestion.types.bug',         emoji: '🐛', color: '#f43f5e', bg: 'rgba(244,63,94,0.15)',   border: 'rgba(244,63,94,0.4)'   },
  { value: 'şikayet',        labelKey: 'suggestion.types.complaint',   emoji: '😤', color: '#fb923c', bg: 'rgba(251,146,60,0.15)',  border: 'rgba(251,146,60,0.4)'  },
  { value: 'diğer',          labelKey: 'suggestion.types.other',       emoji: '📌', color: '#94a3b8', bg: 'rgba(148,163,184,0.15)', border: 'rgba(148,163,184,0.4)' },
]

const INFO_CARDS = [
  {
    emoji: '💡',
    titleKey: 'suggestion.infoCards.suggestion.title',
    descKey: 'suggestion.infoCards.suggestion.desc',
    bg: 'rgba(99,102,241,0.08)',
    border: 'rgba(99,102,241,0.2)',
  },
  {
    emoji: '🐛',
    titleKey: 'suggestion.infoCards.bug.title',
    descKey: 'suggestion.infoCards.bug.desc',
    bg: 'rgba(244,63,94,0.08)',
    border: 'rgba(244,63,94,0.2)',
  },
  {
    emoji: '📅',
    titleKey: 'suggestion.infoCards.eventRequest.title',
    descKey: 'suggestion.infoCards.eventRequest.desc',
    bg: 'rgba(251,146,60,0.08)',
    border: 'rgba(251,146,60,0.2)',
    link: '/etkinlik-talep',
    linkLabelKey: 'suggestion.infoCards.eventRequest.linkLabel',
  },
]

const SuggestionPage = () => {
  const { t, i18n } = useTranslation()
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setValue,
    watch,
  } = useForm()

  const selectedType = watch('suggestion_type')

  useEffect(() => {
    setPageSEO({
      title: 'Öneri ve Şikayet Bildir | TechEventRadar',
      tabTitle: `${t('suggestion.pageTitle')} | TechEventRadar`,
      description: 'TechEventRadar hakkında öneri, hata bildirimi veya şikayetinizi bize iletin.',
      path: '/oneri-sikayet',
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [i18n.language])

  const submitMutation = useMutation(formAPI.submitSuggestion, {
    onSuccess: () => {
      toast.success(t('suggestion.toastSuccess'))
      reset()
    },
    onError: error => {
      toast.error(getErrorMessage(error, t('suggestion.toastErrorFallback')))
    },
  })

  const onSubmit = data => submitMutation.mutate(data)

  return (
    <div className="container py-4">
      <div className="page-hero">
        <h1 className="page-hero-title">{t('suggestion.pageTitle')}</h1>
        <p className="page-hero-subtitle">{t('suggestion.pageSubtitle')}</p>
      </div>

      <div className="form-two-col">
        {/* Left: form */}
        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '16px', padding: '28px' }}>
          <form onSubmit={handleSubmit(onSubmit)}>
            {/* Hidden field bound to react-hook-form */}
            <input type="hidden" {...register('suggestion_type', { required: t('suggestion.typeRequired') })} />

            {/* Type selector */}
            <div style={{ marginBottom: '20px' }}>
              <label id="type-label" className="form-label-dark">
                {t('suggestion.typeLabel')} <span style={{ color: 'var(--danger)' }}>*</span>
              </label>
              <div
                role="group"
                aria-labelledby="type-label"
                aria-describedby={errors.suggestion_type ? 'type-error' : undefined}
                style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}
              >
                {TYPES.map(type => {
                  const active = selectedType === type.value
                  return (
                    <button
                      key={type.value}
                      type="button"
                      className="type-btn"
                      onClick={() => setValue('suggestion_type', type.value, { shouldValidate: true })}
                      aria-pressed={active}
                      style={active ? { background: type.bg, borderColor: type.border, color: type.color } : {}}
                    >
                      {type.emoji} {t(type.labelKey)}
                    </button>
                  )
                })}
              </div>
              {errors.suggestion_type && (
                <p id="type-error" className="field-error" role="alert">{errors.suggestion_type.message}</p>
              )}
            </div>

            {/* Title */}
            <div style={{ marginBottom: '16px' }}>
              <label className="form-label-dark" htmlFor="suggestion_title">
                {t('suggestion.titleLabel')} <span style={{ color: 'var(--danger)' }}>*</span>
              </label>
              <input
                id="suggestion_title"
                className="form-field-dark"
                placeholder={t('suggestion.titlePlaceholder')}
                {...register('suggestion_title', {
                  required: t('suggestion.titleRequired'),
                  minLength: { value: 5, message: t('suggestion.titleMinLength') },
                })}
              />
              {errors.suggestion_title && (
                <p className="field-error">{errors.suggestion_title.message}</p>
              )}
            </div>

            {/* Description */}
            <div style={{ marginBottom: '24px' }}>
              <label className="form-label-dark" htmlFor="suggestion_text">
                {t('suggestion.descLabel')} <span style={{ color: 'var(--danger)' }}>*</span>
              </label>
              <textarea
                id="suggestion_text"
                className="form-field-dark"
                rows={5}
                placeholder={t('suggestion.descPlaceholder')}
                {...register('suggestion_text', {
                  required: t('suggestion.descRequired'),
                  minLength: { value: 10, message: t('suggestion.descMinLength') },
                })}
              />
              {errors.suggestion_text && (
                <p className="field-error">{errors.suggestion_text.message}</p>
              )}
            </div>

            <button type="submit" className="gradient-btn" disabled={submitMutation.isLoading}>
              {submitMutation.isLoading ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true" />
                  {t('suggestion.submitting')}
                </>
              ) : (
                <><i className="fas fa-paper-plane me-2" aria-hidden="true" />{t('suggestion.submitButton')}</>
              )}
            </button>
          </form>
        </div>

        {/* Right: info cards */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {INFO_CARDS.map(card => (
            <div
              key={card.titleKey}
              className="info-card"
              style={{ background: card.bg, borderColor: card.border }}
            >
              <div style={{ fontSize: '1.5rem', marginBottom: '8px' }} aria-hidden="true">{card.emoji}</div>
              <h4 style={{ fontWeight: 700, fontSize: '0.95rem', marginBottom: '4px' }}>{t(card.titleKey)}</h4>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', margin: card.link ? '0 0 10px' : 0 }}>
                {t(card.descKey)}
              </p>
              {card.link && (
                <Link
                  to={card.link}
                  style={{
                    display: 'inline-block',
                    background: 'rgba(251,146,60,0.15)',
                    border: '1px solid rgba(251,146,60,0.3)',
                    borderRadius: '6px',
                    padding: '5px 12px',
                    fontSize: '0.8rem',
                    color: '#fb923c',
                    fontWeight: 700,
                    textDecoration: 'none',
                  }}
                >
                  {t(card.linkLabelKey)}
                </Link>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default SuggestionPage
