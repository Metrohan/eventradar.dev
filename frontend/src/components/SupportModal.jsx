import React, { useState } from 'react'
import { createPortal } from 'react-dom'
import { useTranslation } from 'react-i18next'

const SupportModal = ({ show, handleClose }) => {
    const { t } = useTranslation()
    const [copySuccess, setCopySuccess] = useState(false)

    const handleCopyLink = () => {
        navigator.clipboard.writeText(window.location.origin)
            .then(() => {
                setCopySuccess(true)
                setTimeout(() => setCopySuccess(false), 2000)
            })
            .catch(err => console.error('Link kopyalanamadı', err))
    }

    if (!show) return null

    return createPortal(
        <div className="support-modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="support-modal-title" tabIndex="-1">
            <div className="support-modal-dialog">
                <div className="modal-content border-0 shadow-lg support-modal-content">
                    <div className="modal-header border-0 pb-0 justify-content-end">
                        <button
                            type="button"
                            className="btn-close"
                            onClick={handleClose}
                            aria-label="Close"
                        ></button>
                    </div>
                    <div className="modal-body text-center px-5 pb-5 pt-0">
                        <div className="mb-4">
                            <div className="mx-auto rounded-circle d-flex align-items-center justify-content-center mb-3"
                                style={{ width: '80px', height: '80px', backgroundColor: '#F0F9FF', border: '2px solid #38BDF8' }}>
                                <i className="fas fa-heart fa-2x" style={{ color: '#38BDF8' }}></i>
                            </div>
                            <h3 id="support-modal-title" className="fw-bold mb-3">{t('supportModal.heading')}</h3>
                            <p className="text-muted">
                                {t('supportModal.description')}
                            </p>
                            <div
                                className="d-flex justify-content-center gap-4 mt-3 pt-3"
                                style={{ borderTop: '1px solid var(--border-subtle)' }}
                            >
                                <div className="text-center">
                                    <div className="fw-bold" style={{ fontSize: '1.1rem', color: 'var(--action-primary)' }}>~180₺</div>
                                    <div className="text-muted" style={{ fontSize: '0.72rem' }}>{t('supportModal.serverCost')}</div>
                                </div>
                                <div className="text-center">
                                    <div className="fw-bold" style={{ fontSize: '1.1rem', color: 'var(--action-primary)' }}>~1.700₺</div>
                                    <div className="text-muted" style={{ fontSize: '0.72rem' }}>{t('supportModal.domainCost')}</div>
                                </div>
                            </div>
                        </div>

                        <div className="d-grid gap-3">
                            <a
                                href="https://www.buymeacoffee.com/metehangnn"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="btn btn-lg fw-bold d-flex align-items-center justify-content-center gap-2 transition-all hover-scale"
                                style={{ backgroundColor: '#FFDD00', color: '#000', border: 'none', borderRadius: '0.75rem', padding: '12px' }}
                            >
                                <img src="/coffee.svg" alt="" style={{ width: '28px' }} />
                                Buy Me A Coffee
                            </a>

                            <button
                                onClick={handleCopyLink}
                                className={`btn btn-lg fw-bold d-flex align-items-center justify-content-center gap-2 ${copySuccess ? 'btn-success' : 'btn-outline-primary'}`}
                                style={{ borderRadius: '0.75rem', padding: '12px', transition: 'all 0.3s ease' }}
                            >
                                {copySuccess ? (
                                    <>
                                        <i className="fas fa-check-circle"></i> {t('supportModal.linkCopied')}
                                    </>
                                ) : (
                                    <>
                                        <i className="fas fa-share-alt"></i> {t('supportModal.share')}
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>,
        document.body
    )
}

export default SupportModal
