# FastAPI Application - Complete Working Example

This is a **complete, runnable FastAPI application** demonstrating Ranex Framework integration.

## Structure

```
app/
├── main.py              # FastAPI application entry point
├── commons/             # Shared utilities (Ranex architecture)
│   ├── database.py      # Database connection
│   ├── contract_middleware.py  # Ranex contract middleware
│   ├── metrics.py       # Prometheus metrics
│   ├── rate_limiter.py  # Rate limiting
│   ├── health.py        # Health checks
│   └── ...
│
└── features/            # Feature modules (Vertical Slice Architecture)
    ├── payment/         # Payment feature
    │   ├── routes.py    # API endpoints
    │   ├── service.py   # Business logic
    │   ├── models.py    # Data models
    │   └── state.yaml   # State machine
    ├── user/            # User management
    ├── product/         # Product management
    ├── subscription/    # Subscriptions
    └── auth/           # Authentication
```

## Quick Start

### 1. Install Dependencies

**Option 1: Using requirements.txt (Recommended)**
```bash
pip install -r requirements.txt
```

**Option 2: Manual installation**
```bash
pip install fastapi uvicorn sqlalchemy alembic psycopg[binary] pydantic
```

**Note:** Also install Ranex Core wheel:
```bash
pip install ../wheels/ranex_core-0.0.1-cp312-cp312-linux_x86_64.whl
```

### 2. Set Up Database

```bash
# Using PostgreSQL (recommended)
export DATABASE_URL="postgresql://user:password@localhost:5432/ranex_db"

# Or use SQLite for testing
export DATABASE_URL="sqlite:///./app.db"
```

### 3. Run Database Migrations

```bash
# If using Alembic
alembic upgrade head

# Or create tables manually
python -c "from app.commons.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

### 4. Run the Application

```bash
cd Pre-Release-v0.1
uvicorn app.main:app --reload --port 8000
```

### 5. Access the API

- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Metrics:** http://localhost:8000/metrics

## Features Demonstrated

✅ **Ranex Contract Middleware**
- Multi-tenant support
- Request context tracking
- Contract validation

✅ **Ranex Architecture Enforcement**
- Vertical slice architecture
- Layer enforcement (routes → service → models → commons)
- Structure validation

✅ **State Machine Integration**
- Payment state transitions
- State validation
- Multi-tenant isolation

✅ **Security Features**
- Rate limiting
- Health checks
- Prometheus metrics
- Circuit breakers

## API Endpoints

### Payment Feature
- `POST /payments` - Create payment
- `GET /payments/{id}` - Get payment
- `PUT /payments/{id}` - Update payment

### User Feature
- `POST /users` - Create user
- `GET /users/{id}` - Get user
- `GET /users` - List users

### Product Feature
- `POST /products` - Create product
- `GET /products/{id}` - Get product
- `GET /products` - List products

## Ranex Integration

This application demonstrates:

1. **@Contract Decorator** - See `app/features/payment/routes.py`
2. **Contract Middleware** - See `app/main.py`
3. **State Machines** - See `app/features/payment/state.yaml`
4. **Architecture Enforcement** - See layer structure
5. **Database Schema** - See `app/commons/database.py`

## Notes

- This is a **complete working application**
- All imports use `app.` prefix (correct structure)
- Follows Ranex vertical slice architecture
- Production-ready structure
- Can be used as a template for new projects
