import { generateSessionId, getCurrentTimestamp } from './sessionUtils';

describe('sessionUtils', () => {
  describe('generateSessionId', () => {
    test('should generate a unique session ID with correct format', () => {
      const sessionId = generateSessionId();
      
      expect(sessionId).toMatch(/^session_\d+_[a-z0-9]{9}$/);
    });

    test('should generate different session IDs on subsequent calls', () => {
      const sessionId1 = generateSessionId();
      const sessionId2 = generateSessionId();
      
      expect(sessionId1).not.toBe(sessionId2);
    });

    test('should always start with "session_" prefix', () => {
      const sessionId = generateSessionId();
      
      expect(sessionId).toMatch(/^session_/);
    });

    test('should include timestamp component', () => {
      const beforeTime = Date.now();
      const sessionId = generateSessionId();
      const afterTime = Date.now();
      
      const timestampPart = sessionId.split('_')[1];
      const timestamp = parseInt(timestampPart, 10);
      
      expect(timestamp).toBeGreaterThanOrEqual(beforeTime);
      expect(timestamp).toBeLessThanOrEqual(afterTime);
    });

    test('should include random component', () => {
      const sessionId = generateSessionId();
      const parts = sessionId.split('_');
      
      expect(parts.length).toBe(3);
      expect(parts[2]).toHaveLength(9);
      expect(parts[2]).toMatch(/^[a-z0-9]{9}$/);
    });
  });

  describe('getCurrentTimestamp', () => {
    test('should return a valid ISO timestamp string', () => {
      const timestamp = getCurrentTimestamp();
      
      expect(timestamp).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/);
    });

    test('should return a timestamp that can be parsed as a Date', () => {
      const timestamp = getCurrentTimestamp();
      const date = new Date(timestamp);
      
      expect(date).toBeInstanceOf(Date);
      expect(date.toISOString()).toBe(timestamp);
    });

    test('should return current time (within reasonable tolerance)', () => {
      const beforeTime = new Date();
      const timestamp = getCurrentTimestamp();
      const afterTime = new Date();
      
      const timestampDate = new Date(timestamp);
      
      expect(timestampDate.getTime()).toBeGreaterThanOrEqual(beforeTime.getTime());
      expect(timestampDate.getTime()).toBeLessThanOrEqual(afterTime.getTime());
    });

    test('should return different timestamps when called at different times', async () => {
      const timestamp1 = getCurrentTimestamp();
      
      // Wait a small amount to ensure different timestamps
      await new Promise(resolve => setTimeout(resolve, 1));
      
      const timestamp2 = getCurrentTimestamp();
      
      expect(timestamp1).not.toBe(timestamp2);
    });
  });
});