import React from 'react'

const trainings = [
    {
        id: 'google',
        title: 'Google Cloud Skills Boost',
        description: 'Google Cloud teknolojilerini öğrenmek için laboratuvarlar, görevler ve kurslar. Google Developers sertifikasyon programlarına hazırlık.',
        url: 'https://www.cloudskillsboost.google/',
        icon: 'fab fa-google',
        color: '#4285F4',
        badge: 'Bulut & Yazılım'
    },
    {
        id: 'aws',
        title: 'AWS Skill Builder',
        description: 'Amazon Web Services tarafından sunulan 600\'den fazla ücretsiz dijital kurs. Bulut bilişim kariyerinize başlamak için ideal.',
        url: 'https://explore.skillbuilder.aws/',
        icon: 'fab fa-aws',
        color: '#FF9900',
        badge: 'Bulut Bilişim'
    },
    {
        id: 'microsoft',
        title: 'Microsoft Learn',
        description: 'Azure, .NET, Microsoft 365 ve daha fazlası için interaktif öğrenme yolları ve modüller. Rol tabanlı sertifikasyon hazırlıkları.',
        url: 'https://learn.microsoft.com/',
        icon: 'fab fa-microsoft',
        color: '#00A4EF',
        badge: 'Yazılım & Bulut'
    },
    {
        id: 'ibm',
        title: 'IBM SkillsBuild',
        description: 'Yapay zeka, siber güvenlik, veri bilimi ve profesyonel beceriler üzerine ücretsiz kurslar ve dijital rozetler.',
        url: 'https://skillsbuild.org/',
        icon: 'fas fa-server', // IBM icon might not be in standard fa-brand free set sometimes, but usually is. fallback to server if needed. 'fab fa-ibm' is valid in FA brands.
        color: '#006699',
        badge: 'AI & Veri'
    },
    {
        id: 'btk',
        title: 'BTK Akademi',
        description: 'Bilgi Teknolojileri ve İletişim Kurumu\'nun sunduğu, yazılımdan kişisel gelişime kadar geniş kapsamlı ücretsiz eğitim portalı.',
        url: 'https://www.btkakademi.gov.tr/',
        icon: 'fas fa-graduation-cap',
        color: '#E30A17',
        badge: 'Devlet Destekli'
    },
    {
        id: 'techcareer',
        title: 'Techcareer.net',
        description: 'Bootcamp\'ler, hackathon\'lar ve ücretsiz eğitimlerle teknoloji kariyerinize yön verin. Türkiye\'nin teknoloji kariyer platformu.',
        url: 'https://www.techcareer.net/courses',
        icon: 'fas fa-laptop-code',
        color: '#00C26D',
        badge: 'Kariyer & Bootcamp'
    },
    {
        id: 'linuxfoundation',
        title: 'Linux Foundation',
        description: 'Linux ve açık kaynak teknolojileri üzerine dünyanın en saygın kuruluşundan ücretsiz giriş seviyesi kurslar.',
        url: 'https://training.linuxfoundation.org/resources/free-courses/',
        icon: 'fab fa-linux',
        color: '#003366',
        badge: 'Açık Kaynak'
    },
    {
        id: 'freecodecamp',
        title: 'freeCodeCamp',
        description: 'Web geliştirme, veri analizi ve makine öğrenmesi konularında "gerçek projeler" bitirme şartıyla verilen sektörde saygın sertifikalar.',
        url: 'https://www.freecodecamp.org/',
        icon: 'fab fa-free-code-camp',
        color: '#0a0a23',
        badge: 'Yazılım Geliştirme'
    },
    {
        id: 'kaggle',
        title: 'Kaggle',
        description: 'Derin öğrenme ve veri bilimi üzerine mikro-kurslar. Özellikle medikal hasar tespiti projelerinde kullanabileceğiniz pratik sertifikalar.',
        url: 'https://www.kaggle.com/learn',
        icon: 'fab fa-kaggle',
        color: '#20BEFF',
        badge: 'Veri Bilimi & AI'
    },
    {
        id: 'huggingface',
        title: 'Hugging Face',
        description: 'NLP ve AI modelleri üzerine teknik eğitimler ve rozetler. Ar-Ge projeleriniz için doğrudan ilgili kaynaklar.',
        url: 'https://huggingface.co/learn',
        icon: 'fas fa-robot',
        color: '#FFD21E',
        badge: 'Yapay Zeka & NLP'
    },
    {
        id: 'cognitiveclass',
        title: 'Cognitive Class (IBM)',
        description: 'Veri bilimi, blockchain ve büyük veri konularında ücretsiz ve doğrulanabilir sertifikalar.',
        url: 'https://cognitiveclass.ai/',
        icon: 'fas fa-brain',
        color: '#1F70C1',
        badge: 'Veri & Blockchain'
    },
    {
        id: 'cisco',
        title: 'Cisco Networking Academy',
        description: 'Temel siber güvenlik ve ağ yönetimi (IoT projeleri için kritik) alanında ücretsiz giriş seviyesi sertifikaları.',
        url: 'https://www.netacad.com/courses/all-courses',
        icon: 'fas fa-network-wired',
        color: '#1BA0D7',
        badge: 'Ağ & Güvenlik'
    },
    {
        id: 'odtubilgeis',
        title: 'ODTÜ Bilgeİş',
        description: '100’den fazla ücretsiz kurs ve ODTÜ onaylı sertifika. Türkiye\'deki kurumsal başvurularda geçerliliği yüksek.',
        url: 'https://bilgeis.net/',
        icon: 'fas fa-university',
        color: '#E30A17',
        badge: 'Akademik Sertifika'
    },
    {
        id: 'nvidia',
        title: 'NVIDIA Deep Learning Institute',
        description: 'Derin öğrenme, yapay zeka ve Python üzerine ücretsiz kamplar ve teknik sertifikalar.',
        url: 'https://www.nvidia.com/en-us/deep-learning-ai/education/',
        icon: 'fas fa-microchip',
        color: '#76B900',
        badge: 'Derin Öğrenme'
    },
    {
        id: 'iienstitu',
        title: 'İstanbul İşletme Enstitüsü',
        description: 'Soft-skill, yönetimsel dersler ve geniş ücretsiz eğitim/sertifika seçenekleri.',
        url: 'https://www.iienstitu.com/',
        icon: 'fas fa-briefcase',
        color: '#2C3E50',
        badge: 'Kişisel Gelişim'
    }
]

