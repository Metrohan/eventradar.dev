import React from 'react'
import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import toast from 'react-hot-toast'

const AdminLoginPage = () => {
  const navigate = useNavigate()
  const { login } = useAuth()
  const { register, handleSubmit, formState: { errors } } = useForm()

  const onSubmit = async (data) => {
    const result = await login(data)
    
    if (result.success) {
      toast.success('Giriş başarılı!')
      navigate('/admin/dashboard')
    } else {
      toast.error(result.error)
    }
  }

  return (
    <div className="container py-5">
      <div className="row justify-content-center">
        <div className="col-md-6 col-lg-4">
          <div className="card shadow">
            <div className="card-header bg-primary text-white text-center">
              <h3 className="card-title mb-0">
                <i className="fas fa-lock me-2"></i>
                Admin Girişi
              </h3>
            </div>
            <div className="card-body">
              <form onSubmit={handleSubmit(onSubmit)}>
                {/* Username */}
                <div className="mb-3">
                  <label htmlFor="username" className="form-label">
                    Kullanıcı Adı
                  </label>
                  <input
                    type="text"
                    className={`form-control ${errors.username ? 'is-invalid' : ''}`}
                    id="username"
                    placeholder="Kullanıcı adınızı giriniz"
                    {...register('username', {
                      required: 'Kullanıcı adı gereklidir'
                    })}
                  />
                  {errors.username && (
                    <div className="invalid-feedback">
                      {errors.username.message}
                    </div>
                  )}
                </div>

                {/* Password */}
                <div className="mb-4">
                  <label htmlFor="password" className="form-label">
                    Şifre
                  </label>
                  <input
                    type="password"
                    className={`form-control ${errors.password ? 'is-invalid' : ''}`}
                    id="password"
                    placeholder="Şifrenizi giriniz"
                    {...register('password', {
                      required: 'Şifre gereklidir'
                    })}
                  />
                  {errors.password && (
                    <div className="invalid-feedback">
                      {errors.password.message}
                    </div>
                  )}
                </div>

                {/* Submit Button */}
                <div className="d-grid">
                  <button type="submit" className="btn btn-primary btn-lg">
                    <i className="fas fa-sign-in-alt me-2"></i>
                    Giriş Yap
                  </button>
                </div>
              </form>

              <div className="mt-4 text-center">
                <a href="/" className="btn btn-outline-secondary">
                  <i className="fas fa-arrow-left me-2"></i>
                  Ana Sayfaya Dön
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AdminLoginPage


