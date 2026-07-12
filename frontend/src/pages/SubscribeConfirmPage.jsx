import React, { useEffect, useState } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { publicAPI } from '../services/api'

const SubscribeConfirmPage = () => {
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
        {status === 'loading' && <p>Onaylanıyor...</p>}
        {status === 'success' && (
          <>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Aboneliğin onaylandı 🎉</h1>
            <p className="text-muted">Artık haftalık etkinlik özetlerini e-postanda alacaksın.</p>
          </>
        )}
        {status === 'error' && (
          <>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Bağlantı geçersiz</h1>
            <p className="text-muted">Bu onay bağlantısı geçersiz ya da süresi dolmuş olabilir.</p>
          </>
        )}
        <Link to="/" className="btn-primary" style={{ display: 'inline-block', marginTop: '1rem' }}>
          Anasayfaya Dön
        </Link>
      </div>
    </div>
  )
}

export default SubscribeConfirmPage
