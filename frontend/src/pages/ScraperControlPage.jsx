import React, { useState, useEffect } from 'react'
import { adminAPI } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import { toast } from 'react-hot-toast'
import { format } from 'date-fns'
import { tr } from 'date-fns/locale'
import { useAuth } from '../contexts/AuthContext'
import { Navigate } from 'react-router-dom'
import useSources from '../hooks/useSources'

const ScraperControlPage = () => {
    const { isAuthenticated, loading: authLoading } = useAuth()
    const [statusData, setStatusData] = useState([])
    const [logs, setLogs] = useState([])
    const [dataLoading, setDataLoading] = useState(true)
    const [triggering, setTriggering] = useState(false)
    const { sources: catalogSources } = useSources()

    const fetchData = async () => {
        try {
            const [statusRes, logsRes] = await Promise.all([
                adminAPI.getScraperStatus(),
                adminAPI.getScraperlogs()
            ])
            setStatusData(statusRes.data)
            setLogs(logsRes.data)
        } catch (error) {
            console.error("Error fetching scraper data:", error)
            toast.error("Veriler yüklenirken hata oluştu")
        } finally {
            setDataLoading(false)
        }
    }

    useEffect(() => {
        if (!isAuthenticated) return undefined
        fetchData()
        const interval = setInterval(fetchData, 30000) // auto refresh every 30s
        return () => clearInterval(interval)
    }, [isAuthenticated])

    const handleTrigger = async (source) => {
        setTriggering(true)
        try {
            const res = await adminAPI.triggerScraper(source)
            if (res.data?.already_running) {
                toast.error(res.data.message)
            } else {
                toast.success(`${source} taraması başlatıldı. Arka planda çalışıyor.`)
                // Refresh logs immediately to show 'running' if we had that state,
                // but for now just wait for next poll or manual refresh
                setTimeout(fetchData, 2000)
            }
        } catch {
            toast.error("Tetikleme başarısız")
        } finally {
            setTriggering(false)
        }
    }

    if (authLoading) return <LoadingSpinner />
    if (!isAuthenticated) return <Navigate to="/admin/login" />

    if (dataLoading) return <LoadingSpinner />

    // Helper to get status color
    const getStatusColor = (status) => {
        return status === 'success' ? 'bg-success' : 'bg-danger'
    }

    // Helper to find specific source status
    const getSourceStatus = (source) => {
        return statusData.find(s => s.source.toLowerCase() === source.toLowerCase())
    }

    const sources = [
        { label: 'All', key: 'All' },
        ...catalogSources.map(source => ({ label: source.name, key: source.key })),
    ]

    return (
        <div className="container py-4">
            <h1 className="h3 mb-4">
                <i className="fas fa-robot me-2 text-primary"></i>
                Scraper Kontrol Merkezi (The Heart)
            </h1>

            {/* Status Cards */}
            <div className="row g-4 mb-5">
                {sources.map(({ label, key }) => {
                    const status = getSourceStatus(label)
                    const isHealthy = status?.status === 'success'

                    return (
                        <div key={key} className="col-md-3 col-sm-6">
                            <div className="card bg-card border-secondary h-100 shadow-sm">
                                <div className="card-body text-center">
                                    <h5 className="card-title mb-3">{label}</h5>

                                    <div className="mb-3">
                                        <div
                                            className={`rounded-circle mx-auto d-flex align-items-center justify-content-center shadow-lg ${status ? getStatusColor(status.status) : 'bg-secondary'}`}
                                            style={{ width: '60px', height: '60px', opacity: 0.8 }}
                                        >
                                            <i className={`fas ${isHealthy ? 'fa-check' : 'fa-exclamation-triangle'} fa-xl text-white`}></i>
                                        </div>
                                    </div>

                                    <p className="text-muted small mb-3">
                                        Son Çalışma: {status ? format(new Date(status.created_at), 'dd MMM HH:mm', { locale: tr }) : 'Henüz Veri Yok'}
                                    </p>

                                    <button
                                        className="btn btn-outline-primary w-100 btn-sm"
                                        onClick={() => handleTrigger(key)}
                                        disabled={triggering}
                                    >
                                        {triggering ? <i className="fas fa-spinner fa-spin"></i> : 'Tetikle'}
                                    </button>
                                </div>
                            </div>
                        </div>
                    )
                })}
            </div>

            {/* Logs Table */}
            <div className="card bg-card border-secondary">
                <div className="card-header border-secondary bg-transparent">
                    <h5 className="mb-0">Son İşlem Kayıtları</h5>
                </div>
                <div className="table-responsive">
                    <table className="table table-dark table-hover mb-0 align-middle">
                        <thead>
                            <tr>
                                <th>Kaynak</th>
                                <th>Durum</th>
                                <th>Tarih</th>
                                <th>Süre (sn)</th>
                                <th>Mesaj</th>
                            </tr>
                        </thead>
                        <tbody>
                            {logs.map(log => (
                                <tr key={log.id}>
                                    <td>
                                        <span className="badge bg-dark border border-secondary text-white">
                                            {log.source}
                                        </span>
                                    </td>
                                    <td>
                                        <span className={`badge ${log.status === 'success' ? 'bg-success' : 'bg-danger'} text-white`}>
                                            {log.status === 'success' ? 'Başarılı' : 'Hata'}
                                        </span>
                                    </td>
                                    <td className="text-muted">
                                        {format(new Date(log.created_at), 'dd MMMM HH:mm', { locale: tr })}
                                    </td>
                                    <td className="text-muted">
                                        {log.duration_seconds.toFixed(2)}s
                                    </td>
                                    <td className="text-muted small text-truncate" style={{ maxWidth: '200px' }}>
                                        {log.error_message || '-'}
                                    </td>
                                </tr>
                            ))}
                            {logs.length === 0 && (
                                <tr>
                                    <td colSpan="5" className="text-center py-4 text-muted">
                                        Henüz kayıt bulunmuyor.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            <style jsx>{`
                .bg-card { background-color: var(--bg-card); }
                .border-secondary { border-color: rgba(148, 163, 184, 0.1) !important; }
            `}</style>
        </div>
    )
}

export default ScraperControlPage
