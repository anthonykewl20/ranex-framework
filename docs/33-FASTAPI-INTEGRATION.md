# FastAPI Integration

Complete guide to integrating Ranex with FastAPI.

---

## Quick Setup

### 1. Install Dependencies

```bash
pip install fastapi uvicorn sqlalchemy
pip install ranex_core-*.whl ./ranex
```

### 2. Initialize Project

```bash
ranex init
```

> **Note:** This creates the standard Ranex structure. Then manually create the FastAPI app structure shown below.

### 3. Create Structure

```
app/
├── main.py
├── database.py
├── commons/
│   └── auth.py
└── features/
    └── orders/
        ├── __init__.py
        ├── routes.py
        ├── service.py
        ├── repository.py
        ├── models.py
        └── state.yaml
```

---

## Complete Example

### `app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import init_db
from app.features.orders.routes import router as orders_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Order Management API",
    description="Ranex-protected order management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(orders_router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"status": "healthy", "ranex": "active"}
```

### `app/database.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./data/app.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

async def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### `app/features/orders/state.yaml`

```yaml
feature: orders
description: Order management workflow
initial_state: Pending

states:
  Pending:
    description: New order awaiting confirmation
  Confirmed:
    description: Order confirmed by customer
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
    description: Customer confirms order
  - from: Pending
    to: Cancelled
    description: Cancel before confirmation
  - from: Confirmed
    to: Processing
    description: Start processing
  - from: Confirmed
    to: Cancelled
    description: Cancel confirmed order
  - from: Processing
    to: Shipped
    description: Ship order
  - from: Shipped
    to: Delivered
    description: Mark as delivered
```

### `app/features/orders/models.py`

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Integer, DateTime, Float
from app.database import Base

# SQLAlchemy Model
class OrderDB(Base):
    __tablename__ = "orders"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    product_id = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String, default="Pending")
    shipping_address = Column(String)
    tracking_number = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

# Pydantic Models
class OrderCreate(BaseModel):
    product_id: str = Field(..., description="Product ID")
    quantity: int = Field(..., ge=1, description="Quantity")
    shipping_address: str = Field(..., description="Shipping address")

class OrderResponse(BaseModel):
    id: str
    user_id: str
    product_id: str
    quantity: int
    total_amount: float
    status: str
    shipping_address: str
    tracking_number: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class ConfirmRequest(BaseModel):
    pass  # Empty, just needs order_id from path

class ShipRequest(BaseModel):
    tracking_number: str = Field(..., description="Tracking number")
```

### `app/features/orders/repository.py`

```python
from typing import Optional, List
from sqlalchemy.orm import Session
from .models import OrderDB, OrderCreate
import uuid

class OrderRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, data: OrderCreate, user_id: str, total: float) -> OrderDB:
        order = OrderDB(
            id=str(uuid.uuid4()),
            user_id=user_id,
            product_id=data.product_id,
            quantity=data.quantity,
            total_amount=total,
            shipping_address=data.shipping_address,
            status="Pending"
        )
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order
    
    def get(self, order_id: str) -> Optional[OrderDB]:
        return self.db.query(OrderDB).filter(OrderDB.id == order_id).first()
    
    def get_by_user(self, user_id: str) -> List[OrderDB]:
        return self.db.query(OrderDB).filter(OrderDB.user_id == user_id).all()
    
    def save(self, order: OrderDB) -> OrderDB:
        self.db.commit()
        self.db.refresh(order)
        return order
```

### `app/features/orders/service.py`

```python
from ranex import Contract
from sqlalchemy.orm import Session
from .repository import OrderRepository
from .models import OrderCreate, OrderResponse, OrderDB

PRODUCT_PRICES = {
    "PROD-001": 29.99,
    "PROD-002": 49.99,
    "PROD-003": 99.99,
}

@Contract(feature="orders")
async def create_order(
    data: OrderCreate, 
    user_id: str, 
    db: Session,
    *, _ctx=None
) -> OrderResponse:
    """Create a new order."""
    repo = OrderRepository(db)
    
    # Calculate total
    price = PRODUCT_PRICES.get(data.product_id, 0)
    total = price * data.quantity
    
    # Create order (starts in Pending state)
    order = repo.create(data, user_id, total)
    
    return OrderResponse.from_orm(order)


@Contract(feature="orders")
async def confirm_order(
    order_id: str, 
    db: Session,
    *, _ctx=None
) -> OrderResponse:
    """Confirm an order."""
    repo = OrderRepository(db)
    order = repo.get(order_id)
    
    if not order:
        raise ValueError(f"Order not found: {order_id}")
    
    # Sync state machine with database
    _ctx.current_state = order.status
    
    # Validate and transition
    _ctx.transition("Confirmed")
    
    # Update database
    order.status = "Confirmed"
    repo.save(order)
    
    return OrderResponse.from_orm(order)


@Contract(feature="orders")
async def process_order(
    order_id: str, 
    db: Session,
    *, _ctx=None
) -> OrderResponse:
    """Start processing an order."""
    repo = OrderRepository(db)
    order = repo.get(order_id)
    
    if not order:
        raise ValueError(f"Order not found: {order_id}")
    
    _ctx.current_state = order.status
    _ctx.transition("Processing")
    
    order.status = "Processing"
    repo.save(order)
    
    return OrderResponse.from_orm(order)


