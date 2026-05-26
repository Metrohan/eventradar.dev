import React from 'react'
import { Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { useMutation } from 'react-query'
import toast from 'react-hot-toast'
import { formAPI } from '../services/api'

const TYPES = [
  { value: 'öneri',          label: '💡 Öneri',          color: '#6366f1', bg: 'rgba(99,102,241,0.15)',  border: 'rgba(99,102,241,0.4)'  },
  { value: 'hata_bildirimi', label: '🐛 Hata Bildirimi', color: '#f43f5e', bg: 'rgba(244,63,94,0.15)',   border: 'rgba(244,63,94,0.4)'   },
  { value: 'şikayet',        label: '😤 Şikayet',        color: '#fb923c', bg: 'rgba(251,146,60,0.15)',  border: 'rgba(251,146,60,0.4)'  },
  { value: 'diğer',          label: '📌 Diğer',          color: '#94a3b8', bg: 'rgba(148,163,184,0.15)', border: 'rgba(148,163,184,0.4)' },
]

const INFO_CARDS = [
  {
    emoji: '💡',
    title: 'Öneri',
    desc: 'Yeni özellik veya iyileştirme fikirlerin',
    bg: 'rgba(99,102,241,0.08)',
    border: 'rgba(99,102,241,0.2)',
  },
  {
    emoji: '🐛',
    title: 'Hata Bildirimi',
    desc: 'Karşılaştığın bir sorunu bildir',
    bg: 'rgba(244,63,94,0.08)',
    border: 'rgba(244,63,94,0.2)',
  },
  {
    emoji: '📅',
    title: 'Etkinlik Talebi',
    desc: 'Eklenmesini istediğin bir etkinlik mi var?',
    bg: 'rgba(251,146,60,0.08)',
    border: 'rgba(251,146,60,0.2)',
    link: '/etkinlik-talep',
    linkLabel: 'Talep Oluştur →',
  },
]

const SuggestionPage = () => {
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setValue,
    watch,
  } = useForm()

  const selectedType = watch('suggestion_type')

  const submitMutation = useMutation(formAPI.submitSuggestion, {
    onSuccess: () => {
      toast.success('Öneri/Şikayetiniz başarıyla gönderildi.')
      reset()
    },
    onError: error => {
      toast.error(error.response?.data?.detail || 'Gönderilirken bir hata oluştu.')
    },
  })

  const onSubmit = data => submitMutation.mutate(data)

  return (
    <div className="container py-4">
      <div className="page-hero">
        <h1 className="page-hero-title">Bize Ulaş</h1>
        <p className="page-hero-subtitle">Geri bildiriminiz TechEventRadar'ı daha iyi yapar.</p>
      </div>

      <div className="form-two-col">
        {/* Left: form */}
        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '16px', padding: '28px' }}>
          <form onSubmit={handleSubmit(onSubmit)}>
            {/* Hidden field bound to react-hook-form */}
            <input type="hidden" {...register('suggestion_type', { required: 'Talep türü seçilmelidir' })} />

            {/* Type selector */}
            <div style={{ marginBottom: '20px' }}>
              <label className="form-label-dark">
                Talep Türü <span style={{ color: 'var(--danger)' }}>*</span>
              </label>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {TYPES.map(t => {
                  const active = selectedType === t.value
                  return (
                    <button
                      key={t.value}
                      type="button"
                      className="type-btn"
                      onClick={() => setValue('suggestion_type', t.value, { shouldValidate: true })}
                      aria-pressed={active}
                      style={active ? { background: t.bg, borderColor: t.border, color: t.color } : {}}
                    >
                      {t.label}
                    </button>
                  )
                })}
              </div>
              {errors.suggestion_type && (
                <p className="field-error">{errors.suggestion_type.message}</p>
              )}
            </div>

            {/* Title */}
            <div style={{ marginBottom: '16px' }}>
              <label className="form-label-dark" htmlFor="suggestion_title">
                Başlık <span style={{ color: 'var(--danger)' }}>*</span>
              </label>
              <input
                id="suggestion_title"
                className="form-field-dark"
                placeholder="Öneri/şikayet başlığını giriniz"
                {...register('suggestion_title', {
                  required: 'Başlık gereklidir',
                  minLength: { value: 5, message: 'Başlık en az 5 karakter olmalıdır' },
                })}
              />
              {errors.suggestion_title && (
                <p className="field-error">{errors.suggestion_title.message}</p>
              )}
            </div>

            {/* Description */}
            <div style={{ marginBottom: '24px' }}>
              <label className="form-label-dark" htmlFor="suggestion_text">
                Açıklama <span style={{ color: 'var(--danger)' }}>*</span>
              </label>
              <textarea
                id="suggestion_text"
                className="form-field-dark"
                rows={5}
                placeholder="Öneri/şikayetinizi detaylı olarak açıklayınız..."
                {...register('suggestion_text', {
                  required: 'Açıklama gereklidir',
                  minLength: { value: 10, message: 'Açıklama en az 10 karakter olmalıdır' },
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
                  Gönderiliyor...
                </>
              ) : (
                <><i className="fas fa-paper-plane me-2" aria-hidden="true" />Gönder</>
              )}
            </button>
          </form>
        </div>

        {/* Right: info cards */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {INFO_CARDS.map(card => (
            <div
              key={card.title}
              className="info-card"
              style={{ background: card.bg, borderColor: card.border }}
            >
              <div style={{ fontSize: '1.5rem', marginBottom: '8px' }} aria-hidden="true">{card.emoji}</div>
              <h4 style={{ fontWeight: 700, fontSize: '0.95rem', marginBottom: '4px' }}>{card.title}</h4>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', margin: card.link ? '0 0 10px' : 0 }}>
                {card.desc}
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
                  {card.linkLabel}
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
