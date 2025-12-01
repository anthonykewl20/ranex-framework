# Architecture Enforcement

Ranex validates your project structure to prevent circular imports, layer violations, and architectural drift.

---

## What It Does

Architecture enforcement ensures:

1. **Layer Boundaries** - Presentation layer can't import from database layer directly
2. **Feature Isolation** - Features don't import from each other's internals
3. **Forbidden Folders** - No `utils/`, `helpers/` folders that become dumping grounds

---

## Running Architecture Check

### CLI Command

```bash
ranex arch
```

Output:
```
🏗️ Architecture Validation
==========================

Layer Analysis:
  ✅ Routes → Services: Valid
  ✅ Services → Repositories: Valid
  ❌ Routes → Database: VIOLATION
     - app/features/orders/routes.py:15
       Direct database access from route layer
       Fix: Use service layer instead

Feature Isolation:
  ✅ orders: Isolated
  ⚠️ payments: Imports from orders internals
     - app/features/payments/service.py:8
       Imports app.features.orders.repository

Structure:
  ✅ No forbidden folders found

Result: 2 issues found
```

### Python API

```python
from ranex_core import LayerValidator

validator = LayerValidator("./app")
result = validator.check_layers()

for violation in result.violations:
    print(f"{violation.file}:{violation.line}")
    print(f"  {violation.message}")
```

---

## Layer Architecture

### Recommended Layers

```
┌─────────────────────────────────────────┐
│              Routes (HTTP)              │  ← FastAPI endpoints
├─────────────────────────────────────────┤
│              Services                   │  ← Business logic
├─────────────────────────────────────────┤
│              Repositories               │  ← Data access
├─────────────────────────────────────────┤
│              Database                   │  ← SQLAlchemy models
└─────────────────────────────────────────┘
```

### Valid Import Directions

```
routes.py     → services.py     ✅
services.py   → repository.py   ✅
repository.py → models.py       ✅

routes.py     → repository.py   ❌ (skip layer)
routes.py     → models.py       ❌ (skip layers)
services.py   → routes.py       ❌ (wrong direction)
```

---

## Project Structure

### Recommended Structure

```
app/
├── main.py                    # FastAPI app entry
├── commons/                   # Shared utilities
│   ├── __init__.py
│   ├── auth.py               # Auth utilities
│   └── validation.py         # Validation helpers
└── features/                  # Business features
    ├── orders/
    │   ├── __init__.py
    │   ├── routes.py         # HTTP endpoints
    │   ├── service.py        # Business logic
    │   ├── repository.py     # Database access
    │   ├── models.py         # Pydantic models
    │   └── state.yaml        # State machine
    └── payments/
        ├── __init__.py
        ├── routes.py
        ├── service.py
        └── models.py
```

### Why This Structure?

| Benefit | Explanation |
|---------|-------------|
| **Feature isolation** | Each feature is self-contained |
| **Clear dependencies** | Easy to see what imports what |
| **AI-friendly** | AI can work on one feature without seeing others |
| **Testable** | Each layer can be tested independently |

---

## Layer Violations

### Violation: Route Accessing Database

```python
# ❌ BAD: Route directly uses database
# app/features/orders/routes.py
from fastapi import APIRouter
from app.database import db_session  # Violation!

router = APIRouter()

@router.get("/orders/{order_id}")
async def get_order(order_id: str):
    order = db_session.query(Order).filter_by(id=order_id).first()
    return order
```

**Fix:**

```python
# ✅ GOOD: Route uses service layer
# app/features/orders/routes.py
from fastapi import APIRouter
from .service import get_order_service

router = APIRouter()

@router.get("/orders/{order_id}")
async def get_order(order_id: str):
    return await get_order_service(order_id)


# app/features/orders/service.py
from .repository import OrderRepository

async def get_order_service(order_id: str):
    repo = OrderRepository()
    return await repo.get_by_id(order_id)
```

---

### Violation: Cross-Feature Import

```python
# ❌ BAD: Payments imports from orders internals
# app/features/payments/service.py
from app.features.orders.repository import OrderRepository  # Violation!

class PaymentService:
    def process(self, order_id: str):
        repo = OrderRepository()  # Shouldn't access this directly
        order = repo.get(order_id)
```

