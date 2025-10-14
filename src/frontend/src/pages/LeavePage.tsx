import React, { useState, useEffect } from 'react'
import {
  Card, CardBody, Button, Form, FormSection, FormLabel, FormActions,
  Input, Select, Textarea, showToast, LoadingSpinner
} from '../components'
import { api } from '../services/api'
import { goBack } from '../utils/navigation'

const LeavePage: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    startDate: getDefaultDate(),
    endDate: getDefaultDate(),
    type: 'full-day' as 'full-day' | 'morning' | 'afternoon',
    reason: '',
    description: '',
    emergencyContact: ''
  })

  function getDefaultDate() {
    // Smart default: tomorrow, but skip weekends
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)

    // If tomorrow is weekend, suggest next Monday
    if (tomorrow.getDay() === 0 || tomorrow.getDay() === 6) {
      const nextMonday = new Date()
      nextMonday.setDate(tomorrow.getDate() + (8 - tomorrow.getDay()))
      return nextMonday.toISOString().split('T')[0]
    }

    return tomorrow.toISOString().split('T')[0]
  }

  useEffect(() => {
    // Check if date is provided in URL
    const urlParams = new URLSearchParams(window.location.search)
    const dateParam = urlParams.get('date')
    if (dateParam) {
      setFormData(prev => ({
        ...prev,
        startDate: dateParam,
        endDate: dateParam
      }))
    }
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.startDate || !formData.reason) {
      showToast({
        type: 'warning',
        message: '請填寫必要欄位',
        autoClose: 3000
      })
      return
    }

    // Validate date
    const startDate = new Date(formData.startDate)
    const today = new Date()
    today.setHours(0, 0, 0, 0)

    if (startDate < today) {
      showToast({
        type: 'warning',
        message: '不能申請過去的日期',
        autoClose: 3000
      })
      return
    }

    setLoading(true)

    try {
      const response = await api.submitLeaveRequest({
        startDate: formData.startDate,
        endDate: formData.endDate,
        type: formData.type,
        reason: formData.reason,
        description: formData.description || undefined,
        emergencyContact: formData.emergencyContact || undefined
      })

      if (response.success) {
        showToast({
          type: 'success',
          message: '申請已成功提交！',
          autoClose: 3000
        })

        // Show success animation
        setTimeout(() => {
          window.location.href = `/status?type=leave&id=${response.data.id}`
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
    { value: '', label: '選擇請假原因' },
    { value: 'personal', label: '個人事務' },
    { value: 'sick', label: '身體不適' },
    { value: 'family', label: '家庭事務' },
    { value: 'medical', label: '醫療預約' },
    { value: 'other', label: '其他原因' }
  ]

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
              申請請假
            </h1>
            <div className="ml-auto text-sm text-gray-500">
              步驟 1/2
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-2xl mx-auto p-4">
        <Card>
          <CardBody>
            <Form onSubmit={handleSubmit}>
              {/* Date Selection */}
              <FormSection>
                <FormLabel required>請假日期</FormLabel>
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
                        endDate: e.target.value // Auto-set end date
                      }))}
                      required
                    />
                  </div>
                  <div>
                    <FormLabel className="text-sm text-gray-600">結束日期</FormLabel>
                    <Input
                      type="date"
                      value={formData.endDate}
                      min={formData.startDate}
                      onChange={(e) => setFormData(prev => ({
                        ...prev,
                        endDate: e.target.value
                      }))}
                      required
                    />
                  </div>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  建議提前一天申請
                </p>
              </FormSection>

              {/* Leave Type */}
              <FormSection>
                <FormLabel required>請假類型</FormLabel>
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { value: 'full-day', icon: '📅', label: '全天請假' },
                    { value: 'morning', icon: '🌅', label: '上午請假' },
                    { value: 'afternoon', icon: '🌇', label: '下午請假' }
                  ].map((option) => (
                    <label
                      key={option.value}
                      className={`
                        flex flex-col items-center p-3 rounded-lg border-2 cursor-pointer transition-all
                        ${formData.type === option.value
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                          : 'border-gray-200 dark:border-gray-600 hover:border-gray-300'
                        }
                      `}
                    >
                      <input
                        type="radio"
                        name="leaveType"
                        value={option.value}
                        checked={formData.type === option.value}
                        onChange={(e) => setFormData(prev => ({
                          ...prev,
                          type: e.target.value as any
                        }))}
                        className="sr-only"
                      />
                      <div className="text-xl mb-1">{option.icon}</div>
                      <div className="text-sm font-medium">{option.label}</div>
                    </label>
                  ))}
                </div>
              </FormSection>

              {/* Reason */}
              <FormSection>
                <FormLabel required>請假原因</FormLabel>
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
              {(formData.reason === 'other' || formData.description) && (
                <FormSection>
                  <FormLabel>詳細說明 {formData.reason === 'other' ? '(必填)' : '(可選)'}</FormLabel>
                  <Textarea
                    value={formData.description}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      description: e.target.value
                    }))}
                    placeholder="請簡要說明情況"
                    maxLength={200}
                    required={formData.reason === 'other'}
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    {formData.description.length}/200 字元
                  </p>
                </FormSection>
              )}

              {/* Emergency Contact */}
              <details className="mt-4">
                <summary className="cursor-pointer text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100">
                  進階選項（可選）
                </summary>
                <div className="mt-3">
                  <FormSection>
                    <FormLabel>緊急聯絡方式</FormLabel>
                    <Input
                      type="tel"
                      value={formData.emergencyContact}
                      onChange={(e) => setFormData(prev => ({
                        ...prev,
                        emergencyContact: e.target.value
                      }))}
                      placeholder="手機號碼（可選）"
                    />
                  </FormSection>
                </div>
              </details>

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
                      <span>提交中...</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-2">
                      <span>📤</span>
                      <span>提交申請</span>
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

export default LeavePage