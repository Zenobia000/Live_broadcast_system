import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios'
import { showToast } from '../components'

// API Response Types
export interface ApiResponse<T = any> {
  success: boolean
  data: T
  message?: string
  error?: string
}

export interface User {
  id: string
  email: string
  name: string
  avatar?: string
  role: 'user' | 'admin'
  createdAt: string
  updatedAt: string
}

export interface AttendanceStatus {
  id: string
  userId: string
  eventId: string
  eventTitle: string
  status: 'present' | 'absent' | 'late'
  checkedInAt?: string
  createdAt: string
  updatedAt: string
}

export interface TodayStatus {
  isCheckedIn: boolean
  checkInTime?: string
  eventTitle?: string
  nextEventTime?: string
  status: 'present' | 'absent' | 'late' | 'waiting'
}

export interface LeaveRequest {
  id: string
  userId: string
  startDate: string
  endDate: string
  type: 'full-day' | 'morning' | 'afternoon'
  reason: string
  description?: string
  status: 'pending' | 'approved' | 'rejected'
  emergencyContact?: string
  reviewedBy?: string
  reviewedAt?: string
  createdAt: string
  updatedAt: string
}

export interface MakeupRequest {
  id: string
  userId: string
  missedDate: string
  reason: string
  description?: string
  status: 'pending' | 'approved' | 'rejected'
  reviewedBy?: string
  reviewedAt?: string
  createdAt: string
  updatedAt: string
}

// API Client Class
class ApiClient {
  private client: AxiosInstance
  private baseURL: string

  constructor() {
    this.baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

    this.client = axios.create({
      baseURL: `${this.baseURL}/api/v1`,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true,  // Enable cookies for OAuth session
    })

    this.setupInterceptors()
  }

  private setupInterceptors(): void {
    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('authToken')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        return response
      },
      (error: AxiosError) => {
        this.handleError(error)
        return Promise.reject(error)
      }
    )
  }

  private handleError(error: AxiosError): void {
    if (error.response && error.response.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('authToken')
      localStorage.removeItem('userRole')
      localStorage.removeItem('userProfile')

      showToast({
        type: 'warning',
        message: '登入已過期，請重新登入',
        autoClose: 3000
      })

      setTimeout(() => {
        window.location.href = '/'
      }, 3000)
    } else if (error.response && error.response.status === 403) {
      // Forbidden
      showToast({
        type: 'error',
        message: '您沒有權限執行此操作',
        autoClose: 5000
      })
    } else if (error.response && error.response.status >= 500) {
      // Server error
      showToast({
        type: 'error',
        message: '伺服器發生錯誤，請稍後再試',
        autoClose: 5000
      })
    } else if (error.code === 'ECONNABORTED') {
      // Timeout
      showToast({
        type: 'warning',
        message: '請求逾時，請檢查網路連線',
        autoClose: 5000
      })
    } else if (!navigator.onLine) {
      // Offline
      showToast({
        type: 'warning',
        message: '網路連線中斷，請檢查網路設定',
        autoClose: 5000
      })
    }
  }

  // Authentication APIs
  async getGoogleAuthUrl(): Promise<{ authorization_url: string; state: string }> {
    const response = await this.client.get('/auth/login/google')
    return response.data
  }

  async googleAuth(authCode: string): Promise<ApiResponse<{ token: string; user: User }>> {
    const response = await this.client.post('/auth/google', { code: authCode })
    return response.data
  }

  async logout(): Promise<void> {
    try {
      await this.client.post('/auth/logout')
    } catch (error) {
      // Continue with logout even if API call fails
      console.warn('Logout API call failed:', error)
    } finally {
      // Clear local storage
      localStorage.removeItem('authToken')
      localStorage.removeItem('userRole')
      localStorage.removeItem('userProfile')
      window.location.href = '/'
    }
  }

  // User APIs
  async getCurrentUser(): Promise<ApiResponse<User>> {
    const response = await this.client.get('/users/me')
    return response.data
  }

  async updateUserProfile(data: Partial<User>): Promise<ApiResponse<User>> {
    const response = await this.client.put('/users/me', data)
    return response.data
  }

  // Attendance APIs
  async getTodayStatus(): Promise<ApiResponse<TodayStatus>> {
    const response = await this.client.get('/attendance/today')
    return response.data
  }

  async getAttendanceHistory(limit = 10): Promise<ApiResponse<AttendanceStatus[]>> {
    const response = await this.client.get(`/attendance/history?limit=${limit}`)
    return response.data
  }

  async manualCheckIn(): Promise<ApiResponse<AttendanceStatus>> {
    const response = await this.client.post('/attendance/checkin')
    return response.data
  }

  async autoCheckInFromCalendar(): Promise<ApiResponse<{
    checked_in: boolean
    message: string
    event: {
      id: string
      title: string
      start_time: string
      end_time: string
    } | null
    attendance: {
      id: string
      status: string
      check_in_time: string
      is_late: boolean
      late_minutes: number
    } | null
  }>> {
    const response = await this.client.post('/attendance/auto-checkin-calendar')
    return response.data
  }

  // Calendar APIs
  async getCalendarEvents(daysAhead = 7): Promise<ApiResponse<{
    events: Array<{
      id: string
      title: string
      description?: string
      start_time: string
      end_time: string
      creator?: any
    }>
    total: number
  }>> {
    const response = await this.client.get(`/calendar/events?days_ahead=${daysAhead}`)
    return response.data
  }

  async getTodayCalendarEvents(): Promise<ApiResponse<{
    events: Array<{
      id: string
      title: string
      description?: string
      start_time: string
      end_time: string
    }>
    total: number
  }>> {
    const response = await this.client.get('/calendar/events/today')
    return response.data
  }

  async getCheckInStatus(): Promise<ApiResponse<{
    should_check_in: boolean
    current_event: {
      id: string
      title: string
      start_time: string
      end_time: string
    } | null
    message: string
  }>> {
    const response = await this.client.get('/calendar/check-in-status')
    return response.data
  }

  // Leave Request APIs
  async submitLeaveRequest(data: {
    startDate: string
    endDate: string
    type: 'full-day' | 'morning' | 'afternoon'
    reason: string
    description?: string
    emergencyContact?: string
  }): Promise<ApiResponse<LeaveRequest>> {
    const response = await this.client.post('/requests/leave', data)
    return response.data
  }

  async getLeaveRequests(status?: string): Promise<ApiResponse<LeaveRequest[]>> {
    const params = status ? { status } : {}
    const response = await this.client.get('/requests/leave', { params })
    return response.data
  }

  // Makeup Request APIs
  async submitMakeupRequest(data: {
    missedDate: string
    reason: string
    description?: string
  }): Promise<ApiResponse<MakeupRequest>> {
    const response = await this.client.post('/requests/makeup', data)
    return response.data
  }

  async getMakeupRequests(status?: string): Promise<ApiResponse<MakeupRequest[]>> {
    const params = status ? { status } : {}
    const response = await this.client.get('/requests/makeup', { params })
    return response.data
  }

  // Request Status APIs
  async getRequestById(id: string, type: 'leave' | 'makeup'): Promise<ApiResponse<LeaveRequest | MakeupRequest>> {
    const response = await this.client.get(`/requests/${type}/${id}`)
    return response.data
  }

  // Admin APIs
  async getPendingRequests(): Promise<ApiResponse<{
    leaveRequests: LeaveRequest[]
    makeupRequests: MakeupRequest[]
  }>> {
    const response = await this.client.get('/admin/requests/pending')
    return response.data
  }

  async reviewRequest(
    id: string,
    type: 'leave' | 'makeup',
    action: 'approve' | 'reject',
    comment?: string
  ): Promise<ApiResponse<LeaveRequest | MakeupRequest>> {
    const response = await this.client.put(`/admin/requests/${type}/${id}/review`, {
      action,
      comment
    })
    return response.data
  }

  // Health check
  async healthCheck(): Promise<ApiResponse<{ status: string; version: string }>> {
    const response = await this.client.get('/health')
    return response.data
  }
}

