import React, { useState, useEffect } from 'react'
import { Card, CardBody, Button, Badge, LoadingSpinner, CardSkeleton, showToast, AttendanceHeatmap } from '../components'
import { api, TodayStatus, AttendanceStatus, User, AvailableEvent } from '../services/api'
import { SmartURLGenerator } from '../utils/navigation'

const DashboardPage: React.FC = () => {
  const [todayStatus, setTodayStatus] = useState<TodayStatus | null>(null)
  const [attendanceHistory, setAttendanceHistory] = useState<AttendanceStatus[]>([])
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    loadInitialData()
    setupPolling()
    setupAutoCheckIn()

    // Cleanup polling on unmount
    return () => {
      if (pollingInterval) {
        window.clearInterval(pollingInterval)
      }
      if (autoCheckInInterval) {
        window.clearInterval(autoCheckInInterval)
      }
    }
  }, [])

  let pollingInterval: number | null = null
  let autoCheckInInterval: number | null = null

  const loadInitialData = async () => {
    try {
      setLoading(true)
      await Promise.all([
        loadTodayStatus(),
        loadAttendanceHistory(),
        loadUserProfile()
      ])
    } catch (error) {
      console.error('Failed to load initial data:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadTodayStatus = async () => {
    try {
      const response = await api.getTodayStatus()
      if (response.success) {
        setTodayStatus(response.data)
      }
    } catch (error) {
      console.error('Failed to load today status:', error)
      // Show offline mode or cached data
      const cachedStatus = localStorage.getItem('cached_today_status')
      if (cachedStatus) {
        setTodayStatus(JSON.parse(cachedStatus))
        showToast({
          type: 'info',
          message: '顯示離線資料，請檢查網路連線',
          autoClose: 3000
        })
      }
    }
  }

  const loadAttendanceHistory = async () => {
    try {
      // Load more history for heatmap visualization (12 weeks = 84 days, so fetch 100)
      const response = await api.getAttendanceHistory(100)
      if (response.success) {
        setAttendanceHistory(response.data)
        // Cache for offline use
        localStorage.setItem('cached_attendance_history', JSON.stringify(response.data))
      }
    } catch (error) {
      console.error('Failed to load attendance history:', error)
      // Try to load from cache
      const cachedHistory = localStorage.getItem('cached_attendance_history')
      if (cachedHistory) {
        setAttendanceHistory(JSON.parse(cachedHistory))
      }
    }
  }

  const loadUserProfile = async () => {
    try {
      // First try from localStorage
      const cachedUser = localStorage.getItem('userProfile')
      if (cachedUser) {
        setUser(JSON.parse(cachedUser))
      }

      // Then fetch fresh data
      const response = await api.getCurrentUser()
      if (response.success) {
        setUser(response.data)
        localStorage.setItem('userProfile', JSON.stringify(response.data))
      }
    } catch (error) {
      console.error('Failed to load user profile:', error)
    }
  }

  const setupPolling = () => {
    // Poll every 30 seconds for status updates
    pollingInterval = window.setInterval(async () => {
      if (!document.hidden) {
        await loadTodayStatus()
      }
    }, 30000)

    // Refresh when page becomes visible
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden) {
        loadTodayStatus()
      }
    })
  }

  const setupAutoCheckIn = () => {
    // Auto check-in on page load
    performAutoCheckIn()

    // Check every 5 minutes for auto check-in
    autoCheckInInterval = window.setInterval(async () => {
      if (!document.hidden) {
        await performAutoCheckIn()
      }
    }, 5 * 60 * 1000) // 5 minutes

    // Also check when page becomes visible
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden) {
        performAutoCheckIn()
      }
    })
  }

  const performAutoCheckIn = async () => {
    try {
      const response = await api.autoCheckInFromCalendar()

      if (response.success && response.data.checked_in) {
        const { event, attendance } = response.data

        // Show success notification
        const statusEmoji = attendance?.is_late ? '⏰' : '✅'
        const statusText = attendance?.is_late ? '遲到簽到' : '準時簽到'
        const lateInfo = attendance?.is_late
          ? ` (遲到 ${attendance.late_minutes} 分鐘)`
          : ''

        showToast({
          type: attendance?.is_late ? 'warning' : 'success',
          message: `${statusEmoji} ${statusText}：${event?.title}${lateInfo}`,
          autoClose: 5000
        })

        // Refresh data
        await Promise.all([
          loadTodayStatus(),
          loadAttendanceHistory()
        ])
      }
    } catch (error: any) {
      // Silently handle errors - don't show toast for every check
      console.log('[Auto Check-in] No event or error:', error.response?.data?.message || error.message)
    }
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    await loadInitialData()
    await performAutoCheckIn() // Also check for auto check-in
    setRefreshing(false)

    showToast({
      type: 'success',
      message: '資料已更新',
      autoClose: 2000
    })
  }

  const handleForceAutoCheckIn = async () => {
    try {
      showToast({
        type: 'info',
        message: '檢查中...',
        autoClose: 2000
      })

      const response = await api.autoCheckInFromCalendar()

      if (response.success) {
        if (response.data.checked_in) {
          const { event, attendance } = response.data
          const statusEmoji = attendance?.is_late ? '⏰' : '✅'
          const statusText = attendance?.is_late ? '遲到簽到' : '準時簽到'
          const lateInfo = attendance?.is_late
            ? ` (遲到 ${attendance.late_minutes} 分鐘)`
            : ''

          showToast({
            type: attendance?.is_late ? 'warning' : 'success',
            message: `${statusEmoji} ${statusText}：${event?.title}${lateInfo}`,
            autoClose: 5000
          })

          await Promise.all([
            loadTodayStatus(),
            loadAttendanceHistory()
          ])
        } else {
          showToast({
            type: 'info',
            message: response.data.message || '目前沒有需要簽到的事件',
            autoClose: 3000
          })
        }
      }
    } catch (error: any) {
      showToast({
        type: 'error',
        message: error.response?.data?.message || '自動簽到檢查失敗',
        autoClose: 5000
      })
    }
  }

  const handleManualCheckIn = async (eventId?: string) => {
    try {
      const response = await api.manualCheckIn(eventId)
      if (response.success) {
        showToast({
          type: 'success',
          message: '手動簽到成功！',
          autoClose: 3000
        })
        await loadTodayStatus()
        await loadAttendanceHistory()
      }
    } catch (error: any) {
      showToast({
        type: 'error',
        message: error.response?.data?.message || '簽到失敗，請重試',
        autoClose: 5000
      })
    }
  }

  const handleLogout = async () => {
    if (confirm('確定要登出嗎？')) {
      await api.logout()
    }
  }

  const getGreeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return '早安'
    if (hour < 18) return '午安'
    return '晚安'
  }

  const renderStatusCard = () => {
    if (!todayStatus) return <CardSkeleton />

    const statusConfig = {
      present: {
        icon: '✅',
        text: '已簽到',
        bgColor: 'bg-green-50 dark:bg-green-900/20',
        textColor: 'text-green-800 dark:text-green-200',
        borderColor: 'border-green-200 dark:border-green-700'
      },
      late: {
        icon: '⏰',
        text: '遲到簽到',
        bgColor: 'bg-yellow-50 dark:bg-yellow-900/20',
        textColor: 'text-yellow-800 dark:text-yellow-200',
        borderColor: 'border-yellow-200 dark:border-yellow-700'
      },
      waiting: {
        icon: '⏱️',
        text: '等待事件開始',
        bgColor: 'bg-blue-50 dark:bg-blue-900/20',
        textColor: 'text-blue-800 dark:text-blue-200',
        borderColor: 'border-blue-200 dark:border-blue-700'
      },
      absent: {
        icon: '❌',
        text: '未簽到',
        bgColor: 'bg-red-50 dark:bg-red-900/20',
        textColor: 'text-red-800 dark:text-red-200',
        borderColor: 'border-red-200 dark:border-red-700'
      }
    }

    const config = statusConfig[todayStatus.status] || statusConfig.waiting
    const availableEvents = todayStatus.availableEvents || []

    // If there are multiple available events, show them as a list
    if (availableEvents.length > 0) {
      return (
        <div className="space-y-3">
          {/* Status Summary */}
          <Card className={`${config.bgColor} ${config.borderColor} border-2`}>
            <CardBody>
              <div className="flex items-center space-x-3">
                <div className="text-3xl">{config.icon}</div>
                <div>
                  <div className={`text-lg font-semibold ${config.textColor}`}>
                    {todayStatus.isCheckedIn ? `${config.text}：${todayStatus.eventTitle}` : '可簽到會議'}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    {availableEvents.length} 個會議可簽到
                  </div>
                </div>
              </div>
            </CardBody>
          </Card>

          {/* Available Events List */}
          <div className="space-y-3">
            {availableEvents.map((event) => (
              <div
                key={event.id}
                className="bg-white rounded-xl shadow-apple transition-all duration-200 bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-700 border-2"
              >
                <div className="px-6 py-4">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="font-semibold text-lg text-blue-800 dark:text-blue-200">
                        {event.title}
                      </div>
                      <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        📍 {event.startTime} - {event.endTime}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleForceAutoCheckIn}
                        className="flex items-center gap-1"
                      >
                        <span>📅</span> Calendar
                      </Button>
                      <Button
                        variant="primary"
                        size="sm"
                        onClick={() => handleManualCheckIn(event.id)}
                      >
                        簽到
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )
    }

    // Original single event display
    return (
      <Card className={`${config.bgColor} ${config.borderColor} border-2`}>
        <CardBody className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="text-3xl">{config.icon}</div>
            <div>
              <div className={`text-lg font-semibold ${config.textColor}`}>
                {todayStatus.isCheckedIn ? `${config.text}：${todayStatus.eventTitle}` : config.text}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {todayStatus.isCheckedIn
                  ? todayStatus.checkInTime
                  : todayStatus.eventTitle
                  ? `📍 ${todayStatus.eventTitle} (${todayStatus.eventStartTime} - ${todayStatus.eventEndTime})`
                  : `下次事件：${todayStatus.nextEventTime || '無排程事件'}`
                }
              </div>
            </div>
          </div>

          <div className="flex gap-2">
            {!todayStatus.isCheckedIn && todayStatus.eventTitle && (
              <>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleForceAutoCheckIn}
                  className="flex items-center gap-1"
                >
                  <span>📅</span> Calendar 簽到
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleManualCheckIn()}
                >
                  手動簽到
                </Button>
              </>
            )}
          </div>
        </CardBody>
      </Card>
    )
  }

  const renderQuickActions = () => {
    const userRole = localStorage.getItem('userRole')

    return (
      <div className="grid grid-cols-2 gap-4">
        <Card className="hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => window.location.href = SmartURLGenerator.generateLeaveURL()}>
          <CardBody className="text-center">
            <div className="text-4xl mb-3">🏖️</div>
            <h3 className="font-semibold text-gray-900 dark:text-white">申請請假</h3>
            <p className="text-sm text-gray-500 mt-1">快速提交請假申請</p>
          </CardBody>
        </Card>

        <Card className="hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => window.location.href = '/makeup'}>
          <CardBody className="text-center">
            <div className="text-4xl mb-3">⏰</div>
            <h3 className="font-semibold text-gray-900 dark:text-white">補簽申請</h3>
            <p className="text-sm text-gray-500 mt-1">補簽遺漏的打卡記錄</p>
          </CardBody>
        </Card>

        <Card className="hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => window.location.href = '/create-event'}>
          <CardBody className="text-center">
            <div className="text-4xl mb-3">✨</div>
            <h3 className="font-semibold text-gray-900 dark:text-white">創建會議</h3>
            <p className="text-sm text-gray-500 mt-1">新增簽到事件</p>
          </CardBody>
        </Card>

        {(userRole === 'admin' || userRole === 'ADMIN') && (
          <Card className="hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => window.location.href = '/admin'}>
            <CardBody className="text-center">
              <div className="text-4xl mb-3">👥</div>
              <h3 className="font-semibold text-gray-900 dark:text-white">審核管理</h3>
              <p className="text-sm text-gray-500 mt-1">處理團隊申請</p>
            </CardBody>
          </Card>
        )}
      </div>
    )
  }

  // Convert attendance history to heatmap data
  const generateHeatmapData = () => {
    const dataMap = new Map<string, {
      date: string
      status: 'present' | 'late' | 'absent' | 'leave'
      count: number
    }>()

    attendanceHistory.forEach(record => {
      const date = new Date(record.createdAt).toISOString().split('T')[0]
      const existing = dataMap.get(date)

      if (existing) {
        existing.count += 1
        // Keep the worst status (absent > late > present)
        if (record.status === 'absent' || existing.status !== 'absent' && record.status === 'late') {
          existing.status = record.status as any
        }
      } else {
        dataMap.set(date, {
          date,
          status: record.status as any,
          count: 1
        })
      }
    })

    return Array.from(dataMap.values())
  }

  const renderRecentHistory = () => {
    if (attendanceHistory.length === 0) {
      return (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          <div className="text-4xl mb-4">📊</div>
          <p>暫無簽到記錄</p>
        </div>
      )
    }

    return (
      <div className="space-y-3">
        {attendanceHistory.slice(0, 5).map((record) => (
          <div key={record.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="text-lg">
                {record.status === 'present' && '✅'}
                {record.status === 'late' && '⏰'}
                {record.status === 'absent' && '❌'}
              </div>
              <div>
                <div className="font-medium text-gray-900 dark:text-white">
                  {record.eventTitle}
                </div>
                <div className="text-sm text-gray-500">
                  {new Date(record.createdAt).toLocaleDateString('zh-TW')}
                </div>
              </div>
            </div>
            <div className="text-right">
              <Badge
                variant={record.status === 'present' ? 'success' : record.status === 'late' ? 'warning' : 'error'}
                size="sm"
              >
                {record.status === 'present' && '出席'}
                {record.status === 'late' && '遲到'}
                {record.status === 'absent' && '缺席'}
              </Badge>
              {record.checkedInAt && (
                <div className="text-xs text-gray-400 mt-1">
                  {new Date(record.checkedInAt).toLocaleTimeString('zh-TW', {
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-4">
        <div className="max-w-4xl mx-auto space-y-6">
          <CardSkeleton />
          <div className="grid grid-cols-2 gap-4">
            <CardSkeleton />
            <CardSkeleton />
          </div>
          <CardSkeleton />
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
                {getGreeting()}，{user?.name || 'User'} 👋
              </h1>
            </div>

            <div className="flex items-center space-x-3">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleRefresh}
                disabled={refreshing}
              >
                {refreshing ? (
                  <LoadingSpinner size="sm" />
                ) : (
                  <span className="text-lg">🔄</span>
                )}
              </Button>

              <Button
                variant="ghost"
                size="sm"
                onClick={() => window.location.href = '/profile'}
              >
                {user?.avatar ? (
                  <img
                    src={user.avatar}
                    alt={user.name}
                    className="w-8 h-8 rounded-full"
                  />
                ) : (
                  <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white text-sm">
                    {user?.name?.charAt(0) || 'U'}
                  </div>
                )}
              </Button>

              <Button
                variant="ghost"
                size="sm"
                onClick={handleLogout}
                className="text-red-600 hover:text-red-700"
              >
                🚪
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto p-4 space-y-6">
        {/* Today's Status */}
        <section>
          {renderStatusCard()}
        </section>

        {/* Attendance Heatmap - GitHub Style */}
        <section>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <span>📊</span>
            簽到活動圖
          </h2>
          <Card>
            <CardBody>
              {attendanceHistory.length > 0 ? (
                <AttendanceHeatmap data={generateHeatmapData()} weeks={12} />
              ) : (
                <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                  <div className="text-6xl mb-4">📅</div>
                  <p className="text-lg font-medium mb-2">尚無簽到記錄</p>
                  <p className="text-sm">開始簽到後，這裡會顯示你的簽到活動圖</p>
                </div>
              )}
            </CardBody>
          </Card>
        </section>

        {/* Quick Actions */}
        <section>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            快速操作
          </h2>
          {renderQuickActions()}
        </section>

        {/* Recent History */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              最近記錄
            </h2>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => window.location.href = '/history'}
            >
              查看全部
            </Button>
          </div>

          <Card>
            <CardBody>
              {renderRecentHistory()}
            </CardBody>
          </Card>
        </section>
      </main>
    </div>
  )
}

export default DashboardPage