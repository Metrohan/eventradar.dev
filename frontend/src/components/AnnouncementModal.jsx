import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { format } from 'date-fns'
import { useDateLocale } from '../hooks/useDateLocale'

const AnnouncementModal = ({ announcement }) => {
  const { t } = useTranslation()
  const dateLocale = useDateLocale()
  const [show, setShow] = useState(false)

  useEffect(() => {
    // Show modal after a short delay (converted from Flask template behavior)
    const timer = setTimeout(() => {
      setShow(true)
    }, 1000)

    return () => clearTimeout(timer)
  }, [])

  const handleClose = () => {
    setShow(false)
  }

  const formatDate = (dateString) => {
    try {
      return format(new Date(dateString), 'dd MMMM yyyy, HH:mm', { locale: dateLocale })
    } catch {
      return t('announcement.invalidDate')
    }
  }

  if (!show) return null

  return (
    <>
      <div className="modal-backdrop fade show" style={{ zIndex: 1040 }}></div>
      <div className="modal fade show" style={{ display: 'block', zIndex: 1050 }} tabIndex="-1">
        <div className="modal-dialog">
          <div className="modal-content">
            <div className="modal-header">
              <h5 className="modal-title">{announcement.title}</h5>
              <button
                type="button"
                className="btn-close"
                onClick={handleClose}
                aria-label="Close"
              ></button>
            </div>
            <div className="modal-body">
              <p className="mb-3">{announcement.message}</p>
              <small className="text-muted">
                <i className="fas fa-clock me-1"></i>
                {formatDate(announcement.created_at)}
              </small>
            </div>
            <div className="modal-footer">
              <button
                type="button"
                className="btn btn-primary"
                onClick={handleClose}
              >
                {t('announcement.ok')}
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

export default AnnouncementModal


