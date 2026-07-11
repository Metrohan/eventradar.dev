import React from 'react'
import { useQuery } from 'react-query'
import { adminAPI } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'

const QualityPage = () => {
  const { data, isLoading, error } = useQuery('source-quality', adminAPI.getDataQuality)

  if (isLoading) return <LoadingSpinner message="Kalite metrikleri yükleniyor..." />
  if (error) return <ErrorMessage message="Kalite metrikleri yüklenemedi." />

  const payload = data?.data || {}
  const sources = payload.sources || []

  return (
    <div className="container py-4">
      <h1 className="h3 mb-4"><i className="fas fa-heartbeat me-2 text-info" />Kaynak Kalitesi</h1>
      <div className="row g-3 mb-4">
        <div className="col-md-6"><div className="card bg-card border-secondary p-3"><strong>{payload.total_events || 0}</strong><span className="text-muted"> Toplam etkinlik</span></div></div>
        <div className="col-md-6"><div className="card bg-card border-secondary p-3"><strong>{payload.active_events || 0}</strong><span className="text-muted"> Aktif etkinlik</span></div></div>
      </div>
      <div className="table-responsive">
        <table className="table table-dark table-hover align-middle">
          <thead><tr><th>Kaynak</th><th>Başarı</th><th>Tamlık</th><th>Aktif / Toplam</th><th>Eksikler</th><th>Son durum</th></tr></thead>
          <tbody>
            {sources.map(source => (
              <tr key={source.key}>
                <td><strong>{source.source}</strong></td>
                <td>{source.success_rate_percent == null ? 'Veri yok' : `%${source.success_rate_percent}`}</td>
                <td>%{source.completeness_percent}</td>
                <td>{source.active_events} / {source.total_events}</td>
                <td className="small">Tarih {source.missing_date} · Konum {source.missing_location} · Açıklama {source.missing_description}</td>
                <td>
                  <span className={`badge ${source.last_status === 'success' ? 'bg-success' : source.last_status === 'failed' ? 'bg-danger' : 'bg-secondary'}`}>
                    {source.last_status || 'Henüz çalışmadı'}
                  </span>
                  {source.consecutive_failures > 0 && <div className="small text-danger mt-1">{source.consecutive_failures} ardışık hata</div>}
                  {source.last_error && <div className="small text-muted mt-1">{source.last_error}</div>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default QualityPage
