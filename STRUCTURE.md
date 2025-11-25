# Pre-Release-v0.1 Structure

This document describes the complete structure of the Pre-Release-v0.1 package.

## Directory Structure

```
Pre-Release-v0.1/
├── README.md                    # Main entry point
├── LICENSE                      # MIT License
├── STRUCTURE.md                 # This file
├── .gitignore                   # Git ignore rules
├── pyproject.toml               # Python package configuration
├── maturin.toml                 # Build configuration (reference only)
│
├── ranex/                       # Python package (Ranex Framework)
│   ├── __init__.py              # Package initialization
│   ├── cli.py                   # CLI commands (ranex init, scan, arch, etc.)
│   ├── simulation.py            # Simulation utilities
│   └── templates.py             # Template generation
│
├── app/                         # Complete FastAPI Application (RUNNABLE)
│   ├── main.py                  # FastAPI application entry point
│   ├── commons/                 # Shared utilities (Ranex architecture)
│   │   ├── __init__.py
│   │   ├── database.py          # Database connection (SQLAlchemy)
│   │   ├── contract_middleware.py  # Ranex contract middleware
│   │   ├── metrics.py           # Prometheus metrics
│   │   ├── rate_limiter.py     # Rate limiting middleware
│   │   ├── health.py            # Health check endpoints
│   │   ├── circuit_breaker.py  # Circuit breaker pattern
│   │   ├── ml_integration.py   # ML inference tracking
│   │   ├── security.py          # Security utilities
│   │   ├── validators.py        # Input validators
│   │   └── ... (other commons)
│   │
│   └── features/                # Feature modules (Vertical Slice Architecture)
│       ├── payment/             # Payment feature
│       │   ├── routes.py        # API endpoints
│       │   ├── service.py       # Business logic
│       │   ├── models.py        # Data models (SQLAlchemy)
│       │   └── state.yaml       # State machine definition
│       │
│       ├── user/                # User management feature
│       │   ├── routes.py
│       │   ├── service.py
│       │   ├── models.py
│       │   └── schemas.py       # Pydantic schemas
│       │
│       ├── product/             # Product management feature
│       │   ├── routes.py
│       │   ├── service.py
│       │   ├── models.py
│       │   └── schemas.py
│       │
│       ├── subscription/        # Subscription feature
│       │   ├── routes.py
│       │   ├── service.py
│       │   └── models.py
│       │
│       └── auth/                # Authentication feature
│           ├── routes.py
│           ├── service.py
│           └── models.py
│
├── examples/                    # Demo scripts (17 total)
│   ├── basic_contract.py        # Basic @Contract usage
│   ├── state_machine_demo.py    # State machine validation
│   ├── security_scan_demo.py    # SAST scanning
│   ├── antipattern_demo.py      # Code quality checks
│   ├── dependency_scan_demo.py  # OSV integration
│   ├── unified_security_demo.py # Comprehensive scanning
│   ├── structure_enforcement_demo.py  # Structure validation
│   ├── layer_enforcement_demo.py      # Layer validation
│   ├── import_validation_demo.py       # Import safety
│   ├── database_schema_demo.py        # Schema inspection
│   ├── sql_validation_demo.py         # SQL validation
│   ├── schema_validation_demo.py      # Schema validation
│   ├── ffi_validation_demo.py         # FFI validation
│   ├── workflow_management_demo.py    # Workflow phases
│   ├── intent_airlock_demo.py         # Intent validation
│   ├── semantic_atlas_demo.py         # Semantic search
│   ├── circular_imports_demo.py      # Cycle detection
│   ├── fastapi_contract_demo.py       # FastAPI + @Contract
│   ├── fastapi_middleware_demo.py     # FastAPI middleware
│   ├── cli_demo.sh                    # CLI commands
│   └── fastapi_demo/                  # FastAPI demo (reference)
│
├── docs/                        # User documentation
│   ├── setup/                   # Setup guides
│   │   ├── MCP_SETUP.md         # MCP server setup
│   │   └── QUICK_REFERENCE.md   # Quick reference
│   └── specs/                   # Example specifications
│
├── wheels/                      # Python wheels (after build)
│   └── ranex_core-0.0.1-*.whl  # Compiled Python bindings
│
├── bin/                         # MCP binary (after build)
│   └── ranex_mcp                # MCP server executable
│
└── scripts/                     # Utility scripts
    └── test/                    # Test/verification scripts
        └── verify_structure.sh  # Structure verification
```

