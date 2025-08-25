import { useState, useCallback, useRef } from 'react';

export interface UseAudioReturn {
  play: () => Promise<void>;
  stop: () => void;
  isPlaying: boolean;
  error: string | null;
}

/**
 * Custom hook for managing audio playback
 * Creates a programmatic beep sound for timer notifications
 */
export const useAudio = (): UseAudioReturn => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const gainNodeRef = useRef<GainNode | null>(null);
  const oscillatorRef = useRef<OscillatorNode | null>(null);

  // Initialize audio context
  const initAudioContext = useCallback(() => {
    if (!audioContextRef.current) {
      try {
        audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
        gainNodeRef.current = audioContextRef.current.createGain();
        gainNodeRef.current.connect(audioContextRef.current.destination);
      } catch (err) {
        setError('Audio not supported in this browser');
      }
    }
  }, []);

  // Create and play a beep sound
  const play = useCallback(async (): Promise<void> => {
    try {
      setError(null);
      initAudioContext();
      
      if (!audioContextRef.current || !gainNodeRef.current) {
        throw new Error('Audio context not available');
      }

      // Resume audio context if suspended (required by browser autoplay policies)
      if (audioContextRef.current.state === 'suspended') {
        await audioContextRef.current.resume();
      }

      setIsPlaying(true);

      // Create oscillator for beep sound
      const oscillator = audioContextRef.current.createOscillator();
      oscillatorRef.current = oscillator;
      
      // Configure the beep sound
      oscillator.type = 'sine';
      oscillator.frequency.setValueAtTime(800, audioContextRef.current.currentTime); // 800Hz beep
      
      // Create envelope for smooth attack/decay
      const now = audioContextRef.current.currentTime;
      gainNodeRef.current.gain.setValueAtTime(0, now);
      gainNodeRef.current.gain.linearRampToValueAtTime(0.3, now + 0.01); // Quick attack
      gainNodeRef.current.gain.exponentialRampToValueAtTime(0.01, now + 0.3); // Decay over 300ms
      
      // Connect and start
      oscillator.connect(gainNodeRef.current);
      oscillator.start(now);
      
      // Stop after the envelope completes
      oscillator.stop(now + 0.3);
      
      // Clean up when finished
      oscillator.onended = () => {
        setIsPlaying(false);
        oscillatorRef.current = null;
      };
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to play audio');
      setIsPlaying(false);
    }
  }, [initAudioContext]);

  // Stop the current sound
  const stop = useCallback(() => {
    if (oscillatorRef.current && audioContextRef.current) {
      try {
        oscillatorRef.current.stop();
      } catch (err) {
        // Oscillator might already be stopped
      }
      oscillatorRef.current = null;
      setIsPlaying(false);
    }
  }, []);

  return {
    play,
    stop,
    isPlaying,
    error,
  };
};

/**
 * Alternative hook that plays multiple beeps for completion notification
 */
export const useCompletionSound = (): UseAudioReturn => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  const initAudioContext = useCallback(() => {
    if (!audioContextRef.current) {
      try {
        audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      } catch (err) {
        setError('Audio not supported in this browser');
      }
    }
  }, []);

  const playBeep = useCallback(async (frequency: number, duration: number, delay: number = 0): Promise<void> => {
    if (!audioContextRef.current) return;

    return new Promise((resolve) => {
      setTimeout(async () => {
        if (!audioContextRef.current) {
          resolve();
          return;
        }

        // Resume context if needed
        if (audioContextRef.current.state === 'suspended') {
          await audioContextRef.current.resume();
        }

        const oscillator = audioContextRef.current.createOscillator();
        const gainNode = audioContextRef.current.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContextRef.current.destination);
        
        oscillator.type = 'sine';
        oscillator.frequency.setValueAtTime(frequency, audioContextRef.current.currentTime);
        
        const now = audioContextRef.current.currentTime;
        gainNode.gain.setValueAtTime(0, now);
        gainNode.gain.linearRampToValueAtTime(0.2, now + 0.01);
        gainNode.gain.exponentialRampToValueAtTime(0.01, now + duration);
        
        oscillator.start(now);
        oscillator.stop(now + duration);
        
        setTimeout(resolve, duration * 1000);
      }, delay);
    });
  }, []);

  const play = useCallback(async (): Promise<void> => {
    try {
      setError(null);
      initAudioContext();
      
      if (!audioContextRef.current) {
        throw new Error('Audio context not available');
      }

      setIsPlaying(true);

      // Play three ascending beeps
      await playBeep(600, 0.2, 0);
      await playBeep(800, 0.2, 100);
      await playBeep(1000, 0.4, 100);
      
      setIsPlaying(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to play audio');
      setIsPlaying(false);
    }
  }, [initAudioContext, playBeep]);

  const stop = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    setIsPlaying(false);
  }, []);

  return {
    play,
    stop,
    isPlaying,
    error,
  };
};