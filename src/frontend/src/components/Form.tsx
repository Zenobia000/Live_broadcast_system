import React, { forwardRef } from 'react'

// Form Container
export interface FormProps extends React.FormHTMLAttributes<HTMLFormElement> {
  children: React.ReactNode
  onSubmit?: (e: React.FormEvent<HTMLFormElement>) => void
}

export const Form = forwardRef<HTMLFormElement, FormProps>(
  ({ children, className = '', onSubmit, ...props }, ref) => {
    return (
      <form
        ref={ref}
        className={`space-y-6 ${className}`}
        onSubmit={onSubmit}
        {...props}
      >
        {children}
      </form>
    )
  }
)

Form.displayName = 'Form'

// Form Section
export interface FormSectionProps {
  children: React.ReactNode
  className?: string
}

export const FormSection: React.FC<FormSectionProps> = ({
  children,
  className = ''
}) => {
  return (
    <div className={`space-y-2 ${className}`}>
      {children}
    </div>
  )
}

// Form Label
export interface FormLabelProps extends React.LabelHTMLAttributes<HTMLLabelElement> {
  children: React.ReactNode
  required?: boolean
}

export const FormLabel: React.FC<FormLabelProps> = ({
  children,
  required,
  className = '',
  ...props
}) => {
  return (
    <label
      className={`block text-sm font-medium text-gray-900 dark:text-gray-100 mb-1 ${className}`}
      {...props}
    >
      {children}
      {required && <span className="text-red-500 ml-1">*</span>}
    </label>
  )
}

// Form Helper Text
export interface FormHelperTextProps {
  children: React.ReactNode
  variant?: 'info' | 'error' | 'success'
  className?: string
}

export const FormHelperText: React.FC<FormHelperTextProps> = ({
  children,
  variant = 'info',
  className = ''
}) => {
  const baseClasses = 'text-xs mt-1'

  const variantClasses = {
    info: 'text-gray-500 dark:text-gray-400',
    error: 'text-red-600 dark:text-red-400',
    success: 'text-green-600 dark:text-green-400'
  }

  return (
    <p className={`${baseClasses} ${variantClasses[variant]} ${className}`}>
      {children}
    </p>
  )
}

// Select Component
export interface SelectOption {
  value: string
  label: string
  disabled?: boolean
}

export interface SelectProps extends Omit<React.SelectHTMLAttributes<HTMLSelectElement>, 'size'> {
  options: SelectOption[]
  placeholder?: string
  error?: boolean
  helperText?: string
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({
    options,
    placeholder,
    error,
    helperText,
    className = '',
    ...props
  }, ref) => {
    const baseClasses = `
      w-full px-4 py-3
      bg-white dark:bg-gray-800
      border rounded-xl
      text-gray-900 dark:text-gray-100
      focus:outline-none focus:ring-2 focus:ring-offset-1
      transition-all duration-200
      disabled:opacity-50 disabled:cursor-not-allowed
    `

    const borderClasses = error
      ? 'border-red-300 dark:border-red-600 focus:border-red-500 focus:ring-red-200 dark:focus:ring-red-800'
      : 'border-gray-200 dark:border-gray-600 focus:border-blue-500 focus:ring-blue-200 dark:focus:ring-blue-800 hover:border-gray-300 dark:hover:border-gray-500'

    return (
      <div className="w-full">
        <select
          ref={ref}
          className={`${baseClasses} ${borderClasses} ${className}`}
          {...props}
        >
          {placeholder && (
            <option value="" disabled>
              {placeholder}
            </option>
          )}
          {options.map((option) => (
            <option
              key={option.value}
              value={option.value}
              disabled={option.disabled}
            >
              {option.label}
            </option>
          ))}
        </select>
        {helperText && (
          <FormHelperText variant={error ? 'error' : 'info'}>
            {helperText}
          </FormHelperText>
        )}
      </div>
    )
  }
)

Select.displayName = 'Select'

// Textarea Component
export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  error?: boolean
  helperText?: string
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ error, helperText, className = '', ...props }, ref) => {
    const baseClasses = `
      w-full px-4 py-3
      bg-white dark:bg-gray-800
      border rounded-xl
      text-gray-900 dark:text-gray-100
      placeholder-gray-500 dark:placeholder-gray-400
      focus:outline-none focus:ring-2 focus:ring-offset-1
      transition-all duration-200
      disabled:opacity-50 disabled:cursor-not-allowed
      resize-none
    `

    const borderClasses = error
      ? 'border-red-300 dark:border-red-600 focus:border-red-500 focus:ring-red-200 dark:focus:ring-red-800'
      : 'border-gray-200 dark:border-gray-600 focus:border-blue-500 focus:ring-blue-200 dark:focus:ring-blue-800 hover:border-gray-300 dark:hover:border-gray-500'

    return (
      <div className="w-full">
        <textarea
          ref={ref}
          className={`${baseClasses} ${borderClasses} ${className}`}
          rows={3}
          {...props}
        />
        {helperText && (
          <FormHelperText variant={error ? 'error' : 'info'}>
            {helperText}
          </FormHelperText>
        )}
      </div>
    )
  }
)

Textarea.displayName = 'Textarea'

// Form Actions (for buttons at the bottom)
export interface FormActionsProps {
  children: React.ReactNode
  align?: 'left' | 'center' | 'right'
  className?: string
}

export const FormActions: React.FC<FormActionsProps> = ({
  children,
  align = 'right',
  className = ''
}) => {
  const alignClasses = {
    left: 'justify-start',
    center: 'justify-center',
    right: 'justify-end'
  }

  return (
    <div className={`flex gap-3 ${alignClasses[align]} ${className}`}>
      {children}
    </div>
  )
}

export default Form