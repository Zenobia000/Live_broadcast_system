import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button, Input, LoadingSpinner, showToast } from '../components'
import { api } from '../services/api'

const LoginPage: React.FC = () => {
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(false)
  const [loginMethod, setLoginMethod] = useState<'google' | 'password'>('password')
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  })

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handlePasswordLogin = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.email || !formData.password) {
      showToast({
        type: 'warning',
        message: '請輸入 Email 和密碼',
        autoClose: 3000,
      })
      return
    }

    setIsLoading(true)

    try {
      const response = await api.login({
        email: formData.email,
        password: formData.password,
      })

      // Handle successful login
      if (response.success && response.data) {
        const { access_token, user } = response.data

        // Store auth data
        localStorage.setItem('authToken', access_token)
        localStorage.setItem('userRole', user.role)
        localStorage.setItem('userProfile', JSON.stringify(user))

        showToast({
          type: 'success',
          message: `歡迎回來，${user.name}！`,
          autoClose: 2000,
        })

        // Redirect to dashboard
        setTimeout(() => {
          navigate('/dashboard')
        }, 2000)
      }
    } catch (error: any) {
      console.error('Login failed:', error)
      const errorMessage = error.response?.data?.detail || '登入失敗，請檢查 Email 和密碼'
      showToast({
        type: 'error',
        message: errorMessage,
        autoClose: 5000,
      })
      setIsLoading(false)
    }
  }

  const handleGoogleLogin = async () => {
    setIsLoading(true)

    try {
      // Get authorization URL from backend
      const { authorization_url } = await api.getGoogleAuthUrl()

      // Redirect to Google's authorization page
      window.location.href = authorization_url
    } catch (error: any) {
      console.error('Failed to get Google auth URL:', error)
      showToast({
        type: 'error',
        message: 'Google 登入初始化失敗，請重試',
        autoClose: 5000
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
            智能簽到系統
          </h1>

          <p className="text-gray-600 dark:text-gray-400 mb-2">
            讓簽到變成一種愉悅的儀式
          </p>

          {/* Visual cue - Simple illustration */}
          <div className="flex justify-center items-center gap-2 text-2xl opacity-75 mb-6">
            <span>🤖</span>
            <span className="text-sm text-gray-500">→</span>
            <span>📅</span>
            <span className="text-sm text-gray-500">→</span>
            <span>⚡</span>
          </div>
        </div>

        {/* Login Card */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
          <div className="text-center mb-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              歡迎使用智能簽到系統
            </h2>
          </div>

          {/* Login Method Tabs */}
          <div className="flex gap-2 mb-6 bg-gray-100 dark:bg-gray-700 p-1 rounded-lg">
            <button
              type="button"
              onClick={() => setLoginMethod('password')}
              className={`flex-1 py-2 rounded-md text-sm font-medium transition-colors ${
                loginMethod === 'password'
                  ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              帳號密碼
            </button>
            <button
              type="button"
              onClick={() => setLoginMethod('google')}
              className={`flex-1 py-2 rounded-md text-sm font-medium transition-colors ${
                loginMethod === 'google'
                  ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              Google 登入
            </button>
          </div>

          {/* Password Login Form */}
          {loginMethod === 'password' && (
            <form onSubmit={handlePasswordLogin}>
              <div className="space-y-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Email
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
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    密碼
                  </label>
                  <Input
                    type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    placeholder="輸入您的密碼"
                    required
                    disabled={isLoading}
                    className="w-full"
                  />
                </div>
              </div>

              <Button
                type="submit"
                disabled={isLoading}
                className="w-full py-3 text-lg font-medium bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:from-blue-700 hover:to-indigo-700"
              >
                {isLoading ? '登入中...' : '登入'}
              </Button>

              {/* Register Link */}
              <div className="text-center mt-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  還沒有帳號？{' '}
                  <button
                    type="button"
                    onClick={() => navigate('/register')}
                    className="text-blue-600 hover:text-blue-700 font-medium"
                  >
                    立即註冊
                  </button>
                </p>
              </div>
            </form>
          )}

          {/* Google OAuth Button */}
          {loginMethod === 'google' && (
            <>
              <Button
                onClick={handleGoogleLogin}
                disabled={isLoading}
                className="w-full py-4 text-lg font-medium bg-white border-2 border-gray-300 text-gray-700 hover:bg-gray-50 hover:border-gray-400 dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:hover:bg-gray-600"
              >
                {isLoading ? (
                  <div className="flex items-center justify-center gap-3">
                    <LoadingSpinner size="sm" />
                    <span>正在跳轉至 Google 登入...</span>
                  </div>
                ) : (
                  <div className="flex items-center justify-center gap-3">
                    {/* Google Icon */}
                    <svg width="20" height="20" viewBox="0 0 24 24">
                      <path
                        fill="#4285F4"
                        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                      />
                      <path
                        fill="#34A853"
                        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                      />
                      <path
                        fill="#FBBC05"
                        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                      />
                      <path
                        fill="#EA4335"
                        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                      />
                    </svg>
                    <span>使用 Google 帳號登入</span>
                  </div>
                )}
              </Button>

              {/* Privacy Note */}
              <p className="text-xs text-gray-500 dark:text-gray-400 text-center mt-4 leading-relaxed">
                我們重視您的隱私，僅讀取基本資料用於身份驗證
              </p>
            </>
          )}
        </div>

        {/* Feature Highlights */}
        <div className="mt-8 text-center">
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div className="text-center">
              <div className="text-2xl mb-2">🤖</div>
              <div className="text-gray-600 dark:text-gray-400">自動簽到</div>
            </div>
            <div className="text-center">
              <div className="text-2xl mb-2">📅</div>
              <div className="text-gray-600 dark:text-gray-400">智能提醒</div>
            </div>
            <div className="text-center">
              <div className="text-2xl mb-2">⚡</div>
              <div className="text-gray-600 dark:text-gray-400">快速請假</div>
            </div>
          </div>
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

export default LoginPage