# Ranex Framework Examples

This directory contains 19 example scripts demonstrating various features of the Ranex Framework.

## Quick Start

1. **Install Ranex Core:**
   ```bash
   pip install ../wheels/ranex_core-0.0.1-cp312-cp312-linux_x86_64.whl
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r ../app/requirements.txt
   ```

3. **Run Examples:**
   ```bash
   python3 basic_contract.py
   ```

## Example Categories

### 1. Contract System (3 examples)

#### `basic_contract.py`
**What it demonstrates:** Basic `@Contract` decorator usage with validation
**Key features:**
- Runtime contract enforcement
- Schema validation
- Automatic rollback on failure

**Run:**
```bash
python3 basic_contract.py
```

#### `state_machine_demo.py`
**What it demonstrates:** State machine validation with YAML configuration
**Key features:**
- State transition enforcement
- YAML-based state definitions
- Invalid transition detection

**Run:**
```bash
python3 state_machine_demo.py
```

#### `schema_validation_demo.py`
**What it demonstrates:** Pydantic schema validation integration
**Key features:**
- Schema registration
- Data validation
- Error reporting

**Run:**
```bash
python3 schema_validation_demo.py
```

### 2. Security Scanning (4 examples)

#### `security_scan_demo.py`
**What it demonstrates:** Static Application Security Testing (SAST)
**Key features:**
- Vulnerability detection
- Code pattern analysis
- Security issue reporting

**Run:**
```bash
python3 security_scan_demo.py
```

#### `antipattern_demo.py`
**What it demonstrates:** Code antipattern detection
**Key features:**
- Common Python antipatterns
- Code quality checks
- Best practice enforcement

**Run:**
```bash
python3 antipattern_demo.py
```

#### `dependency_scan_demo.py`
**What it demonstrates:** Dependency vulnerability scanning using OSV
**Key features:**
- Dependency analysis
- Vulnerability database lookup
- Security advisory checking

**Run:**
```bash
python3 dependency_scan_demo.py
```

#### `unified_security_demo.py`
**What it demonstrates:** Combined security scanning (SAST + antipatterns + dependencies)
**Key features:**
- Unified security scanning
- Multiple scan types
- Comprehensive reporting

**Run:**
```bash
python3 unified_security_demo.py
```

### 3. Architecture Enforcement (3 examples)

#### `structure_enforcement_demo.py`
**What it demonstrates:** Architectural structure validation
**Key features:**
- Forbidden folder detection
- 4-file structure validation
- Structure sentinel

**Run:**
```bash
python3 structure_enforcement_demo.py
```

#### `layer_enforcement_demo.py`
**What it demonstrates:** Architectural layer enforcement
**Key features:**
- Layer violation detection
- Import validation
- Architecture report generation

**Run:**
```bash
python3 layer_enforcement_demo.py
```

#### `import_validation_demo.py`
**What it demonstrates:** Import validation and typosquatting detection
**Key features:**
- Package name validation
- Typosquatting detection
- Import safety checks

**Run:**
```bash
python3 import_validation_demo.py
```

### 4. Database Features (2 examples)

#### `database_schema_demo.py`
**What it demonstrates:** Database schema inspection
**Key features:**
- Schema discovery
- Table and column information
- Database context generation

**Run:**
```bash
python3 database_schema_demo.py
```

#### `sql_validation_demo.py`
**What it demonstrates:** SQL query validation
**Key features:**
- SQL syntax validation
- Schema-aware query checking
- Error detection

**Run:**
```bash
python3 sql_validation_demo.py
```

### 5. FastAPI Integration (2 examples)

#### `fastapi_contract_demo.py`
**What it demonstrates:** FastAPI endpoint with `@Contract` decorator
**Key features:**
- Contract decorator on endpoints
- State machine validation in API
- Schema validation

**Run:**
```bash
python3 fastapi_contract_demo.py
# Then visit http://localhost:8000/docs
```

#### `fastapi_middleware_demo.py`
**What it demonstrates:** FastAPI middleware for contract enforcement
**Key features:**
- Middleware-based contracts
- Automatic validation
- Request/response handling

**Run:**
```bash
python3 fastapi_middleware_demo.py
# Then visit http://localhost:8000/docs
```

### 6. Workflow Management (2 examples)

#### `workflow_management_demo.py`
**What it demonstrates:** Project phase management
**Key features:**
- Phase tracking
- Workflow state management
- Phase transitions

**Run:**
```bash
python3 workflow_management_demo.py
```

#### `intent_airlock_demo.py`
**What it demonstrates:** Intent validation for AI agents
**Key features:**
- Feature manifest validation
- Ambiguity detection
- Intent airlock

**Run:**
```bash
python3 intent_airlock_demo.py
```

### 7. Semantic Atlas (2 examples)

#### `semantic_atlas_demo.py`
**What it demonstrates:** Semantic code search and indexing
**Key features:**
- Codebase indexing
- Semantic search
- Code understanding

**Run:**
```bash
python3 semantic_atlas_demo.py
```

#### `circular_imports_demo.py`
**What it demonstrates:** Circular import detection
**Key features:**
- Import graph building
- Cycle detection
- Dependency analysis

**Run:**
```bash
python3 circular_imports_demo.py
```

### 8. FFI Validation (1 example)

#### `ffi_validation_demo.py`
**What it demonstrates:** Foreign Function Interface type validation
**Key features:**
- Type checking
- FFI safety
- Type conversion validation

**Run:**
```bash
python3 ffi_validation_demo.py
```

### 9. CLI Demo (1 example)

#### `cli_demo.sh`
**What it demonstrates:** Ranex CLI tool usage
**Key features:**
- `ranex init` - Initialize project
- `ranex scan` - Security scanning
- `ranex arch` - Architecture checking
- `ranex verify` - Verification
- And more...

**Run:**
```bash
chmod +x cli_demo.sh
./cli_demo.sh
```

## Recommended Learning Path

**For Beginners:**
1. `basic_contract.py` - Start here!
2. `schema_validation_demo.py` - Learn validation
3. `security_scan_demo.py` - See security features
4. `fastapi_contract_demo.py` - Integrate with FastAPI

**For FastAPI Developers:**
1. `fastapi_contract_demo.py`
2. `fastapi_middleware_demo.py`
3. `database_schema_demo.py`
4. `sql_validation_demo.py`

**For Architecture Enthusiasts:**
1. `structure_enforcement_demo.py`
2. `layer_enforcement_demo.py`
3. `import_validation_demo.py`
4. `circular_imports_demo.py`

**For Security Engineers:**
1. `security_scan_demo.py`
2. `antipattern_demo.py`
3. `dependency_scan_demo.py`
4. `unified_security_demo.py`

## Common Issues

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'ranex_core'`

**Solution:**
```bash
pip install ../wheels/ranex_core-0.0.1-cp312-cp312-linux_x86_64.whl
```

### Database Connection Errors

Some examples require a database. Either:
1. Set up PostgreSQL and configure `DATABASE_URL`
2. Or skip database-dependent examples

### FastAPI Examples Won't Start

**Check:**
1. Port 8000 is available
2. Dependencies installed: `pip install -r ../app/requirements.txt`
3. Try a different port: Change `--port 8000` to `--port 8001`

## Next Steps

- 📖 Read [FEATURES.md](../docs/FEATURES.md) for complete feature list
- 📚 Check [API_REFERENCE.md](../docs/API_REFERENCE.md) for API details
- 🚀 See [QUICKSTART.md](../docs/QUICKSTART.md) for getting started guide

---

**Happy Coding!** 🎉

