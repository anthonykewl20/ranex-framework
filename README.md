# Ranex Framework v0.0.1 - Pre-Release

**Hybrid AI-Governance Framework with Rust Core and MCP Architecture**

## ⚠️ Pre-Release Notice

This is a pre-release version (v0.0.1) for testing and evaluation purposes.

## Quick Start

### Installation

**Option 1: Install from Wheel (Recommended) ✅**

Wheel is already built and included:
```bash
pip install wheels/ranex_core-0.0.1-cp312-cp312-linux_x86_64.whl
```

**Option 2: Manual Installation (If wheels not available)**

See `wheels/INSTALL.md` for manual installation instructions.

### Install CLI Dependencies

**Option A: Install via setup.py (Recommended)**
```bash
pip install -e .
```

This installs all CLI dependencies and sets up the `ranex` command automatically.

**Option B: Manual Installation**
```bash
pip install typer rich PyYAML
```

**Note:** The CLI dependencies are required for the `ranex` command-line tool:
- `typer` and `rich` - For CLI functionality
- `PyYAML` - Required for simulations and YAML file handling

These are not included in the wheel package and must be installed separately.

### Verify Installation

```bash
python3 -c "import ranex_core; print('✅ Ranex Core installed')"
python3 -c "import ranex; print('✅ Ranex package installed')"
ranex --help
```

### MCP Server

The MCP binary is included:
```bash
./bin/ranex_mcp
```

See `docs/setup/MCP_SETUP.md` for IDE integration instructions.

## What's Included

- ✅ **Python Package** (`ranex/`) - Main framework package
- ✅ **Complete FastAPI Application** (`app/`) - **Full working application** with multiple features
- ✅ **Examples** (`examples/`) - 19 demo scripts showcasing features
- ✅ **Documentation** (`docs/`) - User-facing documentation
- ✅ **MCP Binary** (`bin/ranex_mcp`) - MCP server executable (17MB)
- ✅ **Python Wheels** (`wheels/`) - Built and ready (5.3MB wheel included)

## Complete FastAPI Application

**Run the full application:**
```bash
cd Pre-Release-v0.1
pip install fastapi uvicorn sqlalchemy alembic psycopg
uvicorn app.main:app --reload --port 8000
```

See `app/README.md` for complete setup instructions.

The `app/` directory contains:
- ✅ Multiple features (payment, user, product, subscription, auth)
- ✅ Ranex middleware integration
- ✅ Database models and migrations
- ✅ Production-ready structure
- ✅ Follows Ranex vertical slice architecture

## Examples

See `examples/` directory for 19 demo scripts:
- `basic_contract.py` - Basic @Contract usage
- `state_machine_demo.py` - State machine validation
- `security_scan_demo.py` - Security scanning
- `fastapi_contract_demo.py` - FastAPI integration
- And 15 more...

## Documentation

- `STRUCTURE.md` - Complete package structure
- `TEST_REPORT.md` - Test results and verification
- `BUILD_INSTRUCTIONS.md` - How to build wheels
- `docs/setup/MCP_SETUP.md` - MCP server setup
- `docs/QUICKSTART.md` - Getting started guide (coming soon)
- `docs/FEATURES.md` - Complete feature list (coming soon)
- `docs/API_REFERENCE.md` - API documentation (coming soon)

## Building Wheels

If wheels are not included, build them:

```bash
# Install maturin
pip install maturin

# Build wheels
maturin build --release

# Copy to Pre-Release-v0.1
cp target/wheels/ranex_core-0.0.1-*.whl Pre-Release-v0.1/wheels/
```

See `BUILD_INSTRUCTIONS.md` for detailed instructions.

## License

MIT License - See LICENSE file

## Support

For issues and questions, please open an issue on GitHub.

---

**Version:** 0.0.1  
**Release Date:** 2025-01-27  
**Status:** Pre-Release  
**Package Size:** ~18MB (with MCP binary)
