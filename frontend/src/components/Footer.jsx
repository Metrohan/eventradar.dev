import React from 'react';

const Footer = () => {
    return (
        <footer className="footer mt-auto py-5 bg-card border-top border-secondary">
            <div className="container">
                <div className="row gy-4">
                    <div className="col-lg-4 col-md-6">
                        <h5 className="h4 text-primary fw-bold mb-3">TechEventRadar</h5>
                        <p className="text-muted">
                            Türkiye'nin en güncel teknoloji etkinliklerini, hackathon'larını ve ücretsiz eğitimlerini tek bir noktadan takip edin.
                        </p>
                        <div className="d-flex gap-3 mt-4">
                            <a href="https://github.com/Metrohan/eventradar.dev" target="_blank" rel="noopener noreferrer" className="text-secondary hover-primary transition-all">
                                <i className="fab fa-github fa-lg"></i>
                            </a>
                            <a href="mailto:metehangnn@outlook.com" className="text-secondary hover-primary transition-all">
                                <i className="fas fa-envelope fa-lg"></i>
                            </a>
                        </div>
                    </div>

                    <div className="col-lg-2 col-md-6">
                        <h6 className="text-white fw-bold mb-3">Hızlı Bağlantılar</h6>
                        <ul className="list-unstyled mb-0">
                            <li className="mb-2">
                                <a href="/" className="text-muted text-decoration-none hover-white transition-all">Anasayfa</a>
                            </li>
                            <li className="mb-2">
                                <a href="/egitim-kaynaklari" className="text-muted text-decoration-none hover-white transition-all">Ücretsiz Eğitimler</a>
                            </li>
                            <li className="mb-2">
                                <a href="/oneri-sikayet" className="text-muted text-decoration-none hover-white transition-all">Öneri & Şikayet</a>
                            </li>
                            <li className="mb-2">
                                <a href="/etkinlik-talep" className="text-muted text-decoration-none hover-white transition-all">Etkinlik Ekle</a>
                            </li>
                        </ul>
                    </div>
                    <div className="col-lg-4 col-md-6 text-lg-end text-center">
                        <div className="p-3 bg-dark rounded-3 d-inline-block border border-secondary">
                            <span className="text-primary fw-bold d-block mb-1">TechEventRadar</span>
                            <small className="text-muted">Open Source Community Project</small>
                        </div>
                    </div>
                </div>

                <div className="row mt-5 pt-4 border-top border-secondary">
                    <div className="col-md-6 text-center text-md-start">
                        <p className="mb-0 text-muted small">
                            &copy; {new Date().getFullYear()} TechEventRadar.
                        </p>
                    </div>
                    <div className="col-md-6 text-center text-md-end">
                        <p className="mb-0 text-muted small">
                            Yazılım alanında kendini geliştirmek isteyenler için tasarlandı. <i className="fas fa-heart text-danger mx-1"></i>
                        </p>
                    </div>
                </div>
            </div>

            <style jsx>{`
                .hover-primary:hover { color: var(--action-primary) !important; }
                .hover-white:hover { color: var(--text-primary) !important; }
                .bg-card { background-color: var(--bg-card); }
                .border-secondary { border-color: rgba(148, 163, 184, 0.1) !important; }
                .text-muted { color: var(--text-secondary) !important; }
                .footer { color: var(--text-primary); }
            `}</style>
        </footer>
    );
};

export default Footer;
