import React, { useState } from 'react'
import {
  Card, CardBody, Button, Form, FormSection, FormLabel, FormActions,
  Input, Textarea, showToast, LoadingSpinner
} from '../components'
import UserSelector from '../components/UserSelector'
import { api } from '../services/api'
import { goBack } from '../utils/navigation'

const CreateEventPage: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    startDate: getTomorrow(),
    startTime: '09:00',
    endDate: getTomorrow(),
    endTime: '10:00',
    gracePeriodMinutes: 5,
    participantIds: [] as number[]
  })

  function getTomorrow() {
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    return tomorrow.toISOString().split('T')[0]
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // Validation
    if (!formData.title || !formData.startDate || !formData.endDate) {
      showToast({
        type: 'warning',
        message: '請填寫必要欄位',
        autoClose: 3000
      })
      return
    }

    // Combine date and time
    const startTime = `${formData.startDate}T${formData.startTime}:00Z`
    const endTime = `${formData.endDate}T${formData.endTime}:00Z`

    // Validate end time after start time
    if (new Date(endTime) <= new Date(startTime)) {
      showToast({
        type: 'warning',
        message: '結束時間必須晚於開始時間',
        autoClose: 3000
      })
      return
    }

    setLoading(true)

    try {
      const response = await api.createEvent({
        title: formData.title,
        description: formData.description || undefined,
        startTime,
        endTime,
        gracePeriodMinutes: formData.gracePeriodMinutes,
        participantIds: formData.participantIds
      })

      if (response.success) {
        showToast({
          type: 'success',
          message: `會議「${formData.title}」已成功創建！`,
          autoClose: 3000
        })

        setTimeout(() => {
          window.location.href = '/dashboard'
        }, 2000)
      }
    } catch (error: any) {
      showToast({
        type: 'error',
        message: error.response?.data?.detail || '創建失敗，請重試',
        autoClose: 5000
      })
    } finally {
      setLoading(false)
    }
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
              創建會議
            </h1>
            <div className="ml-auto text-sm text-gray-500">
              管理功能
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-2xl mx-auto p-4">
        <Card>
          <CardBody>
            <Form onSubmit={handleSubmit}>
              {/* Title */}
              <FormSection>
                <FormLabel required>會議標題</FormLabel>
                <Input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                  placeholder="例如：每週站會、專案討論"
                  required
                  maxLength={100}
                />
                <p className="text-xs text-gray-500 mt-1">
                  {formData.title.length}/100 字元
                </p>
              </FormSection>

              {/* Description */}
              <FormSection>
                <FormLabel>會議描述（可選）</FormLabel>
                <Textarea
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="會議目的、議程等..."
                  maxLength={500}
                />
                <p className="text-xs text-gray-500 mt-1">
                  {formData.description.length}/500 字元
                </p>
              </FormSection>

              {/* Date & Time */}
              <FormSection>
                <FormLabel required>會議時間</FormLabel>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <FormLabel className="text-sm text-gray-600">開始日期</FormLabel>
                    <Input
                      type="date"
                      value={formData.startDate}
                      min={new Date().toISOString().split('T')[0]}
                      onChange={(e) => setFormData(prev => ({
                        ...prev,
                        startDate: e.target.value,
                        endDate: e.target.value // Auto-sync end date
                      }))}
                      required
                    />
                  </div>
                  <div>
                    <FormLabel className="text-sm text-gray-600">開始時間</FormLabel>
                    <Input
                      type="time"
                      value={formData.startTime}
                      onChange={(e) => setFormData(prev => ({ ...prev, startTime: e.target.value }))}
                      required
                    />
                  </div>
                  <div>
                    <FormLabel className="text-sm text-gray-600">結束日期</FormLabel>
                    <Input
                      type="date"
                      value={formData.endDate}
                      min={formData.startDate}
                      onChange={(e) => setFormData(prev => ({ ...prev, endDate: e.target.value }))}
                      required
                    />
                  </div>
                  <div>
                    <FormLabel className="text-sm text-gray-600">結束時間</FormLabel>
                    <Input
                      type="time"
                      value={formData.endTime}
                      onChange={(e) => setFormData(prev => ({ ...prev, endTime: e.target.value }))}
                      required
                    />
                  </div>
                </div>
              </FormSection>

              {/* Grace Period */}
              <FormSection>
                <FormLabel>簽到寬限期（分鐘）</FormLabel>
                <select
                  value={formData.gracePeriodMinutes}
                  onChange={(e) => setFormData(prev => ({ ...prev, gracePeriodMinutes: Number(e.target.value) }))}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                >
                  <option value={0}>0 分鐘（準時）</option>
                  <option value={5}>5 分鐘</option>
                  <option value={10}>10 分鐘</option>
                  <option value={15}>15 分鐘</option>
                  <option value={30}>30 分鐘</option>
                </select>
                <p className="text-xs text-gray-500 mt-1">
                  會議開始後多久內簽到不算遲到
                </p>
              </FormSection>

              {/* Participants */}
              <FormSection>
                <FormLabel>邀請參與者</FormLabel>
                <UserSelector
                  selectedIds={formData.participantIds}
                  onChange={(ids) => setFormData(prev => ({ ...prev, participantIds: ids }))}
                />
                {formData.participantIds.length === 0 && (
                  <p className="text-xs text-amber-600 dark:text-amber-400 mt-2">
                    提示：未選擇參與者時，所有成員都可以簽到
                  </p>
                )}
              </FormSection>

              {/* Actions */}
              <FormActions className="mt-8">
                <Button
                  type="button"
                  variant="outline"
                  onClick={goBack}
                  disabled={loading}
                >
                  取消
                </Button>
                <Button
                  type="submit"
                  disabled={loading}
                  className="min-w-32"
                >
                  {loading ? (
                    <div className="flex items-center gap-2">
                      <LoadingSpinner size="sm" color="white" />
                      <span>創建中...</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-2">
                      <span>✨</span>
                      <span>創建會議</span>
                    </div>
                  )}
                </Button>
              </FormActions>
            </Form>
          </CardBody>
        </Card>
      </main>
    </div>
  )
}

export default CreateEventPage
