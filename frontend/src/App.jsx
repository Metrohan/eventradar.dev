import React, { Suspense, lazy } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Header from './components/Header'
import Footer from './components/Footer'
import LoadingSpinner from './components/LoadingSpinner'
import ErrorBoundary from './components/ErrorBoundary'
import { useAuth } from './contexts/AuthContext'

// Lazy loaded pages
const HomePage = lazy(() => import('./pages/HomePage'))
const EventRequestPage = lazy(() => import('./pages/EventRequestPage'))
const SuggestionPage = lazy(() => import('./pages/SuggestionPage'))
const AdminLoginPage = lazy(() => import('./pages/AdminLoginPage'))
const AdminDashboard = lazy(() => import('./pages/AdminDashboard'))
const ScraperControlPage = lazy(() => import('./pages/ScraperControlPage'))
const NotificationPage = lazy(() => import('./pages/NotificationPage'))
const AnalyticsPage = lazy(() => import('./pages/AnalyticsPage'))
const QualityPage = lazy(() => import('./pages/QualityPage'))
const FreeTrainingsPage = lazy(() => import('./pages/FreeTrainingsPage'))
const EventDetailPage = lazy(() => import('./pages/EventDetailPage'))
const BootcampRehberi = lazy(() => import('./pages/BootcampRehberi'))
const NotFoundPage = lazy(() => import('./pages/NotFoundPage'))
const StatusPage = lazy(() => import('./pages/StatusPage'))
const ServerErrorPage = lazy(() => import('./pages/ServerErrorPage'))
const RedirectPage = lazy(() => import('./pages/RedirectPage'))
const HackathonlarPage = lazy(() => import('./pages/landing/HackathonlarPage'))
const BootcamplarPage = lazy(() => import('./pages/landing/BootcamplarPage'))
const OnlineEtkinliklerPage = lazy(() => import('./pages/landing/OnlineEtkinliklerPage'))
const BuHaftakiEtkinliklerPage = lazy(() => import('./pages/landing/BuHaftakiEtkinliklerPage'))
const SonBasvurularPage = lazy(() => import('./pages/landing/SonBasvurularPage'))
const CalendarPage = lazy(() => import('./pages/CalendarPage'))
import { AuthProvider } from './contexts/AuthContext'
import { ThemeProvider } from './contexts/ThemeContext'
import { Toaster } from 'react-hot-toast'

// Protected Route Wrapper
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return <LoadingSpinner message="Yükleniyor..." />
  }

  if (!isAuthenticated) {
    return <Navigate to="/admin/login" replace />
  }

  return children
}

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <div className="App d-flex flex-column min-vh-100">
          <Header />
          <main className="flex-grow-1">
            <ErrorBoundary>
              <Suspense fallback={<LoadingSpinner />}>
                <Routes>
                  <Route path="/" element={<HomePage />} />
                  <Route path="/etkinlik/:id" element={<EventDetailPage />} />
                  <Route path="/bootcamp-rehberi" element={<BootcampRehberi />} />
                  <Route path="/etkinlik-talep" element={<EventRequestPage />} />
                  <Route path="/oneri-sikayet" element={<SuggestionPage />} />
                  <Route path="/egitim-kaynaklari" element={<FreeTrainingsPage />} />
                  <Route path="/status" element={<StatusPage />} />
                  <Route path="/takvim" element={<CalendarPage />} />
                  <Route path="/hackathonlar" element={<HackathonlarPage />} />
                  <Route path="/bootcamplar" element={<BootcamplarPage />} />
                  <Route path="/online-etkinlikler" element={<OnlineEtkinliklerPage />} />
                  <Route path="/bu-haftaki-etkinlikler" element={<BuHaftakiEtkinliklerPage />} />
                  <Route path="/son-basvurular" element={<SonBasvurularPage />} />

                  {/* Admin Routes */}
                  <Route path="/admin/login" element={<AdminLoginPage />} />
                  <Route path="/admin/dashboard" element={
                    <ProtectedRoute><AdminDashboard /></ProtectedRoute>
                  } />
                  <Route path="/admin/scrapers" element={
                    <ProtectedRoute><ScraperControlPage /></ProtectedRoute>
                  } />
                  <Route path="/admin/notifications" element={
                    <ProtectedRoute><NotificationPage /></ProtectedRoute>
                  } />
                  <Route path="/admin/analytics" element={
                    <ProtectedRoute><AnalyticsPage /></ProtectedRoute>
                  } />
                  <Route path="/admin/quality" element={
                    <ProtectedRoute><QualityPage /></ProtectedRoute>
                  } />

                  {/* Error Routes */}
                  <Route path="/error/server" element={<ServerErrorPage />} />
                  <Route path="/redirect" element={<RedirectPage />} />
                  <Route path="*" element={<NotFoundPage />} />
                </Routes>
              </Suspense>
            </ErrorBoundary>
          </main>
          <Footer />
          <Toaster
            position="top-right"
            toastOptions={{
              style: {
                background: 'var(--bg-card)',
                color: 'var(--text-primary)',
              },
            }}
          />
        </div>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App