// Create singleton instance
export const apiClient = new ApiClient()

// Convenience functions
export const api = {
  // Auth
  getGoogleAuthUrl: () => apiClient.getGoogleAuthUrl(),
  googleAuth: (authCode: string) => apiClient.googleAuth(authCode),
  logout: () => apiClient.logout(),

  // User
  getCurrentUser: () => apiClient.getCurrentUser(),
  updateUserProfile: (data: Partial<User>) => apiClient.updateUserProfile(data),

  // Attendance
  getTodayStatus: () => apiClient.getTodayStatus(),
  getAttendanceHistory: (limit?: number) => apiClient.getAttendanceHistory(limit),
  manualCheckIn: () => apiClient.manualCheckIn(),
  autoCheckInFromCalendar: () => apiClient.autoCheckInFromCalendar(),

  // Calendar
  getCalendarEvents: (daysAhead?: number) => apiClient.getCalendarEvents(daysAhead),
  getTodayCalendarEvents: () => apiClient.getTodayCalendarEvents(),
  getCheckInStatus: () => apiClient.getCheckInStatus(),

  // Leave Requests
  submitLeaveRequest: (data: Parameters<typeof apiClient.submitLeaveRequest>[0]) =>
    apiClient.submitLeaveRequest(data),
  getLeaveRequests: (status?: string) => apiClient.getLeaveRequests(status),

  // Makeup Requests
  submitMakeupRequest: (data: Parameters<typeof apiClient.submitMakeupRequest>[0]) =>
    apiClient.submitMakeupRequest(data),
  getMakeupRequests: (status?: string) => apiClient.getMakeupRequests(status),

  // Request Status
  getRequestById: (id: string, type: 'leave' | 'makeup') =>
    apiClient.getRequestById(id, type),

  // Admin
  getPendingRequests: () => apiClient.getPendingRequests(),
  reviewRequest: (
    id: string,
    type: 'leave' | 'makeup',
    action: 'approve' | 'reject',
    comment?: string
  ) => apiClient.reviewRequest(id, type, action, comment),

  // Health
  healthCheck: () => apiClient.healthCheck(),
}

export default apiClient