/**
 * Generates a unique session ID
 * @returns {string} Unique session identifier
 */
export const generateSessionId = () => {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Gets current timestamp as ISO string
 * @returns {string} ISO timestamp
 */
export const getCurrentTimestamp = () => {
  return new Date().toISOString();
};