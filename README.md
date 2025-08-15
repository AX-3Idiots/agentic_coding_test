# Counter Application

A React-based counter application with comprehensive state management, session tracking, and immediate UI updates. This application implements core counter logic with validation, limits, and proper user feedback.

## Features

### Core Counter Logic
- **State Management**: Maintains current value and timestamp for all operations
- **Increment Operation**: Adds 1 to counter with maximum limit of 999,999
- **Decrement Operation**: Subtracts 1 from counter with minimum limit of -999,999
- **Reset Operation**: Sets counter to 0 regardless of current value
- **Immediate UI Updates**: All operations complete within 100ms with instant feedback

### Session Tracking
- **Unique Session ID**: Generated on application start
- **Last Accessed Tracking**: Updates on counter operations
- **Session Persistence**: Maintains session data throughout user interactions

### User Interface
- **Responsive Design**: Works on desktop and mobile devices
- **Button State Management**: Buttons disabled at limits with visual feedback
- **Number Formatting**: Large numbers displayed with proper thousands separators
- **Visual Feedback**: Limit notifications and smooth animations
- **Accessibility**: Proper ARIA labels and keyboard navigation

## Project Structure

```
src/
├── components/          # React components
│   ├── Counter.js      # Main counter component
│   ├── Counter.css     # Component styles
│   └── Counter.test.js # Component tests
├── hooks/              # Custom React hooks
│   ├── useCounter.js   # Counter state management
│   ├── useCounter.test.js
│   ├── useSession.js   # Session tracking
│   └── useSession.test.js
├── utils/              # Utility functions
│   ├── sessionUtils.js # Session utilities
│   └── sessionUtils.test.js
├── types/              # Type definitions and constants
│   └── index.js        # Domain models and limits
├── App.js              # Main application component
├── App.css             # Application styles
├── index.js            # Application entry point
├── index.css           # Global styles
└── setupTests.js       # Test configuration
```

## Implementation Details

### Counter State Management
The counter uses a custom `useCounter` hook that:
- Maintains current value and timestamp in state
- Implements validation for min/max limits (-999,999 to 999,999)
- Provides operations (increment, decrement, reset) with success/failure feedback
- Updates timestamps automatically on each operation
- Ensures operations complete within 100ms

### Session Tracking
The session tracking uses a custom `useSession` hook that:
- Generates unique session IDs using timestamp and random components
- Tracks last accessed time
- Updates session data on counter operations
- Follows domain model specifications

### UI Components
The main Counter component:
- Displays counter value with proper number formatting
- Manages button states based on counter limits
- Shows visual feedback when limits are reached
- Updates immediately without visible delay
- Provides accessibility features with proper titles and ARIA labels

## Domain Model

### Counter State
```javascript
{
  current_value: number,    // Current counter value
  timestamp: string         // ISO timestamp of last modification
}
```

### Session State
```javascript
{
  session_id: string,       // Unique session identifier
  last_accessed: string     // ISO timestamp of last access
}
```

## Constants
- **Maximum Value**: 999,999
- **Minimum Value**: -999,999
- **Operation Timeout**: 100ms

## Testing

The application includes comprehensive unit tests for:
- Counter state management and operations
- Session tracking functionality
- UI component behavior and rendering
- Button state management and accessibility
- Number formatting and visual feedback
- Utility functions and edge cases

Test coverage includes:
- Initial state validation
- Operation success/failure scenarios
- Limit boundary testing
- Performance validation (100ms timeout)
- Session data structure compliance
- UI update responsiveness

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Run the application:
   ```bash
   npm start
   ```

3. Run tests:
   ```bash
   npm test
   ```

4. Build for production:
   ```bash
   npm run build
   ```

## Technical Requirements Met

✅ Counter state holds current_value and timestamp  
✅ Timestamp updates automatically on each operation  
✅ Counter value persists between operations  
✅ State structure matches domain model requirements  
✅ Increment operation adds exactly 1 to current value  
✅ Counter cannot exceed maximum value of 999,999  
✅ Increment button becomes disabled when maximum value is reached  
✅ Operation completes within 100ms  
✅ Visual feedback provided when limit is reached  
✅ Decrement operation subtracts exactly 1 from current value  
✅ Counter cannot go below minimum value of -999,999  
✅ Decrement button becomes disabled when minimum value is reached  
✅ Reset operation sets counter value to exactly 0  
✅ Reset works regardless of current counter value  
✅ Both increment and decrement buttons become enabled after reset  
✅ Timestamp updates to current time on reset  
✅ Counter value displays immediately on state change  
✅ No visible delay between button press and display update  
✅ Proper number formatting for large positive and negative values  
✅ Display updates are smooth and without flickering  
✅ Unique session_id generated on application start  
✅ Last_accessed timestamp tracked and updated  
✅ Session data updates on counter operations  
✅ Session data structure matches domain model specifications