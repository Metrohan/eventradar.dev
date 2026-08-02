import React from 'react'
import { Link } from 'react-router-dom'
import i18n from '../i18n'

// Class component (error boundaries can't be functions), so it can't call
// useTranslation(); it reads directly off the i18n singleton instead. This
// is non-reactive to language changes, but the boundary only renders once
// per error, so a stale render isn't a practical concern here.
class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props)
        this.state = { hasError: false, error: null }
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error }
    }

    componentDidCatch(error, errorInfo) {
        console.error('ErrorBoundary caught an error:', error, errorInfo)
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="error-page-container">
                    <div className="error-page-content">
                        <div className="error-icon-wrapper">
                            <div className="error-icon-bg error-icon-bg--danger">
                                <i className="fas fa-bug error-icon-main"></i>
                            </div>
                        </div>

                        <h1 className="error-code error-code--danger">{i18n.t('errorBoundary.title')}</h1>
                        <h2 className="error-title">{i18n.t('errorBoundary.heading')}</h2>
                        <p className="error-description">
                            {i18n.t('errorBoundary.description')}
                        </p>

                        <div className="error-actions">
                            <button
                                onClick={() => {
                                    this.setState({ hasError: false, error: null })
                                    window.location.reload()
                                }}
                                className="btn btn-primary btn-lg error-btn"
                            >
                                <i className="fas fa-redo me-2"></i>
                                {i18n.t('serverError.reload')}
                            </button>
                            <Link to="/" className="btn btn-outline-secondary btn-lg error-btn"
                                onClick={() => this.setState({ hasError: false, error: null })}
                            >
                                <i className="fas fa-home me-2"></i>
                                {i18n.t('notFound.backHome')}
                            </Link>
                        </div>
                    </div>
                </div>
            )
        }

        return this.props.children
    }
}

export default ErrorBoundary