## FastAPI Application Structure (app/)

The `app/` directory contains a **complete, runnable FastAPI application** that demonstrates Ranex Framework integration.

### Architecture: Vertical Slice (Ranex Standard)

```
app/
├── commons/          # Shared utilities (bottom layer)
│   ├── database.py   # Database connection
│   ├── validators.py # Input validation
│   └── ...
│
└── features/         # Feature modules (top layer)
    ├── payment/     # Each feature is self-contained
    │   ├── routes.py    # API endpoints (can import: service, commons)
    │   ├── service.py   # Business logic (can import: models, commons)
    │   ├── models.py   # Data models (can import: commons only)
    │   └── state.yaml  # State machine definition
    └── ...
```

### Layer Rules (Enforced by Ranex)

1. **routes/** → Can import: `service`, `commons`
2. **service/** → Can import: `models`, `commons`
3. **models/** → Can import: `commons` only
4. **commons/** → Cannot import from `features`

### Running the FastAPI Application

```bash
# Install dependencies
pip install fastapi uvicorn sqlalchemy alembic psycopg

# Set environment variables
export DATABASE_URL="postgresql://user:pass@localhost:5432/dbname"

# Run the application
cd Pre-Release-v0.1
uvicorn app.main:app --reload --port 8000

# Access API docs
# http://localhost:8000/docs
```

## What's Included

✅ **Python Package** (`ranex/`)
- Main framework package
- CLI commands (`ranex init`, `ranex scan`, etc.)
- Utilities

✅ **Complete FastAPI Application** (`app/`)
- Full working application
- Multiple features (payment, user, product, subscription, auth)
- Ranex middleware integration
- Database models and migrations
- Production-ready structure

✅ **Examples** (`examples/`)
- 17 demo scripts
- CLI demo script
- FastAPI integration demos

✅ **Documentation** (`docs/`)
- Setup guides
- Example specifications
- User-facing documentation only

✅ **Configuration Files**
- `pyproject.toml` - Python package config
- `maturin.toml` - Build config (reference)
- `.gitignore` - Git ignore rules

## What's NOT Included

❌ **Rust Source Code** (`src/`)
- Users don't need Rust source
- Only compiled binaries provided (wheels + MCP binary)

❌ **Build Artifacts** (`target/`)
- Too large (21GB+)
- Users don't need build artifacts

❌ **Internal Documentation** (`DOCS/`)
- Internal development docs
- Not needed by users

❌ **Development Scripts** (`scripts/dev/`)
- Only test scripts included

❌ **Rust Build Files** (`Cargo.toml`, `Cargo.lock`)
- Users don't need Rust build files

## Installation Structure

After building wheels and binary:

```
Pre-Release-v0.1/
├── wheels/
│   └── ranex_core-0.0.1-*.whl  # Python wheel
├── bin/
│   └── ranex_mcp                # MCP server binary
└── ... (rest of structure)
```

## Usage Examples

### 1. Install Python Package
```bash
pip install wheels/ranex_core-0.0.1-*.whl
```

### 2. Run FastAPI Application
```bash
cd Pre-Release-v0.1
uvicorn app.main:app --reload
```

### 3. Run Demo Scripts
```bash
python examples/basic_contract.py
python examples/security_scan_demo.py
```

### 4. Use MCP Binary
```bash
./bin/ranex_mcp
```

## Notes

- This structure follows Python package conventions
- No Rust source code included (users don't need it)
- Complete FastAPI application included for testing
- Clean, minimal, distribution-ready
- All necessary files for installation and usage
