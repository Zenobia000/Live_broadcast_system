import React, { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { LoadingSpinner, showToast } from '../components'

const AuthCallbackPage: React.FC = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  useEffect(() => {
    handleCallback()
  }, [])

  const handleCallback = async () => {
    // Get token from URL query parameters
    const token = searchParams.get('token')
    const error = searchParams.get('error')

    if (error) {
      showToast({
        type: 'error',
        message: `登入失敗: ${error}`,
        autoClose: 5000
      })

      // Redirect to login page after delay
      setTimeout(() => {
        navigate('/', { replace: true })
      }, 2000)
      return
    }

    if (!token) {
      showToast({
        type: 'error',
        message: '未收到授權令牌',
        autoClose: 5000
      })

      setTimeout(() => {
        navigate('/', { replace: true })
      }, 2000)
      return
    }

    try {
      // Store the token
      localStorage.setItem('authToken', token)

      // Fetch user profile with the token
      const response = await fetch('http://localhost:8000/api/v1/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const userData = await response.json()

        // Store user data
        localStorage.setItem('userRole', userData.role)
        localStorage.setItem('userProfile', JSON.stringify(userData))

        showToast({
          type: 'success',
          message: `歡迎，${userData.name}！`,
          autoClose: 2000
        })

        // Redirect to dashboard
        setTimeout(() => {
          navigate('/dashboard', { replace: true })
        }, 1000)
      } else {
        throw new Error('Failed to fetch user profile')
      }
    } catch (error) {
      console.error('Auth callback error:', error)
      showToast({
        type: 'error',
        message: '處理登入資訊時發生錯誤',
        autoClose: 5000
      })

      // Clear invalid token
      localStorage.removeItem('authToken')

      setTimeout(() => {
        navigate('/', { replace: true })
      }, 2000)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
      <div className="text-center">
        <div className="mb-6">
          <LoadingSpinner size="lg" />
        </div>

        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          登入處理中
        </h2>

        <p className="text-gray-600 dark:text-gray-400">
          正在完成登入流程，請稍候...
        </p>
      </div>
    </div>
  )
}

export default AuthCallbackPage
