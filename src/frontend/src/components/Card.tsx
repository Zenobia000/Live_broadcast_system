import React from 'react'

export interface CardProps {
  children: React.ReactNode
  className?: string
  hover?: boolean
  onClick?: () => void
}

const Card: React.FC<CardProps> = ({ children, className = '', hover = false, onClick }) => {
  const baseStyles = `
    bg-white rounded-xl shadow-apple
    transition-all duration-200
  `

  const hoverStyles = hover
    ? `
    hover:shadow-lg hover:-translate-y-1
    cursor-pointer
  `
    : ''

  const interactiveStyles = onClick ? 'cursor-pointer' : ''

  return (
    <div
      className={`
        ${baseStyles}
        ${hoverStyles}
        ${interactiveStyles}
        ${className}
      `
        .replace(/\s+/g, ' ')
        .trim()}
      onClick={onClick}
    >
      {children}
    </div>
  )
}

export interface CardHeaderProps {
  children: React.ReactNode
  className?: string
  onClick?: () => void
}

export const CardHeader: React.FC<CardHeaderProps> = ({ children, className = '', onClick }) => {
  return (
    <div
      className={`px-6 py-4 border-b border-gray-100 ${className}`}
      onClick={onClick}
    >
      {children}
    </div>
  )
}

export interface CardBodyProps {
  children: React.ReactNode
  className?: string
}

export const CardBody: React.FC<CardBodyProps> = ({ children, className = '' }) => {
  return <div className={`px-6 py-4 ${className}`}>{children}</div>
}

export interface CardFooterProps {
  children: React.ReactNode
  className?: string
}

export const CardFooter: React.FC<CardFooterProps> = ({ children, className = '' }) => {
  return (
    <div className={`px-6 py-4 border-t border-gray-100 bg-gray-50 rounded-b-xl ${className}`}>
      {children}
    </div>
  )
}

export default Card
