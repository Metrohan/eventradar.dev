import React from 'react'
import toast from 'react-hot-toast'
import { downloadICS } from '../utils/ics'

const copyLink = async (url) => {
  try {
    await navigator.clipboard.writeText(url)
    toast.success('Link kopyalandı.')
  } catch {
    toast.error('Link kopyalanamadı.')
  }
}

const ShareButtons = ({ event, detailUrl, variant = 'full' }) => {
  const shareText = event.title

  const whatsappHref = `https://wa.me/?text=${encodeURIComponent(`${shareText} ${detailUrl}`)}`
  const linkedinHref = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(detailUrl)}`

  const handleIconShare = async (e) => {
    e.stopPropagation()
    e.preventDefault()
    if (navigator.share) {
      try {
        await navigator.share({ title: shareText, url: detailUrl })
      } catch {
        // kullanıcı paylaşımı iptal etti, sessiz geç
      }
      return
    }
    copyLink(detailUrl)
  }

  if (variant === 'icon') {
    return (
      <button
        type="button"
        onClick={handleIconShare}
        aria-label="Etkinliği paylaş"
        className="event-share-icon-btn"
        style={{
          background: 'rgba(0,0,0,0.45)',
          border: 'none',
          borderRadius: '50%',
          width: '28px',
          height: '28px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#fff',
          cursor: 'pointer',
        }}
      >
        <i className="fas fa-share-alt" style={{ fontSize: '0.75rem' }}></i>
      </button>
    )
  }

  return (
    <div className="d-flex flex-wrap gap-2">
      <a
        href={whatsappHref}
        target="_blank"
        rel="noopener noreferrer"
        className="btn-event"
        style={{ background: '#25D366' }}
      >
        <i className="fab fa-whatsapp"></i> WhatsApp
      </a>
      <a
        href={linkedinHref}
        target="_blank"
        rel="noopener noreferrer"
        className="btn-event"
        style={{ background: '#0A66C2' }}
      >
        <i className="fab fa-linkedin"></i> LinkedIn
      </a>
      <button
        type="button"
        className="btn-event btn-event-outline"
        onClick={() => copyLink(detailUrl)}
      >
        <i className="fas fa-link"></i> Linki Kopyala
      </button>
      <button
        type="button"
        className="btn-event btn-event-outline"
        onClick={() => {
          const ok = downloadICS(event, detailUrl)
          if (!ok) toast.error('Etkinlik tarihi bilinmediği için takvime eklenemedi.')
        }}
      >
        <i className="fas fa-calendar-plus"></i> Takvime Ekle
      </button>
    </div>
  )
}

export default ShareButtons
