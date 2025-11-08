import React from 'react'

const ErrorMessage = ({ message, onRetry }) => {
  return (
    <div className="container py-4">
      <div className="error-message">
        <div className="d-flex align-items-center">
          <i className="fas fa-exclamation-triangle fa-2x me-3"></i>
          <div>
            <h5 className="mb-1">Hata Oluştu</h5>
            <p className="mb-0">{message}</p>
          </div>
        </div>
        {onRetry && (
          <div className="mt-3">
            <button onClick={onRetry} className="btn btn-outline-danger">
              <i className="fas fa-redo me-1"></i>
              Tekrar Dene
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default ErrorMessage


