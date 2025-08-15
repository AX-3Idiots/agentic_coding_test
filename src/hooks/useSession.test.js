import { renderHook, act } from '@testing-library/react';
import { useSession } from './useSession';

// Mock the session utilities
jest.mock('../utils/sessionUtils', () => ({
  generateSessionId: () => 'test_session_123',
  getCurrentTimestamp: () => '2023-01-01T00:00:00.000Z'
}));

describe('useSession Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Initial State', () => {
    test('should initialize with unique session_id and timestamp', () => {
      const { result } = renderHook(() => useSession());
      
      expect(result.current.sessionState.session_id).toBe('test_session_123');
      expect(result.current.sessionState.last_accessed).toBe('2023-01-01T00:00:00.000Z');
    });

    test('should generate different session_id for different instances', () => {
      // Mock to return different values for each call
      const mockGenerateSessionId = require('../utils/sessionUtils').generateSessionId;
      mockGenerateSessionId
        .mockReturnValueOnce('session_1')
        .mockReturnValueOnce('session_2');

      const { result: result1 } = renderHook(() => useSession());
      const { result: result2 } = renderHook(() => useSession());
      
      expect(result1.current.sessionState.session_id).toBe('session_1');
      expect(result2.current.sessionState.session_id).toBe('session_2');
    });
  });

  describe('Session Tracking', () => {
    test('should update last_accessed timestamp', () => {
      const { result } = renderHook(() => useSession());
      
      // Mock new timestamp
      const mockGetCurrentTimestamp = require('../utils/sessionUtils').getCurrentTimestamp;
      mockGetCurrentTimestamp.mockReturnValue('2023-01-01T01:00:00.000Z');
      
      act(() => {
        result.current.updateLastAccessed();
      });

      expect(result.current.sessionState.last_accessed).toBe('2023-01-01T01:00:00.000Z');
    });

    test('should preserve session_id when updating last_accessed', () => {
      const { result } = renderHook(() => useSession());
      const originalSessionId = result.current.sessionState.session_id;
      
      act(() => {
        result.current.updateLastAccessed();
      });

      expect(result.current.sessionState.session_id).toBe(originalSessionId);
    });
  });

  describe('Session Data Structure', () => {
    test('should match domain model specifications', () => {
      const { result } = renderHook(() => useSession());
      
      expect(result.current.sessionState).toHaveProperty('session_id');
      expect(result.current.sessionState).toHaveProperty('last_accessed');
      expect(typeof result.current.sessionState.session_id).toBe('string');
      expect(typeof result.current.sessionState.last_accessed).toBe('string');
    });

    test('should provide updateLastAccessed function', () => {
      const { result } = renderHook(() => useSession());
      
      expect(typeof result.current.updateLastAccessed).toBe('function');
    });
  });
});