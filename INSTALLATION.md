# Installation Guide

Complete installation guide for Ranex Framework Pre-Release v0.0.1.

## Prerequisites

- **Python:** 3.12 or higher
- **pip:** Python package manager
- **Platform:** Linux x86_64 (for included wheel)
- **Optional:** PostgreSQL (for database features)

## Step 1: Install Ranex Core

### Option 1: Install from Wheel (Recommended)

```bash
cd Pre-Release-v0.1
pip install wheels/ranex_core-0.0.1-cp312-cp312-linux_x86_64.whl
```

### Option 2: Manual Installation (If wheel doesn't work)

```bash
# Find Python site-packages
python3 -c "import site; print(site.getsitepackages()[0])"

# Copy .so file
cp wheels/libranex_core.so $(python3 -c "import site; print(site.getsitepackages()[0])")/ranex_core.so
```

### Verify Installation

```bash
python3 -c "import ranex_core; print('✅ Ranex Core installed')"
python3 -c "import ranex; print('✅ Ranex package installed')"
```

## Step 2: Install CLI Dependencies

To use the `ranex` CLI command-line tool, install the required dependencies:

```bash
pip install typer rich PyYAML
```

**Note:** The CLI dependencies are required for the `ranex` command:
- `typer` and `rich` - For CLI functionality
- `PyYAML` - Required for simulations and YAML file handling

These are not included in the wheel package and must be installed separately.

**Verify CLI Installation:**
```bash
ranex --help
```

You should see the CLI help menu with all available commands.

## Step 3: Install FastAPI Dependencies

If you plan to use the FastAPI application:

```bash
pip install -r app/requirements.txt
```

**Key dependencies:**
- FastAPI - Web framework
- Uvicorn - ASGI server
- SQLAlchemy - ORM (optional, for database features)
- Alembic - Database migrations (optional)
- psycopg - PostgreSQL driver (optional)
- Pydantic - Data validation (used by @Contract decorator)

**Note:** The FastAPI application can run without a database. Database dependencies are only needed if you use database features.

**For FastAPI Integration:**
- 📖 See **[docs/FASTAPI_INTEGRATION.md](docs/FASTAPI_INTEGRATION.md)** for complete integration guide
- 🔧 Learn how to use `@Contract` decorator and `ContractMiddleware`
- 🏢 Understand multi-tenant support and state machine integration

## Step 4: Set Up Database (Optional)

The FastAPI app works without a database, but for full functionality:

### PostgreSQL Setup

```bash
# Set environment variable
export DATABASE_URL="postgresql://user:password@localhost:5432/ranex_db"

# Or create .env file
echo "DATABASE_URL=postgresql://user:password@localhost:5432/ranex_db" > .env
```

### SQLite Setup (For Testing)

```bash
export DATABASE_URL="sqlite:///./app.db"
```

## Step 5: Verify Installation

Run the verification script:

```bash
scripts/verify_installation.sh
```

**Expected output:**
```
✅ Python version: 3.12.x (>= 3.12)
✅ ranex_core module imports successfully
✅ ranex package imports successfully
✅ All checks passed!
```

## Step 6: Run Examples

Test the installation with examples:

```bash
cd examples
python3 basic_contract.py
```

See `examples/README.md` for a complete list of examples.

## Step 7: Run FastAPI Application

```bash
cd Pre-Release-v0.1
uvicorn app.main:app --reload --port 8000
```

Visit:
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Metrics:** http://localhost:8000/metrics

## Troubleshooting

### `ranex init` Shows Warnings

When running `ranex init`, you may see warnings that are expected:

**Expected Warnings (Non-Critical):**
- ⚠️ **MCP Server: NOT FOUND** - This is optional. MCP server is only needed for IDE integration (Windsurf, Cursor, Claude Desktop). The CLI works without it.
- ⚠️ **Package 'fastapi': NOT INSTALLED** - This is optional. Only needed if you plan to use the FastAPI application.
- ⚠️ **Project Structure: Missing directories** - This is expected when running `init` for the first time. The command will create these directories.

**Critical Errors (Must Fix):**
- ❌ **Ranex Core: NOT INSTALLED** - Install the wheel: `pip install wheels/ranex_core-0.0.1-*.whl`
- ❌ **PyYAML: NOT INSTALLED** - Install: `pip install PyYAML`

**Note:** The `ranex init` command will proceed even with warnings, but will stop on critical errors.

### Import Error: No module named 'ranex_core'

**Solution:**
```bash
# Reinstall the wheel
pip install --force-reinstall wheels/ranex_core-0.0.1-cp312-cp312-linux_x86_64.whl

# Verify Python can find it
python3 -c "import sys; print('\n'.join(sys.path))"
python3 -c "import ranex_core"
```

### FastAPI App Won't Start

**Check:**
1. Dependencies installed: `pip install -r app/requirements.txt`
2. Database connection (if using DB): Check `DATABASE_URL` environment variable
3. Port available: Try a different port `--port 8001`

### CLI Command Not Found (`ranex: command not found`)

**Solution:**
```bash
# Install CLI dependencies
pip install typer rich PyYAML

# Verify CLI works
ranex --help
```

**Note:** The `ranex` CLI requires `typer`, `rich`, and `PyYAML` packages. These must be installed separately after installing the wheel.

### PyYAML Missing (Required for simulations)

**Solution:**
```bash
pip install PyYAML
```

**Note:** `PyYAML` is required for `ranex verify` simulations and YAML file handling. Install it along with other CLI dependencies.

### Examples Fail to Run

**Check:**
1. Ranex Core installed: `python3 -c "import ranex_core"`
2. Dependencies installed: `pip install -r app/requirements.txt`
3. Python version: `python3 --version` (needs 3.12+)

### Platform Compatibility

**Current wheel:** Linux x86_64, Python 3.12+

**For other platforms:**
- See `BUILD_INSTRUCTIONS.md` (if available) to build wheels with maturin
- Or use manual installation (see `wheels/INSTALL.md`)

## Next Steps

- 📖 Read [docs/QUICKSTART.md](docs/QUICKSTART.md) for getting started
- 🚀 **[docs/FASTAPI_INTEGRATION.md](docs/FASTAPI_INTEGRATION.md)** - Complete FastAPI integration guide (AI-friendly)
- 📚 Check [docs/FEATURES.md](docs/FEATURES.md) for feature list
- 🎯 Explore [examples/README.md](examples/README.md) for examples
- 🔧 See [app/README.md](app/README.md) for FastAPI app details

## Installation Checklist

- [ ] Python 3.12+ installed
- [ ] Ranex Core wheel installed
- [ ] Ranex package imports successfully
- [ ] CLI dependencies installed (`typer`, `rich`)
- [ ] CLI command works (`ranex --help`)
- [ ] FastAPI dependencies installed (if using app)
- [ ] Database configured (optional)
- [ ] Verification script passes
- [ ] Examples run successfully
- [ ] FastAPI app starts (if using app)

---

**Installation Complete!** 🎉

For more help, see:
- [QUICKSTART.md](docs/QUICKSTART.md)
- [Troubleshooting](#troubleshooting) section above
- [examples/README.md](examples/README.md)

