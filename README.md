# FastAPI Authentication API

A robust authentication API server built with FastAPI that provides email/password-based user registration, login, and JWT token authentication functionality.

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

- **User Registration**: Create new accounts with email and password
- **User Authentication**: Login with JWT token generation
- **Protected Endpoints**: Access user information with JWT token verification
- **Password Security**: Secure password hashing using bcrypt
- **Input Validation**: Request/response validation with Pydantic models
- **Interactive Documentation**: Auto-generated API docs with FastAPI

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

## 🧪 Testing

Run the application and test the endpoints:

```bash
# Start the server
uvicorn main:app --reload

# Test registration
curl -X POST "http://localhost:8000/register" \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "testpassword"}'

# Test login
curl -X POST "http://localhost:8000/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "testpassword"}'
```

For detailed testing instructions, see [API_TEST_GUIDE.md](docs/API_TEST_GUIDE.md).

## 📚 Documentation

- [Setup Guide](docs/SETUP_GUIDE.md) - Detailed setup and deployment instructions
- [API Test Guide](docs/API_TEST_GUIDE.md) - Complete API testing examples
- [AI Collaboration Guidelines](CLAUDE.md) - Development guidelines and best practices

## 🤝 Contributing

Please read [CLAUDE.md](CLAUDE.md) for detailed development guidelines, coding standards, and collaboration rules.

## 📝 License

This project is intended for educational and development purposes.
