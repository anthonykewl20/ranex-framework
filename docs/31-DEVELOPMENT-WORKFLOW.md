# Development Workflow

Best practices for developing with Ranex.

---

## Workflow Phases

Ranex supports a structured development workflow:

```
Requirements → Design → Implementation → Review → Maintenance
```

### Check Current Phase

```bash
ranex task status
```

### Move Between Phases

```bash
ranex task design --message "Designing order system"
ranex task build --message "Implementing order confirmation"
```

---

## Feature Development Workflow

### Step 1: Define State Machine First

Before writing any code, define your state machine:

```yaml
# app/features/orders/state.yaml
feature: orders
initial_state: Pending

states:
  Pending: { description: "New order" }
  Confirmed: { description: "Confirmed" }
  Processing: { description: "In progress" }
  Shipped: { description: "Shipped" }
  Delivered: { description: "Complete", terminal: true }
  Cancelled: { description: "Cancelled", terminal: true }

transitions:
  - { from: Pending, to: Confirmed }
  - { from: Pending, to: Cancelled }
  - { from: Confirmed, to: Processing }
  - { from: Processing, to: Shipped }
  - { from: Shipped, to: Delivered }
```

### Step 2: Define Models

```python
# app/features/orders/models.py
from pydantic import BaseModel

class OrderCreate(BaseModel):
    product_id: str
    quantity: int

class OrderResponse(BaseModel):
    id: str
    status: str
    product_id: str
    quantity: int
```

### Step 3: Implement Service with @Contract

```python
# app/features/orders/service.py
from ranex import Contract

@Contract(feature="orders")
async def confirm_order(order_id: str, *, _ctx=None):
    order = await db.get_order(order_id)
    _ctx.current_state = order.status
    _ctx.transition("Confirmed")
    order.status = "Confirmed"
    await db.save(order)
    return order
```

### Step 4: Add Routes

```python
# app/features/orders/routes.py
from fastapi import APIRouter
from .service import confirm_order

router = APIRouter()

@router.post("/{order_id}/confirm")
async def confirm_order_endpoint(order_id: str):
    return await confirm_order(order_id)
```

### Step 5: Run Scan

```bash
ranex scan
```

### Step 6: Write Tests

```python
# tests/features/test_orders.py
import pytest
from app.features.orders.service import confirm_order

async def test_confirm_order():
    result = await confirm_order("ORD-001")
    assert result.status == "Confirmed"
```

---

## AI-Assisted Development

### Prompt Engineering for AI

When using AI (Cursor, Claude, etc.), provide context:

```
I'm working on the orders feature in a Ranex project.

State machine (state.yaml):
- States: Pending, Confirmed, Processing, Shipped, Delivered (terminal), Cancelled (terminal)
- Transitions: Pending→Confirmed, Confirmed→Processing, Processing→Shipped, Shipped→Delivered

Please generate a ship_order function using @Contract decorator.
```

### MCP Integration

With MCP configured, AI automatically:
1. Validates state transitions before generating code
2. Checks for existing functions (avoids duplication)
3. Scans for security issues

---

## Code Review Checklist

### State Machine

- [ ] State machine defined in `state.yaml`
- [ ] All states have descriptions
- [ ] Terminal states marked correctly
- [ ] Transitions cover all business cases

### Service Functions

- [ ] `@Contract` decorator applied
- [ ] Database state synced: `_ctx.current_state = order.status`
- [ ] Transitions validated: `_ctx.transition("NewState")`
- [ ] Database updated after transition

### Security

- [ ] No SQL injection (use parameterized queries)
- [ ] No hardcoded secrets
- [ ] No dangerous imports

### Architecture

- [ ] Routes only call services
- [ ] Services only call repositories
- [ ] No cross-feature internal imports

---

## Common Patterns

### Pattern 1: Load → Sync → Transition → Save

```python
@Contract(feature="orders")
async def process_order(order_id: str, *, _ctx=None):
    # 1. Load from database
    order = await repo.get(order_id)
    
    # 2. Sync state machine
    _ctx.current_state = order.status
    
    # 3. Validate and transition
    _ctx.transition("Processing")
    
    # 4. Update and save
    order.status = "Processing"
    await repo.save(order)
    
    return order
```

### Pattern 2: Conditional Transitions

```python
@Contract(feature="payments")
async def process_payment(payment_id: str, *, _ctx=None):
    payment = await repo.get(payment_id)
    _ctx.current_state = payment.status
    
    result = await gateway.charge(payment.amount)
    
    if result.success:
        _ctx.transition("Completed")
        payment.status = "Completed"
    else:
        _ctx.transition("Failed")
        payment.status = "Failed"
    
    await repo.save(payment)
    return payment
```

### Pattern 3: Check Before Transition

```python
@Contract(feature="orders")
async def can_cancel(order_id: str, *, _ctx=None) -> bool:
    order = await repo.get(order_id)
    _ctx.current_state = order.status
    
    allowed = _ctx.get_allowed_transitions()
    return "Cancelled" in allowed
```

---

## Git Workflow

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: ranex-scan
        name: Ranex Security Scan
        entry: ranex scan --strict
        language: system
        types: [python]
        pass_filenames: false
```

### CI/CD Pipeline

```yaml
# .github/workflows/ranex.yml
name: Ranex Checks
on: [push, pull_request]

jobs:
  ranex:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install Ranex
        run: pip install ./ranex_core-*.whl ./ranex
      
      - name: Security Scan
        run: ranex scan --strict
      
      - name: Architecture Check
        run: ranex arch --strict
      
      - name: Health Check
        run: ranex doctor
```

---

## Debugging

### State Machine Issues

```python
# Debug state machine
from ranex_core import StateMachine

sm = StateMachine("orders")
print(f"Current: {sm.current_state}")
print(f"Allowed: {sm.get_allowed_transitions()}")
```

### Contract Issues

```python
# Add logging
@Contract(feature="orders")
async def confirm_order(order_id: str, *, _ctx=None):
    print(f"Initial state: {_ctx.current_state}")
    print(f"Allowed: {_ctx.get_allowed_transitions()}")
    
    _ctx.transition("Confirmed")
    
    print(f"New state: {_ctx.current_state}")
```

### Scan Issues

```bash
# Verbose scan
ranex scan --verbose

# Single file
ranex scan ./app/features/orders/service.py
```

---

## Performance Tips

### 1. State Machine is Fast

State transitions are 71ns. Don't optimize them.

### 2. Database is the Bottleneck

Focus optimization on:
- Database queries
- External API calls
- File I/O

### 3. Batch Operations

```python
# Instead of
for order_id in order_ids:
    await process_order(order_id)

# Do
orders = await repo.get_many(order_ids)
for order in orders:
    # process in batch
```

---

## Next Steps

- [Testing Guide](./32-TESTING.md) - Testing strategies
- [FastAPI Integration](./33-FASTAPI-INTEGRATION.md) - Full example

