# Makefile for Counter Application with Data Persistence

.PHONY: install dev test clean build start-backend start-frontend start help

# Default target
help:
	@echo "Available commands:"
	@echo "  install       - Install all dependencies (backend and frontend)"
	@echo "  dev          - Start development servers (backend and frontend)"
	@echo "  test         - Run all tests"
	@echo "  clean        - Clean build artifacts and dependencies"
	@echo "  build        - Build production version"
	@echo "  start-backend - Start backend server only"
	@echo "  start-frontend - Start frontend development server only"
	@echo "  start        - Start production servers"

# Install dependencies
install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "✅ All dependencies installed"

# Development mode - start both servers
dev:
	@echo "Starting development servers..."
	@echo "Backend will be available at http://localhost:8000"
	@echo "Frontend will be available at http://localhost:3000"
	@echo "API docs will be available at http://localhost:8000/docs"
	@echo ""
	@echo "Press Ctrl+C to stop both servers"
	@echo ""
	(cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000) & \
	(cd frontend && npm start) & \
	wait

# Run tests
test:
	@echo "Running backend tests..."
	cd backend && python -m pytest tests/ -v
	@echo "Running frontend tests..."
	cd frontend && npm test -- --coverage --watchAll=false
	@echo "✅ All tests completed"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf backend/__pycache__
	rm -rf backend/app/__pycache__
	rm -rf backend/tests/__pycache__
	rm -rf backend/.pytest_cache
	rm -rf backend/data
	rm -rf frontend/build
	rm -rf frontend/node_modules/.cache
	@echo "✅ Clean completed"

# Build for production
build:
	@echo "Building frontend for production..."
	cd frontend && npm run build
	@echo "✅ Production build completed"

# Start backend only
start-backend:
	@echo "Starting backend server..."
	@echo "Available at http://localhost:8000"
	@echo "API docs at http://localhost:8000/docs"
	cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Start frontend development server only
start-frontend:
	@echo "Starting frontend development server..."
	@echo "Available at http://localhost:3000"
	cd frontend && npm start

# Start production servers
start:
	@echo "Starting production servers..."
	@echo "Make sure to build first with 'make build'"
	(cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000) & \
	(cd frontend && npx serve -s build -l 3000) & \
	wait

# Test individual components
test-backend:
	@echo "Running backend tests only..."
	cd backend && python -m pytest tests/ -v

test-frontend:
	@echo "Running frontend tests only..."
	cd frontend && npm test -- --coverage --watchAll=false

# Development utilities
lint:
	@echo "Running linting..."
	cd backend && python -m flake8 app/ tests/ --max-line-length=100
	cd frontend && npm run lint

format:
	@echo "Formatting code..."
	cd backend && python -m black app/ tests/
	cd frontend && npm run format

# Database/Storage management
reset-data:
	@echo "Resetting all data..."
	rm -rf backend/data/
	@echo "✅ All data reset"

backup-data:
	@echo "Creating data backup..."
	mkdir -p backups
	cp -r backend/data backups/data-$(shell date +%Y%m%d-%H%M%S) 2>/dev/null || echo "No data to backup"
	@echo "✅ Data backup created"

# Health checks
health-check:
	@echo "Checking application health..."
	@curl -f http://localhost:8000/api/health || echo "❌ Backend not responding"
	@curl -f http://localhost:3000 || echo "❌ Frontend not responding"
	@echo "✅ Health check completed"

# Performance testing
perf-test:
	@echo "Running performance tests..."
	@echo "Testing API response times..."
	@for i in {1..10}; do \
		curl -w "Response time: %{time_total}s\n" -s -o /dev/null http://localhost:8000/api/counter; \
	done
	@echo "✅ Performance test completed"