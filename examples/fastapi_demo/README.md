# FastAPI Demo Application

This is a complete FastAPI application demonstrating Ranex Framework integration.

## Features

- **FastAPI + PostgreSQL**: Full-stack application with database
- **Ranex Contract Middleware**: Multi-tenant contract enforcement
- **Rate Limiting**: Request rate limiting middleware
- **Health Checks**: Application health monitoring
- **Prometheus Metrics**: Performance metrics export
- **Alembic Migrations**: Database schema management

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL (or use Docker Compose)
- Ranex Framework installed

### Setup

1. **Start PostgreSQL** (using Docker Compose):
   ```bash
   cd /path/to/ranex
   docker-compose up -d postgres
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt  # If you have one, or install from pyproject.toml
   ```

3. **Run database migrations**:
   ```bash
   cd examples/fastapi_demo
   alembic upgrade head
   ```

4. **Run the application**:
   ```bash
   # From project root, add examples/fastapi_demo to Python path
   PYTHONPATH=examples/fastapi_demo:$PYTHONPATH uvicorn app.main:app --reload --port 8000
   ```

   Or from within the fastapi_demo directory:
   ```bash
   cd examples/fastapi_demo
   python -m uvicorn app.main:app --reload --port 8000
   ```

### Access

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics

## Architecture

```
fastapi_demo/
├── app/
│   ├── commons/          # Shared utilities
│   │   ├── database.py   # Database connection
│   │   ├── contract_middleware.py  # Ranex contract middleware
│   │   ├── rate_limiter.py
│   │   ├── health.py
│   │   └── metrics.py
│   └── features/         # Feature modules
│       ├── payment/      # Payment feature
│       ├── user/         # User management
│       └── product/      # Product management
└── alembic/              # Database migrations
```

## Ranex Integration

This demo showcases:

1. **Contract Middleware**: Multi-tenant contract enforcement
2. **State Machine**: Payment state transitions
3. **Architecture Enforcement**: Layer validation (can be enabled)

See `app/main.py` for integration examples.

## Notes

- The application uses `app.` imports, so it should be run with the correct Python path
- Database configuration is in `alembic.ini`
- Environment variables can override defaults

