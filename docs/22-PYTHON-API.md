# Python API Reference

Complete reference for Ranex Python API.

---

## Installation

```python
# Rust core (required)
pip install ranex_core-*.whl

# Python package (required)
pip install ./ranex
```

---

## Module: ranex

### Contract Decorator

```python
from ranex import Contract

@Contract(feature="orders")
async def my_function(arg1, arg2, *, _ctx=None):
    _ctx.transition("NewState")
    return result
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `feature` | `str` | Feature name (matches state.yaml) |

**Injected `_ctx`:**

| Property/Method | Description |
|-----------------|-------------|
| `current_state` | Current state (str, read/write) |
| `transition(state)` | Move to new state |
| `get_allowed_transitions()` | List allowed next states |

### StateTransitionError

```python
from ranex import StateTransitionError

try:
    _ctx.transition("InvalidState")
except StateTransitionError as e:
    print(f"Transition failed: {e}")
```

---

## Module: ranex_core

### StateMachine

Direct state machine access without decorator.

```python
from ranex_core import StateMachine

# Create
sm = StateMachine("orders")

# Properties
print(sm.current_state)      # "Pending"
sm.current_state = "Confirmed"  # Set directly

# Methods
sm.transition("Processing")  # Validate and move
allowed = sm.get_allowed_transitions()  # ["Processing", "Cancelled"]
```

**Constructor:**
```python
StateMachine(feature: str)
```

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `transition(state)` | `state: str` | `None` | Validate and transition |
| `get_allowed_transitions()` | - | `List[str]` | Get allowed states |

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `current_state` | `str` | Current state (read/write) |

---

### SecurityScanner

```python
from ranex_core import SecurityScanner

scanner = SecurityScanner()

# Scan a file
result = scanner.scan_file_py("app/service.py")

print(result.secure)          # bool
print(result.violations)      # List[SecurityViolation]
print(result.scan_time_ms)    # int
```

**SecurityScanResult:**

| Property | Type | Description |
|----------|------|-------------|
| `secure` | `bool` | True if no violations |
| `violations` | `List[SecurityViolation]` | List of findings |
| `scan_time_ms` | `int` | Scan duration |

**SecurityViolation:**

| Property | Type | Description |
|----------|------|-------------|
| `line` | `int` | Line number |
| `column` | `int` | Column number |
| `pattern` | `str` | Pattern type |
| `message` | `str` | Description |
| `severity` | `str` | "high", "medium", "low" |

---

### ImportValidator

```python
from ranex_core import ImportValidator

validator = ImportValidator()

# Check package
result = validator.check_package("reqests")

print(result.is_valid)      # False
print(result.suggestion)    # "requests"
print(result.distance)      # 1
```

**ValidationResult:**

| Property | Type | Description |
|----------|------|-------------|
| `is_valid` | `bool` | True if valid |
| `suggestion` | `str \| None` | Suggested package |
| `distance` | `int` | Levenshtein distance |
| `message` | `str` | Description |

---

### AuditTrail

Cryptographic audit logging.

```python
from ranex_core import AuditTrail

# Create audit trail
audit = AuditTrail("./logs/audit.log", True)  # True = enable signing

# Log event
audit.log_event(
    action_type="order_confirmed",
    feature="orders",
    user_id="user_123",
    data={"order_id": "ORD-001", "amount": 99.99}
)

# Verify integrity
is_valid = audit.verify_integrity()
print(f"Audit log valid: {is_valid}")
```

**Constructor:**
```python
AuditTrail(log_path: str, enable_signing: bool)
```

**Methods:**

| Method | Parameters | Description |
|--------|------------|-------------|
| `log_event(...)` | See below | Log an audit event |
| `verify_integrity()` | - | Verify hash chain |

**log_event parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `action_type` | `str` | Type of action |
| `feature` | `str` | Feature name |
| `user_id` | `str \| None` | User ID |
| `data` | `Dict[str, Any] \| None` | Event data |

---

### PersonaRegistry

```python
from ranex_core import PersonaRegistry

registry = PersonaRegistry()

# List all personas
personas = registry.all_personas()
for p in personas:
    print(f"{p.name}: {p.role}")

