# Ranex Framework API Reference

Complete API documentation for Ranex Framework v0.0.1.

## Table of Contents

1. [Contract System](#contract-system)
2. [Security Scanning](#security-scanning)
3. [Architecture Enforcement](#architecture-enforcement)
4. [Database Features](#database-features)
5. [Schema Validation](#schema-validation)
6. [Workflow Management](#workflow-management)
7. [Semantic Atlas](#semantic-atlas)
8. [CLI Commands](#cli-commands)

---

## Contract System

### `@Contract` Decorator

**Module:** `ranex`

**Signature:**
```python
@Contract(
    feature: str,
    input_schema: Optional[Any] = None,
    auto_validate: bool = True,
    tenant_id: Optional[str] = None
)
```

**Parameters:**
- `feature` (str): Feature name (must match `app/features/{feature}/state.yaml`)
- `input_schema` (Optional[Any]): Pydantic BaseModel class for input validation
- `auto_validate` (bool): Whether to automatically validate state transitions (default: True)
- `tenant_id` (Optional[str]): Tenant ID for multi-tenant support

**Returns:** Decorated function with contract enforcement

**Example:**
```python
from ranex import Contract

@Contract(feature="payment")
async def process_payment(ctx, amount: float):
    await ctx.transition("Processing")
    # Business logic
    await ctx.transition("Paid")
```

---

### `StateMachine`

**Module:** `ranex_core`

**Purpose:** State machine for feature state management

**Methods:**
- `transition(state: str) -> bool`: Transition to a new state
- `current_state: str`: Get current state

**Example:**
```python
from ranex_core import StateMachine

machine = StateMachine("payment")
machine.transition("Processing")
print(machine.current_state)  # "Processing"
```

---

### `SchemaValidator`

**Module:** `ranex_core`

**Status:** ⚠️ **Optional** - May not be available in pre-release builds

**Purpose:** Validate data against registered schemas

**Methods:**
- `register_schema(name: str, schema: dict) -> None`: Register a schema
- `validate(name: str, data: Any) -> ValidationResult`: Validate data

**Note:** Schema validation is also available via the `@Contract` decorator with `input_schema` parameter.

**Example:**
```python
try:
    from ranex_core import SchemaValidator
    validator = SchemaValidator()
    validator.register_schema("user", {"type": "object", "properties": {...}})
    result = validator.validate("user", user_data)
except ImportError:
    # SchemaValidator not available - use @Contract decorator instead
    from ranex import Contract
    # Schema validation handled by @Contract decorator
```

---

## Security Scanning

### `SecurityScanner`

**Module:** `ranex_core`

**Status:** ⚠️ **Internal Only** - Not directly exposed in pre-release

**Purpose:** Static Application Security Testing (SAST) - Internal implementation

**Note:** `SecurityScanner` is used internally by `UnifiedSecurityScanner`. For security scanning, use `UnifiedSecurityScanner` instead.

**Alternative:**
```python
from ranex_core import UnifiedSecurityScanner

scanner = UnifiedSecurityScanner.new()
result = scanner.scan_content(code)
# UnifiedSecurityScanner includes SAST scanning capabilities
```

---

### `AntipatternDetector`

**Module:** `ranex_core`

**Purpose:** Detect code antipatterns

**Methods:**
- `scan_content(code: str) -> AntipatternResult`: Scan for antipatterns

**Example:**
```python
from ranex_core import AntipatternDetector

detector = AntipatternDetector()
result = detector.scan_content(code)
```

---

### `DependencyScannerOSV`

**Module:** `ranex_core`

**Purpose:** Scan dependencies for vulnerabilities using OSV database

**Methods:**
- `scan_project(path: str) -> DependencyScanResult`: Scan project dependencies

**Example:**
```python
from ranex_core import DependencyScannerOSV

scanner = DependencyScannerOSV()
result = scanner.scan_project(".")
```

---

### `UnifiedSecurityScanner`

**Module:** `ranex_core`

**Purpose:** Combined security scanning

**Methods:**
- `scan_content(code: str) -> UnifiedSecurityResult`: Perform unified scan

**Example:**
```python
from ranex_core import UnifiedSecurityScanner

scanner = UnifiedSecurityScanner()
result = scanner.scan_content(code)
```

---

## Architecture Enforcement

### `StructureSentinel`

**Module:** `ranex_core`

**Purpose:** Enforce architectural structure rules

**Methods:**
- `check_file(path: str) -> StructureCheckResult`: Check file structure

**Example:**
```python
from ranex_core import StructureSentinel

sentinel = StructureSentinel(project_root)
result = sentinel.check_file("app/features/payment/routes.py")
```

---

### `LayerEnforcer`

**Module:** `ranex_core`

**Purpose:** Enforce architectural layer rules

**Methods:**
- `scan(path: str) -> ArchitectureReport`: Scan project for layer violations

**Example:**
```python
from ranex_core import LayerEnforcer

enforcer = LayerEnforcer()
report = enforcer.scan(".")
if not report.valid:
    for violation in report.violations:
        print(violation)
```

---

### `ImportValidator`

**Module:** `ranex_core`

**Purpose:** Validate imports and detect typosquatting

**Methods:**
- `check_package(name: str) -> ImportCheckResult`: Check package name

**Example:**
```python
from ranex_core import ImportValidator

validator = ImportValidator()
result = validator.check_package("requests")
```

---

## Database Features

### `DatabaseSchemaProvider`

**Module:** `ranex_core`

**Purpose:** Inspect database schemas

**Methods:**
- `get_schema_context() -> SchemaContext`: Get database schema
- `validate_query(query: str) -> QueryValidationResult`: Validate SQL query

**Example:**
```python
from ranex_core import DatabaseSchemaProvider

provider = DatabaseSchemaProvider("postgresql://user:pass@localhost/db")
schema = provider.get_schema_context()
result = provider.validate_query("SELECT * FROM users")
```

---

## Schema Validation

### `SchemaValidator`

**Module:** `ranex_core`

**Purpose:** Validate data against schemas

**Methods:**
- `register_schema(name: str, schema: dict) -> None`: Register schema
- `validate(name: str, data: Any) -> ValidationResult`: Validate data

**Example:**
```python
from ranex_core import SchemaValidator

validator = SchemaValidator()
validator.register_schema("user", {"type": "object", "properties": {...}})
result = validator.validate("user", user_data)
if not result.valid:
    print(result.errors)
```

---

### `FFIValidator`

**Module:** `ranex_core`

**Purpose:** Validate Foreign Function Interface types

**Methods:**
- `validate_type(value: Any, expected_type: str) -> bool`: Validate type

**Example:**
```python
from ranex_core import FFIValidator

validator = FFIValidator()
is_valid = validator.validate_type(42, "i32")
```

---

## Workflow Management

### `WorkflowManager`

**Module:** `ranex_core`

**Purpose:** Manage project phases

**Methods:**
- `set_phase(phase: ProjectPhase) -> None`: Set current phase
- `get_current_phase() -> ProjectPhase`: Get current phase

**Example:**
```python
from ranex_core import WorkflowManager, ProjectPhase

manager = WorkflowManager()
manager.set_phase(ProjectPhase.IMPLEMENTATION)
phase = manager.get_current_phase()
```

---

### `IntentAirlock`

**Module:** `ranex_core`

**Purpose:** Validate feature manifests

**Methods:**
- `validate_manifest(manifest: dict) -> IntentValidationResult`: Validate manifest

**Example:**
```python
from ranex_core import IntentAirlock

airlock = IntentAirlock()
manifest = {"feature_name": "payment", "description": "..."}
result = airlock.validate_manifest(manifest)
```

---

## Semantic Atlas

### `SemanticAtlas`

**Module:** `ranex_core`

**Purpose:** Semantic code search

**Methods:**
- `load(path: str) -> None`: Load codebase
- `semantic_search(query: str) -> List[SearchResult]`: Search codebase

**Example:**
```python
from ranex_core import SemanticAtlas

atlas = SemanticAtlas()
atlas.load(".")
results = atlas.semantic_search("payment processing")
```

---

### `ImportGraph` and `detect_cycles`

**Module:** `ranex_core.atlas.cycle_detector`

**Purpose:** Detect circular imports

**Example:**
```python
from ranex_core import ImportGraph, detect_cycles

graph = ImportGraph()
# Build graph...
cycles = detect_cycles(graph)
```

---

## CLI Commands

### `ranex init`

Initialize a new Ranex project.

**Usage:**
```bash
ranex init
```

---

### `ranex scan`

Perform security scanning.

**Usage:**
```bash
ranex scan [path]
```

---

### `ranex arch`

Check architecture compliance.

**Usage:**
```bash
ranex arch
```

---

### `ranex task`

Manage tasks and workflow.

**Usage:**
```bash
ranex task start "feature_name"
ranex task list
```

---

### `ranex verify`

Verify project compliance.

**Usage:**
```bash
ranex verify
```

---

### `ranex db`

Database operations.

**Usage:**
```bash
ranex db schema
ranex db validate "SELECT * FROM users"
```

---

### `ranex graph`

Generate dependency graph.

**Usage:**
```bash
ranex graph
```

---

### `ranex fix`

Auto-fix common issues.

**Usage:**
```bash
ranex fix
```

---

## Error Handling

All Ranex APIs follow consistent error handling:

- **Validation Errors:** Return `ValidationResult` with `valid: bool` and `errors: List[str]`
- **Scan Results:** Return result objects with `issues: List[Issue]`
- **Exceptions:** Raise standard Python exceptions with descriptive messages

---

## Type Hints

Ranex Framework uses Python type hints throughout. All functions include type annotations for better IDE support and type checking.

---

## See Also

- [QUICKSTART.md](QUICKSTART.md) - Getting started guide
- [FEATURES.md](FEATURES.md) - Complete feature list
- [examples/README.md](../examples/README.md) - Code examples

---

**API Version:** 0.0.1  
**Last Updated:** 2025-01-27

