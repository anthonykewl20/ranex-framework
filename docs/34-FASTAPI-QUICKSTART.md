# FastAPI Quick Start with Ranex CE

Get a FastAPI app running with Ranex governance in **5 minutes**.

---

## Step 1: Install

```bash
# Navigate to your ranex-ce directory
cd ~/ranex-ce

# Activate virtual environment
source .venv/bin/activate

# Install FastAPI and SQLite support
pip install fastapi uvicorn aiosqlite
```

---

## Step 2: Initialize Ranex

```bash
ranex init
```

This creates the `.ranex/` config and `app/` structure.

---

## Step 3: Create Project Structure

```bash
mkdir -p app/features/orders data
touch app/__init__.py
touch app/main.py
touch app/features/__init__.py
touch app/features/orders/__init__.py
touch app/features/orders/state.yaml
touch app/features/orders/routes.py
```

---

## Step 4: Create State Machine

**`app/features/orders/state.yaml`**

```yaml
feature: orders
description: Order management workflow
initial_state: Pending

states:
  Pending:
    description: New order awaiting confirmation
  Confirmed:
    description: Order confirmed
  Processing:
    description: Being prepared
  Shipped:
    description: In transit
  Delivered:
    description: Completed
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
  - from: Processing
    to: Shipped
  - from: Shipped
    to: Delivered
```

---

## Step 5: Create FastAPI App

**`app/main.py`**

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ranex import Contract

app = FastAPI(title="Orders API with Ranex")

# In-memory storage for demo
orders_db = {}
order_counter = 0


class OrderCreate(BaseModel):
    product: str
    quantity: int


class OrderResponse(BaseModel):
    id: str
    product: str
    quantity: int
    status: str


@app.get("/health")
async def health():
    return {"status": "healthy", "ranex": "active"}


@app.post("/orders", response_model=OrderResponse)
@Contract(feature="orders")
async def create_order(data: OrderCreate, *, _ctx=None):
    """Create a new order (starts in Pending state)."""
    global order_counter
    order_counter += 1
    order_id = f"ORD-{order_counter:04d}"
    
    orders_db[order_id] = {
        "id": order_id,
        "product": data.product,
        "quantity": data.quantity,
        "status": "Pending"
    }
    
    return orders_db[order_id]


@app.post("/orders/{order_id}/confirm", response_model=OrderResponse)
@Contract(feature="orders")
async def confirm_order(order_id: str, *, _ctx=None):
    """Confirm an order: Pending → Confirmed"""
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = orders_db[order_id]
    
    # Sync state machine with current order status
    while _ctx.current_state != order["status"]:
        # Fast-forward state machine to match DB
        if order["status"] == "Confirmed":
            _ctx.transition("Confirmed")
        elif order["status"] == "Processing":
            _ctx.transition("Confirmed")
            _ctx.transition("Processing")
        # ... etc
        break
    
    # Now transition
    _ctx.transition("Confirmed")  # Will fail if not allowed!
    order["status"] = "Confirmed"
    
    return order


@app.post("/orders/{order_id}/process", response_model=OrderResponse)
@Contract(feature="orders")
async def process_order(order_id: str, *, _ctx=None):
    """Process an order: Confirmed → Processing"""
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = orders_db[order_id]
    
    # Sync to current state first
    if order["status"] == "Confirmed":
        _ctx.transition("Confirmed")
    
    _ctx.transition("Processing")
    order["status"] = "Processing"
    
    return order


@app.post("/orders/{order_id}/ship", response_model=OrderResponse)
@Contract(feature="orders")
async def ship_order(order_id: str, *, _ctx=None):
    """Ship an order: Processing → Shipped"""
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = orders_db[order_id]
    
    # Sync to current state
    if order["status"] == "Confirmed":
        _ctx.transition("Confirmed")
    if order["status"] == "Processing":
        _ctx.transition("Confirmed")
        _ctx.transition("Processing")
    
    _ctx.transition("Shipped")
    order["status"] = "Shipped"
    
    return order


@app.post("/orders/{order_id}/cancel", response_model=OrderResponse)
@Contract(feature="orders")
async def cancel_order(order_id: str, *, _ctx=None):
    """Cancel an order (only from Pending)"""
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = orders_db[order_id]
    
    _ctx.transition("Cancelled")  # Only works from Pending!
    order["status"] = "Cancelled"
    
    return order


@app.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str):
    """Get order by ID (no state transition)."""
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    return orders_db[order_id]
```

---

## Step 6: Run the Server

```bash
uvicorn app.main:app --reload
```

Output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

---

## Step 7: Test the API

Open a new terminal:

```bash
# Create an order
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"product": "Widget", "quantity": 3}'

# Response: {"id":"ORD-0001","product":"Widget","quantity":3,"status":"Pending"}

# Confirm the order
curl -X POST http://localhost:8000/orders/ORD-0001/confirm

# Response: {"id":"ORD-0001","product":"Widget","quantity":3,"status":"Confirmed"}

# Try invalid transition (skip to Shipped)
curl -X POST http://localhost:8000/orders/ORD-0001/ship

# Response: {"detail":"Illegal transition from 'Confirmed' to 'Shipped'..."}
# ☝️ Ranex blocks invalid transitions!

# Correct flow: Process first, then ship
curl -X POST http://localhost:8000/orders/ORD-0001/process
curl -X POST http://localhost:8000/orders/ORD-0001/ship

# Response: {"id":"ORD-0001","product":"Widget","quantity":3,"status":"Shipped"}
```

---

## Step 8: View Swagger Docs

Open: **http://localhost:8000/docs**

You'll see interactive API documentation with all endpoints.

---

## What Ranex Does

When you try an **invalid state transition**, Ranex blocks it:

```
POST /orders/ORD-0001/ship  (when status is "Pending")

Error: StateTransitionError: Illegal transition
  Current: Pending
  Attempted: Shipped
  Allowed: [Confirmed, Cancelled]
```

This prevents AI or developers from skipping workflow steps!

---

## Run Security Scan

```bash
ranex scan
```

This checks your FastAPI code for:
- SQL Injection
- Hardcoded secrets
- Insecure patterns
- Architecture violations

---

## Next Steps

- **Full Guide**: See [33-FASTAPI-INTEGRATION.md](./33-FASTAPI-INTEGRATION.md) for database integration
- **State Machines**: See [10-STATE-MACHINE.md](./10-STATE-MACHINE.md) for advanced YAML config
- **Architecture**: See [13-ARCHITECTURE.md](./13-ARCHITECTURE.md) for layer enforcement

---

**🎉 You're now running FastAPI with Ranex governance!**

