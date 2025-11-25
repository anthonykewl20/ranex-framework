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

Ranex Framework provides a comprehensive CLI tool with 15 commands. Use `ranex --help` to see all available commands.

### `ranex init`

Initialize Ranex Governance in this repository.

**Usage:**
```bash
ranex init
```

**Description:** Sets up the `.ranex/` directory structure and configuration files.

**Health Checks:**
The command performs health checks and may show warnings:
- ⚠️ **MCP Server: NOT FOUND** - Optional, only needed for IDE integration
- ⚠️ **FastAPI: NOT INSTALLED** - Optional, only needed for FastAPI app
- ⚠️ **Missing directories** - Expected, will be created by init

**Note:** The command will stop only on critical errors (missing Ranex Core or PyYAML). Warnings are informational.

---

### `ranex scan`

Run the Ranex security & architecture scan.

**Usage:**
```bash
ranex scan
```

**Description:** Performs comprehensive security scanning including SAST, dependency scanning, and architecture validation.

---

### `ranex arch`

Verify architectural layering between routes/service/models/commons.

**Usage:**
```bash
ranex arch
```

**Description:** Checks that the codebase follows Ranex architecture rules and layer dependencies.

---

### `ranex task`

Manage the development workflow (start → design → build).

**Usage:**
```bash
ranex task <action> [name]
```

**Actions:**
- `start <feature_name>` - Start a new task/feature
- `list` - List current tasks
- `lock` - Lock current phase
- `unlock` - Unlock current phase

**Description:** Manages project phases (Requirements, Design, Implementation) and task tracking.

---

### `ranex verify`

Execute 'Holodeck' simulation (live server test) or preview scenario.

**Usage:**
```bash
ranex verify [scenario]
ranex verify --auto
ranex verify --preview
ranex verify --port 8001
```

**Options:**
- `--auto` - Run the simulation linked to current task
- `--preview` - Preview only, don't execute
- `--port <port>` - Port for test server (default: 8001)

**Description:** Runs contract verification and simulation tests.

---

### `ranex db`

Database utilities for schema inspection, SQL validation, and Redis key inference.

**Usage:**
```bash
ranex db <action> [options]
```

**Actions:**
- `inspect` - Inspect database schema
- `check` - Validate SQL query

**Options:**
- `--query <sql>` - SQL query to validate
- `--url <connection>` - Database connection string (sqlite://, postgres://, mysql://, redis://)

**Description:** Provides database schema inspection and SQL validation utilities.

---

### `ranex graph`

Generate a Mermaid.js diagram of the current business logic.

**Usage:**
```bash
ranex graph
ranex graph --feature <feature_name>
```

**Options:**
- `--feature <name>` - Specific feature to graph

**Description:** Generates dependency graphs and architecture diagrams.

---

### `ranex fix`

Auto-correct architectural violations (Quarantine illegal folders AND files).

**Usage:**
```bash
ranex fix
```

**Description:** Automatically fixes common architectural violations and structure issues.

---

### `ranex context`

Generate the 'God Prompt' to align any AI with Ranex Architecture.

**Usage:**
```bash
ranex context
ranex context --output CONTEXT.md
ranex context --feature <feature_name>
ranex context --onboard
```

**Options:**
- `--output <file>` - Save to file (e.g., CONTEXT.md)
- `--feature <name>` - Append per-feature overrides to the system context
- `--onboard` - Automate onboarding by writing docs/onboarding/CONTEXT*.md and checklist

**Description:** Generates comprehensive context documentation for AI agents and developers.

---

### `ranex update-rules`

Force-refresh the advanced AI governance rules file.

**Usage:**
```bash
ranex update-rules
```

**Description:** Updates the `.windsurfrules` file with the latest Ranex governance rules.

---

### `ranex doctor`

Check if the Ranex environment is healthy.

**Usage:**
```bash
ranex doctor
```

**Description:** Diagnoses the Ranex installation and environment configuration.

---

### `ranex bench`

Benchmark Atlas performance (old regex vs new graph-based).

**Usage:**
```bash
ranex bench
ranex bench --mode old
ranex bench --mode new
ranex bench --mode both
```

**Options:**
- `--mode <mode>` - Which Atlas to benchmark: old, new, or both (default: both)

**Description:** Performance benchmarking for semantic atlas implementations.

---

### `ranex stress`

Run a logic gauntlet (matrix + speed run) against the Rust core.

**Usage:**
```bash
ranex stress
ranex stress --feature <feature_name>
```

**Options:**
- `--feature <name>` - Feature to stress test (default: payment)

**Description:** Runs comprehensive stress tests and logic validation.

---

### `ranex config`

Manage Ranex configuration.

**Usage:**
```bash
ranex config <command>
```

**Subcommands:**
- `edit` - Open the architecture config in your editor
- `validate` - Validate the dynamic architecture config for common mistakes

**Description:** Configuration management for Ranex settings and architecture rules.

---

## Quick Reference

**All Commands:**
1. `ranex init` - Initialize project
2. `ranex scan` - Security scanning
3. `ranex arch` - Architecture checking
4. `ranex task` - Task management
5. `ranex verify` - Verification & simulation
6. `ranex db` - Database operations
7. `ranex graph` - Dependency graph generation
8. `ranex fix` - Auto-fix issues
9. `ranex context` - Generate AI context
10. `ranex update-rules` - Update governance rules
11. `ranex doctor` - Environment health check
12. `ranex bench` - Performance benchmarking
13. `ranex stress` - Stress testing
14. `ranex config` - Configuration management

**Get Help:**
```bash
ranex --help              # List all commands
ranex <command> --help     # Get help for specific command
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

