/**
 * Domain model for counter state
 * @typedef {Object} CounterState
 * @property {number} current_value - The current counter value
 * @property {string} timestamp - ISO string of when the counter was last modified
 */

/**
 * Domain model for session tracking
 * @typedef {Object} SessionState
 * @property {string} session_id - Unique identifier for the session
 * @property {string} last_accessed - ISO string of when the session was last accessed
 */

export const COUNTER_LIMITS = {
  MIN: -999999,
  MAX: 999999
};

export const OPERATION_TIMEOUT_MS = 100;