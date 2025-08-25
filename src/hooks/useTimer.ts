import { useState, useEffect, useRef, useCallback } from 'react';

export type TimerMode = 'countdown' | 'stopwatch';
export type TimerState = 'stopped' | 'running' | 'paused';

export interface UseTimerReturn {
  // State
  time: number; // Current time in milliseconds
  mode: TimerMode;
  state: TimerState;
  initialTime: number; // For countdown mode, the starting time
  
  // Actions
  start: () => void;
  pause: () => void;
  reset: () => void;
  setTime: (ms: number) => void;
  setMode: (mode: TimerMode) => void;
  
  // Computed values
  isRunning: boolean;
  isPaused: boolean;
  isStopped: boolean;
  isCountdownComplete: boolean;
}

const INTERVAL_MS = 100; // Update every 100ms for smooth animation

export const useTimer = (defaultMode: TimerMode = 'countdown'): UseTimerReturn => {
  const [mode, setMode] = useState<TimerMode>(defaultMode);
  const [state, setState] = useState<TimerState>('stopped');
  const [time, setTime] = useState<number>(0);
  const [initialTime, setInitialTime] = useState<number>(0);
  
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const lastUpdateRef = useRef<number>(0);

  // Clear interval when component unmounts or timer stops
  const clearInterval = useCallback(() => {
    if (intervalRef.current) {
      window.clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  // Start the timer
  const start = useCallback(() => {
    if (state === 'stopped' && mode === 'countdown' && time === 0) {
      // Cannot start countdown with 0 time
      return;
    }
    
    setState('running');
    lastUpdateRef.current = Date.now();
    
    if (!intervalRef.current) {
      intervalRef.current = setInterval(() => {
        const now = Date.now();
        const elapsed = now - lastUpdateRef.current;
        lastUpdateRef.current = now;
        
        setTime(prevTime => {
          if (mode === 'countdown') {
            const newTime = Math.max(0, prevTime - elapsed);
            
            // If countdown reaches zero, trigger completion
            if (newTime === 0 && prevTime > 0) {
              setState('stopped');
            }
            
            return newTime;
          } else {
            // Stopwatch mode - count up
            return prevTime + elapsed;
          }
        });
      }, INTERVAL_MS);
    }
  }, [state, mode, time]);

  // Pause the timer
  const pause = useCallback(() => {
    if (state === 'running') {
      setState('paused');
      clearInterval();
    }
  }, [state, clearInterval]);

  // Reset the timer
  const reset = useCallback(() => {
    setState('stopped');
    clearInterval();
    
    if (mode === 'countdown') {
      setTime(initialTime);
    } else {
      setTime(0);
    }
  }, [mode, initialTime, clearInterval]);

  // Set timer time (for countdown mode)
  const setTimerTime = useCallback((ms: number) => {
    if (state === 'stopped') {
      setTime(ms);
      if (mode === 'countdown') {
        setInitialTime(ms);
      }
    }
  }, [state, mode]);

  // Set timer mode
  const setTimerMode = useCallback((newMode: TimerMode) => {
    if (newMode !== mode) {
      setState('stopped');
      clearInterval();
      setMode(newMode);
      
      if (newMode === 'stopwatch') {
        setTime(0);
        setInitialTime(0);
      } else {
        // Countdown mode - keep current time if valid, otherwise reset
        if (time === 0) {
          setTime(initialTime || 0);
        }
      }
    }
  }, [mode, time, initialTime, clearInterval]);

  // Computed values
  const isRunning = state === 'running';
  const isPaused = state === 'paused';
  const isStopped = state === 'stopped';
  const isCountdownComplete = mode === 'countdown' && time === 0 && initialTime > 0;

  // Cleanup on unmount
  useEffect(() => {
    return clearInterval;
  }, [clearInterval]);

  // Stop timer when countdown reaches 0
  useEffect(() => {
    if (mode === 'countdown' && time === 0 && state === 'running') {
      setState('stopped');
      clearInterval();
    }
  }, [mode, time, state, clearInterval]);


  return {
    // State
    time,
    mode,
    state,
    initialTime,
    
    // Actions
    start,
    pause,
    reset,
    setTime: setTimerTime,
    setMode: setTimerMode,
    
    // Computed values
    isRunning,
    isPaused,
    isStopped,
    isCountdownComplete,
  };
};