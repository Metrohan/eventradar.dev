import React, { useEffect, useState } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { publicAPI } from '../services/api'

const SubscribeConfirmPage = () => {
  const { t } = useTranslation()
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')
  const [status, setStatus] = useState('loading')

  useEffect(() => {
    if (!token) {
      setStatus('error')
      return
    }
    publicAPI
      .confirmSubscription(token)
      .then(() => setStatus('success'))
      .catch(() => setStatus('error'))
  }, [token])

  return (
    <div className="container py-5 text-center">
      <div style={{ maxWidth: '480px', margin: '0 auto' }}>
        {status === 'loading' && <p>{t('subscribeConfirm.loading')}</p>}
        {status === 'success' && (
          <>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>{t('subscribeConfirm.successTitle')}</h1>
            <p className="text-muted">{t('subscribeConfirm.successText')}</p>
          </>
        )}
        {status === 'error' && (
          <>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>{t('subscribeConfirm.errorTitle')}</h1>
            <p className="text-muted">{t('subscribeConfirm.errorText')}</p>
          </>
        )}
        <Link to="/" className="btn-primary" style={{ display: 'inline-block', marginTop: '1rem' }}>
          {t('subscribeConfirm.backHome')}
        </Link>
      </div>
    </div>
  )
}

export default SubscribeConfirmPage
