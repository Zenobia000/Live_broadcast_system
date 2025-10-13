import React, { useState } from 'react'
import {
  Button,
  Card,
  CardHeader,
  CardBody,
  CardFooter,
  Input,
  Badge,
  StatusBadge,
} from '@components'

const ComponentShowcase: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [inputValue, setInputValue] = useState('')

  const handleLoadingDemo = () => {
    setLoading(true)
    setTimeout(() => setLoading(false), 2000)
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            🎨 Apple-Style UI Components
          </h1>
          <p className="text-lg text-gray-600">
            智能簽到系統 - 組件展示與測試
          </p>
        </div>

        {/* Buttons Section */}
        <Card className="mb-8">
          <CardHeader>
            <h2 className="text-2xl font-semibold text-gray-900">按鈕 (Buttons)</h2>
            <p className="text-sm text-gray-600 mt-1">多種變體和尺寸的按鈕組件</p>
          </CardHeader>
          <CardBody>
            <div className="space-y-6">
              {/* Variants */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-3">變體 (Variants)</h3>
                <div className="flex flex-wrap gap-3">
                  <Button variant="primary">Primary</Button>
                  <Button variant="secondary">Secondary</Button>
                  <Button variant="success">Success</Button>
                  <Button variant="warning">Warning</Button>
                  <Button variant="error">Error</Button>
                  <Button variant="ghost">Ghost</Button>
                </div>
              </div>

              {/* Sizes */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-3">尺寸 (Sizes)</h3>
                <div className="flex items-center gap-3">
                  <Button size="sm">Small</Button>
                  <Button size="md">Medium</Button>
                  <Button size="lg">Large</Button>
                </div>
              </div>

              {/* States */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-3">狀態 (States)</h3>
                <div className="flex flex-wrap gap-3">
                  <Button>Normal</Button>
                  <Button disabled>Disabled</Button>
                  <Button loading={loading} onClick={handleLoadingDemo}>
                    {loading ? 'Loading...' : 'Click to Load'}
                  </Button>
                  <Button fullWidth className="max-w-xs">Full Width</Button>
                </div>
              </div>
            </div>
          </CardBody>
        </Card>

        {/* Cards Section */}
        <Card className="mb-8">
          <CardHeader>
            <h2 className="text-2xl font-semibold text-gray-900">卡片 (Cards)</h2>
            <p className="text-sm text-gray-600 mt-1">靈活的容器組件，支援懸停效果</p>
          </CardHeader>
          <CardBody>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">基礎卡片</h3>
                <p className="text-gray-600">簡單的卡片容器，適合展示內容。</p>
              </Card>

              <Card hover className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">懸停效果</h3>
                <p className="text-gray-600">滑鼠懸停時會有陰影和位移動畫。</p>
              </Card>

              <Card hover className="cursor-pointer">
                <CardHeader>
                  <h3 className="text-lg font-semibold text-gray-900">完整結構</h3>
                </CardHeader>
                <CardBody>
                  <p className="text-gray-600">包含 Header、Body 和 Footer 的完整卡片。</p>
                </CardBody>
                <CardFooter>
                  <Button size="sm" variant="primary">操作</Button>
                </CardFooter>
              </Card>
            </div>
          </CardBody>
        </Card>

        {/* Inputs Section */}
        <Card className="mb-8">
          <CardHeader>
            <h2 className="text-2xl font-semibold text-gray-900">輸入欄位 (Inputs)</h2>
            <p className="text-sm text-gray-600 mt-1">帶標籤、錯誤提示和圖標的輸入組件</p>
          </CardHeader>
          <CardBody>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Input
                label="基礎輸入"
                placeholder="請輸入文字..."
                helperText="這是輔助說明文字"
              />

              <Input
                label="帶圖標輸入"
                placeholder="搜尋..."
                leftIcon={
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                }
              />

              <Input
                label="錯誤狀態"
                placeholder="example@email.com"
                error="請輸入有效的電子郵件地址"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
              />

              <Input
                label="禁用狀態"
                placeholder="無法輸入"
                disabled
                value="Disabled Input"
              />
            </div>
          </CardBody>
        </Card>

        {/* Badges Section */}
        <Card className="mb-8">
          <CardHeader>
            <h2 className="text-2xl font-semibold text-gray-900">徽章 (Badges)</h2>
            <p className="text-sm text-gray-600 mt-1">用於狀態標識和分類標籤</p>
          </CardHeader>
          <CardBody>
            <div className="space-y-6">
              {/* Basic Badges */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-3">基礎徽章</h3>
                <div className="flex flex-wrap gap-3">
                  <Badge variant="default">Default</Badge>
                  <Badge variant="primary">Primary</Badge>
                  <Badge variant="success">Success</Badge>
                  <Badge variant="warning">Warning</Badge>
                  <Badge variant="error">Error</Badge>
                  <Badge variant="info">Info</Badge>
                </div>
              </div>

              {/* Dot Badges */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-3">帶圓點徽章</h3>
                <div className="flex flex-wrap gap-3">
                  <Badge variant="success" dot>線上</Badge>
                  <Badge variant="warning" dot>忙碌</Badge>
                  <Badge variant="error" dot>離線</Badge>
                </div>
              </div>

              {/* Status Badges (Attendance System Specific) */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-3">出勤狀態徽章</h3>
                <div className="flex flex-wrap gap-3">
                  <StatusBadge status="PRESENT" />
                  <StatusBadge status="LATE" />
                  <StatusBadge status="ABSENT" />
                  <StatusBadge status="LEAVE" />
                  <StatusBadge status="MAKEUP" />
                  <StatusBadge status="EARLY_LEAVE" />
                </div>
              </div>

              {/* Request Status Badges */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-3">申請狀態徽章</h3>
                <div className="flex flex-wrap gap-3">
                  <StatusBadge status="PENDING" />
                  <StatusBadge status="APPROVED" />
                  <StatusBadge status="REJECTED" />
                </div>
              </div>

              {/* Badge Sizes */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-3">徽章尺寸</h3>
                <div className="flex items-center gap-3">
                  <Badge variant="primary" size="sm">Small</Badge>
                  <Badge variant="primary" size="md">Medium</Badge>
                  <Badge variant="primary" size="lg">Large</Badge>
                </div>
              </div>
            </div>
          </CardBody>
        </Card>

        {/* Example Use Case */}
        <Card>
          <CardHeader>
            <h2 className="text-2xl font-semibold text-gray-900">實際應用範例</h2>
            <p className="text-sm text-gray-600 mt-1">簽到記錄卡片展示</p>
          </CardHeader>
          <CardBody>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Attendance Record Example 1 */}
              <Card hover className="p-4">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">團隊會議</h3>
                    <p className="text-sm text-gray-600">2025-10-14 14:00 - 15:00</p>
                  </div>
                  <StatusBadge status="PRESENT" />
                </div>
                <p className="text-sm text-gray-600 mb-3">
                  討論專案進度與下週規劃
                </p>
                <div className="flex items-center text-sm text-gray-500">
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  簽到時間: 13:58
                </div>
              </Card>

              {/* Attendance Record Example 2 */}
              <Card hover className="p-4">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">技術分享會</h3>
                    <p className="text-sm text-gray-600">2025-10-14 16:00 - 17:00</p>
                  </div>
                  <StatusBadge status="LATE" />
                </div>
                <p className="text-sm text-gray-600 mb-3">
                  前端架構設計分享
                </p>
                <div className="flex items-center text-sm text-warning">
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  簽到時間: 16:07
                </div>
              </Card>
            </div>
          </CardBody>
          <CardFooter>
            <div className="flex justify-between items-center">
              <p className="text-sm text-gray-600">顯示 2 筆記錄</p>
              <Button variant="primary">查看全部</Button>
            </div>
          </CardFooter>
        </Card>
      </div>
    </div>
  )
}

export default ComponentShowcase
