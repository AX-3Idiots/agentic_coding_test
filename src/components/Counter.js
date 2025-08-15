import React from 'react';
import { useCounter } from '../hooks/useCounter';
import { useSession } from '../hooks/useSession';
import './Counter.css';

/**
 * Main Counter component with immediate UI updates
 */
const Counter = () => {
  const {
    counterState,
    increment,
    decrement,
    reset,
    canIncrement,
    canDecrement
  } = useCounter();

  const { sessionState, updateLastAccessed } = useSession();

  /**
   * Handles increment button click with session tracking
   */
  const handleIncrement = () => {
    const success = increment();
    if (success) {
      updateLastAccessed();
    }
  };

  /**
   * Handles decrement button click with session tracking
   */
  const handleDecrement = () => {
    const success = decrement();
    if (success) {
      updateLastAccessed();
    }
  };

  /**
   * Handles reset button click with session tracking
   */
  const handleReset = () => {
    reset();
    updateLastAccessed();
  };

  /**
   * Formats large numbers with proper thousands separators
   * @param {number} value - The number to format
   * @returns {string} Formatted number string
   */
  const formatCounterValue = (value) => {
    return value.toLocaleString();
  };

  return (
    <div className="counter-container">
      <div className="counter-header">
        <h1>Counter Application</h1>
        <div className="session-info">
          <small>Session: {sessionState.session_id}</small>
          <small>Last updated: {new Date(counterState.timestamp).toLocaleString()}</small>
        </div>
      </div>

      <div className="counter-display">
        <div className="counter-value" data-testid="counter-value">
          {formatCounterValue(counterState.current_value)}
        </div>
      </div>

      <div className="counter-controls">
        <button
          className="counter-button decrement"
          onClick={handleDecrement}
          disabled={!canDecrement}
          data-testid="decrement-button"
          title={!canDecrement ? "Cannot go below -999,999" : "Decrease by 1"}
        >
          -1
        </button>

        <button
          className="counter-button reset"
          onClick={handleReset}
          data-testid="reset-button"
          title="Reset to 0"
        >
          Reset
        </button>

        <button
          className="counter-button increment"
          onClick={handleIncrement}
          disabled={!canIncrement}
          data-testid="increment-button"
          title={!canIncrement ? "Cannot exceed 999,999" : "Increase by 1"}
        >
          +1
        </button>
      </div>

      {!canIncrement && (
        <div className="limit-message limit-max" data-testid="max-limit-message">
          Maximum value reached (999,999)
        </div>
      )}

      {!canDecrement && (
        <div className="limit-message limit-min" data-testid="min-limit-message">
          Minimum value reached (-999,999)
        </div>
      )}

      <div className="counter-info">
        <div className="counter-stats">
          <div>Current Value: {formatCounterValue(counterState.current_value)}</div>
          <div>Last Modified: {new Date(counterState.timestamp).toLocaleString()}</div>
          <div>Session ID: {sessionState.session_id}</div>
          <div>Last Accessed: {new Date(sessionState.last_accessed).toLocaleString()}</div>
        </div>
      </div>
    </div>
  );
};

export default Counter;