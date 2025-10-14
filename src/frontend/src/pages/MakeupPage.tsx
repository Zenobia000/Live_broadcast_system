import React, { useState, useEffect } from 'react'
import {
  Card, CardBody, Button, Form, FormSection, FormLabel, FormActions,
  Select, Textarea, showToast, LoadingSpinner
} from '../components'
import { api } from '../services/api'
import { goBack, URLValidator } from '../utils/navigation'

const MakeupPage: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [missedDate, setMissedDate] = useState('')
  const [formData, setFormData] = useState({
    reason: '',
    description: ''
  })

  useEffect(() => {
    // Validate URL and get missed date
    if (!URLValidator.validateMakeupURL()) {
      return // Validator will handle redirect
    }

    const urlParams = new URLSearchParams(window.location.search)
    const dateParam = urlParams.get('date')
    if (dateParam) {
      setMissedDate(dateParam)
    }
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.reason) {
      showToast({
        type: 'warning',
        message: '請選擇錯過原因',
        autoClose: 3000
      })
      return
    }

    setLoading(true)

    try {
      const response = await api.submitMakeupRequest({
        missedDate,
        reason: formData.reason,
        description: formData.description || undefined
      })

      if (response.success) {
        showToast({
          type: 'success',
          message: '補簽申請已成功提交！',
          autoClose: 3000
        })

        setTimeout(() => {
          window.location.href = `/status?type=makeup&id=${response.data.id}`
        }, 2000)
      }
    } catch (error: any) {
      showToast({
        type: 'error',
        message: error.response?.data?.message || '提交失敗，請重試',
        autoClose: 5000
      })
    } finally {
      setLoading(false)
    }
  }

  const reasonOptions = [
    { value: '', label: '選擇錯過原因' },
    { value: 'forgot', label: '忘記簽到' },
    { value: 'technical', label: '技術問題' },
    { value: 'meeting', label: '會議中無法簽到' },
    { value: 'network', label: '網路問題' },
    { value: 'other', label: '其他原因' }
  ]

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('zh-TW', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      weekday: 'long'
    })
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
              補簽申請
            </h1>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-2xl mx-auto p-4">
        {/* Context Information */}
        <Card className="mb-6 border-yellow-200 dark:border-yellow-800 bg-yellow-50 dark:bg-yellow-900/20">
          <CardBody>
            <div className="flex items-center gap-3">
              <div className="text-2xl">⏰</div>
              <div>
                <h2 className="font-semibold text-yellow-800 dark:text-yellow-200">
                  補簽日期：{missedDate && formatDate(missedDate)}
                </h2>
                <p className="text-sm text-yellow-700 dark:text-yellow-300">
                  為什麼錯過了這天的簽到？請選擇原因並提供說明
                </p>
              </div>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardBody>
            <Form onSubmit={handleSubmit}>
              {/* Reason Selection */}
              <FormSection>
                <FormLabel required>錯過原因</FormLabel>
                <Select
                  options={reasonOptions}
                  value={formData.reason}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    reason: e.target.value
                  }))}
                  required
                />
              </FormSection>

              {/* Description */}
              <FormSection>
                <FormLabel>說明 {formData.reason === 'other' ? '(必填)' : '(可選)'}</FormLabel>
                <Textarea
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    description: e.target.value
                  }))}
                  placeholder="簡要說明情況，幫助審核者理解"
                  maxLength={150}
                  rows={4}
                  required={formData.reason === 'other'}
                />
                <p className="text-xs text-gray-500 mt-1">
                  {formData.description.length}/150 字元
                </p>
              </FormSection>

              {/* Helpful Tips */}
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mt-6">
                <div className="flex items-start gap-3">
                  <div className="text-blue-500 text-lg">💡</div>
                  <div className="text-sm">
                    <p className="font-medium text-blue-800 dark:text-blue-200 mb-2">
                      補簽申請小提醒：
                    </p>
                    <ul className="text-blue-700 dark:text-blue-300 space-y-1 list-disc list-inside">
                      <li>詳細的說明有助於加快審核速度</li>
                      <li>如果是技術問題，請提供具體的錯誤情況</li>
                      <li>提交後可以在狀態頁面追蹤審核進度</li>
                    </ul>
                  </div>
                </div>
              </div>

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
                  disabled={loading || !formData.reason}
                  className="min-w-40"
                >
                  {loading ? (
                    <div className="flex items-center gap-2">
                      <LoadingSpinner size="sm" color="white" />
                      <span>提交中...</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-2">
                      <span>📤</span>
                      <span>提交補簽申請</span>
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

export default MakeupPage