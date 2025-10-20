import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button, Form, Input, showToast } from '../components'
import { api } from '../services/api'

const RegisterPage: React.FC = () => {
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  })

  const [passwordStrength, setPasswordStrength] = useState({
    hasLength: false,
    hasUppercase: false,
    hasLowercase: false,
    hasNumber: false,
    hasSpecial: false,
  })

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))

    // Update password strength indicators
    if (name === 'password') {
      setPasswordStrength({
        hasLength: value.length >= 8,
        hasUppercase: /[A-Z]/.test(value),
        hasLowercase: /[a-z]/.test(value),
        hasNumber: /[0-9]/.test(value),
        hasSpecial: /[!@#$%^&*()_+\-=[\]{}|;:,.<>?]/.test(value),
      })
    }
  }

  const validateForm = (): boolean => {
    if (!formData.name.trim()) {
      showToast({
        type: 'warning',
        message: '請輸入您的名字',
        autoClose: 3000,
      })
      return false
    }

    if (!formData.email.trim()) {
      showToast({
        type: 'warning',
        message: '請輸入您的 Email',
        autoClose: 3000,
      })
      return false
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      showToast({
        type: 'warning',
        message: 'Email 格式不正確',
        autoClose: 3000,
      })
      return false
    }

    if (formData.password.length < 8) {
      showToast({
        type: 'warning',
        message: '密碼至少需要 8 個字元',
        autoClose: 3000,
      })
      return false
    }

    if (!Object.values(passwordStrength).every(Boolean)) {
      showToast({
        type: 'warning',
        message: '密碼強度不足，請滿足所有要求',
        autoClose: 3000,
      })
      return false
    }

    if (formData.password !== formData.confirmPassword) {
      showToast({
        type: 'warning',
        message: '密碼與確認密碼不一致',
        autoClose: 3000,
      })
      return false
    }

    return true
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    setIsLoading(true)

    try {
      const response = await api.register({
        name: formData.name,
        email: formData.email,
        password: formData.password,
      })

      // Handle successful registration
      if (response.success && response.data) {
        const { access_token, user } = response.data

        // Store auth data
        localStorage.setItem('authToken', access_token)
        localStorage.setItem('userRole', user.role)
        localStorage.setItem('userProfile', JSON.stringify(user))

        showToast({
          type: 'success',
          message: `註冊成功！歡迎 ${user.name}`,
          autoClose: 2000,
        })

        // Redirect to dashboard
        setTimeout(() => {
          navigate('/dashboard')
        }, 2000)
      }
    } catch (error: any) {
      console.error('Registration failed:', error)
      const errorMessage = error.response?.data?.detail || '註冊失敗，請重試'
      showToast({
        type: 'error',
        message: errorMessage,
        autoClose: 5000,
      })
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Brand Section */}
        <div className="text-center mb-8">
          <div className="mx-auto w-20 h-20 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl flex items-center justify-center mb-6">
            <span className="text-2xl text-white">✓</span>
          </div>

          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            建立新帳號
          </h1>

          <p className="text-gray-600 dark:text-gray-400">
            加入智能簽到系統，讓簽到更簡單
          </p>
        </div>

        {/* Register Card */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
          <form onSubmit={handleSubmit}>
            {/* Name Field */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                名字 *
              </label>
              <Input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                placeholder="請輸入您的名字"
                required
                disabled={isLoading}
                className="w-full"
              />
            </div>

            {/* Email Field */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Email *
              </label>
              <Input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="your@email.com"
                required
                disabled={isLoading}
                className="w-full"
              />
            </div>

            {/* Password Field */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                密碼 *
              </label>
              <Input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                placeholder="至少 8 個字元"
                required
                disabled={isLoading}
                className="w-full"
              />

              {/* Password Strength Indicators */}
              {formData.password && (
                <div className="mt-3 space-y-2 text-xs">
                  <div
                    className={`flex items-center gap-2 ${
                      passwordStrength.hasLength ? 'text-green-600' : 'text-gray-400'
                    }`}
                  >
                    <span>{passwordStrength.hasLength ? '✓' : '○'}</span>
                    <span>至少 8 個字元</span>
                  </div>
                  <div
                    className={`flex items-center gap-2 ${
                      passwordStrength.hasUppercase ? 'text-green-600' : 'text-gray-400'
                    }`}
                  >
                    <span>{passwordStrength.hasUppercase ? '✓' : '○'}</span>
                    <span>至少 1 個大寫字母</span>
                  </div>
                  <div
                    className={`flex items-center gap-2 ${
                      passwordStrength.hasLowercase ? 'text-green-600' : 'text-gray-400'
                    }`}
                  >
                    <span>{passwordStrength.hasLowercase ? '✓' : '○'}</span>
                    <span>至少 1 個小寫字母</span>
                  </div>
                  <div
                    className={`flex items-center gap-2 ${
                      passwordStrength.hasNumber ? 'text-green-600' : 'text-gray-400'
                    }`}
                  >
                    <span>{passwordStrength.hasNumber ? '✓' : '○'}</span>
                    <span>至少 1 個數字</span>
                  </div>
                  <div
                    className={`flex items-center gap-2 ${
                      passwordStrength.hasSpecial ? 'text-green-600' : 'text-gray-400'
                    }`}
                  >
                    <span>{passwordStrength.hasSpecial ? '✓' : '○'}</span>
                    <span>至少 1 個特殊字元 (!@#$% 等)</span>
                  </div>
                </div>
              )}
            </div>

            {/* Confirm Password Field */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                確認密碼 *
              </label>
              <Input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                placeholder="再次輸入密碼"
                required
                disabled={isLoading}
                className="w-full"
              />
              {formData.confirmPassword && formData.password !== formData.confirmPassword && (
                <p className="mt-2 text-xs text-red-600">密碼不一致</p>
              )}
            </div>

            {/* Submit Button */}
            <Button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 text-lg font-medium bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:from-blue-700 hover:to-indigo-700"
            >
              {isLoading ? '註冊中...' : '建立帳號'}
            </Button>

            {/* Divider */}
            <div className="my-6 flex items-center gap-4">
              <div className="flex-1 border-t border-gray-300 dark:border-gray-600"></div>
              <span className="text-sm text-gray-500">或</span>
              <div className="flex-1 border-t border-gray-300 dark:border-gray-600"></div>
            </div>

            {/* Login Link */}
            <div className="text-center">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                已經有帳號了？{' '}
                <button
                  type="button"
                  onClick={() => navigate('/')}
                  className="text-blue-600 hover:text-blue-700 font-medium"
                >
                  立即登入
                </button>
              </p>
            </div>
          </form>
        </div>

        {/* Footer */}
        <div className="text-center mt-8">
          <p className="text-xs text-gray-400">
            Powered by Smart Attendance System v1.0
          </p>
        </div>
      </div>
    </div>
  )
}

export default RegisterPage
