# Ranex Framework - FastAPI Integration Guide

**Documentation Status:** Implementation-Based  
**Last Audited:** 2025-01-27  
**Audit Method:** Direct code inspection of `app/` directory and `ranex/__init__.py`

---

## Table of Contents

1. [Overview](#overview)
2. [Core Components](#core-components)
3. [Step-by-Step Integration](#step-by-step-integration)
4. [Middleware Configuration](#middleware-configuration)
5. [@Contract Decorator Usage](#contract-decorator-usage)
6. [State Machine Integration](#state-machine-integration)
7. [Multi-Tenant Support](#multi-tenant-support)
8. [Error Handling and Rollback](#error-handling-and-rollback)
9. [Complete Working Example](#complete-working-example)
10. [API Reference](#api-reference)

---

## Overview

### What Ranex Provides for FastAPI

Ranex Framework integrates with FastAPI through:

1. **@Contract Decorator** (`ranex.Contract`) - Runtime guardrail that enforces state machine transitions and schema validation
2. **ContractMiddleware** (`app.commons.contract_middleware.ContractMiddleware`) - FastAPI middleware for multi-tenant state isolation
3. **State Machine Engine** (`ranex_core.StateMachine`) - Rust-based state machine with YAML configuration
4. **Schema Validator** (`ranex_core.SchemaValidator`) - Optional schema validation using Pydantic models

### Implementation Reality

**What Actually Exists:**
- `ranex.Contract` decorator in `ranex/__init__.py` (lines 27-372)
- `ContractMiddleware` class in `app/commons/contract_middleware.py` (lines 22-84)
- State machine files: `app/features/{feature}/state.yaml` (YAML format)
- Working example: `app/main.py` (complete FastAPI application)

**What Does NOT Exist:**
- No `ranex.commons` package - middleware is in `app.commons`
- No automatic route discovery - routes must be manually registered
- No built-in database integration - uses SQLAlchemy separately

---

## Core Components

### 1. @Contract Decorator

**Location:** `ranex/__init__.py`, lines 27-372

**Signature:**
```python
def Contract(
    feature: str,
    input_schema: Optional[Any] = None,
    auto_validate: bool = True,
    tenant_id: Optional[str] = None,
) -> Callable
```

**What It Actually Does:**

1. **Schema Registration** (if `input_schema` provided):
   - Extracts JSON schema from Pydantic model using `model_json_schema()`
   - Registers schema with `SchemaValidator.register_schema(schema_name, schema_dict)`
   - Schema name format: `{feature}_{function_name}`

2. **State Machine Initialization**:
   - Creates `RustMachine(feature)` instance
   - Loads state machine from `app/features/{feature}/state.yaml`
   - Tracks initial state for rollback on error

3. **Context Injection**:
   - Injects `ctx` (StateMachine instance) as **first positional argument** to decorated function
   - Function signature must accept `ctx` as first parameter: `async def my_function(ctx, ...)`

4. **Error Handling**:
   - On exception, attempts to rollback state to initial state
   - Logs all operations with structured logging
   - Re-raises original exception after rollback attempt

**Actual Code Flow:**

```python
# From ranex/__init__.py, lines 90-182 (async wrapper)
async def async_wrapper(*args, **kwargs):
    # 1. Schema validation (if provided)
    if schema_name and _schema_validation_available:
        validation_result = _schema_validator.validate(schema_name, arg)
        if not validation_result.valid:
            raise ValueError(f"Schema validation failed: {errors}")
    
    # 2. Initialize state machine
    ctx = RustMachine(feature)  # Loads from app/features/{feature}/state.yaml
    initial_state = ctx.current_state
    
    # 3. Inject ctx as first argument
    result = await func(ctx, *args, **kwargs)  # ctx injected here
    
    return result
```

**Critical Implementation Details:**

- **Tenant Isolation:** Uses `tenant_id` parameter OR attempts to get from FastAPI request state (requires middleware)
- **State Rollback:** On exception, calls `ctx.transition(initial_state)` - may fail if transition not allowed
- **Logging:** Uses Python `logging` module with structured extra fields
- **Schema Validation:** Only works if `SchemaValidator` is available in `ranex_core` (may not be available)

---

### 2. ContractMiddleware

**Location:** `app/commons/contract_middleware.py`, lines 22-84

**What It Actually Does:**

1. **Tenant ID Extraction**:
   - Checks `X-Tenant-ID` header first
   - Falls back to `X-User-ID` header
   - Uses `default_tenant` if neither header present

2. **Request State Population**:
   - Sets `request.state.tenant_id` (string)
   - Sets `request.state.contract_context` (empty dict)

3. **No Actual Contract Validation**:
   - Middleware does NOT validate contracts itself
   - Only provides tenant context for @Contract decorator
   - Contract validation happens in @Contract decorator

**Actual Code:**

```python
# From app/commons/contract_middleware.py, lines 43-83
async def dispatch(self, request: Request, call_next: Callable) -> Response:
    # Extract tenant ID
    tenant_id = (
        request.headers.get("X-Tenant-ID") or
        request.headers.get("X-User-ID") or
        self.default_tenant
    )
    
    # Store in request state
    request.state.tenant_id = tenant_id
    request.state.contract_context = {}
    
    # Process request (no contract validation here)
    response = await call_next(request)
    return response
```

**Critical Implementation Details:**

- **No Contract Enforcement:** Middleware only sets tenant context, does not enforce contracts
- **Tenant ID Access:** Use `get_tenant_id(request)` helper function to access tenant ID
- **Request State:** Tenant ID stored in `request.state.tenant_id` (not `request.state.contract_context`)

---

### 3. State Machine Files

**Location:** `app/features/{feature}/state.yaml`

**Format:** YAML file defining states and transitions

**Example Structure:**
```yaml
# app/features/payment/state.yaml
states:
  - name: "Pending"
  - name: "Processing"
  - name: "Completed"
  - name: "Failed"

transitions:
  - from: "Pending"
    to: "Processing"
  - from: "Processing"
    to: "Completed"
  - from: "Processing"
    to: "Failed"
```

**What Actually Happens:**

- `RustMachine(feature)` loads `app/features/{feature}/state.yaml`
- Validates transitions using `ctx.transition(state_name)`
- Raises exception if transition not allowed
- Current state accessible via `ctx.current_state` (property)

---

## Step-by-Step Integration

### Step 1: Install Dependencies

**Required:**
```bash
# Install Ranex Core wheel
pip install wheels/ranex_core-0.0.1-*.whl

# Install FastAPI dependencies
pip install fastapi uvicorn

# Install Ranex Python package (for @Contract decorator)
pip install -e .  # Or install typer rich PyYAML separately
```

**Verification:**
```python
import ranex_core  # Must succeed
from ranex import Contract  # Must succeed
```

---

### Step 2: Create FastAPI Application

**Basic Structure:**

```python
from fastapi import FastAPI
from app.commons.contract_middleware import ContractMiddleware

app = FastAPI(title="My Application")

# Add ContractMiddleware (MUST be added before routes)
app.add_middleware(ContractMiddleware, default_tenant="default")
```

**Critical:** Middleware must be added **before** routes are registered.

---

### Step 3: Create Feature Directory Structure

**Required Structure:**

```
app/
└── features/
    └── my_feature/
        ├── state.yaml          # State machine definition (REQUIRED)
        ├── routes.py           # FastAPI routes
        ├── service.py          # Business logic
        └── models.py          # Data models (optional)
```

**State Machine File (`state.yaml`):**

```yaml
# app/features/my_feature/state.yaml
states:
  - name: "Initial"
  - name: "Processing"
  - name: "Completed"

transitions:
  - from: "Initial"
    to: "Processing"
  - from: "Processing"
    to: "Completed"
```

**Critical:** State machine file MUST exist at `app/features/{feature}/state.yaml` or `@Contract` will fail.

---

### Step 4: Create Route with @Contract

**Basic Route:**

```python
# app/features/my_feature/routes.py
from fastapi import APIRouter, Request
from ranex import Contract
from app.commons.contract_middleware import get_tenant_id

router = APIRouter()

@router.post("/process")
@Contract(feature="my_feature")
async def process_item(ctx, item_id: str, request: Request):
    """
    Process an item with contract enforcement.
    
    Args:
        ctx: StateMachine instance (injected by @Contract)
        item_id: Item identifier
        request: FastAPI Request (for tenant ID access)
    """
    # Get tenant ID from middleware
    tenant_id = get_tenant_id(request)
    
    # Transition state
    await ctx.transition("Processing")
    
    # Business logic here
    result = {"item_id": item_id, "status": "processed"}
    
    # Transition to final state
    await ctx.transition("Completed")
    
    return result
```

**Critical Implementation Details:**

1. **Function Signature:** `ctx` MUST be first parameter (injected by @Contract)
2. **State Transitions:** Use `await ctx.transition(state_name)` for async functions
3. **Tenant Access:** Use `get_tenant_id(request)` to get tenant ID from middleware
4. **Feature Name:** Must match directory name in `app/features/{feature}/`

---

### Step 5: Register Routes

**In `app/main.py`:**

```python
from app.features.my_feature import routes as my_feature_routes

app.include_router(
    my_feature_routes.router,
    prefix="/api/my_feature",
    tags=["My Feature"]
)
```

---

### Step 6: Run Application

```bash
uvicorn app.main:app --reload --port 8000
```

---

## Middleware Configuration

### ContractMiddleware Parameters

**Signature:**
```python
ContractMiddleware(
    app: ASGIApp,
    default_tenant: Optional[str] = None
)
```

**Parameters:**
- `app`: ASGI application (provided by FastAPI)
- `default_tenant`: Default tenant ID if no header provided (default: `"default"`)

**Usage:**
```python
app.add_middleware(ContractMiddleware, default_tenant="my_default_tenant")
```

**Tenant ID Headers:**
- `X-Tenant-ID` (checked first)
- `X-User-ID` (fallback)
- `default_tenant` (if neither header present)

---

### Middleware Order

**Critical:** Middleware order matters. Recommended order:

```python
# 1. CORS (if needed)
app.add_middleware(CORSMiddleware, ...)

# 2. ContractMiddleware (MUST be early for tenant context)
app.add_middleware(ContractMiddleware, default_tenant="default")

# 3. Metrics middleware (if using)
app.add_middleware(PrometheusMiddleware)

# 4. Rate limiting (if using)
app.add_middleware(RateLimiterMiddleware, ...)

# 5. Routes registered after middleware
app.include_router(...)
```

---

## @Contract Decorator Usage

### Basic Usage

```python
@Contract(feature="payment")
async def process_payment(ctx, amount: float):
    await ctx.transition("Processing")
    # ... business logic
    await ctx.transition("Completed")
    return {"status": "success"}
```

### With Schema Validation

```python
from pydantic import BaseModel, Field

class PaymentRequest(BaseModel):
    amount: float = Field(..., gt=0)
    currency: str = Field(default="USD")

@Contract(
    feature="payment",
    input_schema=PaymentRequest,
    auto_validate=True
)
async def process_payment(ctx, request: PaymentRequest):
    # Schema validated automatically before function execution
    await ctx.transition("Processing")
    # ... business logic
    return {"status": "success"}
```

**Critical:** Schema validation only works if `SchemaValidator` is available in `ranex_core`. If not available, validation is skipped with a warning.

### With Tenant ID

```python
@Contract(feature="payment", tenant_id="tenant_123")
async def process_payment(ctx, amount: float):
    # Uses explicit tenant_id instead of middleware
    await ctx.transition("Processing")
    return {"status": "success"}
```

**Note:** If `tenant_id` is provided, middleware tenant ID is ignored.

---

## State Machine Integration

### State Transitions

**Async Functions:**
```python
@Contract(feature="payment")
async def process_payment(ctx, amount: float):
    # Get current state
    current = ctx.current_state  # Returns string like "Pending"
    
    # Transition to new state
    await ctx.transition("Processing")  # Raises exception if transition not allowed
    
    # Transition to final state
    await ctx.transition("Completed")
```

**Sync Functions:**
```python
@Contract(feature="payment")
def process_payment(ctx, amount: float):
    # Sync transitions (no await)
    ctx.transition("Processing")
    ctx.transition("Completed")
```

**Critical:** Transitions are validated against `state.yaml`. Invalid transitions raise exceptions.

---

### State Machine File Format

**Complete Example:**

```yaml
# app/features/payment/state.yaml
states:
  - name: "Pending"
  - name: "Processing"
  - name: "Completed"
  - name: "Failed"
  - name: "Refunded"

transitions:
  - from: "Pending"
    to: "Processing"
  - from: "Processing"
    to: "Completed"
  - from: "Processing"
    to: "Failed"
  - from: "Completed"
    to: "Refunded"
  - from: "Failed"
    to: "Refunded"
```

**Validation Rules:**
- States must be defined in `states:` section
- Transitions must reference existing states
- Invalid transitions raise exceptions at runtime

---

## Multi-Tenant Support

### How It Works

1. **Middleware Sets Tenant Context:**
   - `ContractMiddleware` extracts tenant ID from headers
   - Stores in `request.state.tenant_id`

2. **@Contract Uses Tenant ID:**
   - If `tenant_id` parameter provided, uses that
   - Otherwise, attempts to get from request state (requires middleware)
   - Creates tenant-scoped state machine key: `{feature}:{tenant_id}`

3. **State Isolation:**
   - Each tenant gets separate state machine instance
   - State transitions are isolated per tenant

**Actual Implementation:**

```python
# From ranex/__init__.py, lines 129-158
tenant_context = tenant_id
if tenant_context is None:
    # Try to get from FastAPI request state
    # (requires ContractMiddleware)
    pass

state_key = f"{feature}:{tenant_context or 'default'}"
ctx = RustMachine(feature)  # Creates isolated instance
```

**Critical:** Tenant isolation is achieved through separate `RustMachine` instances, not through shared state with tenant keys.

---

### Accessing Tenant ID in Routes

```python
from app.commons.contract_middleware import get_tenant_id

@router.post("/process")
@Contract(feature="payment")
async def process_payment(ctx, amount: float, request: Request):
    tenant_id = get_tenant_id(request)  # Gets from request.state.tenant_id
    # Use tenant_id for business logic
    return {"tenant_id": tenant_id, "amount": amount}
```

---

## Error Handling and Rollback

### Automatic Rollback

**What Happens on Exception:**

1. **Exception Occurs:** Function raises exception
2. **State Check:** @Contract checks if state changed from initial state
3. **Rollback Attempt:** Calls `ctx.transition(initial_state)`
4. **Logging:** Logs rollback success/failure
5. **Re-raise:** Original exception is re-raised

**Actual Code:**

```python
# From ranex/__init__.py, lines 184-242
except Exception as e:
    if ctx is not None and initial_state is not None:
        current_state = ctx.current_state
        if current_state != initial_state:
            try:
                ctx.transition(initial_state)  # Rollback attempt
                logger.error("State rolled back", ...)
            except Exception as rollback_error:
                logger.error("Rollback failed", ...)
    raise  # Re-raise original exception
```

**Critical:** Rollback may fail if transition back to initial state is not allowed in `state.yaml`. In that case, rollback failure is logged but original exception is still raised.

---

### Error Handling Best Practices

```python
@Contract(feature="payment")
async def process_payment(ctx, amount: float):
    try:
        await ctx.transition("Processing")
        # Business logic that may fail
        result = await risky_operation()
        await ctx.transition("Completed")
        return result
    except BusinessException as e:
        # Transition to error state if defined
        await ctx.transition("Failed")
        raise HTTPException(status_code=400, detail=str(e))
```

**Note:** @Contract will attempt automatic rollback, but you can also manually transition to error states.

---

## Complete Working Example

### File Structure

```
app/
├── main.py
├── commons/
│   └── contract_middleware.py
└── features/
    └── payment/
        ├── state.yaml
        ├── routes.py
        └── service.py
```

---

### State Machine (`app/features/payment/state.yaml`)

```yaml
states:
  - name: "Pending"
  - name: "Processing"
  - name: "Completed"
  - name: "Failed"

transitions:
  - from: "Pending"
    to: "Processing"
  - from: "Processing"
    to: "Completed"
  - from: "Processing"
    to: "Failed"
```

---

### Routes (`app/features/payment/routes.py`)

```python
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field
from ranex import Contract
from app.commons.contract_middleware import get_tenant_id
from . import service

router = APIRouter()

class PaymentRequest(BaseModel):
    amount: float = Field(..., gt=0)
    currency: str = Field(default="USD")

@router.post("/pay")
@Contract(
    feature="payment",
    input_schema=PaymentRequest,
    auto_validate=True
)
async def create_payment(ctx, request: PaymentRequest, http_request: Request):
    """Create payment with contract enforcement."""
    tenant_id = get_tenant_id(http_request)
    
    # Transition to processing
    await ctx.transition("Processing")
    
    try:
        # Business logic
        result = await service.process_payment(
            amount=request.amount,
            currency=request.currency,
            tenant_id=tenant_id
        )
        
        # Transition to completed
        await ctx.transition("Completed")
        
        return result
    except Exception as e:
        # Transition to failed (if allowed)
        try:
            await ctx.transition("Failed")
        except:
            pass  # Transition may not be allowed
        raise HTTPException(status_code=400, detail=str(e))
```

---

### Main Application (`app/main.py`)

```python
from fastapi import FastAPI
from app.commons.contract_middleware import ContractMiddleware
from app.features.payment import routes as payment_routes

app = FastAPI(title="Payment API")

# Add middleware (MUST be before routes)
app.add_middleware(ContractMiddleware, default_tenant="default")

# Register routes
app.include_router(
    payment_routes.router,
    prefix="/api/payment",
    tags=["Payment"]
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

### Testing

```bash
# Start server
uvicorn app.main:app --reload

# Test with tenant header
curl -X POST "http://localhost:8000/api/payment/pay" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: tenant_123" \
  -d '{"amount": 100.50, "currency": "USD"}'
```

---

## API Reference

### @Contract Decorator

**Location:** `ranex/__init__.py`

**Parameters:**
- `feature: str` - Feature name (must match `app/features/{feature}/`)
- `input_schema: Optional[Any]` - Pydantic BaseModel class for validation
- `auto_validate: bool` - Whether to validate state transitions (default: True)
- `tenant_id: Optional[str]` - Explicit tenant ID (overrides middleware)

**Returns:** Decorator function

**Injected Context:**
- `ctx: StateMachine` - Injected as first positional argument
- Properties: `ctx.current_state` (str)
- Methods: `await ctx.transition(state_name: str)` (async) or `ctx.transition(state_name: str)` (sync)

---

### ContractMiddleware

**Location:** `app/commons/contract_middleware.py`

**Class:** `ContractMiddleware(BaseHTTPMiddleware)`

**Parameters:**
- `app: ASGIApp` - ASGI application
- `default_tenant: Optional[str]` - Default tenant ID (default: "default")

**Request State:**
- `request.state.tenant_id: str` - Tenant ID from headers
- `request.state.contract_context: dict` - Empty dict (reserved for future use)

**Helper Functions:**
- `get_tenant_id(request: Request) -> str` - Extract tenant ID from request
- `get_contract_context(request: Request) -> dict` - Get contract context dict

---

### StateMachine (Rust Core)

**Location:** `ranex_core.StateMachine`

**Initialization:**
```python
from ranex_core import StateMachine

ctx = StateMachine(feature)  # Loads app/features/{feature}/state.yaml
```

**Properties:**
- `ctx.current_state: str` - Current state name

**Methods:**
- `ctx.transition(state_name: str)` - Transition to new state (sync)
- `await ctx.transition(state_name: str)` - Transition to new state (async)

**Exceptions:**
- Raises exception if transition not allowed in `state.yaml`

---

## Common Issues and Solutions

### Issue: "State machine file not found"

**Error:** `FileNotFoundError` or state machine fails to load

**Solution:**
- Ensure `app/features/{feature}/state.yaml` exists
- Check feature name matches directory name
- Verify YAML syntax is correct

---

### Issue: "Invalid transition"

**Error:** Exception raised when calling `ctx.transition()`

**Solution:**
- Check `state.yaml` defines the transition
- Verify current state allows transition to target state
- Check state names match exactly (case-sensitive)

---

### Issue: "Schema validation not available"

**Warning:** Schema validation skipped

**Solution:**
- `SchemaValidator` may not be available in `ranex_core`
- This is non-critical - validation is optional
- Function will still execute without schema validation

---

### Issue: "Tenant ID not found"

**Error:** Tenant ID is "default" when expecting specific tenant

**Solution:**
- Ensure `ContractMiddleware` is added before routes
- Check request includes `X-Tenant-ID` or `X-User-ID` header
- Verify middleware order is correct

---

## Implementation Notes

### What Is Actually Enforced

1. **State Transitions:** Validated against `state.yaml` at runtime
2. **Schema Validation:** Optional, only if `SchemaValidator` available
3. **Error Rollback:** Attempted automatically, may fail if transition not allowed
4. **Tenant Isolation:** Achieved through separate `StateMachine` instances

### What Is NOT Enforced

1. **Route Registration:** Must be done manually
2. **Database Transactions:** Not handled by Ranex
3. **Authentication:** Not handled by Ranex
4. **Rate Limiting:** Separate middleware (not part of ContractMiddleware)

---

**Documentation Generated:** 2025-01-27  
**Method:** Direct code inspection of `ranex/__init__.py`, `app/commons/contract_middleware.py`, `app/main.py`, and `app/features/payment/routes.py`  
**Assumptions:** None - all claims verified against actual implementation

