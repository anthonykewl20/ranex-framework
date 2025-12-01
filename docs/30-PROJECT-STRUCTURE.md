# Project Structure Guide

Recommended project structure for Ranex projects.

---

## Standard Structure

```
my-project/
├── .ranex/                      # Ranex configuration
│   ├── config.toml             # Project settings
│   └── ignore                  # Files to ignore
│
├── app/                         # Application code
│   ├── __init__.py
│   ├── main.py                 # FastAPI entry point
│   │
│   ├── commons/                # Shared utilities
│   │   ├── __init__.py
│   │   ├── auth.py            # Authentication
│   │   ├── validation.py      # Validation helpers
│   │   └── formatting.py      # Formatting utilities
│   │
│   └── features/               # Business features
│       ├── orders/
│       │   ├── __init__.py    # Public API exports
│       │   ├── routes.py      # HTTP endpoints
│       │   ├── service.py     # Business logic (@Contract)
│       │   ├── repository.py  # Database access
│       │   ├── models.py      # Pydantic models
│       │   └── state.yaml     # State machine
│       │
│       ├── payments/
│       │   └── ...
│       │
│       └── shipping/
│           └── ...
│
├── tests/                       # Test files
│   ├── __init__.py
│   ├── conftest.py            # Pytest fixtures
│   └── features/
│       ├── test_orders.py
│       └── test_payments.py
│
├── data/                        # Local data (SQLite, etc.)
│   └── app.db
│
├── pyproject.toml              # Python package config
├── requirements.txt            # Dependencies
└── README.md
```

---

## Directory Purposes

### `.ranex/` - Configuration

```
.ranex/
├── config.toml    # Project configuration
└── ignore         # Files to exclude from scanning
```

### `app/commons/` - Shared Code

Place code that's used by multiple features:

```python
# app/commons/auth.py
def get_current_user():
    """Get authenticated user."""
    ...

def require_role(role: str):
    """Decorator for role-based access."""
    ...

# app/commons/validation.py
def validate_email(email: str) -> bool:
    """Validate email format."""
    ...
```

### `app/features/` - Business Features

Each feature is self-contained:

```
app/features/orders/
├── __init__.py     # Public exports
├── routes.py       # FastAPI routes (HTTP layer)
├── service.py      # Business logic (@Contract)
├── repository.py   # Database operations
├── models.py       # Pydantic models
└── state.yaml      # State machine definition
```

---

## Feature Structure

### `__init__.py` - Public API

```python
# app/features/orders/__init__.py
"""
Orders feature public API.
Import only these in other features.
"""
from .service import (
    create_order,
    confirm_order,
    process_order,
    ship_order,
)
from .models import (
    Order,
    OrderCreate,
    OrderResponse,
)

__all__ = [
    # Services
    "create_order",
    "confirm_order",
    "process_order",
    "ship_order",
    # Models
    "Order",
    "OrderCreate",
    "OrderResponse",
]
```

### `routes.py` - HTTP Layer

```python
# app/features/orders/routes.py
from fastapi import APIRouter, HTTPException, Depends
from .service import create_order, confirm_order
from .models import OrderCreate, OrderResponse
from app.commons.auth import get_current_user

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", response_model=OrderResponse)
async def create_order_endpoint(
    data: OrderCreate,
    user = Depends(get_current_user)
):
    try:
        return await create_order(data, user.id)
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.post("/{order_id}/confirm")
async def confirm_order_endpoint(order_id: str):
    try:
        return await confirm_order(order_id)
    except ValueError as e:
        raise HTTPException(400, str(e))
```

### `service.py` - Business Logic

```python
# app/features/orders/service.py
from ranex import Contract
from .repository import OrderRepository
from .models import OrderCreate, OrderResponse

@Contract(feature="orders")
async def create_order(data: OrderCreate, user_id: str, *, _ctx=None):
    """Create a new order."""
    repo = OrderRepository()
    order = await repo.create(data, user_id)
    return OrderResponse.from_orm(order)

@Contract(feature="orders")
async def confirm_order(order_id: str, *, _ctx=None):
    """Confirm an order."""
    repo = OrderRepository()
    order = await repo.get(order_id)
    
    # Sync state machine with database
    _ctx.current_state = order.status
    
    # Validate and transition
    _ctx.transition("Confirmed")
    
    # Update database
    order.status = "Confirmed"
    await repo.save(order)
    
    return OrderResponse.from_orm(order)
```