**Fix:**

```python
# ✅ GOOD: Use public interface
# app/features/payments/service.py
from app.features.orders import get_order  # Public API

class PaymentService:
    def process(self, order_id: str):
        order = get_order(order_id)  # Use exported function


# app/features/orders/__init__.py
from .service import get_order_service as get_order

__all__ = ["get_order"]  # Explicit public API
```

---

## Forbidden Folders

Ranex blocks certain folder patterns that lead to code smell:

### Blocked Patterns

| Folder | Why Blocked |
|--------|-------------|
| `utils/` | Becomes catch-all, violates single responsibility |
| `helpers/` | Same as utils, undefined scope |
| `lib/` | Internal libraries should be packages |
| `shared/` | Use `commons/` with clear purpose |
| `misc/` | Undefined content |
| `common/` | Too vague, use `commons/` |

### If You Need Shared Code

```
# ❌ Don't
app/utils/
app/helpers/
app/lib/

# ✅ Do
app/commons/auth.py       # Authentication utilities
app/commons/validation.py # Validation helpers
app/commons/formatting.py # Formatting utilities
```

---

## Configuration

### Custom Layer Rules

In `.ranex/config.toml`:

```toml
[architecture]
enabled = true
layer_validation = true

# Define your layers (top to bottom)
layers = ["routes", "services", "repositories", "models"]

# Allow specific violations
allow = [
    "app/features/*/routes.py -> app/commons/*"
]
```

### Ignoring Files

In `.ranex/ignore`:

```
# Ignore legacy code
app/legacy/**

# Ignore generated code
app/generated/**
```

---

## Integration with CI/CD

### GitHub Actions

```yaml
name: Architecture Check
on: [push, pull_request]

jobs:
  architecture:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install Ranex
        run: pip install ./ranex_core-*.whl
      - name: Check Architecture
        run: ranex arch --strict
```

### Pre-commit

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: ranex-arch
        name: Architecture Check
        entry: ranex arch
        language: system
        pass_filenames: false
```

---

## Common Patterns

### Pattern 1: Dependency Injection

```python
# app/features/orders/service.py
from typing import Protocol

class OrderRepositoryProtocol(Protocol):
    async def get(self, id: str) -> Order: ...
    async def save(self, order: Order) -> None: ...

class OrderService:
    def __init__(self, repo: OrderRepositoryProtocol):
        self.repo = repo
    
    async def confirm_order(self, order_id: str):
        order = await self.repo.get(order_id)
        # ...
```

### Pattern 2: Feature Public API

```python
# app/features/orders/__init__.py
"""
Public API for orders feature.
Only these should be imported by other features.
"""
from .service import (
    get_order,
    create_order,
    confirm_order,
)
from .models import (
    Order,
    OrderCreate,
    OrderResponse,
)

__all__ = [
    "get_order",
    "create_order", 
    "confirm_order",
    "Order",
    "OrderCreate",
    "OrderResponse",
]
```

### Pattern 3: Commons Organization

```python
# app/commons/auth.py
"""Authentication utilities."""

def get_current_user():
    """Get current authenticated user."""
    ...

def require_role(role: str):
    """Decorator to require specific role."""
    ...


# app/commons/validation.py
"""Validation utilities."""

def validate_email(email: str) -> bool:
    """Validate email format."""
    ...
```

---

## Troubleshooting

### "Layer violation but it's intentional"

Add to `.ranex/config.toml`:

```toml
[architecture]
allow = [
    "app/features/orders/routes.py -> app/features/orders/models.py"
]
```

### "Forbidden folder but I need it"

Rename to something specific:

```
utils/ → commons/
helpers/ → shared_logic/
lib/ → internal/
```

---

## Next Steps

- [Import Validation](./14-IMPORT-VALIDATION.md) - Package security
- [Project Structure](./30-PROJECT-STRUCTURE.md) - Full structure guide
- [Development Workflow](./31-DEVELOPMENT-WORKFLOW.md) - Best practices

