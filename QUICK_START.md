# Ranex Community Edition - Quick Start (5 minutes)

## Step 1: Install

```bash
# Option A: Use installer
./install.sh

# Option B: Manual install
pip install ranex_core-*.whl
pip install ./ranex
```

## Step 2: Initialize Your Project

```bash
cd your-fastapi-project
ranex init
```

This creates:
- `.ranex/` - Configuration directory
- State machine templates

## Step 3: Create a State Machine

Create `app/features/orders/state.yaml`:

```yaml
feature: orders
initial_state: Pending

states:
  Pending: { description: "New order" }
  Confirmed: { description: "Order confirmed" }
  Processing: { description: "Being prepared" }
  Shipped: { description: "In transit" }
  Delivered: { description: "Completed", terminal: true }
  Cancelled: { description: "Cancelled", terminal: true }

transitions:
  - { from: Pending, to: Confirmed }
  - { from: Pending, to: Cancelled }
  - { from: Confirmed, to: Processing }
  - { from: Confirmed, to: Cancelled }
  - { from: Processing, to: Shipped }
  - { from: Shipped, to: Delivered }
```

## Step 4: Protect Your Functions

```python
from ranex import Contract

@Contract(feature="orders")
async def confirm_order(order_id: str, *, _ctx=None):
    """
    _ctx is automatically injected with the state machine.
    """
    # Validate transition (will throw if invalid)
    _ctx.transition("Confirmed")
    
    # Your business logic here
    order = await db.get_order(order_id)
    order.status = "confirmed"
    await db.save(order)
    
    return {"order_id": order_id, "status": "confirmed"}
```

## Step 5: Scan for Security Issues

```bash
ranex scan
```

Output:
```
🔍 Scanning project...

Security Scan Results:
  ✅ No SQL injection found
  ✅ No command injection found
  ⚠️  1 hardcoded secret found in config.py:15
  
Architecture Check:
  ✅ Layer boundaries respected
  ✅ No circular imports
```

## That's It!

Your FastAPI app now has:
- ✅ State machine enforcement
- ✅ Security scanning
- ✅ Architecture validation

---

## Common Patterns

### Pattern 1: Order Processing

```python
from ranex import Contract

@Contract(feature="orders")
async def process_order(order_id: str, *, _ctx=None):
    order = await get_order(order_id)
    
    # Sync state machine with database
    _ctx.current_state = order.status
    
    # Validate and execute transition
    _ctx.transition("Processing")
    
    # Business logic
    await process_payment(order)
    await reserve_inventory(order)
    
    # Update database
    order.status = "Processing"
    await save_order(order)
    
    return order
```

### Pattern 2: Handle Multiple Transitions

```python
@Contract(feature="orders")
async def ship_order(order_id: str, tracking_number: str, *, _ctx=None):
    order = await get_order(order_id)
    _ctx.current_state = order.status
    
    # This will fail if not in "Processing" state
    _ctx.transition("Shipped")
    
    order.status = "Shipped"
    order.tracking = tracking_number
    await save_order(order)
    
    return {"status": "shipped", "tracking": tracking_number}
```

### Pattern 3: Cancellation (Terminal State)

```python
@Contract(feature="orders")
async def cancel_order(order_id: str, reason: str, *, _ctx=None):
    order = await get_order(order_id)
    _ctx.current_state = order.status
    
    # Can only cancel from Pending or Confirmed
    _ctx.transition("Cancelled")  # Terminal state - no going back!
    
    order.status = "Cancelled"
    order.cancel_reason = reason
    await save_order(order)
    
    return {"status": "cancelled", "reason": reason}
```

---

## Troubleshooting

### "Feature 'orders' not found"

Make sure your `state.yaml` is in the right location:
```
app/features/orders/state.yaml
```

Or set the environment variable:
```bash
export RANEX_APP_DIR=/path/to/your/app
```

### "Illegal transition from X to Y"

This means your code is trying to skip a state. Check your `state.yaml` transitions.

---

## Next Steps

- Read the full [README.md](./README.md)
- Check out the [documentation](https://ranex.dev/docs)
- Upgrade to Team Edition for RAG, ARBITER, and more

