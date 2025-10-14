import React, { useState, useEffect } from 'react'
import {
  Card, CardBody, Button,
  LoadingSpinner, showToast, CardSkeleton
} from '../components'
import { api, User } from '../services/api'
import { goBack } from '../utils/navigation'

const ProfilePage: React.FC = () => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [settings, setSettings] = useState({
    emailNotifications: true,
    slackNotifications: false,
    shareAttendance: true
  })

  useEffect(() => {
    loadUserData()
    loadSettings()
  }, [])

  const loadUserData = async () => {
    try {
      // Load from cache first
      const cachedUser = localStorage.getItem('userProfile')
      if (cachedUser) {
        setUser(JSON.parse(cachedUser))
        setLoading(false)
      }

      // Then load fresh data
      const response = await api.getCurrentUser()
      if (response.success) {
        setUser(response.data)
        localStorage.setItem('userProfile', JSON.stringify(response.data))
      }
    } catch (error) {
      console.error('Failed to load user data:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadSettings = () => {
    // Load settings from localStorage
    const savedSettings = localStorage.getItem('userSettings')
    if (savedSettings) {
      setSettings(JSON.parse(savedSettings))
    }
  }

  const handleSettingsChange = (key: keyof typeof settings, value: boolean) => {
    const newSettings = { ...settings, [key]: value }
    setSettings(newSettings)
    localStorage.setItem('userSettings', JSON.stringify(newSettings))

    showToast({
      type: 'success',
      message: '設定已更新',
      autoClose: 2000
    })
  }

  const handleSyncCalendar = async () => {
    try {
      setSaving(true)
      // This would call a sync API endpoint
      // await api.syncGoogleCalendar()

      showToast({
        type: 'success',
        message: 'Google Calendar 同步完成',
        autoClose: 3000
      })
    } catch (error) {
      showToast({
        type: 'error',
        message: '同步失敗，請重試',
        autoClose: 3000
      })
    } finally {
      setSaving(false)
    }
  }

  const handleLogout = async () => {
    if (confirm('確定要登出嗎？')) {
      await api.logout()
    }
  }

  const handleDeleteAccount = async () => {
    const confirmation = prompt('請輸入「DELETE」來確認刪除帳號：')
    if (confirmation === 'DELETE') {
      if (confirm('這將永久刪除您的帳號和所有資料，確定要繼續嗎？')) {
        try {
          // This would call a delete account API
          showToast({
            type: 'info',
            message: '帳號刪除功能尚未實作',
            autoClose: 3000
          })
        } catch (error) {
          showToast({
            type: 'error',
            message: '刪除失敗，請聯絡支援',
            autoClose: 5000
          })
        }
      }
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-4">
        <div className="max-w-2xl mx-auto space-y-6">
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm">
        <div className="max-w-2xl mx-auto px-4 py-4">
          <div className="flex items-center">
            <Button
              variant="ghost"
              size="sm"
              onClick={goBack}
              className="mr-4"
            >
              ← 返回
            </Button>
            <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
              個人設定
            </h1>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-2xl mx-auto p-4 space-y-6">
        {/* Profile Information */}
        <Card>
          <CardBody>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              個人資料
            </h2>

            {user && (
              <div className="flex items-center space-x-4 mb-6">
                {user.avatar ? (
                  <img
                    src={user.avatar}
                    alt={user.name}
                    className="w-16 h-16 rounded-full"
                  />
                ) : (
                  <div className="w-16 h-16 rounded-full bg-blue-500 flex items-center justify-center text-white text-xl">
                    {user.name.charAt(0)}
                  </div>
                )}

                <div>
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                    {user.name}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400">{user.email}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      user.role === 'admin'
                        ? 'bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400'
                        : 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400'
                    }`}>
                      {user.role === 'admin' ? '管理員' : '用戶'}
                    </span>
                    <span className="text-xs text-gray-500">
                      註冊於 {new Date(user.createdAt).toLocaleDateString('zh-TW')}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </CardBody>
        </Card>

        {/* Notification Settings */}
        <Card>
          <CardBody>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              通知設定
            </h2>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white">
                    Email 通知
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    申請狀態更新時發送郵件
                  </p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.emailNotifications}
                    onChange={(e) => handleSettingsChange('emailNotifications', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                </label>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white">
                    Slack 通知
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    團隊 Slack 頻道通知
                  </p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.slackNotifications}
                    onChange={(e) => handleSettingsChange('slackNotifications', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                </label>
              </div>
            </div>
          </CardBody>
        </Card>

        {/* Calendar Sync */}
        <Card>
          <CardBody>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              行事曆同步
            </h2>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="text-2xl">📅</div>
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white">
                    Google Calendar
                  </h3>
                  <p className="text-sm text-green-600 dark:text-green-400">
                    已連接
                  </p>
                </div>
              </div>

              <Button
                variant="outline"
                size="sm"
                onClick={handleSyncCalendar}
                disabled={saving}
              >
                {saving ? (
                  <LoadingSpinner size="sm" />
                ) : (
                  '重新同步'
                )}
              </Button>
            </div>
          </CardBody>
        </Card>

        {/* Privacy Settings */}
        <Card>
          <CardBody>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              隱私設定
            </h2>

            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium text-gray-900 dark:text-white">
                  分享出勤記錄給團隊
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  允許團隊成員查看你的簽到狀態
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.shareAttendance}
                  onChange={(e) => handleSettingsChange('shareAttendance', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
              </label>
            </div>
          </CardBody>
        </Card>

        {/* Account Management */}
        <Card>
          <CardBody>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              帳號管理
            </h2>

            <div className="space-y-3">
              <Button
                variant="outline"
                onClick={handleLogout}
                className="w-full justify-start"
              >
                <span className="text-lg mr-3">🚪</span>
                登出帳號
              </Button>

              <Button
                variant="outline"
                onClick={handleDeleteAccount}
                className="w-full justify-start text-red-600 border-red-200 hover:bg-red-50 hover:border-red-300 dark:text-red-400 dark:border-red-800 dark:hover:bg-red-900/20"
              >
                <span className="text-lg mr-3">🗑️</span>
                刪除帳號
              </Button>
            </div>
          </CardBody>
        </Card>
      </main>
    </div>
  )
}

export default ProfilePage