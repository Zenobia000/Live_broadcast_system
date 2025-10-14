import { test, expect } from '@playwright/test'

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Mock Google OAuth for testing
    await page.addInitScript(() => {
      window.google = {
        accounts: {
          oauth2: {
            initTokenClient: () => ({
              requestAccessToken: () => {
                // Simulate successful OAuth
                const callback = window.google?.mockCallback
                if (callback) {
                  callback({ access_token: 'mock-token' })
                }
              }
            })
          }
        },
        mockCallback: null
      }
    })
  })

  test('should display login page correctly', async ({ page }) => {
    await page.goto('/')

    // Check page elements
    await expect(page.getByRole('heading', { name: '智能簽到系統' })).toBeVisible()
    await expect(page.getByText('讓簽到變成一種愉悅的儀式')).toBeVisible()
    await expect(page.getByRole('button', { name: /使用 Google 帳號登入/ })).toBeVisible()

    // Check feature highlights
    await expect(page.getByText('🤖')).toBeVisible()
    await expect(page.getByText('📅')).toBeVisible()
    await expect(page.getByText('⚡')).toBeVisible()
  })

  test('should handle Google OAuth login flow', async ({ page }) => {
    // Mock successful API response
    await page.route('**/api/v1/auth/google', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            token: 'mock-jwt-token',
            user: {
              id: 'user-123',
              email: 'test@example.com',
              name: 'Test User',
              role: 'user'
            }
          },
          is_new_user: false
        })
      })
    })

    await page.goto('/')

    // Click Google login button
    const loginButton = page.getByRole('button', { name: /使用 Google 帳號登入/ })
    await loginButton.click()

    // Should redirect to dashboard
    await expect(page).toHaveURL('/dashboard')
  })

  test('should redirect authenticated users from login page', async ({ page }) => {
    // Set up authenticated state
    await page.addInitScript(() => {
      localStorage.setItem('authToken', 'mock-token')
      localStorage.setItem('userRole', 'user')
      localStorage.setItem('userProfile', JSON.stringify({
        id: 'user-123',
        name: 'Test User',
        email: 'test@example.com'
      }))
    })

    await page.goto('/')

    // Should automatically redirect to dashboard
    await expect(page).toHaveURL('/dashboard')
  })

  test('should show loading state during authentication', async ({ page }) => {
    await page.goto('/')

    const loginButton = page.getByRole('button', { name: /使用 Google 帳號登入/ })

    // Mock slow response
    await page.route('**/api/v1/auth/google', async route => {
      await new Promise(resolve => setTimeout(resolve, 1000))
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true })
      })
    })

    await loginButton.click()

    // Should show loading state
    await expect(page.getByText('登入中...')).toBeVisible()
  })

  test('should handle authentication errors gracefully', async ({ page }) => {
    await page.route('**/api/v1/auth/google', async route => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'Invalid authorization code'
        })
      })
    })

    await page.goto('/')

    const loginButton = page.getByRole('button', { name: /使用 Google 帳號登入/ })
    await loginButton.click()

    // Should show error toast
    await expect(page.getByText(/登入失敗/)).toBeVisible()
  })
})