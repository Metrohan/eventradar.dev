import React, { useState, useMemo, useEffect } from 'react'
import { setPageSEO } from '../utils/seo'

const CATEGORIES = [
  { key: 'bulut',    label: '☁️ Bulut',     color: '#38bdf8' },
  { key: 'yazilim',  label: '💻 Yazılım',   color: '#6366f1' },
  { key: 'ai-veri',  label: '🤖 AI & Veri', color: '#a855f7' },
  { key: 'guvenlik', label: '🔐 Güvenlik',  color: '#f43f5e' },
  { key: 'akademik', label: '🎓 Akademik',  color: '#22c55e' },
  { key: 'kariyer',  label: '🚀 Kariyer',   color: '#fb923c' },
]

const CATEGORY_MAP = Object.fromEntries(CATEGORIES.map(c => [c.key, c]))

const trainings = [
  {
    id: 'google',
    title: 'Google Cloud Skills Boost',
    description: 'Google Cloud teknolojilerini öğrenmek için laboratuvarlar, görevler ve kurslar. Google Developers sertifikasyon programlarına hazırlık.',
    url: 'https://www.cloudskillsboost.google/',
    icon: 'fab fa-google',
    color: '#4285F4',
    category: 'bulut',
  },
  {
    id: 'aws',
    title: 'AWS Skill Builder',
    description: "Amazon Web Services tarafından sunulan 600'den fazla ücretsiz dijital kurs. Bulut bilişim kariyerinize başlamak için ideal.",
    url: 'https://explore.skillbuilder.aws/',
    icon: 'fab fa-aws',
    color: '#FF9900',
    category: 'bulut',
  },
  {
    id: 'microsoft',
    title: 'Microsoft Learn',
    description: 'Azure, .NET, Microsoft 365 ve daha fazlası için interaktif öğrenme yolları ve modüller. Rol tabanlı sertifikasyon hazırlıkları.',
    url: 'https://learn.microsoft.com/',
    icon: 'fab fa-microsoft',
    color: '#00A4EF',
    category: 'bulut',
  },
  {
    id: 'ibm',
    title: 'IBM SkillsBuild',
    description: 'Yapay zeka, siber güvenlik, veri bilimi ve profesyonel beceriler üzerine ücretsiz kurslar ve dijital rozetler.',
    url: 'https://skillsbuild.org/',
    icon: 'fab fa-ibm',
    color: '#006699',
    category: 'akademik',
  },
  {
    id: 'btk',
    title: 'BTK Akademi',
    description: "Bilgi Teknolojileri ve İletişim Kurumu'nun sunduğu, yazılımdan kişisel gelişime kadar geniş kapsamlı ücretsiz eğitim portalı.",
    url: 'https://www.btkakademi.gov.tr/',
    icon: 'fas fa-graduation-cap',
    color: '#E30A17',
    category: 'akademik',
  },
  {
    id: 'techcareer',
    title: 'Techcareer.net',
    description: "Bootcamp'ler, hackathon'lar ve ücretsiz eğitimlerle teknoloji kariyerinize yön verin. Türkiye'nin teknoloji kariyer platformu.",
    url: 'https://www.techcareer.net/courses',
    icon: 'fas fa-laptop-code',
    color: '#00C26D',
    category: 'kariyer',
  },
  {
    id: 'linuxfoundation',
    title: 'Linux Foundation',
    description: 'Linux ve açık kaynak teknolojileri üzerine dünyanın en saygın kuruluşundan ücretsiz giriş seviyesi kurslar.',
    url: 'https://training.linuxfoundation.org/resources/free-courses/',
    icon: 'fab fa-linux',
    color: '#003366',
    category: 'yazilim',
  },
  {
    id: 'freecodecamp',
    title: 'freeCodeCamp',
    description: '"Gerçek projeler" bitirme şartıyla verilen sektörde saygın web, veri ve makine öğrenmesi sertifikaları.',
    url: 'https://www.freecodecamp.org/',
    icon: 'fab fa-free-code-camp',
    color: '#0a0a23',
    category: 'yazilim',
  },
  {
    id: 'kaggle',
    title: 'Kaggle',
    description: 'Derin öğrenme ve veri bilimi üzerine mikro-kurslar. Özellikle veri analitiği projelerinde kullanabileceğiniz pratik sertifikalar.',
    url: 'https://www.kaggle.com/learn',
    icon: 'fab fa-kaggle',
    color: '#20BEFF',
    category: 'ai-veri',
  },
  {
    id: 'huggingface',
    title: 'Hugging Face',
    description: 'NLP ve AI modelleri üzerine teknik eğitimler ve rozetler. Ar-Ge projeleriniz için doğrudan ilgili kaynaklar.',
    url: 'https://huggingface.co/learn',
    icon: 'fas fa-robot',
    color: '#FFD21E',
    category: 'ai-veri',
  },
  {
    id: 'cognitiveclass',
    title: 'Cognitive Class (IBM)',
    description: 'Veri bilimi, blockchain ve büyük veri konularında ücretsiz ve doğrulanabilir sertifikalar.',
    url: 'https://cognitiveclass.ai/',
    icon: 'fas fa-brain',
    color: '#1F70C1',
    category: 'ai-veri',
  },
  {
    id: 'cisco',
    title: 'Cisco Networking Academy',
    description: 'Temel siber güvenlik ve ağ yönetimi alanında ücretsiz giriş seviyesi sertifikaları.',
    url: 'https://www.netacad.com/courses/all-courses',
    icon: 'fas fa-network-wired',
    color: '#1BA0D7',
    category: 'guvenlik',
  },
  {
    id: 'odtubilgeis',
    title: 'ODTÜ Bilgeİş',
    description: "100'den fazla ücretsiz kurs ve ODTÜ onaylı sertifika. Türkiye'deki kurumsal başvurularda geçerliliği yüksek.",
    url: 'https://bilgeis.net/',
    icon: 'fas fa-university',
    color: '#E30A17',
    category: 'akademik',
  },
  {
    id: 'nvidia',
    title: 'NVIDIA Deep Learning Institute',
    description: 'Derin öğrenme, yapay zeka ve Python üzerine ücretsiz kamplar ve teknik sertifikalar.',
    url: 'https://www.nvidia.com/en-us/deep-learning-ai/education/',
    icon: 'fas fa-microchip',
    color: '#76B900',
    category: 'ai-veri',
  },
  {
    id: 'iienstitu',
    title: 'İstanbul İşletme Enstitüsü',
    description: 'Soft-skill, yönetimsel dersler ve geniş ücretsiz eğitim/sertifika seçenekleri.',
    url: 'https://www.iienstitu.com/',
    icon: 'fas fa-briefcase',
    color: '#2C3E50',
    category: 'kariyer',
  },
]

