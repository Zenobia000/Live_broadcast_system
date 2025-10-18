/**
 * AttendanceHeatmap Component
 *
 * GitHub-style contribution graph for attendance visualization
 * Shows last 12 weeks of attendance data in a heatmap format
 */

import React from 'react'

interface AttendanceData {
  date: string
  status: 'present' | 'late' | 'absent' | 'leave' | null
  count: number
}

interface AttendanceHeatmapProps {
  data: AttendanceData[]
  weeks?: number
}

const AttendanceHeatmap: React.FC<AttendanceHeatmapProps> = ({
  data,
  weeks = 12
}) => {
  const today = new Date()

  // Generate all dates for the last N weeks
  const generateDateGrid = () => {
    const grid: AttendanceData[][] = []
    const startDate = new Date(today)
    startDate.setDate(today.getDate() - (weeks * 7))

    // Adjust to start from Sunday
    const dayOfWeek = startDate.getDay()
    startDate.setDate(startDate.getDate() - dayOfWeek)

    let currentWeek: AttendanceData[] = []
    const currentDate = new Date(startDate)

    while (currentDate <= today) {
      const dateStr = currentDate.toISOString().split('T')[0]
      const attendanceRecord = data.find(d => d.date === dateStr)

      currentWeek.push({
        date: dateStr,
        status: attendanceRecord?.status || null,
        count: attendanceRecord?.count || 0
      })

      // New week starts on Sunday
      if (currentWeek.length === 7) {
        grid.push(currentWeek)
        currentWeek = []
      }

      currentDate.setDate(currentDate.getDate() + 1)
    }

    // Add remaining days
    if (currentWeek.length > 0) {
      while (currentWeek.length < 7) {
        currentWeek.push({
          date: '',
          status: null,
          count: 0
        })
      }
      grid.push(currentWeek)
    }

    return grid
  }

  const grid = generateDateGrid()

  // Color scheme based on status
  const getColor = (status: AttendanceData['status'], count: number) => {
    if (!status || count === 0) {
      return 'bg-gray-100 dark:bg-gray-800'
    }

    switch (status) {
      case 'present':
        // Green shades for present
        if (count === 1) return 'bg-green-200 dark:bg-green-900'
        if (count === 2) return 'bg-green-400 dark:bg-green-700'
        return 'bg-green-600 dark:bg-green-600'
      case 'late':
        // Yellow/orange for late
        return 'bg-yellow-400 dark:bg-yellow-600'
      case 'absent':
        // Red for absent
        return 'bg-red-400 dark:bg-red-600'
      case 'leave':
        // Blue for leave
        return 'bg-blue-300 dark:bg-blue-700'
      default:
        return 'bg-gray-100 dark:bg-gray-800'
    }
  }

  const getTooltipText = (cell: AttendanceData) => {
    if (!cell.date) return ''

    const date = new Date(cell.date)
    const dateStr = date.toLocaleDateString('zh-TW', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })

    if (!cell.status) {
      return `${dateStr}\n無記錄`
    }

    const statusMap = {
      present: '✅ 出席',
      late: '⏰ 遲到',
      absent: '❌ 缺席',
      leave: '🏖️ 請假'
    }

    return `${dateStr}\n${statusMap[cell.status]}${cell.count > 1 ? ` (${cell.count}次)` : ''}`
  }

  const dayLabels = ['日', '一', '二', '三', '四', '五', '六']

  // Calculate statistics
  const stats = data.reduce((acc, curr) => {
    if (curr.status === 'present') acc.present += curr.count
    if (curr.status === 'late') acc.late += curr.count
    if (curr.status === 'absent') acc.absent += curr.count
    if (curr.status === 'leave') acc.leave += curr.count
    return acc
  }, { present: 0, late: 0, absent: 0, leave: 0 })

  const totalDays = stats.present + stats.late + stats.absent + stats.leave
  const attendanceRate = totalDays > 0
    ? ((stats.present + stats.late) / totalDays * 100).toFixed(1)
    : '0.0'

  return (
    <div className="space-y-4">
      {/* Statistics Summary */}
      <div className="grid grid-cols-4 gap-3">
        <div className="text-center p-2 bg-green-50 dark:bg-green-900/20 rounded-lg">
          <div className="text-2xl font-bold text-green-600 dark:text-green-400">
            {stats.present}
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400">出席</div>
        </div>
        <div className="text-center p-2 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
          <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
            {stats.late}
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400">遲到</div>
        </div>
        <div className="text-center p-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
            {stats.leave}
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400">請假</div>
        </div>
        <div className="text-center p-2 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <div className="text-2xl font-bold text-gray-900 dark:text-white">
            {attendanceRate}%
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400">出席率</div>
        </div>
      </div>

      {/* Heatmap */}
      <div className="overflow-x-auto">
        <div className="inline-block min-w-full">
          <div className="flex gap-1">
            {/* Day labels */}
            <div className="flex flex-col gap-1 pr-2">
              <div className="h-3"></div>
              {dayLabels.map((day, i) => (
                <div
                  key={i}
                  className="h-3 text-xs text-gray-500 dark:text-gray-400 flex items-center"
                  style={{ minWidth: '16px' }}
                >
                  {day}
                </div>
              ))}
            </div>

            {/* Heatmap grid */}
            <div className="flex gap-1">
              {grid.map((week, weekIndex) => (
                <div key={weekIndex} className="flex flex-col gap-1">
                  {/* Month label (show on first day of month) */}
                  <div className="h-3 text-xs text-gray-500 dark:text-gray-400">
                    {week[0].date && new Date(week[0].date).getDate() <= 7
                      ? new Date(week[0].date).toLocaleDateString('zh-TW', { month: 'short' })
                      : ''
                    }
                  </div>

                  {week.map((cell, dayIndex) => (
                    <div
                      key={dayIndex}
                      className={`
                        w-3 h-3 rounded-sm
                        ${getColor(cell.status, cell.count)}
                        ${cell.date ? 'cursor-pointer hover:ring-2 hover:ring-blue-400' : ''}
                        transition-all
                      `}
                      title={getTooltipText(cell)}
                    />
                  ))}
                </div>
              ))}
            </div>
          </div>

          {/* Legend */}
          <div className="mt-4 flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
            <span>最近 {weeks} 週</span>
            <div className="flex items-center gap-2">
              <span>少</span>
              <div className="flex gap-1">
                <div className="w-3 h-3 bg-gray-100 dark:bg-gray-800 rounded-sm" />
                <div className="w-3 h-3 bg-green-200 dark:bg-green-900 rounded-sm" />
                <div className="w-3 h-3 bg-green-400 dark:bg-green-700 rounded-sm" />
                <div className="w-3 h-3 bg-green-600 dark:bg-green-600 rounded-sm" />
              </div>
              <span>多</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AttendanceHeatmap
