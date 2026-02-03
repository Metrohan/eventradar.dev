import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Header from './components/Header'
import HomePage from './pages/HomePage'
import EventRequestPage from './pages/EventRequestPage'
import SuggestionPage from './pages/SuggestionPage'
import AdminLoginPage from './pages/AdminLoginPage'
import AdminDashboard from './pages/AdminDashboard'
import ScraperControlPage from './pages/ScraperControlPage'
import NotificationPage from './pages/NotificationPage'
import AnalyticsPage from './pages/AnalyticsPage'
import FreeTrainingsPage from './pages/FreeTrainingsPage'
import Footer from './components/Footer'
import { AuthProvider } from './contexts/AuthContext'
import { ThemeProvider } from './contexts/ThemeContext'
import { QueryClient, QueryClientProvider } from 'react-query'
import { Toaster } from 'react-hot-toast'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AuthProvider>
          <div className="App d-flex flex-column min-vh-100">
            <Header />
            <main className="flex-grow-1">
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/etkinlik-talep" element={<EventRequestPage />} />
                <Route path="/oneri-sikayet" element={<SuggestionPage />} />
                <Route path="/admin/login" element={<AdminLoginPage />} />
                <Route path="/admin/dashboard" element={<AdminDashboard />} />
                <Route path="/admin/scrapers" element={<ScraperControlPage />} />
                <Route path="/admin/notifications" element={<NotificationPage />} />
                <Route path="/admin/analytics" element={<AnalyticsPage />} />
                <Route path="/egitim-kaynaklari" element={<FreeTrainingsPage />} />
              </Routes>
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
    </QueryClientProvider>
  )
}

export default App


