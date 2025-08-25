import React, { useState, useMemo } from 'react';
import {
  Box,
  Button,
  ButtonGroup,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
  Stack,
  Typography,
  Grid,
  Chip,
  Divider,
} from '@mui/material';
import {
  PlayArrow,
  Pause,
  Stop,
  Timer,
  Stopwatch,
} from '@mui/icons-material';
import { TimerMode, UseTimerReturn } from '../../hooks/useTimer';
import {
  timeComponentsToMs,
  msToTimeComponents,
  validateTimeInput,
  PRESET_DURATIONS,
  getPresetLabel,
} from '../../utils/timeFormat';

export interface TimerControlsProps {
  timer: UseTimerReturn;
}

export const TimerControls: React.FC<TimerControlsProps> = ({ timer }) => {
  const {
    time,
    mode,
    state,
    initialTime,
    start,
    pause,
    reset,
    setTime,
    setMode,
    isRunning,
    isPaused,
    isStopped,
  } = timer;

  // Local state for time input fields
  const [inputTime, setInputTime] = useState(() => {
    const { hours, minutes, seconds } = msToTimeComponents(mode === 'countdown' ? Math.max(time, initialTime) : 0);
    return { hours, minutes, seconds };
  });

  // Update input fields when timer time changes (e.g., mode switch)
  React.useEffect(() => {
    if (isStopped && mode === 'countdown') {
      const { hours, minutes, seconds } = msToTimeComponents(Math.max(time, initialTime));
      setInputTime({ hours, minutes, seconds });
    }
  }, [time, initialTime, mode, isStopped]);

  // Handle mode change
  const handleModeChange = (_: React.MouseEvent<HTMLElement>, newMode: TimerMode | null) => {
    if (newMode && newMode !== mode) {
      setMode(newMode);
    }
  };

  // Handle time input changes
  const handleTimeInputChange = (field: 'hours' | 'minutes' | 'seconds') => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = Math.max(0, parseInt(event.target.value) || 0);
    const newInputTime = { ...inputTime, [field]: value };
    
    // Validate and constrain values
    if (field === 'minutes' || field === 'seconds') {
      newInputTime[field] = Math.min(59, value);
    } else if (field === 'hours') {
      newInputTime[field] = Math.min(23, value);
    }
    
    setInputTime(newInputTime);
    
    // Update timer if valid and stopped
    if (isStopped && mode === 'countdown') {
      const { hours, minutes, seconds } = newInputTime;
      if (validateTimeInput(hours, minutes, seconds)) {
        const ms = timeComponentsToMs(hours, minutes, seconds);
        setTime(ms);
      }
    }
  };

  // Handle preset button clicks
  const handlePresetClick = (ms: number) => {
    if (isStopped && mode === 'countdown') {
      setTime(ms);
      const { hours, minutes, seconds } = msToTimeComponents(ms);
      setInputTime({ hours, minutes, seconds });
    }
  };

  // Get main action button content
  const getMainButtonContent = () => {
    if (isRunning) {
      return { icon: <Pause />, text: 'Pause', action: pause };
    } else if (isPaused) {
      return { icon: <PlayArrow />, text: 'Resume', action: start };
    } else {
      return { icon: <PlayArrow />, text: 'Start', action: start };
    }
  };

  const mainButton = getMainButtonContent();

  // Check if start button should be disabled
  const isStartDisabled = useMemo(() => {
    if (mode === 'countdown') {
      return time === 0 && initialTime === 0;
    }
    return false;
  }, [mode, time, initialTime]);

  // Preset buttons for countdown mode
  const presetButtons = Object.entries(PRESET_DURATIONS).map(([key, ms]) => (
    <Chip
      key={key}
      label={getPresetLabel(ms)}
      onClick={() => handlePresetClick(ms)}
      disabled={!isStopped || mode !== 'countdown'}
      variant={time === ms ? 'filled' : 'outlined'}
      color={time === ms ? 'primary' : 'default'}
      sx={{ minWidth: 60 }}
    />
  ));

  return (
    <Box sx={{ width: '100%', maxWidth: 600, mx: 'auto' }}>
      <Stack spacing={3}>
        {/* Mode Toggle */}
        <Box sx={{ display: 'flex', justifyContent: 'center' }}>
          <ToggleButtonGroup
            value={mode}
            exclusive
            onChange={handleModeChange}
            disabled={isRunning}
            size="large"
          >
            <ToggleButton value="countdown" sx={{ px: 3 }}>
              <Timer sx={{ mr: 1 }} />
              Countdown
            </ToggleButton>
            <ToggleButton value="stopwatch" sx={{ px: 3 }}>
              <Stopwatch sx={{ mr: 1 }} />
              Stopwatch
            </ToggleButton>
          </ToggleButtonGroup>
        </Box>

        {/* Countdown Time Input */}
        {mode === 'countdown' && (
          <Box>
            <Typography variant="h6" gutterBottom align="center">
              Set Time
            </Typography>
            <Grid container spacing={2} justifyContent="center" alignItems="center">
              <Grid item>
                <TextField
                  label="Hours"
                  type="number"
                  value={inputTime.hours}
                  onChange={handleTimeInputChange('hours')}
                  disabled={!isStopped}
                  inputProps={{ min: 0, max: 23, step: 1 }}
                  sx={{ width: 80 }}
                  size="small"
                />
              </Grid>
              <Grid item>
                <Typography variant="h5">:</Typography>
              </Grid>
              <Grid item>
                <TextField
                  label="Minutes"
                  type="number"
                  value={inputTime.minutes}
                  onChange={handleTimeInputChange('minutes')}
                  disabled={!isStopped}
                  inputProps={{ min: 0, max: 59, step: 1 }}
                  sx={{ width: 80 }}
                  size="small"
                />
              </Grid>
              <Grid item>
                <Typography variant="h5">:</Typography>
              </Grid>
              <Grid item>
                <TextField
                  label="Seconds"
                  type="number"
                  value={inputTime.seconds}
                  onChange={handleTimeInputChange('seconds')}
                  disabled={!isStopped}
                  inputProps={{ min: 0, max: 59, step: 1 }}
                  sx={{ width: 80 }}
                  size="small"
                />
              </Grid>
            </Grid>

            {/* Preset Buttons */}
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom align="center">
                Quick Select
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center', flexWrap: 'wrap' }}>
                {presetButtons}
              </Box>
            </Box>
          </Box>
        )}

        <Divider />

        {/* Main Controls */}
        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2 }}>
          <Button
            variant="contained"
            size="large"
            startIcon={mainButton.icon}
            onClick={mainButton.action}
            disabled={isStartDisabled}
            sx={{
              minWidth: 120,
              height: 56,
              fontSize: '1.1rem',
              backgroundColor: isRunning ? 'warning.main' : 'primary.main',
              '&:hover': {
                backgroundColor: isRunning ? 'warning.dark' : 'primary.dark',
              },
            }}
          >
            {mainButton.text}
          </Button>
          
          <Button
            variant="outlined"
            size="large"
            startIcon={<Stop />}
            onClick={reset}
            disabled={isStopped}
            sx={{
              minWidth: 120,
              height: 56,
              fontSize: '1.1rem',
            }}
          >
            Reset
          </Button>
        </Box>

        {/* Timer State Info */}
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            {mode === 'countdown' ? 'Countdown Timer' : 'Stopwatch'} • {' '}
            {state === 'running' && 'Running'}
            {state === 'paused' && 'Paused'}
            {state === 'stopped' && 'Stopped'}
          </Typography>
        </Box>
      </Stack>
    </Box>
  );
};