### `repository.py` - Data Access

```python
# app/features/orders/repository.py
from typing import Optional
from sqlalchemy.orm import Session
from .models import Order, OrderCreate

class OrderRepository:
    def __init__(self, db: Session = None):
        self.db = db or get_db()
    
    async def create(self, data: OrderCreate, user_id: str) -> Order:
        order = Order(user_id=user_id, **data.dict())
        self.db.add(order)
        await self.db.commit()
        return order
    
    async def get(self, order_id: str) -> Optional[Order]:
        return self.db.query(Order).filter_by(id=order_id).first()
    
    async def save(self, order: Order) -> Order:
        await self.db.commit()
        return order
```

### `models.py` - Data Models

```python
# app/features/orders/models.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class OrderCreate(BaseModel):
    """Request model for creating order."""
    product_id: str
    quantity: int
    shipping_address: str

class OrderResponse(BaseModel):
    """Response model for order."""
    id: str
    user_id: str
    product_id: str
    quantity: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class Order(BaseModel):
    """Internal order model."""
    id: str
    user_id: str
    product_id: str
    quantity: int
    status: str = "Pending"
    shipping_address: str
    created_at: datetime = None
```

### `state.yaml` - State Machine

```yaml
# app/features/orders/state.yaml
feature: orders
description: Order processing workflow
initial_state: Pending

states:
  Pending:
    description: New order awaiting confirmation
  Confirmed:
    description: Order confirmed
  Processing:
    description: Order being prepared
  Shipped:
    description: Order shipped
  Delivered:
    description: Order delivered
    terminal: true
  Cancelled:
    description: Order cancelled
    terminal: true

transitions:
  - from: Pending
    to: Confirmed
  - from: Pending
    to: Cancelled
  - from: Confirmed
    to: Processing
  - from: Confirmed
    to: Cancelled
  - from: Processing
    to: Shipped
  - from: Shipped
    to: Delivered
```

---

## Main Application

### `app/main.py`

```python
# app/main.py
from fastapi import FastAPI
from app.features.orders.routes import router as orders_router
from app.features.payments.routes import router as payments_router

app = FastAPI(
    title="My Ranex App",
    description="API with Ranex governance",
    version="1.0.0"
)

# Register routers
app.include_router(orders_router)
app.include_router(payments_router)

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

---

## Why This Structure?

### 1. AI-Friendly

Each feature folder contains everything AI needs:
- State rules in `state.yaml`
- Models in `models.py`
- Business logic in `service.py`

AI can work on one feature without seeing unrelated code.

### 2. Clear Dependencies

```
routes.py → service.py → repository.py → models.py
```

Each layer only imports from the layer below.

### 3. Testable

```python
# tests/features/test_orders.py
from app.features.orders.service import confirm_order
from app.features.orders.repository import OrderRepository

async def test_confirm_order():
    # Test service directly without HTTP
    result = await confirm_order("ORD-001")
    assert result.status == "Confirmed"
```

### 4. Scalable

Adding new features is straightforward:
```bash
mkdir -p app/features/new_feature
touch app/features/new_feature/{__init__,routes,service,repository,models}.py
touch app/features/new_feature/state.yaml
```

---

## Anti-Patterns to Avoid

### ❌ God Modules

```
# BAD: Everything in one file
app/
└── main.py  # 5000 lines of everything
```

### ❌ Utils/Helpers Folders

```
# BAD: Vague dumping grounds
app/
├── utils/
├── helpers/
└── lib/
```

### ❌ Cross-Feature Imports

```python
# BAD: Payments importing Orders internals
from app.features.orders.repository import OrderRepository
```

### ❌ Routes Accessing Database

```python
# BAD: Skip service layer
@router.get("/orders/{id}")
async def get_order(id: str):
    return db.query(Order).filter_by(id=id).first()
```

---

## Next Steps

- [Development Workflow](./31-DEVELOPMENT-WORKFLOW.md) - Best practices
- [FastAPI Integration](./33-FASTAPI-INTEGRATION.md) - Complete example

