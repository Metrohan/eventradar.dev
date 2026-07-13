import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import toast from 'react-hot-toast'
import { adminAPI } from '../services/api'
import { getErrorMessage } from '../utils/errorMessage'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)

  const handleForceLogout = useCallback(() => {
    localStorage.removeItem('admin_token')
    setIsAuthenticated(false)
    toast.error('Oturumunuz sona erdi, lütfen tekrar giriş yapın.')
  }, [])

  useEffect(() => {
    // Check if user is already authenticated
    const token = localStorage.getItem('admin_token')
    if (token) {
      setIsAuthenticated(true)
    }
    setLoading(false)

    // Listen for forced logout from API interceptor
    window.addEventListener('auth:logout', handleForceLogout)
    return () => {
      window.removeEventListener('auth:logout', handleForceLogout)
    }
  }, [handleForceLogout])

  const login = async (credentials) => {
    try {
      const response = await adminAPI.login(credentials)
      const { access_token } = response.data

      localStorage.setItem('admin_token', access_token)
      setIsAuthenticated(true)

      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: getErrorMessage(error, 'Giriş başarısız')
      }
    }
  }

  const logout = () => {
    localStorage.removeItem('admin_token')
    setIsAuthenticated(false)
  }

  const value = {
    isAuthenticated,
    loading,
    login,
    logout,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
