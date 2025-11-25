# Ranex Framework - AI Integration Guide

**Purpose:** This document provides AI systems (LLMs, code assistants, etc.) with accurate, implementation-based information about integrating Ranex Framework into FastAPI applications.

**Documentation Status:** Implementation-Based  
**Last Audited:** 2025-01-27  
**Audit Method:** Direct code inspection

---

## Quick Reference for AI Systems

### Core Components (What Actually Exists)

1. **@Contract Decorator** (`ranex.Contract`)
   - **Location:** `ranex/__init__.py`, lines 27-372
   - **Purpose:** Runtime guardrail for state machine enforcement
   - **Injects:** `ctx` (StateMachine instance) as first parameter
   - **Validates:** State transitions against `app/features/{feature}/state.yaml`

2. **ContractMiddleware** (`app.commons.contract_middleware.ContractMiddleware`)
   - **Location:** `app/commons/contract_middleware.py`, lines 22-84
   - **Purpose:** Multi-tenant state isolation
   - **Sets:** `request.state.tenant_id` from headers (`X-Tenant-ID` or `X-User-ID`)

3. **StateMachine** (`ranex_core.StateMachine`)
   - **Location:** Rust core (compiled binary)
   - **Purpose:** State machine engine
   - **Loads:** `app/features/{feature}/state.yaml` files

### Critical Implementation Facts

**DO:**
- ✅ Use `@Contract(feature="payment")` decorator on FastAPI routes
- ✅ Accept `ctx` as first parameter in decorated functions
- ✅ Call `await ctx.transition(state_name)` for state transitions
- ✅ Add `ContractMiddleware` before registering routes
- ✅ Create `app/features/{feature}/state.yaml` files for each feature
- ✅ Use `get_tenant_id(request)` to access tenant ID from middleware

**DON'T:**
- ❌ Don't import from `ranex.commons` - middleware is in `app.commons`
- ❌ Don't forget to add `ctx` as first parameter
- ❌ Don't skip state.yaml files - they are required
- ❌ Don't add middleware after routes - order matters
- ❌ Don't assume schema validation is always available

---

## Integration Pattern (Copy-Paste Ready)

### Minimal FastAPI Integration

```python
from fastapi import FastAPI, Request
from ranex import Contract
from app.commons.contract_middleware import ContractMiddleware, get_tenant_id

app = FastAPI()

# 1. Add middleware FIRST (before routes)
app.add_middleware(ContractMiddleware, default_tenant="default")

# 2. Create state.yaml at: app/features/my_feature/state.yaml
# states:
#   - name: "Initial"
#   - name: "Processing"
#   - name: "Completed"
# transitions:
#   - from: "Initial"
#     to: "Processing"
#   - from: "Processing"
#     to: "Completed"

# 3. Create route with @Contract
@router.post("/process")
@Contract(feature="my_feature")
async def process_item(ctx, item_id: str, request: Request):
    tenant_id = get_tenant_id(request)
    await ctx.transition("Processing")
    # ... business logic
    await ctx.transition("Completed")
    return {"status": "success"}
```

---

## File Structure Requirements

```
app/
├── main.py                          # FastAPI app with middleware
├── commons/
│   └── contract_middleware.py      # ContractMiddleware class
└── features/
    └── {feature_name}/
        ├── state.yaml               # REQUIRED: State machine definition
        ├── routes.py                # FastAPI routes with @Contract
        └── service.py               # Business logic (optional)
```

**Critical:** `state.yaml` MUST exist at `app/features/{feature}/state.yaml`

---

## Function Signature Pattern

### Correct Pattern

```python
@Contract(feature="payment")
async def my_function(ctx, param1: str, param2: int, request: Request):
    # ctx is injected by @Contract as first parameter
    await ctx.transition("Processing")
    return {"result": "success"}
```

### Common Mistakes

```python
# WRONG: Missing ctx parameter
@Contract(feature="payment")
async def my_function(param1: str):  # ❌ Missing ctx
    pass

# WRONG: ctx not first parameter
@Contract(feature="payment")
async def my_function(param1: str, ctx):  # ❌ ctx must be first
    pass

# WRONG: Using wrong import path
from ranex.commons.contract_middleware import ContractMiddleware  # ❌ Wrong path
# Correct: from app.commons.contract_middleware import ContractMiddleware
```

---

## State Machine File Format

**Required Format:** YAML

**Location:** `app/features/{feature}/state.yaml`

**Example:**
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

**Validation:** Transitions are validated at runtime. Invalid transitions raise exceptions.

---

## Multi-Tenant Pattern

### How It Works

