import React, { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from 'react-query'
import { publicAPI } from '../services/api'
import EventCard from '../components/EventCard'
import LoadingSpinner from '../components/LoadingSpinner'

const SOURCES = [
  {
    name: 'Patika.dev',
    url: 'https://www.patika.dev',
    desc: 'Yazılım, veri bilimi ve Web3 alanlarında Türkçe ücretsiz bootcamp programları.',
  },
  {
    name: 'Kodluyoruz',
    url: 'https://www.kodluyoruz.org',
    desc: 'Frontend, backend ve mobil geliştirme odaklı ücretsiz bootcamp programları. Mezunlara iş imkânı.',
  },
  {
    name: 'Coderspace',
    url: 'https://coderspace.io',
    desc: 'Hackathon ve kariyer etkinlikleri odaklı topluluk platformu.',
  },
  {
    name: 'Youthall',
    url: 'https://www.youthall.com',
    desc: 'Şirket sponsorlu staj, kariyer etkinliği ve online seminerler.',
  },
  {
    name: 'TechCareer.net',
    url: 'https://techcareer.net',
    desc: 'Yazılım kariyeri için ücretsiz bootcamp ve sertifika programları.',
  },
  {
    name: 'BTK Akademi',
    url: 'https://www.btkakademi.gov.tr',
    desc: 'Devlet destekli ücretsiz yazılım, siber güvenlik ve yapay zeka kursları.',
  },
  {
    name: 'Akbank Gençlik Akademisi',
    url: 'https://www.akbanklabs.com',
    desc: 'Fintech ve yazılım alanında banka destekli ücretsiz bootcamp programları.',
  },
  {
    name: 'Pupilica',
    url: 'https://pupilica.com',
    desc: 'Üniversite öğrencilerine yönelik şirket mentörlüğünde bootcamp etkinlikleri.',
  },
]

const STEPS = [
  { icon: 'fa-search', title: 'Platforma kaydol', desc: 'Kodluyoruz, Patika.dev veya TechCareer gibi platformlarda ücretsiz hesap aç.' },
  { icon: 'fa-calendar-check', title: 'Başvuru tarihini takip et', desc: 'Bootcamp programları genellikle 2-4 haftada bir açılır; başvuru süreleri kısadır.' },
  { icon: 'fa-file-alt', title: 'Başvuru formunu doldur', desc: 'Motivasyon mektubu ve teknik seviyeni anlatan kısa form.' },
  { icon: 'fa-laptop-code', title: 'Programa katıl', desc: 'Çoğu program online ve ücretsiz; sadece düzenli katılım beklenir.' },
]

const BootcampRehberi = () => {
  useEffect(() => {
    document.title = 'Türkiye Ücretsiz Bootcamp Rehberi 2026 | TechEventRadar'
    const desc = 'Türkiye\'deki ücretsiz bootcamp, hackathon ve kariyer etkinliklerinin tam listesi. 2026 güncel.'
    const setMeta = (name, content, property = false) => {
      const attr = property ? `[property="${name}"]` : `[name="${name}"]`
      let el = document.querySelector(`meta${attr}`)
      if (!el) {
        el = document.createElement('meta')
        el.setAttribute(property ? 'property' : 'name', name)
        document.head.appendChild(el)
      }
      el.setAttribute('content', content)
    }
    setMeta('description', desc)
    setMeta('og:title', 'Türkiye Ücretsiz Bootcamp Rehberi 2026 | TechEventRadar', true)
    setMeta('og:description', desc, true)
  }, [])

  const { data, isLoading } = useQuery('events', () => publicAPI.getEvents(true), { staleTime: 5 * 60 * 1000 })

  const bootcampEvents = React.useMemo(() => {
    const events = data?.data?.events || []
    return events
      .filter(e => {
        const tags = e.tags || []
        const title = (e.title || '').toLowerCase()
        return tags.some(t => ['bootcamp', 'hackathon', 'kariyer'].includes(t.toLowerCase()))
          || title.includes('bootcamp')
          || title.includes('hackathon')
      })
      .slice(0, 5)
  }, [data])

  return (
    <div className="container py-5">
      <div className="row justify-content-center">
        <div className="col-lg-8">

          {/* Breadcrumb */}
          <nav style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '2rem' }}>
            <Link to="/" style={{ color: 'var(--text-muted)', textDecoration: 'none' }}>Anasayfa</Link>
            <span className="mx-2">/</span>
            <span>Bootcamp Rehberi</span>
          </nav>

          {/* H1 */}
          <h1 style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--text-primary)', lineHeight: 1.25, marginBottom: '0.5rem' }}>
            Türkiye'de Ücretsiz Bootcamp'lar — 2026 Rehberi
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', marginBottom: '3rem' }}>
            Son güncelleme: Mayıs 2026 · 8 kaynak · Ücretsiz
          </p>

          {/* Bölüm 1 */}
          <section style={{ marginBottom: '3rem' }}>
            <h2 style={h2Style}>Bootcamp Nedir?</h2>
            <p style={pStyle}>
              Bootcamp, kısa sürede (genellikle 4–16 hafta) yoğun pratik eğitim sunan programlardır.
              Üniversite eğitiminin aksine teoriden çok uygulamaya odaklanır. Katılımcılar gerçek projeler
              yaparak yazılım geliştirme, veri bilimi veya siber güvenlik gibi alanlarda iş hayatına hazırlanır.
            </p>
            <p style={pStyle}>
              Türkiye'de devlet kurumları, özel şirketler ve sivil toplum kuruluşları tarafından düzenlenen
              pek çok bootcamp tamamen ücretsizdir. Hatta bir kısmı burs veya iş garantisi de sunmaktadır.
            </p>
          </section>

          {/* Bölüm 2 */}
          <section style={{ marginBottom: '3rem' }}>
            <h2 style={h2Style}>Türkiye'deki Popüler Bootcamp Kaynakları</h2>
            <p style={{ ...pStyle, marginBottom: '1.5rem' }}>
              Aşağıdaki platformlar düzenli olarak ücretsiz bootcamp ve kariyer etkinliği açmaktadır:
            </p>
            <div className="row g-3">
              {SOURCES.map(s => (
                <div key={s.name} className="col-md-6">
                  <a
                    href={s.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      display: 'block',
                      padding: '1rem 1.25rem',
                      background: 'var(--bg-card)',
                      border: '1px solid var(--border-color)',
                      borderRadius: '10px',
                      textDecoration: 'none',
                      transition: 'border-color 0.2s',
                    }}
                    onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--action-primary)'}
                    onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border-color)'}
                  >
                    <strong style={{ color: 'var(--text-primary)', display: 'block', marginBottom: '0.3rem' }}>
                      {s.name}
                    </strong>
                    <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{s.desc}</span>
                  </a>
                </div>
              ))}
            </div>
          </section>

          {/* Bölüm 3 */}
          <section style={{ marginBottom: '3rem' }}>
            <h2 style={h2Style}>Hackathon'a Nasıl Katılırım?</h2>
            <p style={pStyle}>
              Hackathon'lar genellikle 24–72 saat süren, takım halinde yazılım geliştirme yarışmalarıdır.
              Başlangıç seviyesinden uzmana kadar herkese açık etkinlikler düzenlenmektedir.
            </p>
            <div className="row g-3 mt-1">
              {STEPS.map((step, i) => (
                <div key={i} className="col-md-6">
                  <div style={{
                    padding: '1rem 1.25rem',
                    background: 'var(--bg-card)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '10px',
                    display: 'flex',
                    gap: '0.875rem',
                    alignItems: 'flex-start',
                  }}>
                    <div style={{
                      width: '36px', height: '36px', borderRadius: '8px', flexShrink: 0,
                      background: 'rgba(56,189,248,0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center',
                    }}>
                      <i className={`fas ${step.icon}`} style={{ color: 'var(--action-primary)', fontSize: '0.9rem' }}></i>
                    </div>
                    <div>
                      <strong style={{ color: 'var(--text-primary)', fontSize: '0.9rem', display: 'block', marginBottom: '0.2rem' }}>
                        {i + 1}. {step.title}
                      </strong>
                      <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>{step.desc}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Bölüm 4 */}
          <section style={{ marginBottom: '3rem' }}>
            <h2 style={h2Style}>Kariyer Etkinlikleri Neden Önemli?</h2>
            <p style={pStyle}>
              Yazılım sektöründe iş bulmak artık yalnızca teknik bilgiyle değil, doğru ağ ve görünürlükle de
              ilgilidir. Kariyer etkinlikleri işverenlerle doğrudan tanışma, portfolyo sunma ve referans edinme
              fırsatı sunar.
            </p>
            <ul style={{ color: 'var(--text-secondary)', lineHeight: 2, paddingLeft: '1.25rem', margin: 0 }}>
              <li>İşverenler etkinliklerdeki adayları daha fazla hatırlar.</li>
              <li>Bootcamp sertifikaları CV'de somut bir referans oluşturur.</li>
              <li>Hackathon projeleri GitHub portfolyonu güçlendirir.</li>
              <li>Networking, açık ilanlardan önce haberdar olmayı sağlar.</li>
            </ul>
          </section>

          {/* Canlı etkinlikler */}
          <section>
            <h2 style={h2Style}>Şu An Açık Etkinlikler</h2>
            <p style={{ ...pStyle, marginBottom: '1.5rem' }}>
              TechEventRadar'dan canlı çekilen, başvuruya açık etkinlikler:
            </p>
            {isLoading ? (
              <LoadingSpinner />
            ) : bootcampEvents.length > 0 ? (
              <div className="row g-4">
                {bootcampEvents.map(event => (
                  <div key={event.id} className="col-lg-6">
                    <EventCard event={event} />
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>
                Şu an filtreyle eşleşen açık etkinlik bulunmuyor.{' '}
                <Link to="/" style={{ color: 'var(--action-primary)' }}>Tüm etkinliklere bak →</Link>
              </p>
            )}
            <div className="text-center mt-4">
              <Link to="/" className="btn-event" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
                Tüm Etkinlikleri Gör
                <i className="fas fa-arrow-right" style={{ fontSize: '0.75rem' }}></i>
              </Link>
            </div>
          </section>

        </div>
      </div>
    </div>
  )
}

const h2Style = {
  fontSize: '1.35rem',
  fontWeight: 700,
  color: 'var(--text-primary)',
  marginBottom: '0.875rem',
  paddingBottom: '0.5rem',
  borderBottom: '1px solid var(--border-subtle)',
}

const pStyle = {
  color: 'var(--text-secondary)',
  lineHeight: 1.75,
  margin: 0,
}

export default BootcampRehberi
