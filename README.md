# Ranex Framework v0.0.1 - Pre-Release

**🛡️ Hybrid AI-Governance Framework with Rust Core and MCP Architecture**

> **Runtime guardrails for Python applications.** Enforce contracts, validate state machines, scan for security vulnerabilities, and maintain architectural integrity—all powered by a Rust core for maximum performance and safety.

---

## 🎯 What is Ranex Framework?

Ranex Framework is a **runtime governance system** that brings enterprise-grade safety and structure to Python applications. Think of it as **guardrails for your code**—it enforces contracts, validates state transitions, scans for security issues, and maintains architectural integrity—all at runtime.

### Why Ranex?

**The Problem:** Modern Python applications face challenges with:
- ❌ Uncontrolled state transitions leading to bugs
- ❌ Security vulnerabilities slipping into production
- ❌ Architectural violations causing technical debt
- ❌ Lack of runtime contract enforcement
- ❌ Difficult multi-tenant state management

**The Solution:** Ranex Framework provides:
- ✅ **Runtime Contract Enforcement** - `@Contract` decorator enforces state machines and validates schemas
- ✅ **Security Scanning** - Built-in SAST, antipattern detection, and dependency vulnerability scanning
- ✅ **Architecture Enforcement** - Layer enforcement, structure validation, and import safety
- ✅ **FastAPI Integration** - Seamless integration with middleware and decorators
- ✅ **Multi-Tenant Support** - Isolated state machines per tenant
- ✅ **Rust-Powered Core** - High-performance validation engine

---

## ✨ Key Features

### 1. 🎯 Runtime Contract System (`@Contract`)

**Enforce state machines and validate contracts at runtime.**

```python
from ranex import Contract

@Contract(feature="payment")
async def process_payment(ctx, amount: float):
    await ctx.transition("Processing")
    # Business logic here
    await ctx.transition("Completed")
    return {"status": "success"}
```

**What it does:**
- ✅ Validates state transitions against YAML-defined state machines
- ✅ Automatic rollback on errors
- ✅ Schema validation with Pydantic integration
- ✅ Multi-tenant state isolation
- ✅ Comprehensive audit logging

**See:** `examples/basic_contract.py`, `examples/state_machine_demo.py`

---

### 2. 🔒 Security Scanning (with ML-Powered Detection)

**Detect vulnerabilities before they reach production using pattern matching AND machine learning.**

**Capabilities:**
- **SAST Scanning** - SQL injection, XSS, hardcoded secrets, insecure random usage
- **ML-Based Scanning** - Machine learning models for vulnerability classification (powered by Linfa ML framework)
- **Antipattern Detection** - Mutable defaults, bare excepts, code complexity warnings
- **Dependency Scanning** - OSV database integration for known vulnerabilities
- **Unified Security Scanner** - Combines pattern-based and ML-based scanning

```python
from ranex_core import UnifiedSecurityScanner

scanner = UnifiedSecurityScanner.new()
results = scanner.scan_content(code)
# Results include both pattern scans and ML scans
print(f"Pattern scans: {results.stats.pattern_scans}")
print(f"ML scans: {results.stats.ml_scans}")  # ML-powered detection
```

**🤖 ML Features:**
- ML inference tracking with confidence scores
- Vulnerability classifier models
- Prometheus metrics for ML inference
- Circuit breaker protection for ML models

**See:** `examples/security_scan_demo.py`, `examples/unified_security_demo.py`  
**📖 ML Details:** [docs/ML_SECURITY_FEATURES.md](docs/ML_SECURITY_FEATURES.md)

---

### 3. 🏗️ Architecture Enforcement

**Maintain architectural integrity automatically.**

**Features:**
- **Layer Enforcement** - Enforce vertical slice architecture (routes → service → models → commons)
- **Structure Sentinel** - Validate 4-file structure and forbidden folders
- **Import Validation** - Detect typosquatting and unsafe imports

```python
from ranex_core import LayerEnforcer

enforcer = LayerEnforcer()
report = enforcer.scan(project_root)
```

**See:** `examples/layer_enforcement_demo.py`, `examples/structure_enforcement_demo.py`

---

### 4. 🚀 FastAPI Integration

**Seamless integration with FastAPI applications.**

**What you get:**
- `@Contract` decorator for endpoints
- `ContractMiddleware` for multi-tenant support
- State machine validation in API routes
- Automatic schema validation

```python
from fastapi import FastAPI
from ranex import Contract
from app.commons.contract_middleware import ContractMiddleware

app = FastAPI()
app.add_middleware(ContractMiddleware, default_tenant="default")

@Contract(feature="payment")
@app.post("/api/payment")
async def create_payment(ctx, request: PaymentRequest):
    await ctx.transition("Processing")
    return {"status": "success"}
```

**📖 Complete Guide:** [docs/FASTAPI_INTEGRATION.md](docs/FASTAPI_INTEGRATION.md)

**See:** `examples/fastapi_contract_demo.py`, `app/main.py` (complete working application)

---

### 5. 🗄️ Database Features

**Schema inspection and SQL validation.**