1. **Middleware extracts tenant ID:**
   ```python
   # ContractMiddleware checks headers:
   tenant_id = request.headers.get("X-Tenant-ID") or request.headers.get("X-User-ID") or "default"
   request.state.tenant_id = tenant_id
   ```

2. **Access tenant ID in routes:**
   ```python
   from app.commons.contract_middleware import get_tenant_id
   
   @Contract(feature="payment")
   async def process(ctx, amount: float, request: Request):
       tenant_id = get_tenant_id(request)  # Gets from request.state.tenant_id
       # Use tenant_id for business logic
   ```

3. **State isolation:**
   - Each tenant gets separate `StateMachine` instance
   - State transitions are isolated per tenant

---

## Error Handling Pattern

### Automatic Rollback

**What Happens:**
- On exception, @Contract attempts to rollback state to initial state
- Rollback may fail if transition not allowed in state.yaml
- Original exception is always re-raised

**Example:**
```python
@Contract(feature="payment")
async def process(ctx, amount: float):
    initial_state = ctx.current_state  # Tracked automatically
    await ctx.transition("Processing")
    try:
        # Risky operation
        result = await risky_operation()
        await ctx.transition("Completed")
        return result
    except Exception as e:
        # @Contract will attempt rollback automatically
        # You can also manually transition to error state
        try:
            await ctx.transition("Failed")
        except:
            pass  # Transition may not be allowed
        raise
```

---

## Schema Validation Pattern

### With Pydantic Models

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
    return {"status": "success"}
```

**Note:** Schema validation only works if `SchemaValidator` is available in `ranex_core`. If not available, validation is skipped with a warning.

---

## Complete Working Example

See `docs/FASTAPI_INTEGRATION.md` for complete step-by-step guide with full code examples.

**Quick Start:**
1. Install: `pip install wheels/ranex_core-0.0.1-*.whl`
2. Add middleware: `app.add_middleware(ContractMiddleware)`
3. Create state.yaml: `app/features/{feature}/state.yaml`
4. Decorate route: `@Contract(feature="{feature}")`
5. Accept ctx: `async def my_route(ctx, ...)`

---

## Common Integration Scenarios

### Scenario 1: Basic Route with State Machine

```python
@router.post("/process")
@Contract(feature="payment")
async def process_payment(ctx, amount: float, request: Request):
    await ctx.transition("Processing")
    result = await business_logic(amount)
    await ctx.transition("Completed")
    return result
```

### Scenario 2: Route with Schema Validation

```python
@router.post("/pay")
@Contract(feature="payment", input_schema=PaymentRequest)
async def pay(ctx, request: PaymentRequest, http_request: Request):
    tenant_id = get_tenant_id(http_request)
    await ctx.transition("Processing")
    result = await process(amount=request.amount, tenant_id=tenant_id)
    await ctx.transition("Completed")
    return result
```

### Scenario 3: Route with Error Handling

```python
@router.post("/transfer")
@Contract(feature="payment")
async def transfer(ctx, amount: float, request: Request):
    try:
        await ctx.transition("Processing")
        result = await risky_transfer(amount)
        await ctx.transition("Completed")
        return result
    except TransferException as e:
        await ctx.transition("Failed")
        raise HTTPException(status_code=400, detail=str(e))
```

---

## Verification Checklist

When integrating Ranex into FastAPI, verify:

- [ ] `ranex_core` module imports successfully
- [ ] `ContractMiddleware` imported from `app.commons.contract_middleware`
- [ ] Middleware added before routes: `app.add_middleware(ContractMiddleware)`
- [ ] State.yaml file exists at `app/features/{feature}/state.yaml`
- [ ] Route decorated with `@Contract(feature="{feature}")`
- [ ] Function accepts `ctx` as first parameter
- [ ] State transitions use `await ctx.transition(state_name)`
- [ ] Tenant ID accessed via `get_tenant_id(request)`

---

## Reference Documentation

- **Complete Guide:** [docs/FASTAPI_INTEGRATION.md](FASTAPI_INTEGRATION.md)
- **Installation:** [INSTALLATION.md](../INSTALLATION.md)
- **Structure:** [STRUCTURE.md](../STRUCTURE.md)
- **Examples:** `examples/fastapi_contract_demo.py`, `examples/fastapi_middleware_demo.py`
- **Working App:** `app/main.py`, `app/features/payment/routes.py`

---

**Documentation Generated:** 2025-01-27  
**For AI Systems:** This document provides accurate, implementation-verified information for integrating Ranex Framework into FastAPI applications. All claims are backed by direct code inspection.

