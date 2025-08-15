import { renderHook, act } from '@testing-library/react';
import { useCounter } from './useCounter';
import { COUNTER_LIMITS } from '../types';

// Mock getCurrentTimestamp to have predictable test results
jest.mock('../utils/sessionUtils', () => ({
  getCurrentTimestamp: () => '2023-01-01T00:00:00.000Z'
}));

describe('useCounter Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Initial State', () => {
    test('should initialize with value 0 and timestamp', () => {
      const { result } = renderHook(() => useCounter());
      
      expect(result.current.counterState.current_value).toBe(0);
      expect(result.current.counterState.timestamp).toBe('2023-01-01T00:00:00.000Z');
    });

    test('should have correct initial button states', () => {
      const { result } = renderHook(() => useCounter());
      
      expect(result.current.canIncrement).toBe(true);
      expect(result.current.canDecrement).toBe(true);
    });
  });

  describe('Increment Operation', () => {
    test('should increment counter by 1', async () => {
      const { result } = renderHook(() => useCounter());
      
      act(() => {
        const success = result.current.increment();
        expect(success).toBe(true);
      });

      // Wait for state update
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });

      expect(result.current.counterState.current_value).toBe(1);
    });

    test('should update timestamp on increment', async () => {
      const { result } = renderHook(() => useCounter());
      
      act(() => {
        result.current.increment();
      });

      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });

      expect(result.current.counterState.timestamp).toBe('2023-01-01T00:00:00.000Z');
    });

    test('should not increment beyond maximum limit', () => {
      const { result } = renderHook(() => useCounter());
      
      // Set counter to max value
      act(() => {
        for (let i = 0; i < COUNTER_LIMITS.MAX; i++) {
          result.current.increment();
        }
      });

      // Try to increment beyond max
      act(() => {
        const success = result.current.increment();
        expect(success).toBe(false);
      });

      expect(result.current.counterState.current_value).toBe(COUNTER_LIMITS.MAX);
      expect(result.current.canIncrement).toBe(false);
    });

    test('should complete operation within 100ms', async () => {
      const { result } = renderHook(() => useCounter());
      const startTime = Date.now();
      
      act(() => {
        result.current.increment();
      });

      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });

      const endTime = Date.now();
      expect(endTime - startTime).toBeLessThan(100);
    });
  });

  describe('Decrement Operation', () => {
    test('should decrement counter by 1', async () => {
      const { result } = renderHook(() => useCounter());
      
      act(() => {
        const success = result.current.decrement();
        expect(success).toBe(true);
      });

      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });

      expect(result.current.counterState.current_value).toBe(-1);
    });

    test('should not decrement below minimum limit', () => {
      const { result } = renderHook(() => useCounter());
      
      // Set counter to min value
      act(() => {
        for (let i = 0; i > COUNTER_LIMITS.MIN; i--) {
          result.current.decrement();
        }
      });

      // Try to decrement beyond min
      act(() => {
        const success = result.current.decrement();
        expect(success).toBe(false);
      });

      expect(result.current.counterState.current_value).toBe(COUNTER_LIMITS.MIN);
      expect(result.current.canDecrement).toBe(false);
    });

    test('should complete operation within 100ms', async () => {
      const { result } = renderHook(() => useCounter());
      const startTime = Date.now();
      
      act(() => {
        result.current.decrement();
      });

      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });

      const endTime = Date.now();
      expect(endTime - startTime).toBeLessThan(100);
    });
  });

  describe('Reset Operation', () => {
    test('should reset counter to 0 from positive value', async () => {
      const { result } = renderHook(() => useCounter());
      
      // Increment to positive value
      act(() => {
        result.current.increment();
        result.current.increment();
        result.current.increment();
      });

      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });

      expect(result.current.counterState.current_value).toBe(3);

      // Reset
      act(() => {
        result.current.reset();
      });

      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });

      expect(result.current.counterState.current_value).toBe(0);
    });

    test('should reset counter to 0 from negative value', async () => {
      const { result } = renderHook(() => useCounter());
      
      // Decrement to negative value
      act(() => {
        result.current.decrement();
        result.current.decrement();
        result.current.decrement();
      });

      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });

      expect(result.current.counterState.current_value).toBe(-3);

      // Reset
      act(() => {
        result.current.reset();
      });

      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });

      expect(result.current.counterState.current_value).toBe(0);
    });

    test('should enable both buttons after reset from max limit', async () => {
      const { result } = renderHook(() => useCounter());
      
      // Set to max value to disable increment
      act(() => {
        for (let i = 0; i < COUNTER_LIMITS.MAX; i++) {
          result.current.increment();
        }
      });

      expect(result.current.canIncrement).toBe(false);

      // Reset
      act(() => {
        result.current.reset();
      });

      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });

      expect(result.current.canIncrement).toBe(true);
      expect(result.current.canDecrement).toBe(true);
    });

    test('should enable both buttons after reset from min limit', async () => {
      const { result } = renderHook(() => useCounter());
      
      // Set to min value to disable decrement
      act(() => {
        for (let i = 0; i > COUNTER_LIMITS.MIN; i--) {
          result.current.decrement();
        }
      });

      expect(result.current.canDecrement).toBe(false);

      // Reset
      act(() => {
        result.current.reset();
      });

      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });

      expect(result.current.canIncrement).toBe(true);
      expect(result.current.canDecrement).toBe(true);
    });

    test('should complete operation within 100ms', async () => {
      const { result } = renderHook(() => useCounter());
      const startTime = Date.now();
      
      act(() => {
        result.current.reset();
      });

      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });

      const endTime = Date.now();
      expect(endTime - startTime).toBeLessThan(100);
    });

    test('should update timestamp on reset', async () => {
      const { result } = renderHook(() => useCounter());
      
      act(() => {
        result.current.reset();
      });

      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });

      expect(result.current.counterState.timestamp).toBe('2023-01-01T00:00:00.000Z');
    });
  });

  describe('Button State Management', () => {
    test('should correctly identify when increment is allowed', () => {
      const { result } = renderHook(() => useCounter());
      
      expect(result.current.canIncrement).toBe(true);
    });

    test('should correctly identify when decrement is allowed', () => {
      const { result } = renderHook(() => useCounter());
      
      expect(result.current.canDecrement).toBe(true);
    });
  });

  describe('State Persistence', () => {
    test('should maintain counter value between operations', async () => {
      const { result } = renderHook(() => useCounter());
      
      act(() => {
        result.current.increment();
      });

      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });

      const firstValue = result.current.counterState.current_value;
      
      act(() => {
        result.current.increment();
      });

      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });

      expect(result.current.counterState.current_value).toBe(firstValue + 1);
    });
  });
});