# State Machine Validation

The state machine is Ranex's core feature for preventing logic drift in AI-generated code.

---

## What Problem Does It Solve?

AI generates code that skips business logic steps:

```python
# AI-generated code (WRONG!)
def process_order(order):
    order.status = "Delivered"  # Skipped confirmation, processing, shipping!
    return order
```

Your business requires: `Pending → Confirmed → Processing → Shipped → Delivered`

Ranex enforces this at runtime.

---

## How It Works

### 1. Define Rules in YAML

```yaml
# app/features/orders/state.yaml
feature: orders
initial_state: Pending

states:
  Pending: { description: "New order" }
  Confirmed: { description: "Confirmed" }
  Processing: { description: "Being prepared" }
  Shipped: { description: "In transit" }
  Delivered: { description: "Complete", terminal: true }
  Cancelled: { description: "Cancelled", terminal: true }

transitions:
  - { from: Pending, to: Confirmed }
  - { from: Pending, to: Cancelled }
  - { from: Confirmed, to: Processing }
  - { from: Processing, to: Shipped }
  - { from: Shipped, to: Delivered }
```

### 2. Ranex Enforces at Runtime

```python
from ranex_core import StateMachine

sm = StateMachine("orders")  # Loads state.yaml, starts at Pending
sm.transition("Confirmed")   # ✅ Valid
sm.transition("Delivered")   # ❌ Error! Must go through Processing and Shipped
```

---

## YAML Syntax Reference

### Feature Definition

```yaml
feature: orders              # Must match directory name
description: Order workflow  # Human-readable description
initial_state: Pending       # Starting state for new instances
```

### States

```yaml
states:
  StateName:
    description: Human-readable description
    terminal: true  # Optional: Cannot transition FROM this state
```

**Terminal States:**
- Mark states as `terminal: true` when they represent final outcomes
- Examples: `Completed`, `Cancelled`, `Failed`, `Refunded`
- Cannot transition from a terminal state

### Transitions

```yaml
transitions:
  - from: SourceState
    to: TargetState
    description: Optional description of this transition
```

**Rules:**
- Only listed transitions are allowed
- Unlisted transitions throw `ValueError`
- Order of transition definitions doesn't matter

---

## Using StateMachine Directly

### Create Instance

```python
from ranex_core import StateMachine

# Create state machine for a feature
sm = StateMachine("orders")

# Check initial state
print(sm.current_state)  # "Pending"
```

### Check Allowed Transitions

```python
# See what transitions are allowed
allowed = sm.get_allowed_transitions()
print(allowed)  # ["Confirmed", "Cancelled"]
```

### Execute Transition

```python
# Valid transition
sm.transition("Confirmed")
print(sm.current_state)  # "Confirmed"

# Invalid transition - throws error
try:
    sm.transition("Delivered")  # Not allowed from Confirmed!
except ValueError as e:
    print(e)
    # "Illegal transition from 'Confirmed' to 'Delivered'.
    #  Allowed transitions from 'Confirmed': [Processing, Cancelled]"
```

### Set State Directly (Database Sync)

```python
# When loading from database, set current state
sm.current_state = "Processing"

# Now transitions are validated from Processing
sm.transition("Shipped")  # ✅ Valid
```

---

## Performance

| Operation | Latency |
|-----------|---------|
| Create StateMachine | ~50µs |
| Transition | **71ns** |
| Get allowed transitions | ~100ns |

The state machine is implemented in Rust for maximum performance.

---

## Common Patterns

### Pattern 1: Simple Workflow

```yaml
feature: document
initial_state: Draft

states:
  Draft: { description: "Being edited" }
  Review: { description: "Under review" }
  Published: { description: "Live", terminal: true }
  Archived: { description: "Hidden", terminal: true }

transitions:
  - { from: Draft, to: Review }
  - { from: Draft, to: Archived }
  - { from: Review, to: Draft }      # Can go back to Draft
  - { from: Review, to: Published }
  - { from: Published, to: Archived }
```

### Pattern 2: Payment Processing

```yaml
feature: payment
initial_state: Pending

states:
  Pending: { description: "Awaiting payment" }
  Processing: { description: "Being processed" }
  Authorized: { description: "Funds held" }
  Captured: { description: "Payment complete", terminal: true }
  Failed: { description: "Payment failed", terminal: true }
  Refunded: { description: "Money returned", terminal: true }

transitions:
  - { from: Pending, to: Processing }
  - { from: Processing, to: Authorized }
  - { from: Processing, to: Failed }
  - { from: Authorized, to: Captured }
  - { from: Authorized, to: Failed }
  - { from: Captured, to: Refunded }
```

### Pattern 3: Support Ticket

```yaml
feature: ticket
initial_state: Open

states:
  Open: { description: "New ticket" }
  InProgress: { description: "Being worked on" }
  Waiting: { description: "Waiting for customer" }
  Resolved: { description: "Fixed", terminal: true }
  Closed: { description: "Closed without fix", terminal: true }

transitions:
  - { from: Open, to: InProgress }
  - { from: Open, to: Closed }
  - { from: InProgress, to: Waiting }
  - { from: InProgress, to: Resolved }
  - { from: InProgress, to: Closed }
  - { from: Waiting, to: InProgress }  # Customer responded
  - { from: Waiting, to: Closed }      # No response timeout
```

---

## Error Messages

When a transition is blocked, Ranex provides clear error messages:

```
ValueError: Illegal transition from 'Pending' to 'Delivered' for feature 'orders'.
Allowed transitions from 'Pending': [Confirmed, Cancelled]
```

This helps developers (and AI) understand exactly what went wrong.

---

## Best Practices

### 1. Start Simple

Begin with linear workflows, add complexity later:

```yaml
# Start simple
Pending → Processing → Complete

# Add branches as needed
Pending → Processing → Complete
         ↘ Cancelled
```

### 2. Name States Clearly

Use past participles for completed actions:

```yaml
# Good
Confirmed, Shipped, Delivered, Cancelled

# Avoid
Confirm, Ship, Deliver, Cancel
```

### 3. Document Transitions

Add descriptions for non-obvious transitions:

```yaml
transitions:
  - from: Review
    to: Draft
    description: Reviewer requests changes
```

### 4. Use Terminal States

Mark final states to prevent accidental changes:

```yaml
states:
  Delivered:
    description: Order complete
    terminal: true  # Cannot change after delivery
```

---

## Debugging

### Check State File Loaded

```python
from ranex_core import StateMachine

try:
    sm = StateMachine("orders")
    print(f"Loaded: {sm.current_state}")
except ValueError as e:
    print(f"Failed to load: {e}")
```

### Verify File Location

State files must be at:
```
{RANEX_APP_DIR}/features/{feature}/state.yaml
```

Default:
```
./app/features/orders/state.yaml
```

---

## Integration with @Contract

The `@Contract` decorator automatically provides state machine context:

```python
from ranex import Contract

@Contract(feature="orders")
async def confirm_order(order_id: str, *, _ctx=None):
    # _ctx is a StateMachine instance
    _ctx.transition("Confirmed")
    return {"status": "confirmed"}
```

See [@Contract Decorator](./11-CONTRACT-DECORATOR.md) for details.

---

## Next Steps

- [@Contract Decorator](./11-CONTRACT-DECORATOR.md) - Runtime enforcement
- [Python API Reference](./22-PYTHON-API.md) - Full API documentation

