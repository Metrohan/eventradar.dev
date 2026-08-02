import { useTranslation } from 'react-i18next'

const LoadingSpinner = ({ message }) => {
  const { t } = useTranslation()
  const effectiveMessage = message ?? t('common.loading')
  return (
    <div className="loading-spinner">
      <div style={{ textAlign: 'center' }}>
        <div className="spinner-ring" style={{ margin: '0 auto 1rem' }} />
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: 0 }}>{effectiveMessage}</p>
      </div>
    </div>
  )
}

export default LoadingSpinner
