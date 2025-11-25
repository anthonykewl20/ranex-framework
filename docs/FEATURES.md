# Ranex Framework Features

Complete feature list and capabilities of the Ranex Framework.

## Core Features

### 1. Contract System (`@Contract`)

**Purpose:** Runtime contract enforcement with state machine validation and automatic rollback.

**Key Capabilities:**
- Runtime contract enforcement
- State machine validation
- Schema validation (Pydantic integration)
- Automatic rollback on failure
- Multi-tenant support

**Usage:**
```python
from ranex import Contract

@Contract(feature="payment")
async def process_payment(ctx, amount: float):
    await ctx.transition("Processing")
    # Business logic
    await ctx.transition("Paid")
```

**See:** `examples/basic_contract.py`, `examples/state_machine_demo.py`

---

### 2. Security Scanning

#### 2.1 Static Application Security Testing (SAST)

**Purpose:** Detect security vulnerabilities in code.

**Capabilities:**
- SQL injection detection
- XSS vulnerability detection
- Insecure random usage
- Hardcoded secrets detection
- And more...

**Usage:**
```python
from ranex_core import SecurityScanner

scanner = SecurityScanner()
results = scanner.scan_content(code)
```

**See:** `examples/security_scan_demo.py`

#### 2.2 Antipattern Detection

**Purpose:** Detect code quality issues and antipatterns.

**Capabilities:**
- Mutable default arguments
- Bare except clauses
- Unused imports
- Code complexity warnings
- And more...

**Usage:**
```python
from ranex_core import AntipatternDetector

detector = AntipatternDetector()
results = detector.scan_content(code)
```

**See:** `examples/antipattern_demo.py`

#### 2.3 Dependency Vulnerability Scanning

**Purpose:** Scan dependencies for known vulnerabilities using OSV database.

**Capabilities:**
- OSV database integration
- Vulnerability detection
- Security advisory checking
- Dependency analysis

**Usage:**
```python
from ranex_core import DependencyScannerOSV

scanner = DependencyScannerOSV()
results = scanner.scan_project(project_path)
```

**See:** `examples/dependency_scan_demo.py`

#### 2.4 Unified Security Scanner

**Purpose:** Combined security scanning (SAST + antipatterns + dependencies).

**Capabilities:**
- Single interface for all security checks
- Comprehensive reporting
- Multiple scan types

**Usage:**
```python
from ranex_core import UnifiedSecurityScanner

scanner = UnifiedSecurityScanner()
results = scanner.scan_content(code)
```

**See:** `examples/unified_security_demo.py`

---

### 3. Architecture Enforcement

#### 3.1 Structure Sentinel

**Purpose:** Enforce architectural structure rules.

**Capabilities:**
- Forbidden folder detection
- 4-file structure validation
- Structure rule enforcement

**Usage:**
```python
from ranex_core import StructureSentinel

sentinel = StructureSentinel(project_root)
result = sentinel.check_file(file_path)
```

**See:** `examples/structure_enforcement_demo.py`

#### 3.2 Layer Enforcement

**Purpose:** Enforce architectural layer rules.

**Capabilities:**
- Layer violation detection
- Import validation
- Architecture report generation
- Layer dependency checking

**Usage:**
```python
from ranex_core import LayerEnforcer

enforcer = LayerEnforcer()
report = enforcer.scan(project_root)
```

**See:** `examples/layer_enforcement_demo.py`

#### 3.3 Import Validation

**Purpose:** Validate imports and detect typosquatting.

**Capabilities:**
- Package name validation
- Typosquatting detection
- Import safety checks
- Package verification

**Usage:**
```python
from ranex_core import ImportValidator

validator = ImportValidator()
result = validator.check_package(package_name)
```

**See:** `examples/import_validation_demo.py`

---

### 4. Database Features

#### 4.1 Schema Inspection

**Purpose:** Inspect database schemas and generate context.

**Capabilities:**
- Schema discovery
- Table and column information
- Database context generation
- Multi-database support (PostgreSQL, MySQL, SQLite)

**Usage:**
```python
from ranex_core import DatabaseSchemaProvider

provider = DatabaseSchemaProvider(connection_string)
schema = provider.get_schema_context()
```

**See:** `examples/database_schema_demo.py`

#### 4.2 SQL Query Validation

**Purpose:** Validate SQL queries against database schema.

**Capabilities:**
- SQL syntax validation
- Schema-aware query checking
- Error detection
- Query safety validation

**Usage:**
```python
from ranex_core import DatabaseSchemaProvider

provider = DatabaseSchemaProvider(connection_string)
result = provider.validate_query(sql_query)
```

**See:** `examples/sql_validation_demo.py`

---

### 5. Schema Validation

**Purpose:** Validate data against Pydantic schemas.

**Capabilities:**
- Schema registration
- Data validation
- Error reporting
- Field-level validation

**Usage:**
```python
from ranex_core import SchemaValidator

validator = SchemaValidator()
validator.register_schema("user", schema_dict)
result = validator.validate("user", data)
```

**See:** `examples/schema_validation_demo.py`

---

### 6. FFI Validation

**Purpose:** Validate Foreign Function Interface types.

**Capabilities:**
- Type checking
- FFI safety
- Type conversion validation

**Usage:**
```python
from ranex_core import FFIValidator

validator = FFIValidator()
result = validator.validate_type(value, expected_type)
```

**See:** `examples/ffi_validation_demo.py`

---

### 7. Workflow Management

#### 7.1 Project Phase Management

**Purpose:** Manage project phases and workflow state.

**Capabilities:**
- Phase tracking
- Workflow state management
- Phase transitions
- Phase validation

