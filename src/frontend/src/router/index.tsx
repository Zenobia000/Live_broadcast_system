import React, { Suspense } from 'react'
import { createBrowserRouter, Navigate } from 'react-router-dom'
import { PageLoading } from '../components'

// Lazy load pages for better performance
const LoginPage = React.lazy(() => import('../pages/LoginPage'))
const RegisterPage = React.lazy(() => import('../pages/RegisterPage'))
const AuthCallbackPage = React.lazy(() => import('../pages/AuthCallbackPage'))
const DashboardPage = React.lazy(() => import('../pages/DashboardPage'))
const LeavePage = React.lazy(() => import('../pages/LeavePage'))
const MakeupPage = React.lazy(() => import('../pages/MakeupPage'))
const AdminPage = React.lazy(() => import('../pages/AdminPage'))
const AttendanceManagementPage = React.lazy(() => import('../pages/AttendanceManagementPage'))
const CreateEventPage = React.lazy(() => import('../pages/CreateEventPage'))
const ProfilePage = React.lazy(() => import('../pages/ProfilePage'))
const StatusPage = React.lazy(() => import('../pages/StatusPage'))

// Layout Component with Suspense
const PageLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <Suspense fallback={<PageLoading message="Loading page..." />}>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        {children}
      </div>
    </Suspense>
  )
}

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const isAuthenticated = localStorage.getItem('authToken') !== null

  if (!isAuthenticated) {
    return <Navigate to="/" replace />
  }

  return <PageLayout>{children}</PageLayout>
}

// Admin Route Component
const AdminRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const userRole = localStorage.getItem('userRole')

  if (userRole !== 'admin') {
    return <Navigate to="/dashboard" replace />
  }

  return <ProtectedRoute>{children}</ProtectedRoute>
}

// Public Route Component (only for unauthenticated users)
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const isAuthenticated = localStorage.getItem('authToken') !== null

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }

  return <PageLayout>{children}</PageLayout>
}

// Router Configuration
export const router = createBrowserRouter([
  {
    path: '/',
    element: (
      <PublicRoute>
        <LoginPage />
      </PublicRoute>
    ),
  },
  {
    path: '/register',
    element: (
      <PublicRoute>
        <RegisterPage />
      </PublicRoute>
    ),
  },
  {
    path: '/auth/callback',
    element: (
      <PageLayout>
        <AuthCallbackPage />
      </PageLayout>
    ),
  },
  {
    path: '/dashboard',
    element: (
      <ProtectedRoute>
        <DashboardPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/leave',
    element: (
      <ProtectedRoute>
        <LeavePage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/makeup',
    element: (
      <ProtectedRoute>
        <MakeupPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/admin',
    element: (
      <AdminRoute>
        <AdminPage />
      </AdminRoute>
    ),
  },
  {
    path: '/admin/attendance',
    element: (
      <AdminRoute>
        <AttendanceManagementPage />
      </AdminRoute>
    ),
  },
  {
    path: '/create-event',
    element: (
      <ProtectedRoute>
        <CreateEventPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/profile',
    element: (
      <ProtectedRoute>
        <ProfilePage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/status',
    element: (
      <ProtectedRoute>
        <StatusPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '*',
    element: <Navigate to="/dashboard" replace />,
  },
])

export default router