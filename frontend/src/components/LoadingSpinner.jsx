const LoadingSpinner = ({ message = 'Yükleniyor...' }) => {
  return (
    <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '300px' }}>
      <div className="text-center">
        <div className="spinner-border text-primary" role="status" style={{ width: '3rem', height: '3rem' }}>
          <span className="visually-hidden">Yükleniyor...</span>
        </div>
        <p className="mt-3 text-white fs-5">{message}</p>
      </div>
    </div>
  )
}

export default LoadingSpinner


