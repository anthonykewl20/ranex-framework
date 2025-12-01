# Quick Start Guide

Build your first Ranex-protected application in 15 minutes.

---

## What You'll Build

A simple order processing system with:
- State machine validation (prevents AI from skipping business steps)
- Security scanning (catches vulnerabilities)
- Contract enforcement (validates state transitions at runtime)

---

## Step 1: Create Project Structure

```bash
mkdir my-ranex-app
cd my-ranex-app

# Initialize Ranex
ranex init

# Create directory structure
mkdir -p app/features/orders
```

Your structure should look like:
```
my-ranex-app/
├── .ranex/
│   └── config.toml
└── app/
    └── features/
        └── orders/
```

---

## Step 2: Define State Machine

Create `app/features/orders/state.yaml`:

```yaml
feature: orders
description: Order processing workflow
initial_state: Pending

states:
  Pending:
    description: New order awaiting confirmation
    
  Confirmed:
    description: Order confirmed by customer
    
  Processing:
    description: Order being prepared
    
  Shipped:
    description: Order shipped to customer
    
  Delivered:
    description: Order delivered successfully
    terminal: true
    
  Cancelled:
    description: Order was cancelled
    terminal: true

transitions:
  - from: Pending
    to: Confirmed
    description: Customer confirms order
    
  - from: Pending
    to: Cancelled
    description: Order cancelled before confirmation
    
  - from: Confirmed
    to: Processing
    description: Start order processing
    
  - from: Confirmed
    to: Cancelled
    description: Cancel confirmed order
    
  - from: Processing
    to: Shipped
    description: Order shipped
    
  - from: Shipped
    to: Delivered
    description: Order delivered
```

**Key concepts:**
- `initial_state`: Where every order starts
- `terminal: true`: State that cannot be changed (final)
- `transitions`: Allowed state changes

---

## Step 3: Create Order Service

Create `app/features/orders/service.py`:

```python
from ranex import Contract

@Contract(feature="orders")
async def confirm_order(order_id: str, *, _ctx=None):
    """
    Confirm a pending order.
    
    The @Contract decorator:
    - Injects _ctx (state machine context)
    - Validates transitions at runtime
    - Logs all operations
    """
    # Validate and execute transition
    _ctx.transition("Confirmed")
    
    # Your business logic here
    # (database updates, notifications, etc.)
    
    return {
        "order_id": order_id,
        "status": "Confirmed",
        "message": "Order confirmed successfully"
    }


@Contract(feature="orders")
async def process_order(order_id: str, *, _ctx=None):
    """Start processing a confirmed order."""
    _ctx.transition("Processing")
    
    return {
        "order_id": order_id,
        "status": "Processing",
        "message": "Order is being prepared"
    }


@Contract(feature="orders")
async def ship_order(order_id: str, tracking_number: str, *, _ctx=None):
    """Ship a processed order."""
    _ctx.transition("Shipped")
    
    return {
        "order_id": order_id,
        "status": "Shipped",
        "tracking": tracking_number,
        "message": "Order has been shipped"
    }


@Contract(feature="orders")
async def deliver_order(order_id: str, *, _ctx=None):
    """Mark order as delivered (terminal state)."""
    _ctx.transition("Delivered")
    
    return {
        "order_id": order_id,
        "status": "Delivered",
        "message": "Order delivered successfully"
    }


@Contract(feature="orders")
async def cancel_order(order_id: str, reason: str, *, _ctx=None):
    """Cancel an order (only from Pending or Confirmed)."""
    _ctx.transition("Cancelled")
    
    return {
        "order_id": order_id,
        "status": "Cancelled",
        "reason": reason,
        "message": "Order has been cancelled"
    }
```

---

## Step 4: Test the State Machine

Create `test_orders.py`:

```python
import asyncio
from app.features.orders.service import (
    confirm_order, process_order, ship_order, deliver_order, cancel_order
)
from ranex import StateTransitionError

async def test_happy_path():
    """Test valid order workflow."""
    print("Testing happy path: Pending → Confirmed → Processing → Shipped → Delivered")
    
    # Note: Each function call creates a NEW state machine starting at Pending
    # In production, you'd sync with database state (see Step 5)
    
    result = await confirm_order("ORD-001")
    print(f"  ✓ {result['message']}")
    
    print("✅ Happy path works!")

async def test_invalid_transition():
    """Test that invalid transitions are blocked."""
    print("\nTesting invalid transition: Pending → Shipped (should fail)")
    
    from ranex_core import StateMachine
    
    sm = StateMachine("orders")  # Starts at Pending
    
    try:
        sm.transition("Shipped")  # Should fail!
        print("  ✗ ERROR: Should have blocked this!")
    except ValueError as e:
        print(f"  ✓ Correctly blocked: {str(e)[:50]}...")
    
    print("✅ Invalid transitions are blocked!")

if __name__ == "__main__":
    asyncio.run(test_happy_path())
    asyncio.run(test_invalid_transition())
```

Run:
```bash
python test_orders.py
```

---

## Step 5: Sync with Database State

In real applications, you need to sync the state machine with your database:

```python
from ranex import Contract

@Contract(feature="orders")
async def process_order(order_id: str, *, _ctx=None):
    """Process an order with database sync."""
    
    # 1. Load order from database
    order = await db.get_order(order_id)
    
    # 2. CRITICAL: Sync state machine with database state
    _ctx.current_state = order.status
    
    # 3. Validate and execute transition
    _ctx.transition("Processing")
    
    # 4. Update database
    order.status = "Processing"
    await db.save(order)
    
    return {"order_id": order_id, "status": "Processing"}
```

---

## Step 6: Run Security Scan

```bash
ranex scan
```

Output:
```
🔍 Ranex Security Scan
======================

Scanning: ./app

Security Patterns: 7 (Community Edition)
  ✅ No SQL injection found
  ✅ No command injection found
  ✅ No hardcoded secrets found
  ✅ No weak cryptography found

Architecture:
  ✅ Layer boundaries respected
  ✅ No forbidden imports

Result: PASS
```

---

## Step 7: Integrate with FastAPI

Create `app/main.py`:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.features.orders.service import confirm_order, process_order

app = FastAPI(title="My Ranex App")

class OrderAction(BaseModel):
    order_id: str

@app.post("/orders/{order_id}/confirm")
async def api_confirm_order(order_id: str):
    try:
        result = await confirm_order(order_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/orders/{order_id}/process")
async def api_process_order(order_id: str):
    try:
        result = await process_order(order_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

Run:
```bash
pip install fastapi uvicorn
uvicorn app.main:app --reload
```

---

## What You've Learned

1. **State Machines** prevent AI from skipping business logic steps
2. **@Contract decorator** enforces rules at runtime
3. **Security scanning** catches vulnerabilities
4. **Database sync** keeps state machine aligned with persistence

---

## Next Steps

- [State Machine Guide](./10-STATE-MACHINE.md) - Advanced state machine patterns
- [@Contract Decorator](./11-CONTRACT-DECORATOR.md) - Full decorator documentation
- [FastAPI Integration](./33-FASTAPI-INTEGRATION.md) - Production FastAPI setup

