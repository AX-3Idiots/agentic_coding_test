# Timer API with Background Processing & Notifications

A comprehensive FastAPI-based timer application with background processing, notifications, and audio alerts. This application extends a basic authentication system to provide full-featured timer functionality.

## 📁 Project Structure

```
├── README.md                 # Project documentation
├── CLAUDE.md                # AI collaboration guidelines
├── main.py                  # FastAPI application entry point
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore patterns
├── users.json              # Development user data store
└── docs/                   # Additional documentation
    ├── API_TEST_GUIDE.md   # API testing guide
    └── SETUP_GUIDE.md      # Detailed setup instructions
```

## ✨ Features

### Authentication & Security
- **User Registration**: Create new accounts with email and password
- **User Authentication**: Login with JWT token generation
- **Protected Endpoints**: Access user information with JWT token verification
- **Password Security**: Secure password hashing using bcrypt
- **Input Validation**: Request/response validation with Pydantic models

### Timer Management
- **Full Timer CRUD**: Create, update, delete, and manage timers
- **Timer States**: Support for created, running, paused, completed, and cancelled states
- **Accurate Timing**: Background processing maintains precise timer accuracy
- **Persistent Storage**: Timers survive app restarts with automatic recovery
- **User Isolation**: Each user's timers are completely isolated

### Background Processing & Notifications
- **Background Scheduler**: APScheduler handles timer completion events
- **Cross-Platform Notifications**: System notifications using plyer
- **Scheduled Alerts**: Notifications fire at exact timer completion times
- **Notification Settings**: User-configurable notification preferences
- **Resource Recovery**: Handles app suspension/resume without time loss

### Audio Alert System
- **Multiple Audio Formats**: Support for MP3, WAV, OGG files
- **Built-in Sounds**: 5 pre-included alert sounds (chime, bell, beep, nature, digital)
- **Custom Sound Upload**: Users can upload custom alert sounds (max 5MB)
- **Volume Control**: Per-timer volume settings with system integration
- **Background Playback**: Non-blocking audio playback

### Resource Management
- **Wake Lock Management**: Prevents system sleep during active timers
- **CPU Usage Monitoring**: Real-time CPU usage tracking and optimization
- **Power Saving Modes**: User-configurable power management settings
- **Efficient Processing**: Minimal CPU usage during background operation (under 1%)

## 🛠 Technology Stack

