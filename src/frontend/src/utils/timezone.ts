/**
 * Timezone Utilities for Taiwan (UTC+8)
 *
 * Design Philosophy:
 * - All times displayed to users are in Taipei timezone (UTC+8)
 * - All times sent to backend are in UTC
 * - Backend stores all times in UTC with timezone awareness
 * - Backend returns times already converted to Taipei timezone
 */

const TAIPEI_OFFSET_HOURS = 8

/**
 * Convert local datetime input (YYYY-MM-DD HH:mm) to UTC ISO string for API
 * User input is assumed to be in Taipei timezone (UTC+8)
 */
export function localToUTC(dateString: string, timeString: string): string {
  // Create a date object from the local input
  const localDateTime = new Date(`${dateString}T${timeString}:00`)

  // Subtract 8 hours to convert Taipei time to UTC
  const utcDateTime = new Date(localDateTime.getTime() - TAIPEI_OFFSET_HOURS * 60 * 60 * 1000)

  return utcDateTime.toISOString()
}

/**
 * Convert UTC ISO string to Taipei local datetime
 * Used when displaying times from backend
 */
export function utcToLocal(utcString: string): Date {
  const utcDate = new Date(utcString)

  // Add 8 hours to convert UTC to Taipei time
  return new Date(utcDate.getTime() + TAIPEI_OFFSET_HOURS * 60 * 60 * 1000)
}

/**
 * Format datetime to Taipei timezone display string
 */
export function formatTaipeiDateTime(date: Date | string): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date

  return dateObj.toLocaleString('zh-TW', {
    timeZone: 'Asia/Taipei',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  })
}

/**
 * Format time only (HH:mm) in Taipei timezone
 */
export function formatTaipeiTime(date: Date | string): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date

  return dateObj.toLocaleTimeString('zh-TW', {
    timeZone: 'Asia/Taipei',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  })
}

/**
 * Format date only (YYYY-MM-DD) in Taipei timezone
 */
export function formatTaipeiDate(date: Date | string): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date

  return dateObj.toLocaleDateString('zh-TW', {
    timeZone: 'Asia/Taipei',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

/**
 * Get current Taipei time as Date object
 */
export function getTaipeiNow(): Date {
  const now = new Date()
  // JavaScript Date is already in local timezone
  // Just ensure we're working with Taipei time
  return now
}

/**
 * Get tomorrow's date in YYYY-MM-DD format (Taipei timezone)
 */
export function getTomorrowDate(): string {
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  return tomorrow.toISOString().split('T')[0]
}

/**
 * Validate that end time is after start time
 */
export function isEndTimeAfterStart(
  startDate: string,
  startTime: string,
  endDate: string,
  endTime: string
): boolean {
  const start = new Date(`${startDate}T${startTime}:00`)
  const end = new Date(`${endDate}T${endTime}:00`)
  return end > start
}