- **Schema Discovery** - Inspect database schemas (PostgreSQL, MySQL, SQLite)
- **SQL Validation** - Validate queries against database schema
- **Context Generation** - Generate AI-friendly database context

**See:** `examples/database_schema_demo.py`, `examples/sql_validation_demo.py`

---

### 6. 🔍 Semantic Atlas

**Semantic code search and dependency analysis.**

- **Semantic Search** - Find code by meaning, not just keywords
- **Circular Import Detection** - Detect and visualize import cycles
- **Code Understanding** - Generate context for AI agents

**See:** `examples/semantic_atlas_demo.py`, `examples/circular_imports_demo.py`

---

### 7. 🛠️ CLI Tool

**Command-line interface for all Ranex operations.**

```bash
ranex init          # Initialize project
ranex scan          # Security scanning
ranex arch          # Architecture checking
ranex verify        # Verification & simulation
ranex db            # Database operations
ranex graph         # Dependency graph generation
```

**See:** `examples/cli_demo.sh`, [docs/API_REFERENCE.md](docs/API_REFERENCE.md)

---

### 8. 🤖 MCP Server

**Micro-Context Protocol server for AI agent integration.**

- IDE integration (Windsurf, Cursor, Claude Desktop)
- 11 MCP tools for architecture and security validation
- Context management for AI agents

**See:** `docs/setup/MCP_SETUP.md`

---

## 🎯 Best Use Cases

### 1. **Payment Processing Systems**
- ✅ Enforce payment state machines (Pending → Processing → Completed/Failed)
- ✅ Multi-tenant isolation for SaaS platforms
- ✅ Automatic rollback on payment failures
- ✅ Schema validation for payment requests

**Example:** See `app/features/payment/` for complete implementation

---

### 2. **Multi-Tenant SaaS Applications**
- ✅ Tenant-isolated state machines
- ✅ Architecture enforcement for scalability
- ✅ Security scanning for compliance
- ✅ FastAPI middleware integration

**Example:** See `app/main.py` for multi-tenant FastAPI application

---

### 3. **Enterprise API Development**
- ✅ Contract enforcement for API endpoints
- ✅ State machine validation
- ✅ Security scanning in CI/CD
- ✅ Architecture compliance

**Example:** See `examples/fastapi_contract_demo.py`

---

### 4. **AI-Assisted Development**
- ✅ Intent validation for AI agents
- ✅ Architecture enforcement during development
- ✅ Security scanning before commits
- ✅ MCP server for IDE integration

**Example:** See `examples/intent_airlock_demo.py`, `docs/setup/MCP_SETUP.md`

---

### 5. **Legacy Code Modernization**
- ✅ Detect architectural violations
- ✅ Enforce new structure gradually
- ✅ Security vulnerability detection
- ✅ Import safety validation

**Example:** See `examples/layer_enforcement_demo.py`

---

## 🚀 Quick Start

### Installation

**Option 1: Install from Wheel (Recommended) ✅**

```bash
pip install wheels/ranex_core-0.0.1-cp312-cp312-linux_x86_64.whl
```

**Option 2: Manual Installation**

See `wheels/INSTALL.md` for manual installation instructions.

### Install CLI Dependencies

```bash
pip install -e .  # Installs typer, rich, PyYAML and sets up `ranex` command
```

**Or manually:**
```bash
pip install typer rich PyYAML
```

### Verify Installation

```bash
python3 -c "import ranex_core; print('✅ Ranex Core installed')"
python3 -c "import ranex; print('✅ Ranex package installed')"
ranex --help
```

### Run Your First Example

```bash
cd examples
python3 basic_contract.py
```

---

## 📚 Complete Documentation

### Getting Started
- **[INSTALLATION.md](INSTALLATION.md)** - Detailed installation guide
- **[docs/QUICKSTART.md](docs/QUICKSTART.md)** - Getting started guide
- **[docs/FASTAPI_INTEGRATION.md](docs/FASTAPI_INTEGRATION.md)** - Complete FastAPI integration guide
- **[docs/AI_INTEGRATION_GUIDE.md](docs/AI_INTEGRATION_GUIDE.md)** - Quick reference for AI systems

### Reference Documentation
- **[docs/FEATURES.md](docs/FEATURES.md)** - Complete feature list
- **[docs/API_REFERENCE.md](docs/API_REFERENCE.md)** - API documentation
- **[docs/ML_SECURITY_FEATURES.md](docs/ML_SECURITY_FEATURES.md)** - **ML-powered security features**
- **[STRUCTURE.md](STRUCTURE.md)** - Package structure
- **[app/README.md](app/README.md)** - FastAPI application guide

### Examples
- **19 Demo Scripts** - See `examples/` directory
- **Complete FastAPI App** - See `app/` directory (payment, user, product, subscription, auth)

---

## 💡 Common Questions

### Q: What makes Ranex different from other frameworks?

**A:** Ranex provides **runtime governance**—not just static analysis. It enforces contracts, validates state machines, and maintains architectural integrity **while your application runs**. The Rust core ensures high performance, and the `@Contract` decorator makes it easy to use.

