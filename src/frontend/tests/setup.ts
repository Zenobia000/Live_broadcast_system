import { expect, afterEach } from 'vitest'
import { cleanup } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'

// Cleanup after each test case
afterEach(() => {
  cleanup()
})

// Mock environment variables
Object.assign(process.env, {
  VITE_API_BASE_URL: 'http://localhost:8000',
  VITE_GOOGLE_CLIENT_ID: 'test-google-client-id',
  VITE_APP_NAME: '智能簽到系統',
  VITE_APP_VERSION: '1.0.0'
})

// Mock window.google for OAuth tests
Object.defineProperty(window, 'google', {
  value: {
    accounts: {
      oauth2: {
        initTokenClient: vi.fn().mockReturnValue({
          requestAccessToken: vi.fn()
        })
      }
    }
  },
  writable: true
})

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
  length: 0,
  key: vi.fn()
}

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
})

// Mock fetch for API calls
global.fetch = vi.fn()

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn()
}))

// Mock ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn()
}))

// Mock scrollIntoView
Element.prototype.scrollIntoView = vi.fn()

// Mock window.confirm and window.prompt for interactive tests
window.confirm = vi.fn().mockReturnValue(true)
window.prompt = vi.fn().mockReturnValue('test input')

// Setup console error suppression for expected errors in tests
const originalConsoleError = console.error
beforeEach(() => {
  console.error = vi.fn()
})

afterEach(() => {
  console.error = originalConsoleError
})