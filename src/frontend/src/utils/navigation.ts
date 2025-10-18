import { showToast } from '../components'

// Navigation Manager Class
export class NavigationManager {
  private static instance: NavigationManager
  private history: NavigationHistoryItem[] = []
  private currentPage: string
  private userRole: string

  constructor() {
    this.currentPage = this.getCurrentPage()
    this.userRole = this.getUserRole()
    this.loadHistory()
  }

  static getInstance(): NavigationManager {
    if (!NavigationManager.instance) {
      NavigationManager.instance = new NavigationManager()
    }
    return NavigationManager.instance
  }

  // Get current page from URL
  getCurrentPage(): string {
    const path = window.location.pathname
    return path === '/' ? 'login' : path.slice(1).split('/')[0]
  }

  // Get user role from localStorage
  getUserRole(): string {
    return localStorage.getItem('userRole') || 'user'
  }

  // Check if user has required permission
  hasPermission(requiredRole: 'user' | 'admin' = 'user'): boolean {
    const roleHierarchy = ['user', 'admin']
    const userRoleIndex = roleHierarchy.indexOf(this.userRole)
    const requiredRoleIndex = roleHierarchy.indexOf(requiredRole)
    return userRoleIndex >= requiredRoleIndex
  }

  // Safe navigation with permission and data validation
  safeNavigate(targetPath: string, options: NavigationOptions = {}): boolean {
    const { requiredRole = 'user', fallback = '/dashboard' } = options

    // Check user permissions
    if (!this.hasPermission(requiredRole)) {
      this.showAccessDenied()
      return false
    }

    // Validate required parameters
    if (targetPath.includes('status') && !this.getURLParam('id')) {
      showToast({
        type: 'warning',
        message: '缺少必要參數，將返回儀表板',
        autoClose: 3000
      })
      this.navigateWithFallback(fallback)
      return false
    }

    if (targetPath.includes('makeup') && !this.getURLParam('date')) {
      showToast({
        type: 'warning',
        message: '請先選擇要補簽的日期',
        action: {
          text: '返回儀表板',
          handler: () => this.navigateWithFallback('/dashboard')
        }
      })
      return false
    }

    // Record navigation history
    this.recordNavigation(this.currentPage, targetPath)

    // Execute navigation
    const fullPath = targetPath.startsWith('/') ? targetPath : `/${targetPath}`
    window.location.href = fullPath
    return true
  }

  // Navigate with transition animation
  async navigateWithTransition(targetURL: string): Promise<void> {
    try {
      // Add fade out animation
      document.body.classList.add('page-transition-out')

      // Wait for animation
      await new Promise(resolve => setTimeout(resolve, 200))

      // Navigate
      window.location.href = targetURL
    } catch (error) {
      console.error('Navigation transition failed:', error)
      // Fallback to normal navigation
      window.location.href = targetURL
    }
  }

  // Smart back navigation
  goBack(): void {
    // Simple back navigation without permission checks
    // Permission checks should only be for initial page load, not navigation
    if (window.history.length > 1) {
      window.history.back()
    } else {
      window.location.href = '/dashboard'
    }
  }

  // Get URL parameter
  private getURLParam(paramName: string): string | null {
    const urlParams = new URLSearchParams(window.location.search)
    return urlParams.get(paramName)
  }

  // Navigate with fallback
  private navigateWithFallback(fallbackPath: string): void {
    setTimeout(() => {
      window.location.href = fallbackPath
    }, 2000)
  }

  // Show access denied message
  private showAccessDenied(): void {
    showToast({
      type: 'error',
      message: '您沒有權限訪問此頁面',
      action: {
        text: '返回儀表板',
        handler: () => this.navigateWithFallback('/dashboard')
      }
    })
  }

  // Record navigation in history
  private recordNavigation(from: string, to: string, data: Record<string, any> = {}): void {
    const navigationItem: NavigationHistoryItem = {
      from,
      to,
      timestamp: Date.now(),
      data
    }

    this.history.push(navigationItem)

    // Keep only last 50 records
    if (this.history.length > 50) {
      this.history.shift()
    }

    this.saveHistory()
  }

  // Get last valid page from history
  private getLastValidPage(): string | null {
    for (let i = this.history.length - 1; i >= 0; i--) {
      const item = this.history[i]
      if (item.from !== this.currentPage && this.isValidPage(item.from)) {
        return item.from
      }
    }
    return null
  }

  // Check if page is valid for navigation
  private isValidPage(page: string): boolean {
    const validPages = ['dashboard', 'leave', 'makeup', 'admin', 'profile', 'status']
    return validPages.includes(page)
  }

