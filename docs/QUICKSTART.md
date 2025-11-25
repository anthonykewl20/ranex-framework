# Quick Start Guide

Get up and running with Ranex Framework in 5 minutes!

## Prerequisites

- Python 3.12 or higher
- pip (Python package manager)
- Linux x86_64 (for the included wheel)

## Step 1: Install Ranex Core

```bash
cd Pre-Release-v0.1
pip install wheels/ranex_core-0.0.1-cp312-cp312-linux_x86_64.whl
```

**Verify Installation:**
```bash
python3 -c "import ranex_core; print('✅ Ranex Core installed')"
python3 -c "import ranex; print('✅ Ranex package installed')"
ranex --help
```

## Step 2: Run Your First Example

Let's start with a simple contract example:

```bash
cd examples
python3 basic_contract.py
```

**Expected Output:**
```
✅ Contract validation passed
✅ State machine transition successful
```

## Step 3: Explore More Examples

See `examples/README.md` for a complete list of examples and what they demonstrate.

**Recommended Order:**
1. `basic_contract.py` - Basic contract usage
2. `state_machine_demo.py` - State machine validation
3. `schema_validation_demo.py` - Schema validation
4. `security_scan_demo.py` - Security scanning
5. `fastapi_contract_demo.py` - FastAPI integration

## Step 4: Run the FastAPI Application

### Install Dependencies

```bash
pip install -r app/requirements.txt
```

### Set Up Database (Optional)

The app works without a database, but for full functionality:

```bash
# Set environment variable
export DATABASE_URL="postgresql://user:password@localhost/ranex_db"

# Or create a .env file
echo "DATABASE_URL=postgresql://user:password@localhost/ranex_db" > .env
```

### Run the Application

```bash
cd app
uvicorn main:app --reload --port 8000
```

Visit: http://localhost:8000

**API Endpoints:**
- `GET /` - API information
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics
- `GET /api/users` - User endpoints
- `GET /api/products` - Product endpoints
- `GET /api/payment` - Payment endpoints

## Step 5: Verify Everything Works

Run the installation verification script:

```bash
scripts/verify_installation.sh
```

**Expected Output:**
```
✅ Ranex Core installed
✅ Ranex package installed
✅ Examples directory exists
✅ FastAPI app structure correct
✅ All checks passed
```

## Troubleshooting

### Import Error: No module named 'ranex_core'

**Solution:**
```bash
# Reinstall the wheel
pip install --force-reinstall wheels/ranex_core-0.0.1-cp312-cp312-linux_x86_64.whl

# Verify Python can find it
python3 -c "import sys; print('\n'.join(sys.path))"
```

### FastAPI App Won't Start

**Check:**
1. Dependencies installed: `pip install -r app/requirements.txt`
2. Database connection (if using DB): Check `DATABASE_URL` environment variable
3. Port available: Try a different port `--port 8001`

### Examples Fail to Run

**Check:**
1. Ranex Core installed: `python3 -c "import ranex_core"`
2. Dependencies installed: `pip install -r app/requirements.txt`
3. Python version: `python3 --version` (needs 3.12+)

## Next Steps

- 📖 Read [FEATURES.md](FEATURES.md) to learn about all features
- 📚 Check [API_REFERENCE.md](API_REFERENCE.md) for detailed API docs
- 🎯 Explore [examples/](../examples/README.md) for code examples
- 🚀 See [app/README.md](../app/README.md) for FastAPI app details

## Getting Help

- Check the [Troubleshooting](#troubleshooting) section above
- Review example code in `examples/`
- See full documentation in `docs/`

---

**Congratulations!** You're now ready to build with Ranex Framework! 🎉

