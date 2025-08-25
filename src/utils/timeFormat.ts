/**
 * Time formatting utilities for the digital timer application
 */

export interface TimeComponents {
  hours: number;
  minutes: number;
  seconds: number;
  milliseconds: number;
}

/**
 * Converts milliseconds to time components
 */
export const msToTimeComponents = (ms: number): TimeComponents => {
  const totalSeconds = Math.floor(ms / 1000);
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  const milliseconds = ms % 1000;

  return { hours, minutes, seconds, milliseconds };
};

/**
 * Converts time components to total milliseconds
 */
export const timeComponentsToMs = (hours: number, minutes: number, seconds: number): number => {
  return (hours * 3600 + minutes * 60 + seconds) * 1000;
};

/**
 * Formats time for display (MM:SS or HH:MM:SS)
 */
export const formatTime = (ms: number, showMilliseconds = false): string => {
  const { hours, minutes, seconds, milliseconds } = msToTimeComponents(ms);
  
  // Pad numbers with leading zeros
  const pad = (num: number, length = 2): string => num.toString().padStart(length, '0');
  
  let formatted = '';
  
  // Show hours only if > 0 or if we have more than 59 minutes
  if (hours > 0) {
    formatted = `${pad(hours)}:${pad(minutes)}:${pad(seconds)}`;
  } else {
    formatted = `${pad(minutes)}:${pad(seconds)}`;
  }
  
  if (showMilliseconds) {
    formatted += `.${pad(Math.floor(milliseconds / 10))}`;
  }
  
  return formatted;
};

/**
 * Validates time input values
 */
export const validateTimeInput = (hours: number, minutes: number, seconds: number): boolean => {
  return (
    hours >= 0 && hours <= 23 &&
    minutes >= 0 && minutes <= 59 &&
    seconds >= 0 && seconds <= 59
  );
};

/**
 * Parses time string input (HH:MM:SS or MM:SS) to milliseconds
 */
export const parseTimeString = (timeString: string): number => {
  const parts = timeString.split(':').map(part => parseInt(part, 10));
  
  if (parts.length === 2) {
    // MM:SS format
    const [minutes, seconds] = parts;
    if (validateTimeInput(0, minutes, seconds)) {
      return timeComponentsToMs(0, minutes, seconds);
    }
  } else if (parts.length === 3) {
    // HH:MM:SS format
    const [hours, minutes, seconds] = parts;
    if (validateTimeInput(hours, minutes, seconds)) {
      return timeComponentsToMs(hours, minutes, seconds);
    }
  }
  
  return 0; // Invalid input returns 0
};

/**
 * Gets the color for countdown display based on remaining time
 */
export const getCountdownColor = (ms: number): 'success' | 'warning' | 'error' => {
  if (ms > 30000) return 'success'; // Green for > 30 seconds
  if (ms > 10000) return 'warning'; // Yellow for 10-30 seconds
  return 'error'; // Red for < 10 seconds
};

/**
 * Common preset durations in milliseconds
 */
export const PRESET_DURATIONS = {
  oneMinute: 60 * 1000,
  fiveMinutes: 5 * 60 * 1000,
  tenMinutes: 10 * 60 * 1000,
  thirtyMinutes: 30 * 60 * 1000,
} as const;

/**
 * Gets preset duration labels
 */
export const getPresetLabel = (ms: number): string => {
  switch (ms) {
    case PRESET_DURATIONS.oneMinute: return '1 min';
    case PRESET_DURATIONS.fiveMinutes: return '5 min';
    case PRESET_DURATIONS.tenMinutes: return '10 min';
    case PRESET_DURATIONS.thirtyMinutes: return '30 min';
    default: return 'Custom';
  }
};