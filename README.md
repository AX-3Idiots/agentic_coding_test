# Counter Application with Data Persistence

A comprehensive counter application implementing robust data persistence and storage management features.

## Features

### 🔄 Auto-Save & Auto-Restore
- **Automatic saving**: Counter value saves automatically on each change
- **Timestamp tracking**: Every save includes timestamp information
- **Debounced writes**: Prevents excessive storage operations (300ms debounce)
- **Performance optimized**: Save operations complete within 50ms
- **Auto-restore**: Counter value loads automatically on application start
- **Graceful defaults**: Defaults to 0 if no saved value exists

### 📊 Session Management
- **Session persistence**: Session data persists across app launches
- **Usage statistics**: Tracks increments, decrements, resets, and total operations
- **Automatic cleanup**: Old session data is cleaned up periodically
- **Timestamp tracking**: Records session start time and last activity

### 🚫 Offline Support
- **Works offline**: All counter operations work without internet connection
- **Data validation**: Validates data when loading from local storage
- **Corruption recovery**: Handles damaged data gracefully
- **Error handling**: Storage errors are handled with user notifications
- **Schema migration**: Supports data migration between versions

### 💾 Backup & Restore
- **Export functionality**: Export counter data to downloadable JSON file
- **Import functionality**: Import counter data from uploaded JSON file
- **Data validation**: Ensures imported data is valid before applying
- **User confirmation**: Requires confirmation before overwriting existing data
- **Clear error messages**: Provides helpful error messages for invalid files

## Technology Stack

### Backend (FastAPI)
- **FastAPI**: Modern, fast web framework for Python
- **Pydantic**: Data validation and serialization
- **Atomic file operations**: Prevents data corruption during saves
- **JSON storage**: Simple, human-readable data format
- **Performance monitoring**: Tracks operation timing

### Frontend (React + TypeScript)
- **React 18**: Modern React with concurrent features
- **TypeScript**: Type-safe development
- **Local Storage**: Browser-based caching and offline support
- **Performance tracking**: Monitors operation performance
- **Responsive design**: Works on desktop and mobile devices

## Getting Started

### Prerequisites
- Python 3.8+ (for backend)
- Node.js 16+ (for frontend)

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## API Endpoints

### Counter Operations
- `GET /api/counter` - Get current counter value
- `POST /api/counter/increment` - Increment counter
- `POST /api/counter/decrement` - Decrement counter
- `POST /api/counter/reset` - Reset counter to 0

### Session Management
- `GET /api/session` - Get current session data
- `POST /api/session/start` - Start new session

### Backup Operations
- `GET /api/backup/export` - Export data as JSON
- `POST /api/backup/import` - Import data from JSON

### Monitoring
- `GET /api/health` - Health check endpoint

## Data Storage

### Backend Storage
- **Location**: `backend/data/` directory
- **Format**: JSON files for human readability
- **Files**:
  - `counter.json`: Counter value, timestamp, and version
  - `session.json`: Session statistics and metadata

### Frontend Storage
- **Location**: Browser localStorage
- **Caching**: Automatic caching for offline support
- **Expiration**: 24-hour cache expiration for counter data
- **Migration**: Automatic schema migration between versions

## Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Performance Characteristics

- **Save operations**: Complete within 50ms
- **Debounced writes**: 300ms debounce prevents excessive operations
- **Memory usage**: Minimal memory footprint
- **Storage efficiency**: Compact JSON format
- **Network optimization**: Efficient API calls with error handling

## Error Handling

- **Network errors**: Graceful fallback to local storage
- **Data corruption**: Automatic recovery with default values
- **Invalid input**: Comprehensive validation with user feedback
- **Storage failures**: Non-blocking error handling
- **Import errors**: Clear error messages for invalid backup files

## Browser Compatibility

- **Modern browsers**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Mobile support**: iOS Safari, Chrome Mobile
- **Offline support**: Service worker for offline functionality
- **Local storage**: 5MB+ storage capacity recommended

## Architecture

### Data Flow
1. **User action** → Counter component
2. **Debounced save** → Local storage (immediate)
3. **API call** → Backend service (if online)
4. **Response** → Update UI with confirmation

### Error Recovery
1. **Network failure** → Continue with local storage
2. **Data corruption** → Reset to default values
3. **Storage full** → Clean up expired cache data
4. **Import error** → Validate and show specific error messages

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License.