### Q: Do I need Rust knowledge to use Ranex?

**A:** No! Ranex is a Python framework. The Rust core is compiled and provided as a wheel. You only need Python knowledge.

### Q: Can I use Ranex with existing FastAPI applications?

**A:** Yes! Ranex integrates seamlessly with FastAPI. Just add `ContractMiddleware` and use `@Contract` decorator on your routes. See [docs/FASTAPI_INTEGRATION.md](docs/FASTAPI_INTEGRATION.md) for step-by-step guide.

### Q: What Python versions are supported?

**A:** Python 3.12 or higher. The included wheel is for Linux x86_64, Python 3.12+.

### Q: Is Ranex production-ready?

**A:** This is a pre-release (v0.0.1) for testing and evaluation. The framework is functional and includes a complete FastAPI application example, but it's recommended for evaluation purposes at this stage.

### Q: How does multi-tenant support work?

**A:** `ContractMiddleware` extracts tenant ID from `X-Tenant-ID` or `X-User-ID` headers. Each tenant gets an isolated `StateMachine` instance, ensuring state transitions are isolated per tenant.

### Q: Can I use Ranex without FastAPI?

**A:** Yes! The `@Contract` decorator works with any Python function. FastAPI integration is optional but provides additional middleware features.

### Q: What security vulnerabilities does Ranex detect?

**A:** SQL injection, XSS, hardcoded secrets, insecure random usage, and more. See `examples/security_scan_demo.py` for complete list.

### Q: How do I define state machines?

**A:** Create YAML files at `app/features/{feature}/state.yaml`. See `app/features/payment/state.yaml` for an example.

### Q: Does Ranex work with other web frameworks?

**A:** The `@Contract` decorator works with any Python code. FastAPI-specific features (middleware) are FastAPI-only, but core contract enforcement works everywhere.

---

## 🎬 What's Included

- ✅ **Python Package** (`ranex/`) - Main framework package with `@Contract` decorator
- ✅ **Complete FastAPI Application** (`app/`) - Full working application with multiple features
- ✅ **19 Demo Scripts** (`examples/`) - Examples for every feature
- ✅ **CLI Tool** (`ranex` command) - Command-line interface
- ✅ **MCP Server** (`bin/ranex_mcp`) - AI agent integration (17MB)
- ✅ **Python Wheels** (`wheels/`) - Pre-built binaries (5.3MB wheel included)
- ✅ **Comprehensive Documentation** (`docs/`) - Guides, API reference, examples

---

## 🏃 Run the Complete FastAPI Application

**See a complete working application:**

```bash
cd Pre-Release-v0.1
pip install fastapi uvicorn sqlalchemy alembic psycopg
uvicorn app.main:app --reload --port 8000
```

**Access:**
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Metrics:** http://localhost:8000/metrics

**Features demonstrated:**
- ✅ Payment processing with state machines
- ✅ User management
- ✅ Product catalog
- ✅ Subscription management
- ✅ Authentication
- ✅ Multi-tenant support
- ✅ Rate limiting
- ✅ Health checks
- ✅ Prometheus metrics

**See:** `app/README.md` for complete setup instructions

---

## 🔒 Security

Ranex Framework takes security seriously:

- **Security Scanning** - Built-in SAST, antipattern detection, dependency scanning
- **Threat Model** - `docs/security/THREAT_MODEL.md`
- **Security Audit** - `docs/security/SECURITY_AUDIT.md`
- **SBOM** - Software Bill of Materials
- **Security Policy** - `.github/SECURITY.md`
- **Dependabot** - Automated dependency updates

---

## 🛠️ Development & CI/CD

- **CI Pipeline** - `.github/workflows/ci.yml`
- **Security Pipeline** - `.github/workflows/security.yml`
- **Release Checks** - `.github/workflows/release-check.yml`
- **Testing** - `docs/TESTING.md`
- **Build Instructions** - `BUILD_INSTRUCTIONS.md`

---

## 📦 Building Wheels

If wheels are not included for your platform:

```bash
pip install maturin
maturin build --release
cp target/wheels/ranex_core-0.0.1-*.whl Pre-Release-v0.1/wheels/
```

See `BUILD_INSTRUCTIONS.md` for detailed instructions.

---

## 📄 License

MIT License - See LICENSE file

---

## 🤝 Support

For issues and questions:
- Open an issue on GitHub
- Check [INSTALLATION.md](INSTALLATION.md) for troubleshooting
- See [docs/QUICKSTART.md](docs/QUICKSTART.md) for getting started
- Review [docs/FASTAPI_INTEGRATION.md](docs/FASTAPI_INTEGRATION.md) for FastAPI help

---

## 📊 Version Information

**Version:** 0.0.1  
**Release Date:** 2025-01-27  
**Status:** Pre-Release (for testing and evaluation)  
**Package Size:** ~18MB (with MCP binary)  
**Python:** 3.12+  
**Platform:** Linux x86_64 (wheel included)

---

**Ready to get started?** Check out [INSTALLATION.md](INSTALLATION.md) or run `python3 examples/basic_contract.py` to see Ranex in action! 🚀
