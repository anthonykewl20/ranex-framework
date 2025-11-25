#!/bin/bash
# Development Setup Script for Ranex Framework
# Makes ranex package importable without setting PYTHONPATH manually

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "🔧 Setting up Ranex Framework for development..."
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Install ranex_core wheel if not already installed
if ! python3 -c "import ranex_core" 2>/dev/null; then
    echo "📥 Installing ranex_core..."
    pip install wheels/ranex_core-0.0.1-cp312-cp312-linux_x86_64.whl
else
    echo "✅ ranex_core already installed"
fi

# Create .pth file in site-packages to add project to Python path
SITE_PACKAGES=$(python3 -c "import site; print(site.getsitepackages()[0])")
PTH_FILE="$SITE_PACKAGES/ranex-dev.pth"

echo "📝 Creating .pth file for development..."
echo "$SCRIPT_DIR" > "$PTH_FILE"
echo "✅ Created $PTH_FILE"

# Verify installation
echo ""
echo "✅ Verifying installation..."
python3 -c "import ranex_core; print('✅ ranex_core imported')" || exit 1
python3 -c "import ranex; print('✅ ranex imported')" || exit 1
python3 -c "from ranex import Contract; print('✅ Contract decorator available')" || exit 1

echo ""
echo "🎉 Development setup complete!"
echo ""
echo "You can now run examples and tests without setting PYTHONPATH:"
echo "  python3 examples/basic_contract.py"
echo "  pytest tests/"
echo ""
echo "Note: The .pth file will persist until you remove it manually."
echo "To remove: rm $PTH_FILE"
