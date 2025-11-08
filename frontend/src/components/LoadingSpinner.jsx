import React from 'react'

const LoadingSpinner = ({ message = 'Yükleniyor...' }) => {
  return (
    <div className="loading-spinner">
      <div className="text-center">
        <div className="spinner mb-3"></div>
        <p className="text-muted">{message}</p>
      </div>
    </div>
  )
}

export default LoadingSpinner