const FreeTrainingsPage = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState(null)

  useEffect(() => {
    setPageSEO({
      title: 'Ücretsiz Eğitim Kaynakları | TechEventRadar',
      description: 'Google, AWS, Microsoft ve diğer teknoloji şirketlerinin sunduğu ücretsiz eğitim, sertifika ve öğrenme kaynaklarını tek listede keşfet.',
      path: '/egitim-kaynaklari',
    })
  }, [])

  const filtered = useMemo(() => {
    const q = searchQuery.toLowerCase()
    return trainings.filter(t => {
      const matchesSearch =
        !q ||
        t.title.toLowerCase().includes(q) ||
        t.description.toLowerCase().includes(q)
      const matchesCategory = !selectedCategory || t.category === selectedCategory
      return matchesSearch && matchesCategory
    })
  }, [searchQuery, selectedCategory])

  const toggleCategory = (key) =>
    setSelectedCategory(prev => (prev === key ? null : key))

  return (
    <div className="container py-4">
      <div className="page-hero">
        <h1 className="page-hero-title">Ücretsiz Eğitim Kaynakları</h1>
        <p className="page-hero-subtitle">
          Dünyanın önde gelen teknoloji şirketlerinin sunduğu ücretsiz eğitimler ile kariyerinize değer katın.
        </p>
      </div>

      {/* Search */}
      <div className="filter-row" style={{ marginBottom: '0.75rem' }}>
        <div className="filter-search-wrap">
          <i className="fas fa-search filter-search-icon" />
          <input
            type="text"
            className="filter-input"
            placeholder="Platform veya konu ara..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* Category badges */}
      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center', marginBottom: '1.5rem' }}>
        <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          KATEGORİ:
        </span>
        {CATEGORIES.map(cat => {
          const active = selectedCategory === cat.key
          return (
            <button
              key={cat.key}
              type="button"
              className="cat-badge"
              onClick={() => toggleCategory(cat.key)}
              aria-pressed={active}
              style={{
                background: active ? `${cat.color}30` : `${cat.color}18`,
                borderColor: active ? cat.color : `${cat.color}50`,
                color: cat.color,
              }}
            >
              {cat.label}
            </button>
          )
        })}
      </div>

      {/* Result count */}
      <div style={{ marginBottom: '1rem' }}>
        <span className="results-count">{filtered.length} kaynak</span>
      </div>

      {/* Grid */}
      <div className="row g-3">
        {filtered.length === 0 && (
          <div className="col-12 text-center py-5">
            <p style={{ color: 'var(--text-muted)' }}>Aramanızla eşleşen kaynak bulunamadı.</p>
          </div>
        )}
        {filtered.map(training => {
          const cat = CATEGORY_MAP[training.category]
          return (
            <div key={training.id} className="col-12 col-md-6 col-lg-4">
              <div className="training-card">
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                  <div
                    className="training-icon-wrap"
                    style={{ background: `${training.color}20`, color: training.color }}
                  >
                    <i className={`${training.icon} fa-lg`} />
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    {cat && (
                      <span
                        className="cat-badge"
                        style={{
                          background: `${cat.color}18`,
                          borderColor: `${cat.color}50`,
                          color: cat.color,
                          fontSize: '0.65rem',
                          padding: '2px 8px',
                          marginBottom: '4px',
                          display: 'inline-flex',
                        }}
                      >
                        {cat.label}
                      </span>
                    )}
                    <h3 style={{ fontSize: '0.95rem', fontWeight: 700, margin: 0, lineHeight: 1.3 }}>
                      {training.title}
                    </h3>
                  </div>
                </div>
                <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', lineHeight: 1.6, flex: 1, marginBottom: '16px' }}>
                  {training.description}
                </p>
                <a
                  href={training.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="training-cta"
                  style={{ background: training.color }}
                >
                  Eğitime Başla <i className="fas fa-external-link-alt" aria-hidden="true" style={{ fontSize: '0.75rem', marginLeft: '6px' }} />
                </a>
              </div>
            </div>
          )
        })}
      </div>

      {/* Info footer */}
      <div style={{ marginTop: '2.5rem', padding: '20px', background: 'var(--bg-card)', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
          <i className="fas fa-info-circle" style={{ color: 'var(--action-primary)', fontSize: '1.25rem', marginTop: '2px', flexShrink: 0 }} />
          <div>
            <h5 style={{ fontWeight: 700, marginBottom: '6px', fontSize: '0.95rem' }}>Bu Kaynaklar Hakkında</h5>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', margin: 0 }}>
              Listelenen eğitim platformları, ilgili teknoloji devlerinin resmi ve ücretsiz öğrenme merkezleridir.
              Sertifikasyon sınavları genellikle ücretli olsa da, eğitim içeriklerinin büyük kısmı ücretsizdir.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default FreeTrainingsPage
