import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import Button from '../../src/components/Button'

describe('Button Component', () => {
  it('renders with default props', () => {
    render(<Button>Click me</Button>)

    const button = screen.getByRole('button', { name: /click me/i })
    expect(button).toBeInTheDocument()
    expect(button).toHaveClass('bg-primary') // Default variant is primary
  })

  it('renders different variants correctly', () => {
    const variants = ['primary', 'secondary', 'success', 'warning', 'error', 'ghost', 'outline'] as const

    variants.forEach((variant) => {
      render(<Button variant={variant} data-testid={`button-${variant}`}>{variant}</Button>)
      const button = screen.getByTestId(`button-${variant}`)
      expect(button).toBeInTheDocument()
    })
  })

  it('renders different sizes correctly', () => {
    const sizes = ['sm', 'md', 'lg'] as const

    sizes.forEach((size) => {
      render(<Button size={size} data-testid={`button-${size}`}>Size {size}</Button>)
      const button = screen.getByTestId(`button-${size}`)
      expect(button).toBeInTheDocument()
    })
  })

  it('handles click events', () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick}>Click me</Button>)

    const button = screen.getByRole('button', { name: /click me/i })
    fireEvent.click(button)

    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('shows loading state correctly', () => {
    render(<Button loading>Loading button</Button>)

    const button = screen.getByRole('button')
    expect(button).toBeDisabled()
    expect(button).toHaveAttribute('disabled')

    // Check for loading spinner by class
    const spinner = screen.getByText('Loading button').closest('button')?.querySelector('.animate-spin')
    expect(spinner).toBeInTheDocument()
  })

  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Disabled button</Button>)

    const button = screen.getByRole('button', { name: /disabled button/i })
    expect(button).toBeDisabled()
  })

  it('renders full width when specified', () => {
    render(<Button fullWidth>Full width button</Button>)

    const button = screen.getByRole('button', { name: /full width button/i })
    expect(button).toHaveClass('w-full')
  })

  it('renders with icon when provided', () => {
    render(
      <Button icon={<span data-testid="icon">🚀</span>}>
        With icon
      </Button>
    )

    const icon = screen.getByTestId('icon')
    expect(icon).toBeInTheDocument()
    expect(icon).toHaveTextContent('🚀')
  })

  it('applies custom className correctly', () => {
    render(<Button className="custom-class">Custom button</Button>)

    const button = screen.getByRole('button', { name: /custom button/i })
    expect(button).toHaveClass('custom-class')
  })

  it('prevents click when loading', () => {
    const handleClick = vi.fn()
    render(<Button loading onClick={handleClick}>Loading button</Button>)

    const button = screen.getByRole('button')
    fireEvent.click(button)

    expect(handleClick).not.toHaveBeenCalled()
  })

  it('prevents click when disabled', () => {
    const handleClick = vi.fn()
    render(<Button disabled onClick={handleClick}>Disabled button</Button>)

    const button = screen.getByRole('button')
    fireEvent.click(button)

    expect(handleClick).not.toHaveBeenCalled()
  })
})