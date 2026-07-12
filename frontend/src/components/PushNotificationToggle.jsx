import React from 'react'
import toast from 'react-hot-toast'

import { publicAPI } from '../services/api'

const urlBase64ToUint8Array = value => {
  const padding = '='.repeat((4 - (value.length % 4)) % 4)
  const base64 = (value + padding).replace(/-/g, '+').replace(/_/g, '/')
  return Uint8Array.from([...window.atob(base64)].map(character => character.charCodeAt(0)))
}

const PushNotificationToggle = () => {
  const supported = typeof window !== 'undefined' && 'serviceWorker' in navigator && 'PushManager' in window
  const [enabled, setEnabled] = React.useState(false)
  const [loading, setLoading] = React.useState(false)

  React.useEffect(() => {
    if (!supported) return
    navigator.serviceWorker.ready
      .then(registration => registration.pushManager.getSubscription())
      .then(subscription => setEnabled(Boolean(subscription)))
      .catch(() => {})
  }, [supported])

  if (!supported) return null

  const toggle = async () => {
    setLoading(true)
    try {
      const registration = await navigator.serviceWorker.ready
      const current = await registration.pushManager.getSubscription()
      if (current) {
        await publicAPI.pushUnsubscribe(current.endpoint)
        await current.unsubscribe()
        setEnabled(false)
        toast.success('Tarayıcı bildirimleri kapatıldı.')
        return
      }

      const permission = await Notification.requestPermission()
      if (permission !== 'granted') throw new Error('permission-denied')
      const { data } = await publicAPI.getVapidPublicKey()
      if (!data.key) {
        toast.error('Tarayıcı bildirimleri henüz yapılandırılmamış.')
        return
      }
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(data.key),
      })
      await publicAPI.pushSubscribe(subscription.toJSON())
      setEnabled(true)
      toast.success('Tarayıcı bildirimleri açıldı.')
    } catch (error) {
      toast.error(error.message === 'permission-denied' ? 'Bildirim izni verilmedi.' : 'Tarayıcı bildirimi etkinleştirilemedi.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <button type="button" className={`footer-push-toggle ${enabled ? 'active' : ''}`} onClick={toggle} disabled={loading}>
      <i className={`${enabled ? 'fas' : 'far'} fa-bell`} />
      {loading ? 'Kontrol ediliyor…' : enabled ? 'Bildirimler açık' : 'Tarayıcı bildirimlerini aç'}
    </button>
  )
}

export default PushNotificationToggle
