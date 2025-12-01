# @Contract Decorator

The `@Contract` decorator enforces state machine rules at runtime for your business logic functions.

---

## What It Does

The `@Contract` decorator wraps your functions to provide:

1. **State machine injection** - Provides `_ctx` parameter with state machine
2. **Transition validation** - Validates state changes at runtime
3. **Error handling** - Graceful failures with clear messages
4. **Logging** - Automatic operation logging

---

## Basic Usage

```python
from ranex import Contract

@Contract(feature="orders")
async def confirm_order(order_id: str, *, _ctx=None):
    """
    The @Contract decorator injects _ctx (state machine context).
    """
    # Validate and execute transition
    _ctx.transition("Confirmed")
    
    # Your business logic
    return {"order_id": order_id, "status": "Confirmed"}
```

### Key Points:

1. **`feature="orders"`** - Must match your `state.yaml` feature name
2. **`_ctx=None`** - Keyword-only argument, automatically injected
3. **`async def`** - Supports both sync and async functions

---

## The `_ctx` Object

The `_ctx` parameter is a `StateMachine` instance with these properties and methods:

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `current_state` | `str` | Current state (read/write) |

### Methods

| Method | Description |
|--------|-------------|
| `transition(state)` | Validate and move to new state |
| `get_allowed_transitions()` | List allowed next states |

### Example

```python
@Contract(feature="orders")
async def ship_order(order_id: str, *, _ctx=None):
    # Read current state
    print(f"Current: {_ctx.current_state}")  # e.g., "Processing"
    
    # Check allowed transitions
    allowed = _ctx.get_allowed_transitions()
    print(f"Allowed: {allowed}")  # e.g., ["Shipped", "Cancelled"]
    
    # Execute transition
    _ctx.transition("Shipped")
    
    return {"status": "Shipped"}
```

---

## Syncing with Database State

**Critical:** The state machine starts at `initial_state` from your YAML file. For existing records, you must sync with database state:

```python
@Contract(feature="orders")
async def process_order(order_id: str, *, _ctx=None):
    # 1. Load order from database
    order = await db.get_order(order_id)
    
    # 2. SYNC: Set state machine to match database
    _ctx.current_state = order.status
    
    # 3. Now validate transition from actual state
    _ctx.transition("Processing")
    
    # 4. Update database
    order.status = "Processing"
    await db.save(order)
    
    return {"order_id": order_id, "status": "Processing"}
```

### Why This Matters

Without sync:
```python
# Each call creates NEW state machine at initial_state
# This is WRONG for existing records!

@Contract(feature="orders")
async def ship_order(order_id, *, _ctx=None):
    _ctx.transition("Shipped")  # ❌ Fails! State is "Pending", not "Processing"
```

With sync:
```python
@Contract(feature="orders")
async def ship_order(order_id, *, _ctx=None):
    order = await db.get_order(order_id)
    _ctx.current_state = order.status  # "Processing"
    _ctx.transition("Shipped")  # ✅ Works!
```

---

## Error Handling

### Invalid Transition

```python
@Contract(feature="orders")
async def bad_transition(order_id: str, *, _ctx=None):
    _ctx.transition("Delivered")  # Pending → Delivered not allowed!
```

**Error:**
```
ValueError: Illegal transition from 'Pending' to 'Delivered' for feature 'orders'.
Allowed transitions from 'Pending': [Confirmed, Cancelled]
```

### Catching Errors

```python
from ranex import Contract, StateTransitionError

@Contract(feature="orders")
async def try_transition(order_id: str, target_state: str, *, _ctx=None):
    try:
        _ctx.transition(target_state)
        return {"success": True, "state": target_state}
    except (ValueError, StateTransitionError) as e:
        return {"success": False, "error": str(e)}
```

---

## Sync vs Async Functions

The decorator supports both:

### Async (Recommended for FastAPI)

```python
@Contract(feature="orders")
async def confirm_order(order_id: str, *, _ctx=None):
    _ctx.transition("Confirmed")
    return {"status": "Confirmed"}
```

### Sync

```python
@Contract(feature="orders")
def confirm_order_sync(order_id: str, *, _ctx=None):
    _ctx.transition("Confirmed")
    return {"status": "Confirmed"}
```

---

## Multiple Parameters

Pass any parameters you need:

```python
@Contract(feature="orders")
async def ship_order(
    order_id: str,
    tracking_number: str,
    carrier: str = "ups",
    *,
    _ctx=None  # Must be keyword-only (after *)
):
    _ctx.transition("Shipped")
    
    return {
        "order_id": order_id,
        "tracking": tracking_number,
        "carrier": carrier,
        "status": "Shipped"
    }
```

