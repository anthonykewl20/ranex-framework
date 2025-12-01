#!/bin/bash
# Ranex Community Edition Installer
# Usage: ./install.sh

set -e

echo "🤖 Ranex Community Edition Installer"
echo "===================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1-2)
REQUIRED_VERSION="3.12"

if [[ "$PYTHON_VERSION" != "$REQUIRED_VERSION" ]]; then
    echo "⚠️  Warning: This wheel was built for Python $REQUIRED_VERSION"
    echo "   Your version: Python $PYTHON_VERSION"
    echo ""
    echo "   The wheel may not work. Consider using Python 3.12."
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create virtual environment if it doesn't exist
if [[ ! -d "$VENV_DIR" ]]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
pip install --upgrade pip --quiet

# Install the wheel (includes ranex Python package)
echo "📦 Installing ranex_core wheel..."
pip install --force-reinstall "$SCRIPT_DIR"/ranex_core-*.whl
echo "✅ ranex_core and ranex Python package installed"

# Install binaries (optional - requires sudo)
echo ""
echo "📦 Installing binaries..."

INSTALL_DIR="/usr/local/bin"
if [[ -w "$INSTALL_DIR" ]]; then
    cp "$SCRIPT_DIR/ranex_mcp" "$INSTALL_DIR/"
    cp "$SCRIPT_DIR/ranex-cli" "$INSTALL_DIR/"
    echo "✅ Binaries installed to $INSTALL_DIR"
else
    echo "⚠️  Cannot write to $INSTALL_DIR (need sudo)"
    echo "   To install binaries system-wide, run:"
    echo "   sudo cp ranex_mcp ranex-cli /usr/local/bin/"
    echo ""
    echo "   Or install to user directory:"
    mkdir -p ~/.local/bin
    cp "$SCRIPT_DIR/ranex_mcp" ~/.local/bin/
    cp "$SCRIPT_DIR/ranex-cli" ~/.local/bin/
    echo "✅ Binaries installed to ~/.local/bin"
    echo "   Make sure ~/.local/bin is in your PATH"
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📌 IMPORTANT: Activate the virtual environment before use:"
echo ""
echo "   source $VENV_DIR/bin/activate"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Quick start:"
echo "  cd your-project"
echo "  ranex init"
echo "  ranex scan"
echo ""
echo "MCP Setup (for Cursor/Claude):"
echo "  See MCP_SETUP.md"
echo ""
echo "Documentation: https://ranex.dev/docs"

