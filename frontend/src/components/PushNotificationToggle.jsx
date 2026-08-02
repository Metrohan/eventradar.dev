import React from 'react'
import toast from 'react-hot-toast'
import { useTranslation } from 'react-i18next'

import { publicAPI } from '../services/api'

const urlBase64ToUint8Array = value => {
  const padding = '='.repeat((4 - (value.length % 4)) % 4)
  const base64 = (value + padding).replace(/-/g, '+').replace(/_/g, '/')
  return Uint8Array.from([...window.atob(base64)].map(character => character.charCodeAt(0)))
}

const PushNotificationToggle = () => {
  const { t } = useTranslation()
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
        toast.success(t('pushToggle.disabled'))
        return
      }

      const permission = await Notification.requestPermission()
      if (permission !== 'granted') throw new Error('permission-denied')
      const { data } = await publicAPI.getVapidPublicKey()
      if (!data.key) {
        toast.error(t('pushToggle.notConfigured'))
        return
      }
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(data.key),
      })
      await publicAPI.pushSubscribe(subscription.toJSON())
      setEnabled(true)
      toast.success(t('pushToggle.enabled'))
    } catch (error) {
      toast.error(error.message === 'permission-denied' ? t('pushToggle.permissionDenied') : t('pushToggle.enableFailed'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <button type="button" className={`footer-push-toggle ${enabled ? 'active' : ''}`} onClick={toggle} disabled={loading}>
      <i className={`${enabled ? 'fas' : 'far'} fa-bell`} />
      {loading ? t('pushToggle.checking') : enabled ? t('pushToggle.on') : t('pushToggle.turnOn')}
    </button>
  )
}

export default PushNotificationToggle