**Usage:**
```python
from ranex_core import WorkflowManager, ProjectPhase

manager = WorkflowManager()
manager.set_phase(ProjectPhase.IMPLEMENTATION)
phase = manager.get_current_phase()
```

**See:** `examples/workflow_management_demo.py`

#### 7.2 Intent Airlock

**Purpose:** Validate feature manifests for AI agents.

**Capabilities:**
- Feature manifest validation
- Ambiguity detection
- Intent validation
- Requirement checking

**Usage:**
```python
from ranex_core import IntentAirlock

airlock = IntentAirlock()
result = airlock.validate_manifest(manifest_json)
```

**See:** `examples/intent_airlock_demo.py`

---

### 8. Semantic Atlas

#### 8.1 Semantic Code Search

**Purpose:** Semantic code search and indexing.

**Capabilities:**
- Codebase indexing
- Semantic search
- Code understanding
- Context retrieval

**Usage:**
```python
from ranex_core import SemanticAtlas

atlas = SemanticAtlas()
atlas.load(codebase_path)
results = atlas.semantic_search(query)
```

**See:** `examples/semantic_atlas_demo.py`

#### 8.2 Circular Import Detection

**Purpose:** Detect circular import dependencies.

**Capabilities:**
- Import graph building
- Cycle detection
- Dependency analysis
- Import path visualization

**Usage:**
```python
from ranex_core import ImportGraph, detect_cycles

graph = ImportGraph()
# Build graph...
cycles = detect_cycles(graph)
```

**See:** `examples/circular_imports_demo.py`

---

### 9. FastAPI Integration

#### 9.1 Contract Decorator

**Purpose:** Use `@Contract` decorator on FastAPI endpoints.

**Capabilities:**
- Endpoint contract enforcement
- State machine validation in API
- Schema validation
- Automatic rollback

**Usage:**
```python
from fastapi import FastAPI
from ranex import Contract

app = FastAPI()

@Contract(feature="payment")
@app.post("/api/payment")
async def create_payment(ctx, request: PaymentRequest):
    await ctx.transition("Processing")
    # Business logic
    return {"status": "success"}
```

**See:** `examples/fastapi_contract_demo.py`

#### 9.2 Contract Middleware

**Purpose:** Middleware-based contract enforcement.

**Capabilities:**
- Automatic validation
- Request/response handling
- Middleware integration
- Global contract enforcement

**Usage:**
```python
from fastapi import FastAPI
from app.commons.contract_middleware import ContractMiddleware

app = FastAPI()
app.add_middleware(ContractMiddleware, default_tenant="default")
```

**See:** `examples/fastapi_middleware_demo.py`

---

### 10. CLI Tool

**Purpose:** Command-line interface for Ranex operations.

**Commands:**
- `ranex init` - Initialize project
- `ranex scan` - Security scanning
- `ranex arch` - Architecture checking
- `ranex task` - Task management
- `ranex verify` - Verification
- `ranex db` - Database operations
- `ranex graph` - Dependency graph
- `ranex fix` - Auto-fix issues

**Usage:**
```bash
ranex init
ranex scan
ranex arch
```

**See:** `examples/cli_demo.sh`

---

### 11. MCP Server

**Purpose:** Micro-Context Protocol server for AI agent integration.

**Capabilities:**
- IDE integration
- AI agent tools
- Context management
- Tool execution

**Usage:**
```bash
./bin/ranex_mcp
```

**See:** `docs/setup/MCP_SETUP.md`

---

## Feature Matrix

| Feature | Category | Status | Examples |
|---------|----------|--------|----------|
| `@Contract` Decorator | Contract | ✅ | `basic_contract.py` |
| State Machine | Contract | ✅ | `state_machine_demo.py` |
| Schema Validation | Contract | ✅ | `schema_validation_demo.py` |
| SAST Scanning | Security | ✅ | `security_scan_demo.py` |
| Antipattern Detection | Security | ✅ | `antipattern_demo.py` |
| Dependency Scanning | Security | ✅ | `dependency_scan_demo.py` |
| Unified Security | Security | ✅ | `unified_security_demo.py` |
| Structure Enforcement | Architecture | ✅ | `structure_enforcement_demo.py` |
| Layer Enforcement | Architecture | ✅ | `layer_enforcement_demo.py` |
| Import Validation | Architecture | ✅ | `import_validation_demo.py` |
| Schema Inspection | Database | ✅ | `database_schema_demo.py` |
| SQL Validation | Database | ✅ | `sql_validation_demo.py` |
| FFI Validation | Validation | ✅ | `ffi_validation_demo.py` |
| Workflow Management | Workflow | ✅ | `workflow_management_demo.py` |
| Intent Airlock | Workflow | ✅ | `intent_airlock_demo.py` |
| Semantic Atlas | Atlas | ✅ | `semantic_atlas_demo.py` |
| Circular Imports | Atlas | ✅ | `circular_imports_demo.py` |
| FastAPI Contract | Integration | ✅ | `fastapi_contract_demo.py` |
| FastAPI Middleware | Integration | ✅ | `fastapi_middleware_demo.py` |
| CLI Tool | Tooling | ✅ | `cli_demo.sh` |
| MCP Server | Tooling | ✅ | `bin/ranex_mcp` |

---

## Getting Started

1. **Install Ranex Core:**
   ```bash
   pip install wheels/ranex_core-0.0.1-*.whl
   ```

2. **Run Examples:**
   ```bash
   cd examples
   python3 basic_contract.py
   ```

3. **Read Documentation:**
   - [QUICKSTART.md](QUICKSTART.md) - Getting started guide
   - [API_REFERENCE.md](API_REFERENCE.md) - Complete API documentation
   - [examples/README.md](../examples/README.md) - Example guide

---

**For detailed API documentation, see [API_REFERENCE.md](API_REFERENCE.md)**