---

## With Pydantic Models

```python
from pydantic import BaseModel
from ranex import Contract

class ShipOrderRequest(BaseModel):
    order_id: str
    tracking_number: str
    carrier: str = "ups"

class ShipOrderResponse(BaseModel):
    order_id: str
    status: str
    tracking: str

@Contract(feature="orders")
async def ship_order(request: ShipOrderRequest, *, _ctx=None) -> ShipOrderResponse:
    order = await db.get_order(request.order_id)
    _ctx.current_state = order.status
    _ctx.transition("Shipped")
    
    order.status = "Shipped"
    order.tracking = request.tracking_number
    await db.save(order)
    
    return ShipOrderResponse(
        order_id=request.order_id,
        status="Shipped",
        tracking=request.tracking_number
    )
```

---

## FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
from ranex import Contract, StateTransitionError

app = FastAPI()

@Contract(feature="orders")
async def confirm_order_service(order_id: str, *, _ctx=None):
    order = await db.get_order(order_id)
    _ctx.current_state = order.status
    _ctx.transition("Confirmed")
    order.status = "Confirmed"
    await db.save(order)
    return {"order_id": order_id, "status": "Confirmed"}

@app.post("/orders/{order_id}/confirm")
async def confirm_order_endpoint(order_id: str):
    try:
        return await confirm_order_service(order_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Common Patterns

### Pattern 1: State Check Before Action

```python
@Contract(feature="orders")
async def can_cancel(order_id: str, *, _ctx=None) -> bool:
    order = await db.get_order(order_id)
    _ctx.current_state = order.status
    
    allowed = _ctx.get_allowed_transitions()
    return "Cancelled" in allowed
```

### Pattern 2: Multiple Transitions in One Function

```python
@Contract(feature="orders")
async def rush_order(order_id: str, *, _ctx=None):
    """Quickly move order through multiple states."""
    order = await db.get_order(order_id)
    _ctx.current_state = order.status
    
    # Execute multiple transitions
    if _ctx.current_state == "Pending":
        _ctx.transition("Confirmed")
        _ctx.transition("Processing")
    elif _ctx.current_state == "Confirmed":
        _ctx.transition("Processing")
    
    order.status = _ctx.current_state
    await db.save(order)
    
    return {"status": _ctx.current_state}
```

### Pattern 3: Conditional Transition

```python
@Contract(feature="orders")
async def process_payment(order_id: str, *, _ctx=None):
    order = await db.get_order(order_id)
    _ctx.current_state = order.status
    
    # Attempt payment
    payment_result = await payment_gateway.charge(order.amount)
    
    if payment_result.success:
        _ctx.transition("Paid")
        order.status = "Paid"
    else:
        _ctx.transition("Failed")
        order.status = "Failed"
    
    await db.save(order)
    return {"status": order.status}
```

---

## Best Practices

### 1. Always Sync with Database

```python
# ALWAYS do this for existing records
_ctx.current_state = order.status
```

### 2. Keep Functions Focused

One function = one transition (usually):

```python
# Good: One function, one transition
async def confirm_order(order_id, *, _ctx=None):
    _ctx.transition("Confirmed")

async def process_order(order_id, *, _ctx=None):
    _ctx.transition("Processing")
```

### 3. Handle Errors Gracefully

```python
try:
    _ctx.transition("NextState")
except ValueError as e:
    logger.error(f"Transition failed: {e}")
    raise
```

### 4. Use Type Hints

```python
@Contract(feature="orders")
async def confirm_order(order_id: str, *, _ctx=None) -> dict:
    ...
```

---

## Troubleshooting

### "Feature 'x' not found"

Ensure your `state.yaml` exists at:
```
{RANEX_APP_DIR}/features/{feature}/state.yaml
```

### "_ctx is None"

Make sure `_ctx` is a keyword-only argument:
```python
# Correct
async def func(order_id, *, _ctx=None):

# Wrong
async def func(order_id, _ctx=None):
```

### "Illegal transition"

Check your `state.yaml` transitions:
1. Is the transition defined?
2. Did you sync with database state?

---

## Next Steps

- [State Machine Guide](./10-STATE-MACHINE.md) - Define complex workflows
- [FastAPI Integration](./33-FASTAPI-INTEGRATION.md) - Production setup
- [Python API Reference](./22-PYTHON-API.md) - Full API docs

