import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Counter from './Counter';

// Mock the hooks
jest.mock('../hooks/useCounter');
jest.mock('../hooks/useSession');

describe('Counter Component', () => {
  const mockIncrement = jest.fn();
  const mockDecrement = jest.fn();
  const mockReset = jest.fn();
  const mockUpdateLastAccessed = jest.fn();

  const defaultCounterState = {
    current_value: 0,
    timestamp: '2023-01-01T00:00:00.000Z'
  };

  const defaultSessionState = {
    session_id: 'test_session_123',
    last_accessed: '2023-01-01T00:00:00.000Z'
  };

  beforeEach(() => {
    jest.clearAllMocks();
    
    const { useCounter } = require('../hooks/useCounter');
    const { useSession } = require('../hooks/useSession');
    
    useCounter.mockReturnValue({
      counterState: defaultCounterState,
      increment: mockIncrement,
      decrement: mockDecrement,
      reset: mockReset,
      canIncrement: true,
      canDecrement: true
    });

    useSession.mockReturnValue({
      sessionState: defaultSessionState,
      updateLastAccessed: mockUpdateLastAccessed
    });
  });

  describe('Rendering', () => {
    test('should render counter component with initial value', () => {
      render(<Counter />);
      
      expect(screen.getByText('Counter Application')).toBeInTheDocument();
      expect(screen.getByTestId('counter-value')).toHaveTextContent('0');
    });

    test('should render all control buttons', () => {
      render(<Counter />);
      
      expect(screen.getByTestId('increment-button')).toBeInTheDocument();
      expect(screen.getByTestId('decrement-button')).toBeInTheDocument();
      expect(screen.getByTestId('reset-button')).toBeInTheDocument();
    });

    test('should display session information', () => {
      render(<Counter />);
      
      expect(screen.getByText(/Session: test_session_123/)).toBeInTheDocument();
    });

    test('should format large positive numbers correctly', () => {
      const { useCounter } = require('../hooks/useCounter');
      useCounter.mockReturnValue({
        counterState: { ...defaultCounterState, current_value: 123456 },
        increment: mockIncrement,
        decrement: mockDecrement,
        reset: mockReset,
        canIncrement: true,
        canDecrement: true
      });

      render(<Counter />);
      
      expect(screen.getByTestId('counter-value')).toHaveTextContent('123,456');
    });

    test('should format large negative numbers correctly', () => {
      const { useCounter } = require('../hooks/useCounter');
      useCounter.mockReturnValue({
        counterState: { ...defaultCounterState, current_value: -123456 },
        increment: mockIncrement,
        decrement: mockDecrement,
        reset: mockReset,
        canIncrement: true,
        canDecrement: true
      });

      render(<Counter />);
      
      expect(screen.getByTestId('counter-value')).toHaveTextContent('-123,456');
    });
  });

  describe('Increment Functionality', () => {
    test('should call increment and update session on increment button click', async () => {
      mockIncrement.mockReturnValue(true);
      
      render(<Counter />);
      
      const incrementButton = screen.getByTestId('increment-button');
      await userEvent.click(incrementButton);
      
      expect(mockIncrement).toHaveBeenCalledTimes(1);
      expect(mockUpdateLastAccessed).toHaveBeenCalledTimes(1);
    });

    test('should not update session when increment fails', async () => {
      mockIncrement.mockReturnValue(false);
      
      render(<Counter />);
      
      const incrementButton = screen.getByTestId('increment-button');
      await userEvent.click(incrementButton);
      
      expect(mockIncrement).toHaveBeenCalledTimes(1);
      expect(mockUpdateLastAccessed).not.toHaveBeenCalled();
    });

    test('should disable increment button when canIncrement is false', () => {
      const { useCounter } = require('../hooks/useCounter');
      useCounter.mockReturnValue({
        counterState: { ...defaultCounterState, current_value: 999999 },
        increment: mockIncrement,
        decrement: mockDecrement,
        reset: mockReset,
        canIncrement: false,
        canDecrement: true
      });

      render(<Counter />);
      
      const incrementButton = screen.getByTestId('increment-button');
      expect(incrementButton).toBeDisabled();
    });

    test('should show maximum limit message when at max value', () => {
      const { useCounter } = require('../hooks/useCounter');
      useCounter.mockReturnValue({
        counterState: { ...defaultCounterState, current_value: 999999 },
        increment: mockIncrement,
        decrement: mockDecrement,
        reset: mockReset,
        canIncrement: false,
        canDecrement: true
      });

      render(<Counter />);
      
      expect(screen.getByTestId('max-limit-message')).toBeInTheDocument();
      expect(screen.getByText('Maximum value reached (999,999)')).toBeInTheDocument();
    });
  });

  describe('Decrement Functionality', () => {
    test('should call decrement and update session on decrement button click', async () => {
      mockDecrement.mockReturnValue(true);
      
      render(<Counter />);
      
      const decrementButton = screen.getByTestId('decrement-button');
      await userEvent.click(decrementButton);
      
      expect(mockDecrement).toHaveBeenCalledTimes(1);
      expect(mockUpdateLastAccessed).toHaveBeenCalledTimes(1);
    });

    test('should not update session when decrement fails', async () => {
      mockDecrement.mockReturnValue(false);
      
      render(<Counter />);
      
      const decrementButton = screen.getByTestId('decrement-button');
      await userEvent.click(decrementButton);
      
      expect(mockDecrement).toHaveBeenCalledTimes(1);
      expect(mockUpdateLastAccessed).not.toHaveBeenCalled();
    });

    test('should disable decrement button when canDecrement is false', () => {
      const { useCounter } = require('../hooks/useCounter');
      useCounter.mockReturnValue({
        counterState: { ...defaultCounterState, current_value: -999999 },
        increment: mockIncrement,
        decrement: mockDecrement,
        reset: mockReset,
        canIncrement: true,
        canDecrement: false
      });

      render(<Counter />);
      
      const decrementButton = screen.getByTestId('decrement-button');
      expect(decrementButton).toBeDisabled();
    });

    test('should show minimum limit message when at min value', () => {
      const { useCounter } = require('../hooks/useCounter');
      useCounter.mockReturnValue({
        counterState: { ...defaultCounterState, current_value: -999999 },
        increment: mockIncrement,
        decrement: mockDecrement,
        reset: mockReset,
        canIncrement: true,
        canDecrement: false
      });

      render(<Counter />);
      
      expect(screen.getByTestId('min-limit-message')).toBeInTheDocument();
      expect(screen.getByText('Minimum value reached (-999,999)')).toBeInTheDocument();
    });
  });

  describe('Reset Functionality', () => {
    test('should call reset and update session on reset button click', async () => {
      render(<Counter />);
      
      const resetButton = screen.getByTestId('reset-button');
      await userEvent.click(resetButton);
      
      expect(mockReset).toHaveBeenCalledTimes(1);
      expect(mockUpdateLastAccessed).toHaveBeenCalledTimes(1);
    });

    test('should always enable reset button', () => {
      render(<Counter />);
      
      const resetButton = screen.getByTestId('reset-button');
      expect(resetButton).not.toBeDisabled();
    });
  });

  describe('UI Updates', () => {
    test('should display counter value immediately without delay', () => {
      const { useCounter } = require('../hooks/useCounter');
      const { rerender } = render(<Counter />);
      
      // Update the counter state
      useCounter.mockReturnValue({
        counterState: { ...defaultCounterState, current_value: 42 },
        increment: mockIncrement,
        decrement: mockDecrement,
        reset: mockReset,
        canIncrement: true,
        canDecrement: true
      });

      rerender(<Counter />);
      
      expect(screen.getByTestId('counter-value')).toHaveTextContent('42');
    });

    test('should update timestamps in info section', () => {
      const { useCounter } = require('../hooks/useCounter');
      useCounter.mockReturnValue({
        counterState: { 
          current_value: 0, 
          timestamp: '2023-01-01T12:00:00.000Z' 
        },
        increment: mockIncrement,
        decrement: mockDecrement,
        reset: mockReset,
        canIncrement: true,
        canDecrement: true
      });

      render(<Counter />);
      
      expect(screen.getByText(/Last Modified:/)).toBeInTheDocument();
    });
  });

  describe('Accessibility and UX', () => {
    test('should have proper button titles for accessibility', () => {
      render(<Counter />);
      
      expect(screen.getByTestId('increment-button')).toHaveAttribute('title', 'Increase by 1');
      expect(screen.getByTestId('decrement-button')).toHaveAttribute('title', 'Decrease by 1');
      expect(screen.getByTestId('reset-button')).toHaveAttribute('title', 'Reset to 0');
    });

    test('should show appropriate title when buttons are disabled', () => {
      const { useCounter } = require('../hooks/useCounter');
      useCounter.mockReturnValue({
        counterState: { ...defaultCounterState, current_value: 999999 },
        increment: mockIncrement,
        decrement: mockDecrement,
        reset: mockReset,
        canIncrement: false,
        canDecrement: true
      });

      render(<Counter />);
      
      expect(screen.getByTestId('increment-button')).toHaveAttribute('title', 'Cannot exceed 999,999');
    });
  });
});