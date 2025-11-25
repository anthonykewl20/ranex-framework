# Changelog

All notable changes to Ranex Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.1] - 2025-01-27

### Pre-Release

This is the first pre-release of Ranex Framework for external testing and evaluation.

### Added

#### Core Framework
- **Contract System** (`@Contract` decorator)
  - Runtime contract enforcement
  - State machine validation
  - Schema validation (Pydantic integration)
  - Automatic rollback on failure
  - Multi-tenant support

- **Security Scanning**
  - Static Application Security Testing (SAST)
  - Antipattern detection
  - Dependency vulnerability scanning (OSV database)
  - Unified security scanner

- **Architecture Enforcement**
  - Structure sentinel (4-file structure validation)
  - Layer enforcement
  - Import validation and typosquatting detection

- **Database Features**
  - Schema inspection
  - SQL query validation
  - Multi-database support (PostgreSQL, MySQL, SQLite)

- **Schema Validation**
  - Pydantic schema validation
  - FFI type validation

- **Workflow Management**
  - Project phase management
  - Intent airlock (feature manifest validation)

- **Semantic Atlas**
  - Semantic code search
  - Circular import detection

#### Integration
- **FastAPI Integration**
  - `@Contract` decorator for endpoints
  - Contract middleware
  - Complete FastAPI demo application

- **MCP Server**
  - Micro-Context Protocol server for AI agent integration
  - 11 MCP tools for architecture and security validation
  - WindSurf and Cursor IDE support

#### CLI Tool
- `ranex init` - Initialize project
- `ranex scan` - Security scanning
- `ranex arch` - Architecture checking
- `ranex task` - Task management
- `ranex verify` - Verification
- `ranex db` - Database operations
- `ranex graph` - Dependency graph
- `ranex fix` - Auto-fix issues

#### Documentation
- Complete API reference
- Quick start guide
- Features documentation
- Installation guide
- MCP setup guide
- Examples documentation

#### Examples
- 19 example scripts demonstrating all features
- Complete FastAPI application with 6 features
- CLI usage examples

### Technical Details

- **Python Version:** 3.12+
- **Platform:** Linux x86_64 (for included binaries)
- **Package Size:** ~37MB
- **Wheel:** `ranex_core-0.0.1-cp312-cp312-linux_x86_64.whl` (5.3MB)
- **MCP Binary:** `bin/ranex_mcp` (17MB)

### Known Limitations

- **Platform Support:** Currently only Linux x86_64 binaries included
- **Python Version:** Requires Python 3.12 or higher
- **Pre-Release Status:** This is a pre-release for testing purposes

### Installation

See [INSTALLATION.md](INSTALLATION.md) for complete installation instructions.

### Documentation

- [README.md](README.md) - Main entry point
- [QUICKSTART.md](docs/QUICKSTART.md) - Getting started guide
- [FEATURES.md](docs/FEATURES.md) - Complete feature list
- [API_REFERENCE.md](docs/API_REFERENCE.md) - API documentation
- [MCP_SETUP.md](docs/setup/MCP_SETUP.md) - MCP server setup

---

## [Unreleased]

### Fixed
- **Example Scripts:** Fixed path resolution issues - examples now work when run from any directory
  - Added automatic project root detection to examples using StateMachine/Contract decorators
  - Examples can now be run from `examples/` directory or project root
- **LayerEnforcer:** Fixed instantiation method (changed `.new()` to direct constructor call)
- **Optional Features:** Added graceful handling for missing optional features
  - UnifiedSecurityScanner
  - AntipatternDetector
  - DependencyScannerOSV
  - FFIValidator
  - Examples now show informative messages instead of crashing when features are unavailable
- **State Machine:** Fixed state.yaml format for payment feature (corrected transition syntax)
- **Demo Feature:** Created missing demo feature with state.yaml for fastapi_middleware_demo.py

### Changed
- **Documentation:** Updated installation guides to include CLI dependencies
  - Added explicit instructions to install `typer` and `rich` for CLI functionality
  - Updated README.md, INSTALLATION.md, and QUICKSTART.md
  - Added troubleshooting section for "CLI command not found" errors
- **Setup:** Updated setup.py to include CLI dependencies (`typer`, `rich`) in install_requires
  - Added console_scripts entry point for `ranex` command

### Improved
- **Examples:** All 19 example scripts now run successfully without errors
- **Error Handling:** Better error messages and graceful degradation when optional features are missing
- **Documentation:** More comprehensive installation instructions with troubleshooting

### Planned Features
- Additional platform support (Windows, macOS)
- More examples and tutorials
- Performance optimizations
- Extended database support

---

**Note:** This is a pre-release version. Features and APIs may change before the official v1.0.0 release.

