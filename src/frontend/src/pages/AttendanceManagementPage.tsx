import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardHeader, CardBody, Button, Badge, showToast, LoadingSpinner } from '../components'
import { api, EventAttendanceOverview } from '../services/api'

export default function AttendanceManagementPage() {
  const navigate = useNavigate()
  const [events, setEvents] = useState<EventAttendanceOverview[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedEvent, setSelectedEvent] = useState<number | null>(null)
  const [refreshing, setRefreshing] = useState(false)

  // Fetch attendance overview
  const fetchAttendanceOverview = async () => {
    try {
      setLoading(true)
      const response = await api.getAttendanceOverview({ limit: 50 })

      if (response.success && response.data) {
        // Backend returns { success: true, data: [...], total: N }
        setEvents(Array.isArray(response.data) ? response.data : [])
      } else {
        setEvents([]) // Ensure events is always an array
        showToast({
          type: 'error',
          message: response.error || '無法獲取出席統計'
        })
      }
    } catch (error: any) {
      setEvents([]) // Ensure events is always an array on error
      console.error('Attendance overview error:', error)
      showToast({
        type: 'error',
        message: error.response?.data?.detail || error.response?.data?.message || '載入出席統計失敗'
      })
    } finally {
      setLoading(false)
    }
  }

  // Refresh data
  const handleRefresh = async () => {
    setRefreshing(true)
    await fetchAttendanceOverview()
    setRefreshing(false)
    showToast({
      type: 'success',
      message: '資料已更新'
    })
  }

  // Initial load
  useEffect(() => {
    fetchAttendanceOverview()
  }, [])

  // Format date for display
  const formatDateTime = (dateStr: string) => {
    const date = new Date(dateStr)
    const month = (date.getMonth() + 1).toString().padStart(2, '0')
    const day = date.getDate().toString().padStart(2, '0')
    const hours = date.getHours().toString().padStart(2, '0')
    const minutes = date.getMinutes().toString().padStart(2, '0')
    return `${month}/${day} ${hours}:${minutes}`
  }

  // Get status badge
  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { variant: 'success' | 'warning' | 'error' | 'default'; label: string }> = {
      'present': { variant: 'success', label: '出席' },
      'late': { variant: 'warning', label: '遲到' },
      'absent': { variant: 'error', label: '缺席' },
      'leave': { variant: 'default', label: '請假' },
      'makeup': { variant: 'default', label: '補簽' },
    }

    const config = statusMap[status.toLowerCase()] || { variant: 'default' as const, label: status }
    return <Badge variant={config.variant} size="sm">{config.label}</Badge>
  }

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate('/dashboard')}
              >
                🏠 首頁
              </Button>
              <span className="text-gray-300 dark:text-gray-600">|</span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate('/admin')}
              >
                ← 返回管理
              </Button>
              <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">
                會議出席統計
              </h1>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              disabled={refreshing}
            >
              {refreshing ? '更新中...' : '🔄 重新整理'}
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 py-6">
        {/* Stats Summary */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <Card className="bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
            <CardBody className="text-center">
              <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                {events.length}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                會議總數
              </div>
            </CardBody>
          </Card>

          <Card className="bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800">
            <CardBody className="text-center">
              <div className="text-3xl font-bold text-green-600 dark:text-green-400">
                {events.reduce((sum, e) => sum + e.statistics.attended_count, 0)}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                累計實到人次
              </div>
            </CardBody>
          </Card>

          <Card className="bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800">
            <CardBody className="text-center">
              <div className="text-3xl font-bold text-orange-600 dark:text-orange-400">
                {events.reduce((sum, e) => sum + e.statistics.absent_count, 0)}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                累計未到人次
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Empty State */}
        {events.length === 0 ? (
          <Card>
            <CardBody className="py-12 text-center">
              <div className="text-6xl mb-4">📊</div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                目前沒有會議資料
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                系統中尚未有任何會議記錄
              </p>
            </CardBody>
          </Card>
        ) : (
          /* Events List */
          <div className="space-y-4">
            {events.map((event) => (
              <Card
                key={event.id}
                className={`transition-all ${
                  selectedEvent === event.id
                    ? 'ring-2 ring-blue-500 shadow-lg'
                    : 'hover:shadow-md'
                }`}
              >
                <CardHeader
                  className="cursor-pointer"
                  onClick={() => setSelectedEvent(selectedEvent === event.id ? null : event.id)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                          {event.title}
                        </h3>
                        <Badge variant="default" size="sm">
                          ID: {event.id}
                        </Badge>
                      </div>
                      <div className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                        <div className="flex items-center space-x-2">
                          <span>📅</span>
                          <span>{formatDateTime(event.start_time)} - {formatDateTime(event.end_time)}</span>
                        </div>
                        {event.description && (
                          <div className="flex items-start space-x-2">
                            <span>📝</span>
                            <span>{event.description}</span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Statistics */}
                    <div className="flex items-center space-x-4 ml-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                          {event.statistics.expected_count}
                        </div>
                        <div className="text-xs text-gray-600 dark:text-gray-400">應到</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                          {event.statistics.attended_count}
                        </div>
                        <div className="text-xs text-gray-600 dark:text-gray-400">實到</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-red-600 dark:text-red-400">
                          {event.statistics.absent_count}
                        </div>
                        <div className="text-xs text-gray-600 dark:text-gray-400">未到</div>
                      </div>
                      <button className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-transform">
                        {selectedEvent === event.id ? '▼' : '▶'}
                      </button>
                    </div>
                  </div>
                </CardHeader>

                {/* Detailed Attendance */}
                {selectedEvent === event.id && (
                  <CardBody className="border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {/* Attended Users */}
                      <div>
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                          <span className="text-green-600 mr-2">✓</span>
                          已簽到 ({event.statistics.attended_count})
                        </h4>
                        <div className="space-y-2">
                          {event.attended_users.length === 0 ? (
                            <p className="text-sm text-gray-500 dark:text-gray-400 italic">
                              無人簽到
                            </p>
                          ) : (
                            event.attended_users.map((user) => (
                              <div
                                key={user.id}
                                className="flex items-center justify-between p-3 bg-white dark:bg-gray-800 rounded-lg shadow-sm"
                              >
                                <div className="flex items-center space-x-3">
                                  <div className="w-8 h-8 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center text-green-600 dark:text-green-400 font-semibold">
                                    {user.name.charAt(0)}
                                  </div>
                                  <div>
                                    <div className="font-medium text-gray-900 dark:text-white">
                                      {user.name}
                                    </div>
                                    <div className="text-xs text-gray-500 dark:text-gray-400">
                                      {user.email}
                                    </div>
                                  </div>
                                </div>
                                <div className="text-right">
                                  {getStatusBadge(user.status)}
                                  {user.check_in_time && (
                                    <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                      {new Date(user.check_in_time).toLocaleTimeString('zh-TW', {
                                        hour: '2-digit',
                                        minute: '2-digit'
                                      })}
                                    </div>
                                  )}
                                </div>
                              </div>
                            ))
                          )}
                        </div>
                      </div>

                      {/* Absent Users */}
                      <div>
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                          <span className="text-red-600 mr-2">✗</span>
                          未簽到 ({event.statistics.absent_count})
                        </h4>
                        <div className="space-y-2">
                          {event.absent_users.length === 0 ? (
                            <p className="text-sm text-gray-500 dark:text-gray-400 italic">
                              全員到齊 🎉
                            </p>
                          ) : (
                            event.absent_users.map((user) => (
                              <div
                                key={user.id}
                                className="flex items-center justify-between p-3 bg-white dark:bg-gray-800 rounded-lg shadow-sm"
                              >
                                <div className="flex items-center space-x-3">
                                  <div className="w-8 h-8 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center text-gray-600 dark:text-gray-400 font-semibold">
                                    {user.name.charAt(0)}
                                  </div>
                                  <div>
                                    <div className="font-medium text-gray-900 dark:text-white">
                                      {user.name}
                                    </div>
                                    <div className="text-xs text-gray-500 dark:text-gray-400">
                                      {user.email}
                                    </div>
                                  </div>
                                </div>
                                <div>
                                  {getStatusBadge(user.status)}
                                </div>
                              </div>
                            ))
                          )}
                        </div>
                      </div>
                    </div>
                  </CardBody>
                )}
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
