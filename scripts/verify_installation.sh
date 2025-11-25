#!/bin/bash
# Installation Verification Script for Ranex Framework
# Verifies that all components are properly installed and working

set -e

echo "🔍 Ranex Framework Installation Verification"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

# Function to print success
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
    ((PASSED++))
}

# Function to print error
print_error() {
    echo -e "${RED}❌ $1${NC}"
    ((FAILED++))
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((WARNINGS++))
}

# Check Python version
echo "1. Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 12) else 1)"; then
    print_success "Python version: $PYTHON_VERSION (>= 3.12)"
else
    print_error "Python version $PYTHON_VERSION is too old (requires >= 3.12)"
fi

# Check Ranex Core installation
echo ""
echo "2. Checking Ranex Core installation..."
if python3 -c "import ranex_core" 2>/dev/null; then
    print_success "ranex_core module imports successfully"
    
    # Try to get version info
    if python3 -c "import ranex_core; print('Ranex Core loaded')" 2>/dev/null; then
        print_success "Ranex Core is functional"
    else
        print_warning "Ranex Core imports but may have issues"
    fi
else
    print_error "ranex_core module not found - install with: pip install wheels/ranex_core-0.0.1-*.whl"
fi

# Check Ranex package installation
echo ""
echo "3. Checking Ranex package installation..."
if python3 -c "import ranex" 2>/dev/null; then
    print_success "ranex package imports successfully"
    
    # Check for Contract decorator
    if python3 -c "from ranex import Contract" 2>/dev/null; then
        print_success "Contract decorator available"
    else
        print_warning "Contract decorator not found"
    fi
else
    print_error "ranex package not found"
fi

# Check CLI tool
echo ""
echo "4. Checking CLI tool..."
if command -v ranex &> /dev/null; then
    print_success "ranex CLI tool is available"
    if ranex --help &> /dev/null; then
        print_success "ranex CLI tool is functional"
    else
        print_warning "ranex CLI tool exists but may have issues"
    fi
else
    print_warning "ranex CLI tool not in PATH (may need to install package)"
fi

# Check MCP binary
echo ""
echo "5. Checking MCP binary..."
if [ -f "bin/ranex_mcp" ]; then
    print_success "MCP binary exists"
    if [ -x "bin/ranex_mcp" ]; then
        print_success "MCP binary is executable"
    else
        print_warning "MCP binary is not executable (run: chmod +x bin/ranex_mcp)"
    fi
else
    print_error "MCP binary not found at bin/ranex_mcp"
fi

# Check examples directory
echo ""
echo "6. Checking examples..."
if [ -d "examples" ]; then
    EXAMPLE_COUNT=$(find examples -name "*.py" -type f | wc -l)
    if [ "$EXAMPLE_COUNT" -gt 0 ]; then
        print_success "Examples directory exists ($EXAMPLE_COUNT Python files)"
    else
        print_warning "Examples directory exists but no Python files found"
    fi
else
    print_error "Examples directory not found"
fi

# Check FastAPI app structure
echo ""
echo "7. Checking FastAPI app structure..."
if [ -f "app/main.py" ]; then
    print_success "FastAPI app main.py exists"
    
    if [ -d "app/commons" ]; then
        print_success "app/commons directory exists"
    else
        print_warning "app/commons directory not found"
    fi
    
    if [ -d "app/features" ]; then
        FEATURE_COUNT=$(find app/features -mindepth 1 -maxdepth 1 -type d | wc -l)
        print_success "app/features directory exists ($FEATURE_COUNT features)"
    else
        print_warning "app/features directory not found"
    fi
else
    print_error "FastAPI app main.py not found"
fi

# Check dependencies (if requirements.txt exists)
echo ""
echo "8. Checking dependencies..."
if [ -f "app/requirements.txt" ]; then
    print_success "requirements.txt exists"
    
    # Check if key dependencies are installed
    if python3 -c "import fastapi" 2>/dev/null; then
        print_success "FastAPI is installed"
    else
        print_warning "FastAPI not installed (install with: pip install -r app/requirements.txt)"
    fi
    
    if python3 -c "import sqlalchemy" 2>/dev/null; then
        print_success "SQLAlchemy is installed"
    else
        print_warning "SQLAlchemy not installed"
    fi
else
    print_warning "requirements.txt not found"
fi

# Check documentation
echo ""
echo "9. Checking documentation..."
DOCS=("README.md" "docs/QUICKSTART.md" "docs/FEATURES.md" "docs/API_REFERENCE.md" "examples/README.md")
for doc in "${DOCS[@]}"; do
    if [ -f "$doc" ]; then
        print_success "$doc exists"
    else
        print_warning "$doc not found"
    fi
done

# Summary
echo ""
echo "=============================================="
echo "Verification Summary"
echo "=============================================="
echo -e "${GREEN}✅ Passed: $PASSED${NC}"
if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Warnings: $WARNINGS${NC}"
fi
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}❌ Failed: $FAILED${NC}"
fi
echo ""

if [ $FAILED -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo -e "${GREEN}🎉 All checks passed! Installation is complete.${NC}"
        exit 0
    else
        echo -e "${YELLOW}⚠️  Installation is functional but has warnings.${NC}"
        exit 0
    fi
else
    echo -e "${RED}❌ Installation has errors. Please fix the issues above.${NC}"
    exit 1
fi

