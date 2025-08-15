import { useState, useCallback, useEffect } from 'react';
import { generateSessionId, getCurrentTimestamp } from '../utils/sessionUtils';

/**
 * Custom hook for session tracking
 * @returns {Object} Session state and operations
 */
export const useSession = () => {
  const [sessionState, setSessionState] = useState(() => ({
    session_id: generateSessionId(),
    last_accessed: getCurrentTimestamp()
  }));

  /**
   * Updates the last accessed timestamp
   */
  const updateLastAccessed = useCallback(() => {
    setSessionState(prevState => ({
      ...prevState,
      last_accessed: getCurrentTimestamp()
    }));
  }, []);

  // Update last accessed on component mount
  useEffect(() => {
    updateLastAccessed();
  }, [updateLastAccessed]);

  return {
    sessionState,
    updateLastAccessed
  };
};