import React, { useEffect, useState } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { publicAPI } from '../services/api'

const UnsubscribePage = () => {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')
  const [status, setStatus] = useState('loading')

  useEffect(() => {
    if (!token) {
      setStatus('error')
      return
    }
    publicAPI
      .unsubscribe(token)
      .then(() => setStatus('success'))
      .catch(() => setStatus('error'))
  }, [token])

  return (
    <div className="container py-5 text-center">
      <div style={{ maxWidth: '480px', margin: '0 auto' }}>
        {status === 'loading' && <p>İşleniyor...</p>}
        {status === 'success' && (
          <>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Abonelikten çıktın</h1>
            <p className="text-muted">Artık e-posta özeti almayacaksın. İstediğin zaman tekrar abone olabilirsin.</p>
          </>
        )}
        {status === 'error' && (
          <>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Bağlantı geçersiz</h1>
            <p className="text-muted">Bu bağlantı geçersiz olabilir.</p>
          </>
        )}
        <Link to="/" className="btn-primary" style={{ display: 'inline-block', marginTop: '1rem' }}>
          Anasayfaya Dön
        </Link>
      </div>
    </div>
  )
}

export default UnsubscribePage
