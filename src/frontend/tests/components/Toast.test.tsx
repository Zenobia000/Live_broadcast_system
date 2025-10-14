import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import Toast, { ToastContainer, ToastManager, useToast } from '../../src/components/Toast'

describe('Toast Component', () => {
  beforeEach(() => {
    // Clear any existing toasts
    ToastManager.getInstance().clear()
  })

  it('renders toast with correct message and type', () => {
    const mockOnClose = vi.fn()

    render(
      <Toast
        id="test-toast"
        type="success"
        message="Test success message"
        onClose={mockOnClose}
      />
    )

    expect(screen.getByText('Test success message')).toBeInTheDocument()
    expect(screen.getByLabelText('success')).toBeInTheDocument()
  })

  it('renders different toast types with correct styling', () => {
    const mockOnClose = vi.fn()
    const types = ['info', 'success', 'warning', 'error'] as const

    types.forEach((type) => {
      render(
        <Toast
          id={`test-${type}`}
          type={type}
          message={`${type} message`}
          onClose={mockOnClose}
        />
      )

      expect(screen.getByText(`${type} message`)).toBeInTheDocument()
    })
  })

  it('calls onClose when close button is clicked', () => {
    const mockOnClose = vi.fn()

    render(
      <Toast
        id="test-toast"
        type="info"
        message="Test message"
        onClose={mockOnClose}
      />
    )

    const closeButton = screen.getByLabelText('Close notification')
    fireEvent.click(closeButton)

    // Should call onClose after animation delay
    expect(mockOnClose).toHaveBeenCalledWith('test-toast')
  })

  it('renders action button when provided', () => {
    const mockOnClose = vi.fn()
    const mockAction = vi.fn()

    render(
      <Toast
        id="test-toast"
        type="warning"
        message="Test message"
        action={{
          text: 'Take Action',
          handler: mockAction
        }}
        onClose={mockOnClose}
      />
    )

    const actionButton = screen.getByRole('button', { name: /take action/i })
    expect(actionButton).toBeInTheDocument()

    fireEvent.click(actionButton)
    expect(mockAction).toHaveBeenCalled()
  })

  it('auto closes after specified time', async () => {
    const mockOnClose = vi.fn()

    render(
      <Toast
        id="test-toast"
        type="info"
        message="Auto close message"
        autoClose={1000}
        onClose={mockOnClose}
      />
    )

    // Should auto close after 1 second + animation delay
    await waitFor(
      () => expect(mockOnClose).toHaveBeenCalledWith('test-toast'),
      { timeout: 2000 }
    )
  })

  it('does not auto close when autoClose is false', async () => {
    const mockOnClose = vi.fn()

    render(
      <Toast
        id="test-toast"
        type="info"
        message="No auto close"
        autoClose={false}
        onClose={mockOnClose}
      />
    )

    // Wait a bit and ensure onClose is not called
    await new Promise(resolve => setTimeout(resolve, 1000))
    expect(mockOnClose).not.toHaveBeenCalled()
  })
})

describe('Toast Manager', () => {
  beforeEach(() => {
    ToastManager.getInstance().clear()
  })

  it('is a singleton', () => {
    const manager1 = ToastManager.getInstance()
    const manager2 = ToastManager.getInstance()

    expect(manager1).toBe(manager2)
  })

  it('manages toast state correctly', () => {
    const manager = ToastManager.getInstance()
    const mockCallback = vi.fn()

    manager.subscribe(mockCallback)

    // Add a toast
    manager.show({
      type: 'success',
      message: 'Test toast'
    })

    expect(mockCallback).toHaveBeenCalled()
  })
})

// Test Hook
const TestComponent = () => {
  const { showToast } = useToast()

  return (
    <div>
      <button
        onClick={() => showToast({ type: 'success', message: 'Hook test' })}
      >
        Show Toast
      </button>
      <ToastContainer />
    </div>
  )
}

describe('useToast Hook', () => {
  beforeEach(() => {
    ToastManager.getInstance().clear()
  })

  it('shows toast through hook', async () => {
    render(<TestComponent />)

    const button = screen.getByRole('button', { name: /show toast/i })
    fireEvent.click(button)

    await waitFor(() => {
      expect(screen.getByText('Hook test')).toBeInTheDocument()
    })
  })
})