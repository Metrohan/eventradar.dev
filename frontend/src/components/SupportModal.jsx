import React, { useState } from 'react'

const SupportModal = ({ show, handleClose }) => {
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

    return (
        <div className="modal fade show" style={{ display: 'block', backgroundColor: 'rgba(15, 23, 42, 0.7)' }} tabIndex="-1">
            <div className="modal-dialog modal-dialog-centered">
                <div className="modal-content border-0 shadow-lg" style={{ borderRadius: '1rem', overflow: 'hidden' }}>
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
                            <h3 className="fw-bold mb-3 text-muted">Projeye Destek Ol</h3>
                            <p className="text-muted">
                                TechEventRadar tamamen gönüllülük esasıyla geliştirilen açık kaynaklı bir projedir.
                                Geliştirmemize katkıda bulunmak için bize bir kahve ısmarlayabilir veya projemizi çevrenizle paylaşabilirsiniz.
                            </p>
                        </div>

                        <div className="d-grid gap-3">
                            <a
                                href="https://www.buymeacoffee.com/metehangnn"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="btn btn-lg fw-bold d-flex align-items-center justify-content-center gap-2 transition-all hover-scale"
                                style={{ backgroundColor: '#FFDD00', color: '#000', border: 'none', borderRadius: '0.75rem', padding: '12px' }}
                            >
                                <img src="/coffee.svg" alt="Coffee" style={{ width: '28px' }} />
                                Buy Me A Coffee
                            </a>

                            <button
                                onClick={handleCopyLink}
                                className={`btn btn-lg fw-bold d-flex align-items-center justify-content-center gap-2 ${copySuccess ? 'btn-success' : 'btn-outline-primary'}`}
                                style={{ borderRadius: '0.75rem', padding: '12px', transition: 'all 0.3s ease' }}
                            >
                                {copySuccess ? (
                                    <>
                                        <i className="fas fa-check-circle"></i> Link Kopyalandı!
                                    </>
                                ) : (
                                    <>
                                        <i className="fas fa-share-nodes"></i> Paylaş
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default SupportModal
