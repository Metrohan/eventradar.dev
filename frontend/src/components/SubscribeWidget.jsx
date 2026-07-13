import React from 'react'
import toast from 'react-hot-toast'
import { publicAPI } from '../services/api'
import { getErrorMessage } from '../utils/errorMessage'

const urlBase64ToUint8Array = (base64String) => {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')
  const rawData = window.atob(base64)
  return Uint8Array.from([...rawData].map((c) => c.charCodeAt(0)))
}

const SubscribeWidget = () => {
  const [email, setEmail] = React.useState('')
  const [submitting, setSubmitting] = React.useState(false)
  const [pushEnabled, setPushEnabled] = React.useState(false)
  const [pushSupported] = React.useState(
    typeof window !== 'undefined' && 'serviceWorker' in navigator && 'PushManager' in window
  )

  React.useEffect(() => {
    if (!pushSupported) return
    navigator.serviceWorker.ready.then((reg) =>
      reg.pushManager.getSubscription().then((sub) => setPushEnabled(!!sub))
    )
  }, [pushSupported])

  const handleEmailSubmit = async (e) => {
    e.preventDefault()
    if (!email) return
    setSubmitting(true)
    try {
      const { data } = await publicAPI.subscribeEmail(email)
      toast.success(data.message || 'Onay e-postası gönderildi.')
      setEmail('')
    } catch (err) {
      toast.error(getErrorMessage(err, 'Abonelik başarısız oldu.'))
    } finally {
      setSubmitting(false)
    }
  }

  const handlePushToggle = async () => {
    if (!pushSupported) return

    if (pushEnabled) {
      const reg = await navigator.serviceWorker.ready
      const sub = await reg.pushManager.getSubscription()
      if (sub) {
        await publicAPI.pushUnsubscribe(sub.endpoint)
        await sub.unsubscribe()
      }
      setPushEnabled(false)
      toast.success('Push bildirimleri kapatıldı.')
      return
    }

    try {
      const permission = await Notification.requestPermission()
      if (permission !== 'granted') {
        toast.error('Bildirim izni verilmedi.')
        return
      }
      const { data } = await publicAPI.getVapidPublicKey()
      if (!data.key) {
        toast.error('Push bildirimleri şu anda yapılandırılmamış.')
        return
      }
      const reg = await navigator.serviceWorker.ready
      const sub = await reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(data.key),
      })
      await publicAPI.pushSubscribe(sub.toJSON())
      setPushEnabled(true)
      toast.success('Push bildirimleri etkinleştirildi.')
    } catch (err) {
      toast.error('Push bildirimi etkinleştirilemedi.')
    }
  }

  return (
    <div
      style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-subtle)',
        borderRadius: '16px',
        padding: '1.5rem',
      }}
    >
      <h5 style={{ fontWeight: 700, marginBottom: '0.5rem' }}>
        Yeni etkinlikleri kaçırma
      </h5>
      <p className="text-muted" style={{ fontSize: '0.85rem', marginBottom: '1rem' }}>
        Haftalık özet e-postası al ya da tarayıcı bildirimlerini aç.
      </p>

      <form onSubmit={handleEmailSubmit} className="d-flex gap-2 mb-3" style={{ flexWrap: 'wrap' }}>
        <input
          type="email"
          required
          placeholder="E-posta adresin"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="filter-select"
          style={{ flex: '1 1 200px' }}
        />
        <button type="submit" className="btn-primary" disabled={submitting}>
          {submitting ? '...' : 'Abone Ol'}
        </button>
      </form>

      {pushSupported && (
        <button type="button" className="filter-toggle" onClick={handlePushToggle}>
          <i className={`fas fa-bell${pushEnabled ? '' : '-slash'}`}></i>
          {pushEnabled ? ' Push Bildirimlerini Kapat' : ' Push Bildirimlerini Aç'}
        </button>
      )}
    </div>
  )
}

export default SubscribeWidget