# Get specific persona
persona = registry.get_persona("python_engineer")
print(persona.capabilities)
print(persona.boundaries)
```

**Persona:**

| Property | Type | Description |
|----------|------|-------------|
| `name` | `str` | Persona identifier |
| `role` | `str` | Role description |
| `capabilities` | `List[str]` | What persona can do |
| `boundaries` | `List[str]` | What persona cannot do |

---

### StructureSentinel

```python
from ranex_core import StructureSentinel

sentinel = StructureSentinel("./app")

# Check a file
try:
    sentinel.check_file("app/utils/helper.py")
except Exception as e:
    print(f"Structure violation: {e}")
```

**Constructor:**
```python
StructureSentinel(root: str)
```

**Methods:**

| Method | Parameters | Description |
|--------|------------|-------------|
| `check_file(path)` | `path: str` | Check file location |

---

### SqlValidator

```python
from ranex_core import SqlValidator

validator = SqlValidator()

# Validate query
result = validator.validate("SELECT * FROM users WHERE id = 1")

print(result.is_valid)     # True
print(result.query_type)   # "SELECT"
print(result.tables)       # ["users"]
```

---

### SemanticAtlas

```python
from ranex_core import SemanticAtlas

atlas = SemanticAtlas()

# Search for functions (TF-IDF in Community Edition)
results = atlas.search("calculate tax", top_k=5)

for r in results:
    print(f"{r.function_name} in {r.file_path}")
    print(f"  Signature: {r.signature}")
    print(f"  Similarity: {r.score}")
```

---

## Complete Example

```python
from ranex import Contract
from ranex_core import (
    StateMachine,
    SecurityScanner,
    ImportValidator,
    AuditTrail,
)

# Setup
audit = AuditTrail("./audit.log", True)
scanner = SecurityScanner()

# Service with contract
@Contract(feature="orders")
async def process_order(order_id: str, *, _ctx=None):
    """Process an order with full Ranex integration."""
    
    # Log action
    audit.log_event(
        action_type="process_started",
        feature="orders",
        user_id="system",
        data={"order_id": order_id}
    )
    
    # Validate and transition
    _ctx.transition("Processing")
    
    # Business logic here...
    
    return {"order_id": order_id, "status": "Processing"}


# Direct state machine usage
def check_order_state(order_id: str, db_status: str):
    """Check if order can be shipped."""
    sm = StateMachine("orders")
    sm.current_state = db_status
    
    allowed = sm.get_allowed_transitions()
    return "Shipped" in allowed


# Security scanning
def validate_file(file_path: str) -> bool:
    """Validate a file for security issues."""
    result = scanner.scan_file_py(file_path)
    
    if not result.secure:
        for v in result.violations:
            print(f"[{v.severity}] {v.message} at line {v.line}")
    
    return result.secure


# Import validation
def check_imports(imports: list[str]) -> list[str]:
    """Check imports for typosquatting."""
    validator = ImportValidator()
    suspicious = []
    
    for imp in imports:
        result = validator.check_package(imp)
        if not result.is_valid:
            suspicious.append(f"{imp} → {result.suggestion}")
    
    return suspicious
```

---

## Type Hints

For type checking, Ranex exports types:

```python
from ranex import Contract
from ranex_core import (
    StateMachine,
    SecurityScanner,
    SecurityScanResult,
    SecurityViolation,
    ImportValidator,
    ValidationResult,
    AuditTrail,
    PersonaRegistry,
    Persona,
    StructureSentinel,
    SemanticAtlas,
    SqlValidator,
)
```

---

## Error Handling

```python
from ranex import Contract, StateTransitionError

@Contract(feature="orders")
async def safe_transition(order_id: str, target: str, *, _ctx=None):
    try:
        _ctx.transition(target)
        return {"success": True, "state": target}
    except (ValueError, StateTransitionError) as e:
        return {"success": False, "error": str(e)}
```

---

## Next Steps

- [State Machine Guide](./10-STATE-MACHINE.md) - State machine patterns
- [@Contract Decorator](./11-CONTRACT-DECORATOR.md) - Decorator usage
- [FastAPI Integration](./33-FASTAPI-INTEGRATION.md) - Full stack setup

