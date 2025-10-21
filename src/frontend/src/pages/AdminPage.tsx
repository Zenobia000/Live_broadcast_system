import React, { useState, useEffect } from 'react'
import {
  Card, CardBody, Button, Badge, LoadingSpinner, showToast, CardSkeleton
} from '../components'
import { api, LeaveRequest, MakeupRequest } from '../services/api'
import { goBack } from '../utils/navigation'

interface PendingRequests {
  leaveRequests: LeaveRequest[]
  makeupRequests: MakeupRequest[]
}

const AdminPage: React.FC = () => {
  const [loading, setLoading] = useState(true)
  const [processing, setProcessing] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'pending' | 'all'>('pending')
  const [pendingRequests, setPendingRequests] = useState<PendingRequests>({
    leaveRequests: [],
    makeupRequests: []
  })
  const [allRequests, setAllRequests] = useState<PendingRequests>({
    leaveRequests: [],
    makeupRequests: []
  })
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set())

  useEffect(() => {
    loadPendingRequests()
    loadAllRequests()
  }, [])

  const loadPendingRequests = async () => {
    try {
      setLoading(true)
      const response = await api.getPendingRequests()
      if (response.success) {
        setPendingRequests(response.data)
      }
    } catch (error: any) {
      showToast({
        type: 'error',
        message: error.response?.data?.message || '載入申請失敗',
        autoClose: 5000
      })
    } finally {
      setLoading(false)
    }
  }

  const loadAllRequests = async () => {
    try {
      const [leaveResponse, makeupResponse] = await Promise.all([
        api.getLeaveRequests(),
        api.getMakeupRequests()
      ])

      setAllRequests({
        leaveRequests: leaveResponse.success ? leaveResponse.data : [],
        makeupRequests: makeupResponse.success ? makeupResponse.data : []
      })
    } catch (error: any) {
      console.error('Failed to load all requests:', error)
    }
  }

  const handleReview = async (
    id: string,
    type: 'leave' | 'makeup',
    action: 'approve' | 'reject'
  ) => {
    const comment = action === 'reject'
      ? prompt('請輸入拒絕原因（可選）:')
      : undefined

    if (action === 'reject' && comment === null) {
      return
    }

    try {
      setProcessing(id)
      const response = await api.reviewRequest(id, type, action, comment || undefined)

      if (response.success) {
        showToast({
          type: 'success',
          message: `申請已${action === 'approve' ? '批准' : '拒絕'}`,
          autoClose: 3000
        })

        await loadPendingRequests()
      }
    } catch (error: any) {
      showToast({
        type: 'error',
        message: error.response?.data?.message || '操作失敗，請重試',
        autoClose: 5000
      })
    } finally {
      setProcessing(null)
    }
  }

  const handleBatchReview = async (action: 'approve' | 'reject') => {
    if (selectedItems.size === 0) {
      showToast({
        type: 'warning',
        message: '請選擇要處理的申請',
        autoClose: 3000
      })
      return
    }

    const comment = action === 'reject'
      ? prompt('請輸入拒絕原因（可選）:')
      : undefined

    if (action === 'reject' && comment === null) {
      return
    }

    if (!confirm(`確定要${action === 'approve' ? '批准' : '拒絕'} ${selectedItems.size} 個申請嗎？`)) {
      return
    }

    try {
      setProcessing('batch')

      const promises: Promise<any>[] = []
      selectedItems.forEach(itemId => {
        const [type, id] = itemId.split('-')
        promises.push(api.reviewRequest(id, type as 'leave' | 'makeup', action, comment || undefined))
      })

      await Promise.all(promises)

      showToast({
        type: 'success',
        message: `已${action === 'approve' ? '批准' : '拒絕'} ${selectedItems.size} 個申請`,
        autoClose: 3000
      })

      setSelectedItems(new Set())
      await loadPendingRequests()
    } catch (error: any) {
      showToast({
        type: 'error',
        message: '批量操作失敗，部分申請可能未處理',
        autoClose: 5000
      })
    } finally {
      setProcessing(null)
    }
  }

  const toggleSelection = (itemId: string) => {
    const newSelection = new Set(selectedItems)
    if (newSelection.has(itemId)) {
      newSelection.delete(itemId)
    } else {
      newSelection.add(itemId)
    }
    setSelectedItems(newSelection)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('zh-TW', {
      month: 'short',
      day: 'numeric',
      weekday: 'short'
    })
  }

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString('zh-TW', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const renderRequestItem = (item: { request: LeaveRequest | MakeupRequest, type: 'leave' | 'makeup' }) => {
    const { request, type } = item
    const itemId = `${type}-${request.id}`
    const isSelected = selectedItems.has(itemId)
    const isProcessing = processing === request.id

    return (
      <Card key={request.id} className={`transition-all ${
        isSelected ? 'ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-900/20' : ''
      }`}>
        <CardBody>
          <div className="flex items-start space-x-4">
            <label className="flex items-center mt-1">
              <input
                type="checkbox"
                checked={isSelected}
                onChange={() => toggleSelection(itemId)}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                disabled={isProcessing}
              />
            </label>

            <div className="flex-1">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white">
                    {type === 'leave' ? '請假申請' : '補簽申請'}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    申請人：User
                  </p>
                  <p className="text-sm text-gray-500">
                    {formatDateTime(request.createdAt)}
                  </p>
                </div>

                <Badge variant="warning" size="sm">
                  待審核
                </Badge>
              </div>

              <div className="mt-3">
                {type === 'leave' && 'startDate' in request && (
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600 dark:text-gray-400">日期：</span>
                      <span className="font-medium">
                        {formatDate(request.startDate)}
                        {request.startDate !== request.endDate && ` - ${formatDate(request.endDate)}`}
                      </span>
                    </div>
                    {'type' in request && (
                      <div>
                        <span className="text-gray-600 dark:text-gray-400">類型：</span>
                        <span className="font-medium">
                          {request.type === 'full-day' ? '全天' : request.type === 'morning' ? '上午' : '下午'}
                        </span>
                      </div>
                    )}
                  </div>
                )}

                {type === 'makeup' && 'missedDate' in request && (
                  <div className="text-sm">
                    <span className="text-gray-600 dark:text-gray-400">補簽日期：</span>
                    <span className="font-medium">{formatDate(request.missedDate)}</span>
                  </div>
                )}

                <div className="mt-2 text-sm">
                  <span className="text-gray-600 dark:text-gray-400">原因：</span>
                  <span className="font-medium">{request.reason}</span>
                </div>

                {request.description && (
                  <div className="mt-2 text-sm">
                    <span className="text-gray-600 dark:text-gray-400">說明：</span>
                    <span className="text-gray-900 dark:text-white">{request.description}</span>
                  </div>
                )}
              </div>

              <div className="mt-4 flex space-x-2">
                <Button
                  size="sm"
                  onClick={() => handleReview(request.id, type, 'approve')}
                  disabled={isProcessing}
                  className="bg-green-600 hover:bg-green-700"
                >
                  {isProcessing ? (
                    <LoadingSpinner size="sm" color="white" />
                  ) : (
                    <span className="flex items-center gap-1">
                      <span>✅</span>
                      <span>批准</span>
                    </span>
                  )}
                </Button>

                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleReview(request.id, type, 'reject')}
                  disabled={isProcessing}
                  className="border-red-200 text-red-600 hover:bg-red-50 dark:border-red-800 dark:text-red-400 dark:hover:bg-red-900/20"
                >
                  <span className="flex items-center gap-1">
                    <span>❌</span>
                    <span>拒絕</span>
                  </span>
                </Button>

                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => window.location.href = `/status?type=${type}&id=${request.id}`}
                  disabled={isProcessing}
                >
                  詳情
                </Button>
              </div>
            </div>
          </div>
        </CardBody>
      </Card>
    )
  }

  const allPendingRequests = [
    ...pendingRequests.leaveRequests.map(req => ({ request: req, type: 'leave' as const })),
    ...pendingRequests.makeupRequests.map(req => ({ request: req, type: 'makeup' as const }))
  ].sort((a, b) => new Date(b.request.createdAt).getTime() - new Date(a.request.createdAt).getTime())

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-4">
        <div className="max-w-4xl mx-auto space-y-6">
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <header className="bg-white dark:bg-gray-800 shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => window.location.href = '/dashboard'}
              >
                🏠 首頁
              </Button>
              <span className="text-gray-300 dark:text-gray-600">|</span>
              <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
                審核管理
              </h1>
            </div>

            <div className="flex gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => window.location.href = '/admin/attendance'}
              >
                📊 出席統計
              </Button>
              <Button
                variant="primary"
                size="sm"
                onClick={() => window.location.href = '/create-event'}
              >
                ✨ 創建會議
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={loadPendingRequests}
                disabled={loading}
              >
                {loading ? <LoadingSpinner size="sm" /> : '🔄 重新整理'}
              </Button>
            </div>
          </div>

          <div className="mt-4">
            <nav className="flex space-x-8">
              <button
                onClick={() => setActiveTab('pending')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'pending'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                待審核
                {allPendingRequests.length > 0 && (
                  <Badge size="sm" className="ml-2">
                    {allPendingRequests.length}
                  </Badge>
                )}
              </button>
              <button
                onClick={() => setActiveTab('all')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'all'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                全部記錄
              </button>
            </nav>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto p-4">
        {selectedItems.size > 0 && (
          <Card className="mb-6 border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-900/20">
            <CardBody>
              <div className="flex items-center justify-between">
                <span className="text-blue-800 dark:text-blue-200">
                  已選擇 {selectedItems.size} 項申請
                </span>
                <div className="flex space-x-2">
                  <Button
                    size="sm"
                    onClick={() => handleBatchReview('approve')}
                    disabled={processing === 'batch'}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    {processing === 'batch' ? (
                      <LoadingSpinner size="sm" color="white" />
                    ) : (
                      '批量批准'
                    )}
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleBatchReview('reject')}
                    disabled={processing === 'batch'}
                    className="border-red-200 text-red-600 hover:bg-red-50"
                  >
                    批量拒絕
                  </Button>
                </div>
              </div>
            </CardBody>
          </Card>
        )}

        {activeTab === 'pending' && (
          <div className="space-y-4">
            {allPendingRequests.length === 0 ? (
              <Card>
                <CardBody className="text-center py-12">
                  <div className="text-6xl mb-4">🎉</div>
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    沒有待審核的申請
                  </h2>
                  <p className="text-gray-600 dark:text-gray-400">
                    所有申請都已處理完畢
                  </p>
                </CardBody>
              </Card>
            ) : (
              allPendingRequests.map((item) =>
                renderRequestItem(item)
              )
            )}
          </div>
        )}

        {activeTab === 'all' && (
          <div className="space-y-4">
            {loading ? (
              <CardSkeleton count={3} />
            ) : (
              <>
                {allRequests.leaveRequests.length === 0 && allRequests.makeupRequests.length === 0 ? (
                  <Card>
                    <CardBody className="text-center py-12">
                      <div className="text-6xl mb-4">📋</div>
                      <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                        沒有任何申請記錄
                      </h2>
                      <p className="text-gray-600 dark:text-gray-400">
                        系統中暫無請假或補簽申請
                      </p>
                    </CardBody>
                  </Card>
                ) : (
                  [...allRequests.leaveRequests, ...allRequests.makeupRequests]
                    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
                    .map((request) => {
                      const type = 'missedDate' in request ? 'makeup' : 'leave'
                      const isProcessing = processing === request.id

                      const getStatusBadge = () => {
                        if (request.status === 'approved') {
                          return <Badge variant="success" size="sm">✅ 已批准</Badge>
                        } else if (request.status === 'rejected') {
                          return <Badge variant="error" size="sm">❌ 已拒絕</Badge>
                        } else {
                          return <Badge variant="warning" size="sm">⏳ 待審核</Badge>
                        }
                      }

                      return (
                        <Card key={`${type}-${request.id}`}>
                          <CardBody>
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center space-x-2 mb-2">
                                  <h3 className="font-medium text-gray-900 dark:text-white">
                                    {type === 'leave' ? '請假申請' : '補簽申請'}
                                  </h3>
                                  {getStatusBadge()}
                                </div>
                                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                                  申請時間：{formatDateTime(request.createdAt)}
                                </p>
                                {type === 'leave' && 'startDate' in request && (
                                  <p className="text-sm text-gray-600 dark:text-gray-400">
                                    請假日期：{formatDate(request.startDate)}
                                    {request.startDate !== request.endDate && ` - ${formatDate(request.endDate)}`}
                                  </p>
                                )}
                                {type === 'makeup' && 'missedDate' in request && (
                                  <p className="text-sm text-gray-600 dark:text-gray-400">
                                    補簽日期：{formatDate(request.missedDate)}
                                  </p>
                                )}
                                <p className="text-sm text-gray-900 dark:text-white mt-2">
                                  <span className="font-medium">原因：</span>{request.reason}
                                </p>
                                {request.reviewedBy && request.reviewedAt && (
                                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                                    審核時間：{formatDateTime(request.reviewedAt)}
                                  </p>
                                )}
                              </div>
                            </div>
                          </CardBody>
                        </Card>
                      )
                    })
                )}
              </>
            )}
          </div>
        )}
      </main>
    </div>
  )
}

export default AdminPage