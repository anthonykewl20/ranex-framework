# Configuration Guide

Configure Ranex for your project.

---

## Configuration File

After running `ranex init`, a configuration file is created at `.ranex/config.toml`:

```toml
[project]
name = "my-project"
framework = "fastapi"

[paths]
app_dir = "./app"
features_dir = "./app/features"

[security]
# Security scanning settings
enabled = true
patterns = 7  # Community Edition limit

[architecture]
# Architecture enforcement
enabled = true
layer_validation = true

[workflow]
# Development workflow
current_phase = "implementation"
```

---

## Environment Variables

Ranex can be configured via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `RANEX_APP_DIR` | Path to your app directory | `./app` |
| `RANEX_FEATURES_DIR` | Path to features directory | `./app/features` |
| `RANEX_LOG_LEVEL` | Log level (debug, info, warn, error) | `info` |
| `RANEX_DB_PRIMARY_URL` | Primary database connection URL | Auto-detect |

### Setting Environment Variables

```bash
# In your shell
export RANEX_APP_DIR="./src/app"
export RANEX_LOG_LEVEL="debug"

# Or in .env file
RANEX_APP_DIR=./src/app
RANEX_LOG_LEVEL=debug
```

---

## Project Structure Configuration

### Default Structure (Recommended)

```
project/
├── .ranex/
│   └── config.toml
├── app/
│   ├── main.py
│   ├── commons/          # Shared utilities
│   │   └── utils.py
│   └── features/         # Business features
│       ├── orders/
│       │   ├── state.yaml
│       │   ├── service.py
│       │   └── routes.py
│       └── payments/
│           ├── state.yaml
│           └── service.py
└── tests/
```

### Custom Structure

If your project uses a different structure, configure the paths:

```toml
# .ranex/config.toml
[paths]
app_dir = "./src"
features_dir = "./src/modules"
```

Or via environment:
```bash
export RANEX_APP_DIR="./src"
export RANEX_FEATURES_DIR="./src/modules"
```

---

## State Machine Configuration

### State File Location

State machines are defined in `state.yaml` files within feature directories:

```
app/features/orders/state.yaml
app/features/payments/state.yaml
app/features/shipping/state.yaml
```

### State File Format

```yaml
feature: orders                    # Feature name (must match directory)
description: Order processing      # Human-readable description
initial_state: Pending             # Starting state

states:
  Pending:
    description: Awaiting action
  Confirmed:
    description: Order confirmed
  Completed:
    description: Done
    terminal: true                 # Cannot transition from this state

transitions:
  - from: Pending
    to: Confirmed
    description: Confirm order     # Optional description
  - from: Confirmed
    to: Completed
```

---

## Security Configuration

### Scanning Patterns (Community Edition)

Community Edition includes 7 security patterns:

| Pattern | Detects |
|---------|---------|
| SQL Injection | `f"SELECT * FROM {user_input}"` |
| Hardcoded Secrets | `API_KEY = "sk-..."` |
| Command Injection | `os.system(user_input)` |
| Weak Cryptography | `hashlib.md5()` |
| Insecure Deserialization | `pickle.loads()` |
| Path Traversal | `"../" in path` |
| Insecure Random | `random.randint()` for security |

### Configuring Scan Exclusions

Create `.ranex/ignore`:

```
# Ignore test files
tests/
test_*.py

# Ignore migrations
**/migrations/

# Ignore virtual environment
.venv/
venv/
```

---

## Database Configuration

### Auto-Detection

Ranex automatically detects databases in your project:

```
# SQLite (auto-detected)
./data/*.db
./data/*.sqlite
./db/*.db

# PostgreSQL (via environment)
export RANEX_DB_PRIMARY_URL="postgresql://user:pass@localhost/mydb"

# MySQL (via environment)
export RANEX_DB_PRIMARY_URL="mysql://user:pass@localhost/mydb"
```

### Database Aliases

Configure database aliases in `.ranex/config.toml`:

```toml
[databases]
primary = "postgresql://localhost/main"
read_replica = "postgresql://localhost/replica"
analytics = "postgresql://localhost/analytics"
```

---

## Logging Configuration

### Log Levels

```bash
# Debug (most verbose)
export RANEX_LOG_LEVEL="debug"

# Info (default)
export RANEX_LOG_LEVEL="info"

# Warning
export RANEX_LOG_LEVEL="warn"

# Error (least verbose)
export RANEX_LOG_LEVEL="error"
```

### Log Output

Logs are output to stderr by default. In production, redirect to a file:

```bash
ranex scan 2> ranex.log
```

---

## MCP Server Configuration

Configure MCP server for AI integration:

```json
// .cursor/mcp.json
{
  "mcpServers": {
    "ranex": {
      "command": "/usr/local/bin/ranex_mcp",
      "args": [],
      "env": {
        "RANEX_APP_DIR": "./app",
        "RANEX_LOG_LEVEL": "warn"
      }
    }
  }
}
```

---

## Configuration Precedence

Configuration is loaded in this order (later overrides earlier):

1. Built-in defaults
2. `.ranex/config.toml`
3. Environment variables
4. Command-line arguments

---

## Validating Configuration

Check your configuration:

```bash
ranex doctor
```

Output:
```
🩺 Ranex Health Check
=====================

Configuration:
  ✅ .ranex/config.toml found
  ✅ App directory: ./app
  ✅ Features directory: ./app/features

Features:
  ✅ orders - state.yaml found
  ✅ payments - state.yaml found

Database:
  ✅ SQLite detected: ./data/app.db

Status: HEALTHY
```

---

## Next Steps

- [State Machine Guide](./10-STATE-MACHINE.md) - Configure state machines
- [CLI Reference](./20-CLI-REFERENCE.md) - All CLI commands

