# Installation Guide

This guide walks you through installing Ranex Community Edition.

---

## System Requirements

| Requirement | Version |
|-------------|---------|
| **Python** | 3.12+ |
| **Operating System** | Linux (x86_64), macOS, Windows (via WSL) |
| **Disk Space** | ~50MB |

---

## Installation Methods

### Method 1: Easy Installer (Recommended)

```bash
cd community-edition
./install.sh
```

This will:
1. Install the `ranex_core` wheel (Rust core)
2. Install the `ranex` Python package
3. Install CLI and MCP binaries to `~/.local/bin`

### Method 2: Manual Installation

```bash
# 1. Install the Rust core wheel
pip install ranex_core-0.0.1-cp312-cp312-manylinux_2_28_x86_64.whl

# 2. Install the Python package
pip install ./ranex

# 3. Install binaries (optional)
sudo cp ranex_mcp ranex-cli /usr/local/bin/
# or for user-only installation:
mkdir -p ~/.local/bin
cp ranex_mcp ranex-cli ~/.local/bin/
```

### Method 3: Virtual Environment

```bash
# Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# Install
pip install ranex_core-*.whl
pip install ./ranex
```

---

## Verify Installation

### Check Python Package

```python
# Test in Python
from ranex import Contract
from ranex_core import SecurityScanner, ImportValidator

print("✅ Ranex installed successfully!")
```

### Check CLI

```bash
ranex --help
# or if not in PATH:
~/.local/bin/ranex-cli --help
```

Expected output:
```
Ranex Governance CLI (Rust)

Usage: ranex-cli [OPTIONS] <COMMAND>

Commands:
  init         Initialize a new Ranex project
  scan         Run security & architecture scan
  doctor       System health check
  ...
```

### Check MCP Server

```bash
ranex_mcp --help
# The MCP server communicates via stdio for AI integration
```

---

## Post-Installation Setup

### 1. Initialize Your Project

```bash
cd your-project
ranex init
```

This creates:
- `.ranex/` - Configuration directory
- `.ranex/config.toml` - Project settings

### 2. Set Environment Variable (Optional)

```bash
# Add to ~/.bashrc or ~/.zshrc
export RANEX_APP_DIR="./app"
```

### 3. Configure MCP for AI Integration

See [MCP Tools Documentation](./21-MCP-TOOLS.md) for setup instructions.

---

## Troubleshooting Installation

### "Python version mismatch"

The wheel is built for Python 3.12. If you have a different version:

```bash
# Check your Python version
python3 --version

# Use pyenv to install Python 3.12
pyenv install 3.12.3
pyenv local 3.12.3
```

### "Command not found: ranex"

Make sure the binary directory is in your PATH:

```bash
# Add to ~/.bashrc
export PATH="$HOME/.local/bin:$PATH"
source ~/.bashrc
```

### "ModuleNotFoundError: No module named 'ranex_core'"

Ensure you installed the wheel:

```bash
pip list | grep ranex
# Should show: ranex_core 0.0.1
```

---

## Uninstallation

```bash
# Remove Python packages
pip uninstall ranex_core ranex

# Remove binaries
rm ~/.local/bin/ranex_mcp ~/.local/bin/ranex-cli

# Remove project configuration
rm -rf .ranex/
```

---

## Next Steps

- [Quick Start Guide](./02-QUICKSTART.md) - Build your first Ranex project
- [Configuration](./03-CONFIGURATION.md) - Customize Ranex settings

