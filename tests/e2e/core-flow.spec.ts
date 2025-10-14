import { test, expect } from '@playwright/test'

test.describe('Core User Flow', () => {
  // Setup authenticated user before each test
  test.beforeEach(async ({ page }) => {
    // Mock authentication
    await page.addInitScript(() => {
      localStorage.setItem('authToken', 'mock-token')
      localStorage.setItem('userRole', 'user')
      localStorage.setItem('userProfile', JSON.stringify({
        id: 'user-123',
        name: 'Test User',
        email: 'test@example.com',
        avatar: 'https://example.com/avatar.jpg'
      }))
    })

    // Mock API responses
    await page.route('**/api/v1/attendance/today', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            isCheckedIn: true,
            checkInTime: '09:00',
            eventTitle: 'Daily Standup',
            status: 'present'
          }
        })
      })
    })

    await page.route('**/api/v1/attendance/history*', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: [
            {
              id: 'att-1',
              eventTitle: 'Daily Standup',
              status: 'present',
              checkedInAt: '2025-10-14T09:00:00Z',
              createdAt: '2025-10-14T09:00:00Z'
            },
            {
              id: 'att-2',
              eventTitle: 'Team Meeting',
              status: 'late',
              checkedInAt: '2025-10-13T10:05:00Z',
              createdAt: '2025-10-13T10:05:00Z'
            }
          ]
        })
      })
    })

    await page.route('**/api/v1/users/me', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            id: 'user-123',
            name: 'Test User',
            email: 'test@example.com',
            role: 'user'
          }
        })
      })
    })
  })

  test('should display dashboard correctly for authenticated user', async ({ page }) => {
    await page.goto('/dashboard')

    // Check greeting and user name
    await expect(page.getByText(/早安，Test User/)).toBeVisible()

    // Check today's status
    await expect(page.getByText('已簽到：Daily Standup')).toBeVisible()
    await expect(page.getByText('09:00')).toBeVisible()

    // Check quick actions
    await expect(page.getByRole('button', { name: /申請請假/ })).toBeVisible()
    await expect(page.getByRole('button', { name: /補簽申請/ })).toBeVisible()

    // Check recent history section
    await expect(page.getByText('最近記錄')).toBeVisible()
    await expect(page.getByText('Daily Standup')).toBeVisible()
    await expect(page.getByText('Team Meeting')).toBeVisible()
  })

  test('should navigate to leave application page', async ({ page }) => {
    await page.goto('/dashboard')

    // Click leave application button
    await page.click('text=申請請假')

    // Should navigate to leave page
    await expect(page).toHaveURL(/\/leave/)
    await expect(page.getByRole('heading', { name: '申請請假' })).toBeVisible()
  })

  test('complete leave application flow', async ({ page }) => {
    // Mock leave request submission
    await page.route('**/api/v1/requests/leave', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            id: 'leave-123',
            status: 'pending',
            startDate: '2025-10-15',
            endDate: '2025-10-15'
          }
        })
      })
    })

    await page.goto('/leave')

    // Fill out form
    await page.fill('input[type="date"][name="startDate"]', '2025-10-15')
    await page.fill('input[type="date"][name="endDate"]', '2025-10-15')

    // Select leave type
    await page.click('input[value="full-day"]')

    // Select reason
    await page.selectOption('select', { value: 'personal' })

    // Submit form
    await page.click('button[type="submit"]')

    // Should show success message
    await expect(page.getByText('申請已成功提交！')).toBeVisible()

    // Should redirect to status page
    await expect(page).toHaveURL(/\/status\?type=leave&id=leave-123/)
  })

  test('should handle navigation between pages', async ({ page }) => {
    await page.goto('/dashboard')

    // Navigate to profile
    await page.click('text=⚙️')  // Settings icon
    await expect(page).toHaveURL('/profile')
    await expect(page.getByRole('heading', { name: '個人設定' })).toBeVisible()

    // Navigate back to dashboard
    await page.click('text=← 返回')
    await expect(page).toHaveURL('/dashboard')

    // Navigate to leave page
    await page.click('text=申請請假')
    await expect(page).toHaveURL(/\/leave/)

    // Cancel back to dashboard
    await page.click('text=取消')
    await expect(page).toHaveURL('/dashboard')
  })

  test('should protect routes requiring authentication', async ({ page }) => {
    // Clear authentication
    await page.addInitScript(() => {
      localStorage.clear()
    })

    // Try to access protected route
    await page.goto('/dashboard')

    // Should redirect to login
    await expect(page).toHaveURL('/')
  })

  test('should handle offline mode gracefully', async ({ page }) => {
    await page.goto('/dashboard')

    // Simulate network failure
    await page.route('**/api/v1/**', route => route.abort())

    // Trigger API call (refresh button)
    await page.click('text=🔄')

    // Should show offline notification
    await expect(page.getByText(/網路連線中斷/)).toBeVisible()
  })

  test('should be responsive on mobile devices', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/dashboard')

    // Check mobile layout
    await expect(page.getByRole('heading', { name: /早安/ })).toBeVisible()

    // Quick actions should be stacked on mobile
    const quickActions = page.locator('.quick-actions')
    await expect(quickActions).toBeVisible()

    // Test touch interaction
    await page.tap('text=申請請假')
    await expect(page).toHaveURL(/\/leave/)
  })

  test('should handle dark mode correctly', async ({ page }) => {
    await page.goto('/dashboard')

    // Toggle dark mode (if implemented)
    await page.evaluate(() => {
      document.documentElement.classList.toggle('dark')
    })

    // Check that dark mode styles are applied
    const body = page.locator('body')
    await expect(body).toHaveClass(/dark:bg-gray-900/)
  })
})