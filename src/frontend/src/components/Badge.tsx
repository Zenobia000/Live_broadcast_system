import React from 'react'

export type BadgeVariant = 'default' | 'primary' | 'success' | 'warning' | 'error' | 'info'
export type BadgeSize = 'sm' | 'md' | 'lg'

export interface BadgeProps {
  children: React.ReactNode
  variant?: BadgeVariant
  size?: BadgeSize
  dot?: boolean
  className?: string
}

const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  size = 'md',
  dot = false,
  className = '',
}) => {
  const baseStyles = `
    inline-flex items-center gap-1.5
    font-medium rounded-full
    transition-colors duration-200
  `

  const variantStyles = {
    default: 'bg-gray-100 text-gray-700',
    primary: 'bg-primary-light/10 text-primary',
    success: 'bg-success-light/10 text-success',
    warning: 'bg-warning-light/10 text-warning',
    error: 'bg-error-light/10 text-error',
    info: 'bg-blue-100 text-blue-700',
  }

  const sizeStyles = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base',
  }

  const dotColorStyles = {
    default: 'bg-gray-500',
    primary: 'bg-primary',
    success: 'bg-success',
    warning: 'bg-warning',
    error: 'bg-error',
    info: 'bg-blue-600',
  }

  return (
    <span
      className={`
        ${baseStyles}
        ${variantStyles[variant]}
        ${sizeStyles[size]}
        ${className}
      `
        .replace(/\s+/g, ' ')
        .trim()}
    >
      {dot && (
        <span className={`w-2 h-2 rounded-full ${dotColorStyles[variant]}`} aria-hidden="true" />
      )}
      {children}
    </span>
  )
}

export interface StatusBadgeProps {
  status:
    | 'PRESENT'
    | 'LATE'
    | 'ABSENT'
    | 'LEAVE'
    | 'MAKEUP'
    | 'EARLY_LEAVE'
    | 'PENDING'
    | 'APPROVED'
    | 'REJECTED'
  size?: BadgeSize
  className?: string
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  size = 'md',
  className = '',
}) => {
  const statusConfig = {
    PRESENT: { label: '出席', variant: 'success' as BadgeVariant, dot: true },
    LATE: { label: '遲到', variant: 'warning' as BadgeVariant, dot: true },
    ABSENT: { label: '缺席', variant: 'error' as BadgeVariant, dot: true },
    LEAVE: { label: '請假', variant: 'info' as BadgeVariant, dot: true },
    MAKEUP: { label: '補簽', variant: 'primary' as BadgeVariant, dot: true },
    EARLY_LEAVE: { label: '早退', variant: 'warning' as BadgeVariant, dot: true },
    PENDING: { label: '待審核', variant: 'default' as BadgeVariant, dot: true },
    APPROVED: { label: '已批准', variant: 'success' as BadgeVariant, dot: false },
    REJECTED: { label: '已拒絕', variant: 'error' as BadgeVariant, dot: false },
  }

  const config = statusConfig[status]

  return (
    <Badge variant={config.variant} size={size} dot={config.dot} className={className}>
      {config.label}
    </Badge>
  )
}

export default Badge
