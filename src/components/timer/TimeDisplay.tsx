import React from 'react';
import { Typography, Box, useTheme } from '@mui/material';
import { formatTime, getCountdownColor } from '../../utils/timeFormat';
import { TimerMode } from '../../hooks/useTimer';

export interface TimeDisplayProps {
  time: number; // Time in milliseconds
  mode: TimerMode;
  isRunning: boolean;
  isCountdownComplete: boolean;
  showMilliseconds?: boolean;
}

export const TimeDisplay: React.FC<TimeDisplayProps> = ({
  time,
  mode,
  isRunning,
  isCountdownComplete,
  showMilliseconds = false,
}) => {
  const theme = useTheme();

  // Get color based on mode and time remaining
  const getDisplayColor = () => {
    if (isCountdownComplete) {
      return theme.palette.error.main;
    }
    
    if (mode === 'countdown') {
      const colorVariant = getCountdownColor(time);
      switch (colorVariant) {
        case 'success': return theme.palette.success.main;
        case 'warning': return theme.palette.warning.main;
        case 'error': return theme.palette.error.main;
        default: return theme.palette.primary.main;
      }
    }
    
    return theme.palette.primary.main;
  };

  // Get background glow effect for countdown completion
  const getBackgroundStyle = () => {
    if (isCountdownComplete && isRunning) {
      return {
        backgroundColor: `${theme.palette.error.main}20`,
        borderRadius: 2,
        animation: 'pulse 1s ease-in-out infinite alternate',
      };
    }
    return {};
  };

  // Format the time display
  const displayTime = formatTime(time, showMilliseconds && mode === 'stopwatch');

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        p: { xs: 2, sm: 4 },
        ...getBackgroundStyle(),
        // CSS keyframes for pulse animation
        '@keyframes pulse': {
          '0%': { opacity: 0.8 },
          '100%': { opacity: 1.0 },
        },
      }}
    >
      <Typography
        variant="h1"
        component="div"
        sx={{
          fontFamily: '"Roboto Mono", "Courier New", monospace',
          fontWeight: 300,
          fontSize: {
            xs: '3rem',    // Mobile: smaller but still prominent
            sm: '4rem',    // Small screens
            md: '6rem',    // Medium screens
            lg: '8rem',    // Large screens: very prominent
          },
          color: getDisplayColor(),
          textAlign: 'center',
          letterSpacing: '0.1em',
          lineHeight: 1,
          transition: theme.transitions.create(['color'], {
            duration: theme.transitions.duration.short,
          }),
          // Text glow effect for countdown completion
          ...(isCountdownComplete && {
            textShadow: `0 0 20px ${theme.palette.error.main}50`,
          }),
          // Subtle shadow for better visibility
          textShadow: isCountdownComplete 
            ? `0 0 30px ${theme.palette.error.main}80`
            : `0 2px 8px ${theme.palette.background.default}80`,
        }}
      >
        {displayTime}
      </Typography>
    </Box>
  );
};