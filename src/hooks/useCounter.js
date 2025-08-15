import { useState, useCallback, useRef, useEffect } from 'react';
import { COUNTER_LIMITS, OPERATION_TIMEOUT_MS } from '../types';
import { getCurrentTimestamp } from '../utils/sessionUtils';

/**
 * Custom hook for counter state management
 * @returns {Object} Counter state and operations
 */
export const useCounter = () => {
  const [counterState, setCounterState] = useState({
    current_value: 0,
    timestamp: getCurrentTimestamp()
  });

  const timeoutRef = useRef(null);

  /**
   * Updates counter state with new value and timestamp
   * @param {number} newValue - The new counter value
   */
  const updateCounterState = useCallback((newValue) => {
    // Clear any existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    // Set timeout to ensure operation completes within 100ms
    timeoutRef.current = setTimeout(() => {
      setCounterState({
        current_value: newValue,
        timestamp: getCurrentTimestamp()
      });
    }, 0);
  }, []);

  /**
   * Increments counter by 1, respecting maximum limit
   * @returns {boolean} True if operation succeeded, false if at limit
   */
  const increment = useCallback(() => {
    if (counterState.current_value >= COUNTER_LIMITS.MAX) {
      return false;
    }
    
    const newValue = counterState.current_value + 1;
    updateCounterState(newValue);
    return true;
  }, [counterState.current_value, updateCounterState]);

  /**
   * Decrements counter by 1, respecting minimum limit
   * @returns {boolean} True if operation succeeded, false if at limit
   */
  const decrement = useCallback(() => {
    if (counterState.current_value <= COUNTER_LIMITS.MIN) {
      return false;
    }
    
    const newValue = counterState.current_value - 1;
    updateCounterState(newValue);
    return true;
  }, [counterState.current_value, updateCounterState]);

  /**
   * Resets counter to 0
   */
  const reset = useCallback(() => {
    updateCounterState(0);
  }, [updateCounterState]);

  /**
   * Checks if increment is allowed
   * @returns {boolean} True if increment is allowed
   */
  const canIncrement = counterState.current_value < COUNTER_LIMITS.MAX;

  /**
   * Checks if decrement is allowed
   * @returns {boolean} True if decrement is allowed
   */
  const canDecrement = counterState.current_value > COUNTER_LIMITS.MIN;

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return {
    counterState,
    increment,
    decrement,
    reset,
    canIncrement,
    canDecrement
  };
};