  // Load navigation history from localStorage
  private loadHistory(): void {
    try {
      const savedHistory = localStorage.getItem('nav_history')
      if (savedHistory) {
        this.history = JSON.parse(savedHistory)
      }
    } catch (error) {
      console.warn('Failed to load navigation history:', error)
      this.history = []
    }
  }

  // Save navigation history to localStorage
  private saveHistory(): void {
    try {
      localStorage.setItem('nav_history', JSON.stringify(this.history))
    } catch (error) {
      console.warn('Failed to save navigation history:', error)
    }
  }
}

// Types
interface NavigationHistoryItem {
  from: string
  to: string
  timestamp: number
  data: Record<string, any>
}

interface NavigationOptions {
  requiredRole?: 'user' | 'admin'
  fallback?: string
}

// Smart URL Generator
export class SmartURLGenerator {
  // Generate leave application URL with smart date selection
  static generateLeaveURL(preferredDate?: string): string {
    if (preferredDate) {
      return `/leave?date=${preferredDate}`
    }

    // Smart selection of next workday
    const nextWorkday = this.getNextWorkday()
    return `/leave?date=${nextWorkday}`
  }

  // Generate makeup application URL
  static generateMakeupURL(missedDate: string): string {
    if (!missedDate) {
      throw new Error('補簽申請必須指定日期')
    }
    return `/makeup?date=${missedDate}`
  }

  // Generate status query URL
  static generateStatusURL(type: 'leave' | 'makeup', requestId: string): string {
    return `/status?type=${type}&id=${requestId}`
  }

  // Generate dashboard URL with section anchor
  static generateDashboardURL(section?: 'today' | 'history'): string {
    return section ? `/dashboard#${section}` : '/dashboard'
  }

  // Get next workday (skip weekends)
  private static getNextWorkday(): string {
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)

    // Skip weekends
    while (tomorrow.getDay() === 0 || tomorrow.getDay() === 6) {
      tomorrow.setDate(tomorrow.getDate() + 1)
    }

    return tomorrow.toISOString().split('T')[0]
  }
}

// URL Validator
export class URLValidator {
  // Validate status page URL
  static validateStatusURL(): boolean {
    const params = new URLSearchParams(window.location.search)
    const type = params.get('type')
    const id = params.get('id')

    if (!type || !['leave', 'makeup'].includes(type)) {
      this.handleInvalidType()
      return false
    }

    if (!id || !/^\d+$/.test(id)) {
      this.handleInvalidId()
      return false
    }

    return true
  }

  // Validate makeup application URL
  static validateMakeupURL(): boolean {
    const params = new URLSearchParams(window.location.search)
    const date = params.get('date')

    if (!date) {
      this.handleMissingDate()
      return false
    }

    // Check date format YYYY-MM-DD
    if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) {
      this.handleInvalidDateFormat()
      return false
    }

    // Check if it's a future date
    if (new Date(date) >= new Date()) {
      this.handleFutureDate()
      return false
    }

    return true
  }

  // Error handlers
  private static handleInvalidType(): void {
    showToast({
      type: 'error',
      message: '無效的申請類型',
      autoClose: 3000
    })
    setTimeout(() => {
      window.location.href = '/dashboard'
    }, 3000)
  }

  private static handleInvalidId(): void {
    showToast({
      type: 'error',
      message: '申請ID無效，將為您返回儀表板',
      autoClose: 3000
    })
    setTimeout(() => {
      window.location.href = '/dashboard'
    }, 3000)
  }

  private static handleMissingDate(): void {
    showToast({
      type: 'warning',
      message: '請先選擇要補簽的日期',
      action: {
        text: '返回儀表板',
        handler: () => window.location.href = '/dashboard'
      }
    })
  }

  private static handleInvalidDateFormat(): void {
    showToast({
      type: 'error',
      message: '日期格式無效',
      autoClose: 3000
    })
    setTimeout(() => {
      window.location.href = '/dashboard'
    }, 3000)
  }

  private static handleFutureDate(): void {
    showToast({
      type: 'info',
      message: '無法補簽未來日期，請選擇過去的日期',
      action: {
        text: '重新選擇',
        handler: () => window.location.href = '/dashboard'
      }
    })
  }
}

// Global navigation manager instance
export const navManager = NavigationManager.getInstance()

// Convenience functions
export const safeNavigate = (path: string, options?: NavigationOptions) =>
  navManager.safeNavigate(path, options)

export const goBack = () => navManager.goBack()

export default NavigationManager