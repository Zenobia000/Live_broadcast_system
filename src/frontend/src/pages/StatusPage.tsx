import React, { useState, useEffect } from 'react'
import {
  Card, CardBody, Button, Badge, LoadingSpinner, showToast
} from '../components'
import { api, LeaveRequest, MakeupRequest } from '../services/api'
import { URLValidator, goBack } from '../utils/navigation'

const StatusPage: React.FC = () => {
  const [loading, setLoading] = useState(true)
  const [request, setRequest] = useState<LeaveRequest | MakeupRequest | null>(null)
  const [requestType, setRequestType] = useState<'leave' | 'makeup'>('leave')

  useEffect(() => {
    loadRequestData()
  }, [])

  const loadRequestData = async () => {
    // Validate URL parameters
    if (!URLValidator.validateStatusURL()) {
      return // Validator will handle redirect
    }

    const urlParams = new URLSearchParams(window.location.search)
    const type = urlParams.get('type') as 'leave' | 'makeup'
    const id = urlParams.get('id')!

    setRequestType(type)

    try {
      setLoading(true)
      const response = await api.getRequestById(id, type)

      if (response.success) {
        setRequest(response.data)
      }
    } catch (error: any) {
      showToast({
        type: 'error',
        message: error.response?.data?.message || '載入申請資料失敗',
        autoClose: 5000
      })
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pending':
        return <Badge variant="warning">審核中</Badge>
      case 'approved':
        return <Badge variant="success">已批准</Badge>
      case 'rejected':
        return <Badge variant="error">已拒絕</Badge>
      default:
        return <Badge variant="default">{status}</Badge>
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return '⏳'
      case 'approved':
        return '✅'
      case 'rejected':
        return '❌'
      default:
        return '❓'
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('zh-TW', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      weekday: 'long'
    })
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-gray-600 dark:text-gray-400">載入申請資料...</p>
        </div>
      </div>
    )
  }

  if (!request) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">❓</div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            找不到申請資料
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            申請可能已被刪除或您沒有查看權限
          </p>
          <Button onClick={() => window.location.href = '/dashboard'}>
            返回儀表板
          </Button>
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
              申請狀態
            </h1>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-2xl mx-auto p-4 space-y-6">
        {/* Status Overview */}
        <Card>
          <CardBody>
            <div className="text-center">
              <div className="text-6xl mb-4">{getStatusIcon(request.status)}</div>
              <div className="mb-4">{getStatusBadge(request.status)}</div>

              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                {requestType === 'leave' ? '請假申請' : '補簽申請'}
              </h2>

              <p className="text-gray-600 dark:text-gray-400">
                {request.status === 'pending' && '您的申請正在審核中，請耐心等候'}
                {request.status === 'approved' && '恭喜！您的申請已被批准'}
                {request.status === 'rejected' && '很抱歉，您的申請已被拒絕'}
              </p>
            </div>
          </CardBody>
        </Card>

        {/* Request Details */}
        <Card>
          <CardBody>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              申請詳情
            </h3>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    申請編號
                  </label>
                  <p className="text-gray-900 dark:text-white">{request.id}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    申請時間
                  </label>
                  <p className="text-gray-900 dark:text-white">
                    {new Date(request.createdAt).toLocaleString('zh-TW')}
                  </p>
                </div>
              </div>

              {requestType === 'leave' && 'startDate' in request && (
                <>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        開始日期
                      </label>
                      <p className="text-gray-900 dark:text-white">
                        {formatDate(request.startDate)}
                      </p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        結束日期
                      </label>
                      <p className="text-gray-900 dark:text-white">
                        {formatDate(request.endDate)}
                      </p>
                    </div>
                  </div>

                  {'type' in request && (
                    <div>
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        請假類型
                      </label>
                      <p className="text-gray-900 dark:text-white">
                        {request.type === 'full-day' && '全天請假'}
                        {request.type === 'morning' && '上午請假'}
                        {request.type === 'afternoon' && '下午請假'}
                      </p>
                    </div>
                  )}
                </>
              )}

              {requestType === 'makeup' && 'missedDate' in request && (
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    補簽日期
                  </label>
                  <p className="text-gray-900 dark:text-white">
                    {formatDate(request.missedDate)}
                  </p>
                </div>
              )}

              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  {requestType === 'leave' ? '請假原因' : '錯過原因'}
                </label>
                <p className="text-gray-900 dark:text-white">{request.reason}</p>
              </div>

              {request.description && (
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    詳細說明
                  </label>
                  <p className="text-gray-900 dark:text-white whitespace-pre-wrap">
                    {request.description}
                  </p>
                </div>
              )}

              {requestType === 'leave' && 'emergencyContact' in request && request.emergencyContact && (
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    緊急聯絡方式
                  </label>
                  <p className="text-gray-900 dark:text-white">{request.emergencyContact}</p>
                </div>
              )}
            </div>
          </CardBody>
        </Card>

        {/* Review Information */}
        {request.reviewedBy && (
          <Card>
            <CardBody>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                審核資訊
              </h3>
              <div className="space-y-3">
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    審核者
                  </label>
                  <p className="text-gray-900 dark:text-white">{request.reviewedBy}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    審核時間
                  </label>
                  <p className="text-gray-900 dark:text-white">
                    {request.reviewedAt && new Date(request.reviewedAt).toLocaleString('zh-TW')}
                  </p>
                </div>
              </div>
            </CardBody>
          </Card>
        )}

        {/* Actions */}
        <div className="flex justify-center space-x-4">
          <Button
            variant="outline"
            onClick={() => window.location.href = '/dashboard'}
          >
            返回儀表板
          </Button>
          <Button
            onClick={loadRequestData}
            disabled={loading}
          >
            {loading ? <LoadingSpinner size="sm" color="white" /> : '重新整理'}
          </Button>
        </div>
      </main>
    </div>
  )
}

export default StatusPage