# Digital Timer App - Frontend Development Guide

## Project Overview

This is a React-based digital timer application built with TypeScript, Vite, and Material-UI. The app provides both countdown and stopwatch functionality with a clean, dark-themed interface optimized for visibility and usability.

## Architecture Decisions

### Why This Structure?

**Feature-Based Organization**: The project follows a feature-based directory structure to enhance modularity and maintainability:

- `src/components/timer/`: Timer-specific components (TimeDisplay, TimerControls, ModeToggle)
- `src/components/common/`: Reusable UI components that could be used across features
- `src/hooks/`: Custom React hooks for timer logic and state management
- `src/utils/`: Utility functions for time formatting, validation, and audio handling
- `src/assets/sounds/`: Audio files for timer notifications

**Material-UI Integration**: We chose Material-UI for several reasons:
- Consistent, professional design system
- Built-in dark theme support (matches spec requirement)
- Accessible components out of the box
- Responsive design capabilities
- Rich component library for buttons, inputs, and layouts

**TypeScript Configuration**: The tsconfig.json is optimized for modern React development:
- Strict type checking enabled for better code quality
- Modern ES2020 target for optimal performance
- Bundler module resolution for Vite compatibility

## Component Architecture

### Core Components to Implement

1. **TimeDisplay Component** (`src/components/timer/TimeDisplay.tsx`)
   - Large, prominent digital display using monospace typography
   - Dynamic formatting (MM:SS vs HH:MM:SS)
   - Color transitions for countdown warnings
   - Responsive scaling for different screen sizes

2. **TimerControls Component** (`src/components/timer/TimerControls.tsx`)
   - Start/Pause toggle button with state-aware text
   - Reset functionality
   - Time input fields for countdown mode
   - Preset duration buttons (1min, 5min, 10min, 30min)
   - Input validation for time values

3. **ModeToggle Component** (`src/components/timer/ModeToggle.tsx`)
   - Switch between Countdown and Stopwatch modes
   - Clear visual indication of current mode

### Custom Hooks

1. **useTimer Hook** (`src/hooks/useTimer.ts`)
   - Manages timer state (running, paused, stopped)
   - Handles interval-based time updates (100ms precision)
   - Provides start, pause, reset, and setTime functions
   - Manages mode switching logic

2. **useAudio Hook** (`src/hooks/useAudio.ts`)
   - Handles audio notification playback
   - Manages audio loading and error states

### Utility Functions

1. **Time Formatting** (`src/utils/timeFormat.ts`)
   - Convert milliseconds to display format
   - Handle MM:SS vs HH:MM:SS logic
   - Validation functions for time inputs

2. **Audio Utils** (`src/utils/audio.ts`)
   - Audio file management
   - Notification sound playback

## Development Guidelines

### State Management Strategy
- **Local State First**: Timer state is managed locally within components using useState and custom hooks
- **Prop Drilling Minimization**: Use custom hooks to share timer logic between components
- **No Global State**: The app is simple enough that Redux/Context is not needed

### Performance Considerations
- **useCallback/useMemo**: Memoize timer functions and computed values to prevent unnecessary re-renders
- **Interval Management**: Properly clean up intervals in useEffect to prevent memory leaks
- **Component Optimization**: Use React.memo for components that receive stable props

### Styling Approach
- **Material-UI Theme**: Leverage MUI's dark theme for consistent styling
- **sx Prop**: Use MUI's sx prop for component-specific styling
- **Responsive Design**: Utilize MUI's breakpoint system for mobile optimization

### Error Handling
- **Input Validation**: Validate time inputs to prevent invalid timer states
- **Audio Fallbacks**: Handle cases where audio files fail to load
- **Timer Edge Cases**: Handle scenarios like negative time values or extremely large durations

## File Structure

```
src/
├── components/
│   ├── timer/           # Timer-specific components
│   │   ├── TimeDisplay.tsx
│   │   ├── TimerControls.tsx
│   │   └── ModeToggle.tsx
│   └── common/          # Reusable components
├── hooks/               # Custom React hooks
│   ├── useTimer.ts
│   └── useAudio.ts
├── utils/               # Utility functions
│   ├── timeFormat.ts
│   └── audio.ts
├── assets/
│   └── sounds/          # Audio notification files
├── App.tsx              # Main application component
└── main.tsx            # Application entry point
```

## Next Steps for Development

1. **Implement Core Timer Logic**: Start with the useTimer hook to manage timer state and intervals
2. **Build TimeDisplay Component**: Create the large digital display with proper formatting
3. **Add Timer Controls**: Implement start/pause/reset functionality with input validation
4. **Integrate Audio Notifications**: Add sound alerts for countdown completion
5. **Responsive Design**: Ensure the app works well on mobile devices
6. **Testing**: Add unit tests for timer logic and component interactions

## Technical Requirements

- **React 18+**: Modern React with hooks and concurrent features
- **TypeScript**: Strict type checking for better code quality
- **Material-UI v5**: Latest version with emotion styling
- **Vite**: Fast development server and build tool
- **ESLint/Prettier**: Code formatting and linting (to be configured)

This architecture provides a solid foundation for building a robust, maintainable timer application while following React best practices and the specified requirements.