@Contract(feature="orders")
async def ship_order(
    order_id: str, 
    tracking_number: str,
    db: Session,
    *, _ctx=None
) -> OrderResponse:
    """Ship an order."""
    repo = OrderRepository(db)
    order = repo.get(order_id)
    
    if not order:
        raise ValueError(f"Order not found: {order_id}")
    
    _ctx.current_state = order.status
    _ctx.transition("Shipped")
    
    order.status = "Shipped"
    order.tracking_number = tracking_number
    repo.save(order)
    
    return OrderResponse.from_orm(order)


@Contract(feature="orders")
async def deliver_order(
    order_id: str, 
    db: Session,
    *, _ctx=None
) -> OrderResponse:
    """Mark order as delivered."""
    repo = OrderRepository(db)
    order = repo.get(order_id)
    
    if not order:
        raise ValueError(f"Order not found: {order_id}")
    
    _ctx.current_state = order.status
    _ctx.transition("Delivered")
    
    order.status = "Delivered"
    repo.save(order)
    
    return OrderResponse.from_orm(order)


@Contract(feature="orders")
async def cancel_order(
    order_id: str, 
    db: Session,
    *, _ctx=None
) -> OrderResponse:
    """Cancel an order."""
    repo = OrderRepository(db)
    order = repo.get(order_id)
    
    if not order:
        raise ValueError(f"Order not found: {order_id}")
    
    _ctx.current_state = order.status
    _ctx.transition("Cancelled")
    
    order.status = "Cancelled"
    repo.save(order)
    
    return OrderResponse.from_orm(order)


async def get_order(order_id: str, db: Session) -> OrderResponse:
    """Get order by ID (no state transition)."""
    repo = OrderRepository(db)
    order = repo.get(order_id)
    
    if not order:
        raise ValueError(f"Order not found: {order_id}")
    
    return OrderResponse.from_orm(order)
```

### `app/features/orders/routes.py`

```python
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from .models import OrderCreate, OrderResponse, ShipRequest
from .service import (
    create_order,
    confirm_order,
    process_order,
    ship_order,
    deliver_order,
    cancel_order,
    get_order,
)

router = APIRouter(prefix="/orders", tags=["orders"])

# Fake user ID for demo (use real auth in production)
def get_current_user_id() -> str:
    return "user_123"


@router.post("/", response_model=OrderResponse)
async def create_order_endpoint(
    data: OrderCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Create a new order."""
    try:
        return await create_order(data, user_id, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_endpoint(
    order_id: str,
    db: Session = Depends(get_db)
):
    """Get order by ID."""
    try:
        return await get_order(order_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{order_id}/confirm", response_model=OrderResponse)
async def confirm_order_endpoint(
    order_id: str,
    db: Session = Depends(get_db)
):
    """Confirm an order."""
    try:
        return await confirm_order(order_id, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{order_id}/process", response_model=OrderResponse)
async def process_order_endpoint(
    order_id: str,
    db: Session = Depends(get_db)
):
    """Start processing an order."""
    try:
        return await process_order(order_id, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{order_id}/ship", response_model=OrderResponse)
async def ship_order_endpoint(
    order_id: str,
    data: ShipRequest,
    db: Session = Depends(get_db)
):
    """Ship an order."""
    try:
        return await ship_order(order_id, data.tracking_number, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{order_id}/deliver", response_model=OrderResponse)
async def deliver_order_endpoint(
    order_id: str,
    db: Session = Depends(get_db)
):
    """Mark order as delivered."""
    try:
        return await deliver_order(order_id, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order_endpoint(
    order_id: str,
    db: Session = Depends(get_db)
):
    """Cancel an order."""
    try:
        return await cancel_order(order_id, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### `app/features/orders/__init__.py`

```python
"""Orders feature public API."""
from .service import (
    create_order,
    confirm_order,
    process_order,
    ship_order,
    deliver_order,
    cancel_order,
    get_order,
)
from .models import OrderCreate, OrderResponse
from .routes import router

__all__ = [
    "create_order",
    "confirm_order",
    "process_order",
    "ship_order",
    "deliver_order",
    "cancel_order",
    "get_order",
    "OrderCreate",
    "OrderResponse",
    "router",
]
```

---

## Running the Application

```bash
# Development
uvicorn app.main:app --reload

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## API Usage

```bash
# Create order
curl -X POST http://localhost:8000/api/v1/orders/ \
  -H "Content-Type: application/json" \
  -d '{"product_id": "PROD-001", "quantity": 2, "shipping_address": "123 Main St"}'

# Confirm order
curl -X POST http://localhost:8000/api/v1/orders/{order_id}/confirm

# Process order
curl -X POST http://localhost:8000/api/v1/orders/{order_id}/process

# Ship order
curl -X POST http://localhost:8000/api/v1/orders/{order_id}/ship \
  -H "Content-Type: application/json" \
  -d '{"tracking_number": "TRK123456"}'

# Invalid transition (will fail)
curl -X POST http://localhost:8000/api/v1/orders/{order_id}/ship
# Returns: {"detail": "Illegal transition from 'Pending' to 'Shipped'..."}
```

---

## Next Steps

- [Troubleshooting](./40-TROUBLESHOOTING.md) - Common issues
- [FAQ](./41-FAQ.md) - Frequently asked questions

