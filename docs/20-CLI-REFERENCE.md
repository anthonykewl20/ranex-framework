# CLI Reference

Complete reference for all Ranex Community Edition CLI commands.

---

## Overview

```bash
ranex [OPTIONS] <COMMAND>
```

### Global Options

| Option | Description |
|--------|-------------|
| `--help` | Show help message |
| `--version` | Show version |
| `--strict` | Exit with error on any issue |

---

## Commands (8 Available)

| Command | Description |
|---------|-------------|
| `ranex init` | Initialize a new Ranex project |
| `ranex scan` | Run security + architecture scan |
| `ranex arch` | Architecture validation only |
| `ranex fix` | Auto-remediation for structure issues |
| `ranex doctor` | System health check |
| `ranex task status` | Show workflow status |
| `ranex task design` | Move to design phase |
| `ranex task build` | Move to implementation phase |

---

## ranex init

Initialize Ranex in your project.

### Usage

```bash
ranex init [OPTIONS]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--framework` | `fastapi` | Framework (fastapi, django, flask) |
| `--force` | `false` | Overwrite existing config |

### Example

```bash
# Initialize with defaults
ranex init

# Initialize for Django
ranex init --framework django

# Reinitialize (overwrite)
ranex init --force
```

### Output

```
🚀 Initializing Ranex Project
============================

Framework: FastAPI
Project: my-project

Created:
  ✅ .ranex/config.toml
  ✅ .ranex/ignore

Next steps:
  1. Create state machine: app/features/{name}/state.yaml
  2. Run scan: ranex scan
  3. Check health: ranex doctor
```

---

## ranex scan

Run security and architecture scan.

### Usage

```bash
ranex scan [OPTIONS] [PATH]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--security` | `true` | Run security scan |
| `--architecture` | `true` | Run architecture check |
| `--imports` | `true` | Check imports |
| `--strict` | `false` | Exit with error on any finding |
| `--json` | `false` | Output as JSON |

### Example

```bash
# Full scan
ranex scan

# Security only
ranex scan --security --no-architecture

# Specific directory
ranex scan ./app/features

# CI/CD mode
ranex scan --strict --json
```

### Output

```
🔍 Ranex Security Scan
======================

Security (7 patterns):
  ✅ SQL Injection: None
  ⚠️  Hardcoded Secrets: 1 found
     - app/config.py:15 - API key detected
  ✅ Command Injection: None
  ✅ Weak Crypto: None
  ✅ Insecure Deserialization: None
  ✅ Path Traversal: None
  ✅ Insecure Random: None

Architecture:
  ✅ Layer boundaries: Valid
  ✅ Feature isolation: Valid
  ✅ No forbidden folders

Imports:
  ✅ All imports valid

Summary: 1 issue found
```

---

## ranex arch

Architecture validation only.

### Usage

```bash
ranex arch [OPTIONS] [PATH]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--layers` | `true` | Check layer boundaries |
| `--features` | `true` | Check feature isolation |
| `--structure` | `true` | Check folder structure |
| `--strict` | `false` | Exit on any violation |

### Example

```bash
# Full architecture check
ranex arch

# Layers only
ranex arch --layers --no-features --no-structure

# Specific path
ranex arch ./app/features/orders
```

### Output

```
🏗️ Architecture Validation
==========================

Layers:
  ✅ routes → services: Valid
  ✅ services → repositories: Valid
  ❌ routes → database: VIOLATION
     - app/features/orders/routes.py:23

Features:
  ✅ orders: Isolated
  ✅ payments: Isolated
  ⚠️  shipping: Imports from orders internals

Structure:
  ✅ No forbidden folders

Result: 2 violations found
```

---

## ranex fix

Auto-remediation for structure issues.

### Usage

```bash
ranex fix [OPTIONS]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--dry-run` | `false` | Show what would be fixed |
| `--structure` | `true` | Fix structure issues |

### Example

```bash
# Preview fixes
ranex fix --dry-run

# Apply fixes
ranex fix
```

