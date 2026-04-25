const LoadingSpinner = ({ message = 'Yükleniyor...' }) => (
  <div className="loading-spinner">
    <div style={{ textAlign: 'center' }}>
      <div className="spinner-ring" style={{ margin: '0 auto 1rem' }} />
      <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: 0 }}>{message}</p>
    </div>
  </div>
)

export default LoadingSpinner
