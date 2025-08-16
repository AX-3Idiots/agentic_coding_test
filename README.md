# Simple Dashboard API

A FastAPI-based backend service for a simple dashboard application.

## Features

- Dashboard metrics endpoint (users, orders, revenue with growth rates)
- Recent activities endpoint (user signups and order creations)
- Mock data service (ready for database integration)
- CORS enabled for frontend integration
- Health check endpoint

## Getting Started

### Prerequisites

- Python 3.8+
- uv (recommended) or pip

### Installation

1. Install dependencies:
```bash
uv sync
```

2. Run the development server:
```bash
uvicorn app.main:app --reload
```

3. Open your browser and visit:
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health
   - Root Endpoint: http://localhost:8000/

## API Endpoints

### Dashboard Metrics
- **GET** `/api/dashboard/metrics`
- Returns total users, orders, revenue and growth percentages

### Recent Activities  
- **GET** `/api/dashboard/recent-activities?limit=10`
- Returns recent user signups and order creations
- Query parameter: `limit` (1-50, default: 10)

## Project Structure

```
app/
├── main.py                 # FastAPI application entry point
├── api/v1/routes/         # API route definitions
├── core/                  # Configuration and settings
├── schemas/               # Pydantic models for request/response
├── services/              # Business logic layer
└── tests/                 # Test files
```

## Development

The project follows FastAPI best practices with:
- Pydantic v2 for data validation
- Service layer for business logic
- Structured project layout
- Mock data service (ready for database integration)

For detailed development guidelines, see `CLAUDE.md`.

