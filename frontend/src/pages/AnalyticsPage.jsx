import React, { useState, useEffect } from 'react'
import { adminAPI } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import { toast } from 'react-hot-toast'
import { useAuth } from '../contexts/AuthContext'
import { Navigate } from 'react-router-dom'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const AnalyticsPage = () => {
    const { isAuthenticated, loading: authLoading } = useAuth()
    const [stats, setStats] = useState(null)
    const [dataLoading, setDataLoading] = useState(true)

    // Early returns moved to bottom to satisfy Rules of Hooks

    const fetchData = async () => {
        try {
            const res = await adminAPI.getTrafficStats(30)
            setStats(res.data)
        } catch (error) {
            console.error(error)
            toast.error("Analiz verileri yüklenemedi")
        } finally {
            setDataLoading(false)
        }
    }

    useEffect(() => {
        if (isAuthenticated) {
            fetchData()
        }
    }, [isAuthenticated])

    if (authLoading) return <LoadingSpinner />
    if (!isAuthenticated) return <Navigate to="/admin/login" />

    if (dataLoading) return <LoadingSpinner />

    return (
        <div className="container py-4">
            <h1 className="h3 mb-4">
                <i className="fas fa-chart-line me-2 text-info"></i>
                Site Trafik Analizi
            </h1>

            {/* Overview Cards */}
            <div className="row g-4 mb-5">
                <div className="col-md-6">
                    <div className="card bg-card border-secondary h-100">
                        <div className="card-body text-center">
                            <h2 className="display-4 fw-bold text-success mb-0">{stats?.today_visitors}</h2>
                            <p className="text-secondary">Bugünkü Ziyaretçi</p>
                        </div>
                    </div>
                </div>
                <div className="col-md-6">
                    <div className="card bg-card border-secondary h-100">
                        <div className="card-body text-center">
                            <h2 className="display-4 fw-bold mb-0">{stats?.total_visitors}</h2>
                            <p className="text-secondary">Toplam Görüntülenme (Tüm Zamanlar)</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Graph */}
            <div className="card bg-card border-secondary mb-5">
                <div className="card-header border-secondary bg-transparent">
                    <h5 className="mb-0">Son 30 Gün Ziyaretçi Grafiği</h5>
                </div>
                <div className="card-body" style={{ height: '400px' }}>
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={stats?.daily_traffic}>
                            <defs>
                                <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#38BDF8" stopOpacity={0.8} />
                                    <stop offset="95%" stopColor="#38BDF8" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                            <XAxis dataKey="date" stroke="#94a3b8" />
                            <YAxis stroke="#94a3b8" />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#fff' }}
                                itemStyle={{ color: '#38BDF8' }}
                            />
                            <Area type="monotone" dataKey="count" stroke="#38BDF8" fillOpacity={1} fill="url(#colorCount)" />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Top Pages */}
            <div className="card bg-card border-secondary">
                <div className="card-header border-secondary bg-transparent">
                    <h5 className="mb-0">En Çok Ziyaret Edilen Sayfalar</h5>
                </div>
                <div className="table-responsive">
                    <table className="table table-dark table-hover mb-0 align-middle">
                        <thead>
                            <tr>
                                <th>Sayfa URL</th>
                                <th className="text-end">Görüntülenme Sayısı</th>
                            </tr>
                        </thead>
                        <tbody>
                            {stats?.top_pages?.map((page, index) => (
                                <tr key={index}>
                                    <td className="text-info">{page.path}</td>
                                    <td className="text-end fw-bold">{page.count}</td>
                                </tr>
                            ))}
                            {stats?.top_pages?.length === 0 && (
                                <tr>
                                    <td colSpan="2" className="text-center text-muted">Henüz veri yok.</td>
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

export default AnalyticsPage
