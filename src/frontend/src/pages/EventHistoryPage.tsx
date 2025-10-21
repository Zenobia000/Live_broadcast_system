import React, { useState, useEffect } from 'react'
import { ChevronDownIcon, ChevronRightIcon } from '@heroicons/react/24/outline'
import api from '../services/api'
import { useToast } from '../contexts/ToastContext'

interface ParticipantDetail {
  user_id: number
  user_name: string
  user_email: string
  status: string
  check_in_time: string | null
  note: string | null
}

interface EventDetail {
  event_id: number
  event_title: string
  event_description: string | null
  start_time: string
  end_time: string
  total_participants: number
  present_count: number
  late_count: number
  absent_count: number
  leave_count: number
  participants: ParticipantDetail[]
}

interface AttendanceHistoryItem {
  id: string
  eventTitle: string
  eventId: number
  status: string
  checkInTime: string
  createdAt: string
}

const EventHistoryPage: React.FC = () => {
  const [attendanceHistory, setAttendanceHistory] = useState<AttendanceHistoryItem[]>([])
  const [expandedEvents, setExpandedEvents] = useState<Set<number>>(new Set())
  const [eventDetails, setEventDetails] = useState<Map<number, EventDetail>>(new Map())
  const [loadingDetails, setLoadingDetails] = useState<Set<number>>(new Set())
  const { showToast } = useToast()

  useEffect(() => {
    loadAttendanceHistory()
  }, [])

  const loadAttendanceHistory = async () => {
    try {
      const response = await api.getAttendanceHistory(100)
      setAttendanceHistory(response.data || [])
    } catch (error) {
      console.error('Failed to load attendance history:', error)
      showToast({
        type: 'error',
        message: '無法載入歷史記錄',
        autoClose: 3000
      })
    }
  }

  const toggleEventExpand = async (eventId: number) => {
    const newExpanded = new Set(expandedEvents)

    if (newExpanded.has(eventId)) {
      // Collapse
      newExpanded.delete(eventId)
      setExpandedEvents(newExpanded)
    } else {
      // Expand
      newExpanded.add(eventId)
      setExpandedEvents(newExpanded)

      // Load details if not already loaded
      if (!eventDetails.has(eventId)) {
        await loadEventDetails(eventId)
      }
    }
  }

  const loadEventDetails = async (eventId: number) => {
    setLoadingDetails(prev => new Set(prev).add(eventId))
    try {
      const response = await api.getEventAttendanceDetail(eventId)
      setEventDetails(prev => new Map(prev).set(eventId, response.data))
    } catch (error) {
      console.error(`Failed to load details for event ${eventId}:`, error)
      showToast({
        type: 'error',
        message: '無法載入會議詳情',
        autoClose: 3000
      })
    } finally {
      setLoadingDetails(prev => {
        const newSet = new Set(prev)
        newSet.delete(eventId)
        return newSet
      })
    }
  }

  const getStatusBadge = (status: string) => {
    const statusLower = status.toLowerCase()
    switch (statusLower) {
      case 'present':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
            ✅ 出席
          </span>
        )
      case 'late':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
            ⏰ 遲到
          </span>
        )
      case 'leave':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
            📋 請假
          </span>
        )
      default:
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">
            ❌ 缺席
          </span>
        )
    }
  }

  // Group attendance by event
  const groupedByEvent = attendanceHistory.reduce((acc, item) => {
    const eventId = item.eventId
    if (!acc[eventId]) {
      acc[eventId] = {
        eventId,
        eventTitle: item.eventTitle,
        date: item.createdAt,
        attendances: []
      }
    }
    acc[eventId].attendances.push(item)
    return acc
  }, {} as Record<number, { eventId: number; eventTitle: string; date: string; attendances: AttendanceHistoryItem[] }>)

  const eventGroups = Object.values(groupedByEvent).sort((a, b) =>
    new Date(b.date).getTime() - new Date(a.date).getTime()
  )

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            📊 會議出席統計
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            查看所有會議的詳細出席記錄
          </p>
        </div>

        {/* Events List */}
        <div className="space-y-4">
          {eventGroups.length === 0 ? (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-12 text-center">
              <div className="text-6xl mb-4">📅</div>
              <p className="text-gray-500 dark:text-gray-400 text-lg">暫無會議記錄</p>
            </div>
          ) : (
            eventGroups.map(group => {
              const isExpanded = expandedEvents.has(group.eventId)
              const details = eventDetails.get(group.eventId)
              const isLoading = loadingDetails.has(group.eventId)

              return (
                <div
                  key={group.eventId}
                  className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden transition-all duration-200 hover:shadow-xl"
                >
                  {/* Event Header */}
                  <button
                    onClick={() => toggleEventExpand(group.eventId)}
                    className="w-full p-6 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    <div className="flex items-center space-x-4 flex-1">
                      {isExpanded ? (
                        <ChevronDownIcon className="w-5 h-5 text-gray-400" />
                      ) : (
                        <ChevronRightIcon className="w-5 h-5 text-gray-400" />
                      )}
                      <div className="text-left flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                          {group.eventTitle}
                        </h3>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {new Date(group.date).toLocaleString('zh-TW', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </p>
                      </div>
                    </div>

                    {/* Summary Stats */}
                    {details && (
                      <div className="flex items-center space-x-4 mr-4">
                        <div className="text-center">
                          <div className="text-sm text-gray-500 dark:text-gray-400">總計</div>
                          <div className="text-xl font-bold text-gray-900 dark:text-white">
                            {details.total_participants}
                          </div>
                        </div>
                        <div className="text-center">
                          <div className="text-sm text-green-600 dark:text-green-400">出席</div>
                          <div className="text-xl font-bold text-green-600 dark:text-green-400">
                            {details.present_count}
                          </div>
                        </div>
                        <div className="text-center">
                          <div className="text-sm text-yellow-600 dark:text-yellow-400">遲到</div>
                          <div className="text-xl font-bold text-yellow-600 dark:text-yellow-400">
                            {details.late_count}
                          </div>
                        </div>
                        <div className="text-center">
                          <div className="text-sm text-red-600 dark:text-red-400">缺席</div>
                          <div className="text-xl font-bold text-red-600 dark:text-red-400">
                            {details.absent_count}
                          </div>
                        </div>
                      </div>
                    )}
                  </button>

                  {/* Expanded Details */}
                  {isExpanded && (
                    <div className="border-t border-gray-200 dark:border-gray-700">
                      {isLoading ? (
                        <div className="p-8 text-center">
                          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                          <p className="mt-4 text-gray-500 dark:text-gray-400">載入中...</p>
                        </div>
                      ) : details ? (
                        <div className="p-6">
                          {/* Event Description */}
                          {details.event_description && (
                            <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                              <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                                會議說明
                              </h4>
                              <p className="text-gray-600 dark:text-gray-400">
                                {details.event_description}
                              </p>
                            </div>
                          )}

                          {/* Participants Table */}
                          <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                              <thead className="bg-gray-50 dark:bg-gray-700">
                                <tr>
                                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                    姓名
                                  </th>
                                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                    Email
                                  </th>
                                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                    狀態
                                  </th>
                                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                    簽到時間
                                  </th>
                                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                    備註
                                  </th>
                                </tr>
                              </thead>
                              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                                {details.participants.map((participant) => (
                                  <tr key={participant.user_id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                                    <td className="px-6 py-4 whitespace-nowrap">
                                      <div className="text-sm font-medium text-gray-900 dark:text-white">
                                        {participant.user_name}
                                      </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                      <div className="text-sm text-gray-500 dark:text-gray-400">
                                        {participant.user_email}
                                      </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                      {getStatusBadge(participant.status)}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                      <div className="text-sm text-gray-500 dark:text-gray-400">
                                        {participant.check_in_time
                                          ? new Date(participant.check_in_time).toLocaleString('zh-TW', {
                                              month: 'short',
                                              day: 'numeric',
                                              hour: '2-digit',
                                              minute: '2-digit'
                                            })
                                          : '-'}
                                      </div>
                                    </td>
                                    <td className="px-6 py-4">
                                      <div className="text-sm text-gray-500 dark:text-gray-400">
                                        {participant.note || '-'}
                                      </div>
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>

                          {/* Statistics Summary */}
                          <div className="mt-6 grid grid-cols-2 md:grid-cols-5 gap-4">
                            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 text-center">
                              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                                {details.total_participants}
                              </div>
                              <div className="text-sm text-gray-500 dark:text-gray-400">應到人數</div>
                            </div>
                            <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 text-center">
                              <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                                {details.present_count}
                              </div>
                              <div className="text-sm text-green-600 dark:text-green-400">出席</div>
                            </div>
                            <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4 text-center">
                              <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
                                {details.late_count}
                              </div>
                              <div className="text-sm text-yellow-600 dark:text-yellow-400">遲到</div>
                            </div>
                            <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-4 text-center">
                              <div className="text-2xl font-bold text-red-600 dark:text-red-400">
                                {details.absent_count}
                              </div>
                              <div className="text-sm text-red-600 dark:text-red-400">缺席</div>
                            </div>
                            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 text-center">
                              <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                                {Math.round(((details.present_count + details.late_count) / details.total_participants) * 100)}%
                              </div>
                              <div className="text-sm text-blue-600 dark:text-blue-400">出席率</div>
                            </div>
                          </div>
                        </div>
                      ) : (
                        <div className="p-8 text-center text-gray-500 dark:text-gray-400">
                          無法載入會議詳情
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )
            })
          )}
        </div>

        {/* Back Button */}
        <div className="mt-8 text-center">
          <button
            onClick={() => window.location.href = '/'}
            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
          >
            返回主頁
          </button>
        </div>
      </div>
    </div>
  )
}

export default EventHistoryPage
