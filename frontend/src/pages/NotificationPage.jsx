import React, { useState, useEffect } from 'react'
import { adminAPI } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import { toast } from 'react-hot-toast'
import { useAuth } from '../contexts/AuthContext'
import { Navigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'

const NotificationPage = () => {
    const { isAuthenticated, loading: authLoading } = useAuth()
    const [stats, setStats] = useState(null)
    const [dataLoading, setDataLoading] = useState(true)
    const { register, handleSubmit, reset, formState: { errors } } = useForm()
    const [sending, setSending] = useState(false)

    // Early returns moved to bottom to satisfy Rules of Hooks

    const fetchData = async () => {
        try {
            const res = await adminAPI.getNotificationStats()
            setStats(res.data)
        } catch (error) {
            console.error(error)
            toast.error("İstatistikler yüklenemedi")
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

    const onSubmit = async (data) => {
        setSending(true)
        try {
            await adminAPI.broadcastMessage({
                message: data.message,
                target_channel: data.target_channel
            })
            toast.success("Mesaj başarıyla gönderildi!")
            reset()
        } catch (error) {
            toast.error("Mesaj gönderilemedi.")
        } finally {
            setSending(false)
        }
    }

    if (dataLoading) return <LoadingSpinner />

    return (
        <div className="container py-4">
            <h1 className="h3 mb-4 text-white">
                <i className="fas fa-bullhorn me-2 text-warning"></i>
                Akıllı Bildirim Yönetimi
            </h1>

            {/* Stats Cards */}
            <div className="row g-4 mb-5">
                <div className="col-md-3">
                    <div className="card bg-card border-secondary h-100">
                        <div className="card-body text-center">
                            <h2 className="display-4 fw-bold text-white mb-0">{stats?.total_subscribers}</h2>
                            <p className="text-secondary">Toplam Abone</p>
                        </div>
                    </div>
                </div>
                <div className="col-md-3">
                    <div className="card bg-card border-secondary h-100">
                        <div className="card-body text-center">
                            <h2 className="display-4 fw-bold text-info mb-0">{stats?.telegram_count}</h2>
                            <p className="text-info">Telegram</p>
                            <i className="fab fa-telegram fa-2x text-info opacity-50"></i>
                        </div>
                    </div>
                </div>
                <div className="col-md-3">
                    <div className="card bg-card border-secondary h-100">
                        <div className="card-body text-center">
                            <h2 className="display-4 fw-bold text-warning mb-0">{stats?.email_count}</h2>
                            <p className="text-warning">E-Posta</p>
                            <i className="fas fa-envelope fa-2x text-warning opacity-50"></i>
                        </div>
                    </div>
                </div>
                <div className="col-md-3">
                    <div className="card bg-card border-secondary h-100">
                        <div className="card-body text-center">
                            <h2 className="display-4 fw-bold text-success mb-0">{stats?.active_count}</h2>
                            <p className="text-success">Aktif Kullanıcı</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Broadcast Form */}
            <div className="card bg-card border-secondary">
                <div className="card-header border-secondary bg-transparent">
                    <h5 className="mb-0 text-white">Broadcast Mesaj Gönder</h5>
                </div>
                <div className="card-body">
                    <form onSubmit={handleSubmit(onSubmit)}>
                        <div className="row">
                            <div className="col-md-4 mb-3">
                                <label className="form-label text-white">Hedef Kitle</label>
                                <select
                                    className="form-select bg-dark text-white border-secondary"
                                    {...register('target_channel')}
                                >
                                    <option value="all">Tüm Aboneler</option>
                                    <option value="telegram">Sadece Telegram</option>
                                    <option value="email">Sadece E-Posta</option>
                                </select>
                            </div>
                        </div>

                        <div className="mb-3">
                            <label className="form-label text-white">Mesaj İçeriği</label>
                            <textarea
                                className={`form-control bg-dark text-white border-secondary ${errors.message ? 'is-invalid' : ''}`}
                                rows="4"
                                placeholder="Duyurunuzu buraya yazın..."
                                {...register('message', { required: "Mesaj boş olamaz", minLength: { value: 10, message: "En az 10 karakter yazmalısınız" } })}
                            ></textarea>
                            {errors.message && <div className="invalid-feedback">{errors.message.message}</div>}
                            <div className="form-text text-muted">Bu mesaj seçili kanaldaki tüm aktif kullanıcılara gönderilecektir.</div>
                        </div>

                        <button type="button" className="btn btn-primary" onClick={handleSubmit(onSubmit)} disabled={sending}>
                            {sending ? <i className="fas fa-spinner fa-spin me-2"></i> : <i className="fas fa-paper-plane me-2"></i>}
                            Gönder
                        </button>
                    </form>
                </div>
            </div>

            <style jsx>{`
                .bg-card { background-color: var(--bg-card); }
                .border-secondary { border-color: rgba(148, 163, 184, 0.1) !important; }
            `}</style>
        </div>
    )
}

export default NotificationPage