- **[FastAPI](https://fastapi.tiangolo.com/)**: High-performance web framework for Python
- **[bcrypt](https://pypi.org/project/bcrypt/)**: Secure password hashing
- **[PyJWT](https://pypi.org/project/PyJWT/)**: JWT token creation and verification
- **[uvicorn](https://www.uvicorn.org/)**: Lightning-fast ASGI server
- **[Pydantic](https://docs.pydantic.dev/)**: Data validation using Python type hints

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. **Create and activate virtual environment** (recommended)
   ```bash
   # Using venv
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Or using conda
   conda create -n fastapi-auth python=3.8
   conda activate fastapi-auth
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment** (optional)
   ```bash
   cp .env.example .env
   # Edit .env file to customize configuration
   ```

5. **Start the development server**
   ```bash
   uvicorn main:app --reload
   ```

6. **Access the API**
   - API Server: http://localhost:8000
   - Interactive API Documentation: http://localhost:8000/docs
   - Alternative Documentation: http://localhost:8000/redoc

## 📋 API Endpoints

### Authentication

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| POST | `/register` | Create new user account | None |
| POST | `/login` | Authenticate user and get JWT token | None |
| GET | `/me` | Get current user information | JWT Bearer Token |

### Timer Management

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| POST | `/timers` | Create a new timer | JWT Bearer Token |
| GET | `/timers` | List all user timers | JWT Bearer Token |
| GET | `/timers/{timer_id}` | Get specific timer details | JWT Bearer Token |
| PUT | `/timers/{timer_id}` | Update timer settings | JWT Bearer Token |
| DELETE | `/timers/{timer_id}` | Delete timer | JWT Bearer Token |

### Timer Operations

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| POST | `/timers/{timer_id}/start` | Start timer | JWT Bearer Token |
| POST | `/timers/{timer_id}/pause` | Pause running timer | JWT Bearer Token |
| POST | `/timers/{timer_id}/stop` | Stop/cancel timer | JWT Bearer Token |

### Sound Management

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| POST | `/sounds/upload` | Upload custom sound file | JWT Bearer Token |
| GET | `/sounds/available` | List available sounds | JWT Bearer Token |

### System Management

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| GET | `/system/status` | Get system status and resource usage | JWT Bearer Token |
| GET | `/system/notifications/settings` | Get notification settings | JWT Bearer Token |
| POST | `/system/notifications/settings` | Update notification settings | JWT Bearer Token |
| POST | `/system/test-notification` | Send test notification | JWT Bearer Token |
| POST | `/system/test-sound` | Play test sound | JWT Bearer Token |

### Request/Response Examples

See [API_TEST_GUIDE.md](docs/API_TEST_GUIDE.md) for detailed examples and testing instructions.

## 🔧 Configuration

The application can be configured using environment variables. Copy `.env.example` to `.env` and modify as needed:

```bash
# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Server
HOST=0.0.0.0
PORT=8000

# Development
ENVIRONMENT=development
DEBUG=true
```

## 💾 Data Storage

For development purposes, user information is temporarily stored in a JSON file (`users.json`). 

**⚠️ Important**: For production environments, replace the JSON file storage with a proper database system like PostgreSQL, MySQL, or MongoDB.

## 🔒 Security Features

- **Password Hashing**: All passwords are securely hashed using bcrypt
- **JWT Tokens**: Stateless authentication with configurable expiration
- **Input Validation**: All API inputs are validated using Pydantic models
- **Environment Variables**: Sensitive configuration stored in environment variables
- **CORS Support**: Configurable CORS settings for frontend integration

## 💡 Usage Examples

### User Registration and Login
```bash
# Register a new user
curl -X POST "http://localhost:8000/register" \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "yourpassword"}'

# Login to get JWT token
curl -X POST "http://localhost:8000/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "yourpassword"}'
```

### Timer Management
```bash
# Create a 5-minute timer with chime alert
curl -X POST "http://localhost:8000/timers" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"label": "Pomodoro Session", "duration_seconds": 300, "alert_sound": "chime", "volume": 0.8}'

# List all your timers
curl -X GET "http://localhost:8000/timers" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Start a timer
curl -X POST "http://localhost:8000/timers/{timer_id}/start" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Check timer status
curl -X GET "http://localhost:8000/timers/{timer_id}" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Pause timer
curl -X POST "http://localhost:8000/timers/{timer_id}/pause" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Sound Management
```bash
# Upload custom sound file
curl -X POST "http://localhost:8000/sounds/upload" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -F "file=@custom_alert.wav"

# List available sounds
curl -X GET "http://localhost:8000/sounds/available" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Test a sound
curl -X POST "http://localhost:8000/system/test-sound?sound=chime&volume=0.5" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### System Status and Configuration
```bash
# Get system status
curl -X GET "http://localhost:8000/system/status" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Test notification system
curl -X POST "http://localhost:8000/system/test-notification" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Update notification settings
curl -X POST "http://localhost:8000/system/notifications/settings" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"enabled": true, "power_saving_mode": "balanced"}'
```

## 🧪 Testing

Run the comprehensive test suite:
```bash
# Install test dependencies (if not already installed)
pip install pytest httpx

# Run all tests
pytest test_timers.py -v

# Run specific test categories
pytest test_timers.py::TestTimerCRUD -v          # Timer CRUD operations
pytest test_timers.py::TestTimerOperations -v    # Timer start/pause/stop
pytest test_timers.py::TestSoundManagement -v    # Sound management
pytest test_timers.py::TestSystemStatus -v       # System status and settings
```

The test suite covers:
- Timer CRUD operations
- Timer state transitions and operations  
- Authentication and authorization
- Sound management and file upload
- System status and notifications
- Error handling and edge cases
- Background processing functionality

For detailed testing instructions, see [API_TEST_GUIDE.md](docs/API_TEST_GUIDE.md).

## 📚 Documentation

- [Setup Guide](docs/SETUP_GUIDE.md) - Detailed setup and deployment instructions
- [API Test Guide](docs/API_TEST_GUIDE.md) - Complete API testing examples
- [AI Collaboration Guidelines](CLAUDE.md) - Development guidelines and best practices

## 🤝 Contributing

Please read [CLAUDE.md](CLAUDE.md) for detailed development guidelines, coding standards, and collaboration rules.

## 📝 License

This project is intended for educational and development purposes.