const FreeTrainingsPage = () => {
    return (
        <div className="container py-4">
            {/* Header Section */}
            <div className="header-info mb-5">
                <div className="row">
                    <div className="col-md-8">
                        <h1 className="display-4 fw-bold text-primary mb-3">
                            Ücretsiz Eğitim Kaynakları
                        </h1>
                        <p className="lead text-muted">
                            Dünyanın önde gelen teknoloji şirketlerinin sunduğu ücretsiz eğitimler ile kariyerinize değer katın.
                        </p>
                    </div>
                </div>
            </div>

            {/* Trainings Grid */}
            <div className="row g-4">
                {trainings.map((training) => (
                    <div key={training.id} className="col-md-6 col-lg-6">
                        <div className="card h-100 bg-card border-0 shadow-sm hover-elevate transition-all">
                            <div className="card-body p-4 d-flex flex-column h-100">
                                <div className="d-flex align-items-center mb-4">
                                    <div
                                        className="icon-wrapper d-flex align-items-center justify-content-center rounded-3 me-3"
                                        style={{
                                            width: '60px',
                                            height: '60px',
                                            backgroundColor: `${training.color}20`, // 20 varies opacity 
                                            color: training.color
                                        }}
                                    >
                                        <i className={`${training.icon} fa-2x`}></i>
                                    </div>
                                    <div>
                                        <span className="badge bg-success mb-1">
                                            {training.badge}
                                        </span>
                                        <h3 className="h4 card-title mb-0 fw-bold">
                                            {training.title}
                                        </h3>
                                    </div>
                                </div>

                                <p className="card-text text-muted mb-4 fs-5 flex-grow-0">
                                    {training.description}
                                </p>

                                <div className="mt-auto">
                                    <a
                                        href={training.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="btn btn-lg w-100 fw-bold"
                                        style={{
                                            backgroundColor: training.color,
                                            color: '#fff',
                                            border: 'none'
                                        }}
                                    >
                                        Eğitime Başla <i className="fas fa-external-link-alt ms-2"></i>
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Info Section */}
            <div className="mt-5 p-4 bg-card rounded-3 border">
                <div className="d-flex align-items-start">
                    <i className="fas fa-info-circle text-primary fa-2x me-3 mt-1"></i>
                    <div>
                        <h5 className="fw-bold">Bu Kaynaklar Hakkında</h5>
                        <p className="mb-0 text-muted">
                            Listelenen eğitim platformları, ilgili teknoloji devlerinin resmi ve ücretsiz öğrenme merkezleridir.
                            Sertifikasyon sınavları genellikle ücretli olsa da, eğitim içeriklerinin ve laboratuvarların büyük bir kısmı ücretsiz olarak sunulmaktadır.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default FreeTrainingsPage