### Output

```
🔧 Ranex Auto-Fix
=================

Fixable issues:
  1. Rename utils/ → commons/
  2. Rename helpers/ → shared/

Dry run: No changes made.
Run without --dry-run to apply.
```

**Note:** Community Edition only fixes structure issues. Team Edition includes security auto-fixes.

---

## ranex doctor

System health check.

### Usage

```bash
ranex doctor [OPTIONS]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--verbose` | `false` | Show detailed output |

### Example

```bash
ranex doctor

ranex doctor --verbose
```

### Output

```
🩺 Ranex Health Check
=====================

Configuration:
  ✅ .ranex/config.toml: Found
  ✅ App directory: ./app
  ✅ Features directory: ./app/features

Features:
  ✅ orders: state.yaml found (7 states, 8 transitions)
  ✅ payments: state.yaml found (5 states, 6 transitions)
  ⚠️  shipping: state.yaml missing

Database:
  ✅ SQLite: ./data/app.db (4 tables)

Python:
  ✅ ranex_core: 0.0.1
  ✅ ranex: 0.0.1

Status: HEALTHY (1 warning)
```

---

## ranex task status

Show current workflow phase.

### Usage

```bash
ranex task status
```

### Example

```bash
ranex task status
```

### Output

```
🤖 Ranex Workflow Engine
========================

Current Phase: Implementation
Current Task: Build order processing

Phase History:
  ✅ Requirements (completed)
  ✅ Design (completed)
  → Implementation (in progress)
  ○ Review (pending)
  ○ Maintenance (pending)

Next: Complete implementation, then run 'ranex task review'
```

---

## ranex task design

Move to design phase.

### Usage

```bash
ranex task design [OPTIONS]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--message` | - | Description of design work |

### Example

```bash
ranex task design --message "Design order processing flow"
```

### Output

```
📐 Moving to Design Phase
=========================

Previous: Requirements
New: Design

Message: Design order processing flow

Suggestions:
  1. Create state machine diagrams
  2. Define API contracts
  3. Document data models

Next: Run 'ranex task build' when design is complete
```

---

## ranex task build

Move to implementation phase.

### Usage

```bash
ranex task build [OPTIONS]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--message` | - | Description of build work |

### Example

```bash
ranex task build --message "Implement order confirmation"
```

### Output

```
🔨 Moving to Implementation Phase
=================================

Previous: Design
New: Implementation

Message: Implement order confirmation

Checklist:
  □ Create state.yaml
  □ Implement service functions
  □ Add @Contract decorators
  □ Write tests

Next: Run 'ranex scan' to validate implementation
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success (no issues or non-strict mode) |
| 1 | Issues found (with --strict) |
| 2 | Configuration error |
| 3 | File not found |

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `RANEX_APP_DIR` | App directory path |
| `RANEX_FEATURES_DIR` | Features directory path |
| `RANEX_LOG_LEVEL` | Log level (debug, info, warn, error) |
| `RANEX_DB_PRIMARY_URL` | Primary database URL |

---

## Team Edition Commands

The following commands require Team Edition:

| Command | Description |
|---------|-------------|
| `ranex verify` | Holodeck simulation |
| `ranex arbiter validate` | Test integrity |
| `ranex drift snapshot` | Create spec snapshot |
| `ranex drift check` | Check for drift |
| `ranex rag search` | Semantic search |
| `ranex rag index` | Index codebase |
| `ranex persona set` | Set active persona |
| `ranex persona list` | List personas |
| `ranex govern check` | Governance check |
| `ranex govern transition` | Governance transition |
| `ranex attestation list` | List attestations |
| `ranex attestation verify` | Verify attestation |
| `ranex config edit` | Edit configuration |
| `ranex update-rules` | Update security rules |

Contact sales@ranex.dev for Team Edition.

---

## Next Steps

- [MCP Tools Reference](./21-MCP-TOOLS.md) - AI integration
- [Python API Reference](./22-PYTHON-API.md) - Python usage

