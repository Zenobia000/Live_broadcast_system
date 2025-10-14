import React from 'react'

export interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  color?: 'blue' | 'white' | 'gray' | 'green'
  className?: string
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  color = 'blue',
  className = ''
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12'
  }

  const colorClasses = {
    blue: 'text-blue-600',
    white: 'text-white',
    gray: 'text-gray-600',
    green: 'text-green-600'
  }

  return (
    <div
      className={`
        inline-block animate-spin rounded-full border-2 border-solid
        border-current border-r-transparent
        ${sizeClasses[size]} ${colorClasses[color]} ${className}
      `}
      role="status"
      aria-label="Loading"
    >
      <span className="sr-only">Loading...</span>
    </div>
  )
}

// Loading Overlay Component
export interface LoadingOverlayProps {
  isVisible: boolean
  message?: string
  className?: string
  children?: React.ReactNode
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  isVisible,
  message = 'Loading...',
  className = '',
  children
}) => {
  if (!isVisible) return <>{children}</>

  return (
    <div className="relative">
      {/* Content with overlay */}
      <div className={isVisible ? 'opacity-50 pointer-events-none' : ''}>
        {children}
      </div>

      {/* Overlay */}
      {isVisible && (
        <div
          className={`
            absolute inset-0 z-50
            flex items-center justify-center
            bg-white/80 dark:bg-gray-900/80
            backdrop-blur-sm
            ${className}
          `}
        >
          <div className="text-center">
            <LoadingSpinner size="lg" />
            {message && (
              <p className="mt-3 text-sm text-gray-600 dark:text-gray-400">
                {message}
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

// Page Loading Component (Full Screen)
export interface PageLoadingProps {
  message?: string
}

export const PageLoading: React.FC<PageLoadingProps> = ({
  message = 'Loading...'
}) => {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-white dark:bg-gray-900">
      <div className="text-center">
        <LoadingSpinner size="xl" />
        <p className="mt-4 text-lg text-gray-600 dark:text-gray-400">
          {message}
        </p>
      </div>
    </div>
  )
}

// Button Loading State (inline with text)
export interface ButtonLoadingProps {
  isLoading: boolean
  children: React.ReactNode
}

export const ButtonLoading: React.FC<ButtonLoadingProps> = ({
  isLoading,
  children
}) => {
  if (!isLoading) return <>{children}</>

  return (
    <span className="flex items-center gap-2">
      <LoadingSpinner size="sm" color="white" />
      {children}
    </span>
  )
}

// Skeleton Loading Component
export interface SkeletonProps {
  width?: string | number
  height?: string | number
  rounded?: boolean
  className?: string
}

export const Skeleton: React.FC<SkeletonProps> = ({
  width = '100%',
  height = '1rem',
  rounded = false,
  className = ''
}) => {
  const widthStyle = typeof width === 'number' ? `${width}px` : width
  const heightStyle = typeof height === 'number' ? `${height}px` : height

  return (
    <div
      className={`
        animate-pulse bg-gray-200 dark:bg-gray-700
        ${rounded ? 'rounded-full' : 'rounded'}
        ${className}
      `}
      style={{
        width: widthStyle,
        height: heightStyle
      }}
      aria-label="Loading content"
    />
  )
}

// Card Skeleton (for dashboard cards)
export const CardSkeleton: React.FC = () => {
  return (
    <div className="p-6 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
      <div className="animate-pulse">
        <div className="flex items-center space-x-4">
          <Skeleton width={48} height={48} rounded />
          <div className="flex-1 space-y-2">
            <Skeleton height={20} width="60%" />
            <Skeleton height={16} width="40%" />
          </div>
        </div>
        <div className="mt-4 space-y-3">
          <Skeleton height={16} />
          <Skeleton height={16} width="80%" />
        </div>
      </div>
    </div>
  )
}

// List Skeleton (for history items)
export const ListSkeleton: React.FC<{ items?: number }> = ({ items = 3 }) => {
  return (
    <div className="space-y-3">
      {Array.from({ length: items }).map((_, index) => (
        <div key={index} className="flex items-center space-x-3 p-3">
          <Skeleton width={10} height={10} rounded />
          <div className="flex-1 space-y-2">
            <Skeleton height={16} width="30%" />
            <Skeleton height={14} width="60%" />
          </div>
          <Skeleton width={60} height={20} rounded />
        </div>
      ))}
    </div>
  )
}

export default LoadingSpinner