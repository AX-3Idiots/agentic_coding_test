import React, { useEffect } from "react";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import { AppBar, Toolbar, Typography, Container, Box, Paper } from "@mui/material";
import { Timer } from "@mui/icons-material";
import { useTimer } from "./hooks/useTimer";
import { useCompletionSound } from "./hooks/useAudio";
import { TimeDisplay } from "./components/timer/TimeDisplay";
import { TimerControls } from "./components/timer/TimerControls";

const darkTheme = createTheme({
  palette: {
    mode: "dark",
    primary: {
      main: "#90caf9",
    },
    success: {
      main: "#4caf50",
    },
    warning: {
      main: "#ff9800",
    },
    error: {
      main: "#f44336",
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

function App() {
  const timer = useTimer('countdown');
  const completionSound = useCompletionSound();

  // Play sound when countdown completes
  useEffect(() => {
    if (timer.isCountdownComplete && timer.mode === 'countdown') {
      completionSound.play().catch(console.error);
    }
  }, [timer.isCountdownComplete, timer.mode, completionSound]);

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <AppBar position="static" elevation={0}>
        <Toolbar>
          <Timer sx={{ mr: 2 }} />
          <Typography variant="h6" component="div">
            Digital Timer
          </Typography>
        </Toolbar>
      </AppBar>
      
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            minHeight: 'calc(100vh - 200px)',
            gap: 4,
          }}
        >
          {/* Time Display */}
          <Paper
            elevation={3}
            sx={{
              width: '100%',
              maxWidth: 800,
              borderRadius: 3,
              overflow: 'hidden',
            }}
          >
            <TimeDisplay
              time={timer.time}
              mode={timer.mode}
              isRunning={timer.isRunning}
              isCountdownComplete={timer.isCountdownComplete}
              showMilliseconds={timer.mode === 'stopwatch'}
            />
          </Paper>

          {/* Timer Controls */}
          <Paper
            elevation={2}
            sx={{
              width: '100%',
              maxWidth: 600,
              p: 3,
              borderRadius: 3,
            }}
          >
            <TimerControls timer={timer} />
          </Paper>

          {/* Footer Info */}
          <Box sx={{ textAlign: 'center', mt: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Use Countdown for timed activities or Stopwatch for tracking elapsed time
            </Typography>
            {completionSound.error && (
              <Typography variant="body2" color="error" sx={{ mt: 1 }}>
                Audio notification not available: {completionSound.error}
              </Typography>
            )}
          </Box>
        </Box>
      </Container>
    </ThemeProvider>
  );
}

export default App;
