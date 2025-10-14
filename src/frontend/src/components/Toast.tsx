import React, { useEffect, useState } from 'react'
import Button from './Button'

export type ToastType = 'info' | 'success' | 'warning' | 'error'

export interface ToastAction {
  text: string
  handler: () => void
}

export interface ToastProps {
  id: string
  type: ToastType
  message: string
  action?: ToastAction
  autoClose?: boolean | number
  onClose: (id: string) => void
}

export const Toast: React.FC<ToastProps> = ({
  id,
  type,
  message,
  action,
  autoClose = true,
  onClose
}) => {
  const [isVisible, setIsVisible] = useState(false)

  // Animation on mount
  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), 10)
    return () => clearTimeout(timer)
  }, [])

  // Auto close functionality
  useEffect(() => {
    if (autoClose === false) return

    const delay = typeof autoClose === 'number' ? autoClose : 5000
    const timer = setTimeout(() => {
      handleClose()
    }, delay)

    return () => clearTimeout(timer)
  }, [autoClose])

  const handleClose = () => {
    setIsVisible(false)
    // Wait for animation to complete before removing from DOM
    setTimeout(() => onClose(id), 300)
  }

  const typeStyles = {
    info: {
      bg: 'bg-blue-50 dark:bg-blue-900/20',
      border: 'border-blue-200 dark:border-blue-800',
      text: 'text-blue-800 dark:text-blue-200',
      icon: '🔵'
    },
    success: {
      bg: 'bg-green-50 dark:bg-green-900/20',
      border: 'border-green-200 dark:border-green-800',
      text: 'text-green-800 dark:text-green-200',
      icon: '✅'
    },
    warning: {
      bg: 'bg-yellow-50 dark:bg-yellow-900/20',
      border: 'border-yellow-200 dark:border-yellow-800',
      text: 'text-yellow-800 dark:text-yellow-200',
      icon: '⚠️'
    },
    error: {
      bg: 'bg-red-50 dark:bg-red-900/20',
      border: 'border-red-200 dark:border-red-800',
      text: 'text-red-800 dark:text-red-200',
      icon: '❌'
    }
  }

  const style = typeStyles[type]

  return (
    <div
      className={`
        max-w-sm w-full
        ${style.bg} ${style.border} ${style.text}
        border rounded-xl shadow-lg
        transform transition-all duration-300 ease-in-out
        ${isVisible
          ? 'translate-x-0 opacity-100'
          : 'translate-x-full opacity-0'
        }
      `}
    >
      <div className="p-4">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <span className="text-lg" role="img" aria-label={type}>
              {style.icon}
            </span>
          </div>

          <div className="ml-3 w-0 flex-1">
            <p className="text-sm font-medium leading-5">
              {message}
            </p>

            {action && (
              <div className="mt-3">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    action.handler()
                    handleClose()
                  }}
                >
                  {action.text}
                </Button>
              </div>
            )}
          </div>

          <div className="ml-4 flex-shrink-0 flex">
            <button
              type="button"
              onClick={handleClose}
              className={`
                inline-flex rounded-md
                ${style.text}
                hover:opacity-75 focus:outline-none
                focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
                transition-opacity duration-150
              `}
              aria-label="Close notification"
            >
              <span className="sr-only">Close</span>
              <svg
                className="w-5 h-5"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

// Toast Container Component
export interface ToastContainerProps {
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left'
}

interface ToastData extends Omit<ToastProps, 'onClose'> {
  // All props except onClose
}

let toastId = 0

// Toast Context and Provider
export class ToastManager {
  private static instance: ToastManager
  private subscribers: Array<(toasts: ToastData[]) => void> = []
  private toasts: ToastData[] = []

  static getInstance(): ToastManager {
    if (!ToastManager.instance) {
      ToastManager.instance = new ToastManager()
    }
    return ToastManager.instance
  }

  subscribe(callback: (toasts: ToastData[]) => void) {
    this.subscribers.push(callback)
    return () => {
      this.subscribers = this.subscribers.filter(sub => sub !== callback)
    }
  }

  private notify() {
    this.subscribers.forEach(callback => callback(this.toasts))
  }

  show(toast: Omit<ToastData, 'id'>) {
    const newToast: ToastData = {
      ...toast,
      id: `toast-${++toastId}`
    }
    this.toasts = [...this.toasts, newToast]
    this.notify()
  }

  remove(id: string) {
    this.toasts = this.toasts.filter(toast => toast.id !== id)
    this.notify()
  }

  clear() {
    this.toasts = []
    this.notify()
  }
}

// Hook for using toasts
export const useToast = () => {
  const manager = ToastManager.getInstance()

  return {
    showToast: (toast: Omit<ToastData, 'id'>) => manager.show(toast),
    clearToasts: () => manager.clear()
  }
}

// Toast Container Component
export const ToastContainer: React.FC<ToastContainerProps> = ({
  position = 'top-right'
}) => {
  const [toasts, setToasts] = useState<ToastData[]>([])
  const manager = ToastManager.getInstance()

  useEffect(() => {
    const unsubscribe = manager.subscribe(setToasts)
    return unsubscribe
  }, [manager])

  const positionClasses = {
    'top-right': 'top-5 right-5',
    'top-left': 'top-5 left-5',
    'bottom-right': 'bottom-5 right-5',
    'bottom-left': 'bottom-5 left-5'
  }

  if (toasts.length === 0) return null

  return (
    <div className={`fixed z-50 ${positionClasses[position]}`}>
      <div className="flex flex-col space-y-3">
        {toasts.map((toast) => (
          <Toast
            key={toast.id}
            {...toast}
            onClose={(id) => manager.remove(id)}
          />
        ))}
      </div>
    </div>
  )
}

// Convenience functions
export const showToast = (toast: Omit<ToastData, 'id'>) => {
  ToastManager.getInstance().show(toast)
}

export default Toast