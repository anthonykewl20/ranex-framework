#!/bin/bash
# Verify Pre-Release-v0.1 Structure

set -e

echo "======================================================================"
echo "Pre-Release-v0.1 Structure Verification"
echo "======================================================================"
echo ""

ERRORS=0
WARNINGS=0

# Check for required files
echo "📋 Checking Required Files..."
echo "----------------------------------------------------------------------"

REQUIRED_FILES=(
    "README.md"
    "LICENSE"
    "pyproject.toml"
    "maturin.toml"
    ".gitignore"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (MISSING)"
        ((ERRORS++))
    fi
done
echo ""

# Check for required directories
echo "📁 Checking Required Directories..."
echo "----------------------------------------------------------------------"

REQUIRED_DIRS=(
    "ranex"
    "app"
    "app/commons"
    "app/features"
    "examples"
    "docs"
    "wheels"
    "bin"
    "scripts/test"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "  ✅ $dir/"
    else
        echo "  ❌ $dir/ (MISSING)"
        ((ERRORS++))
    fi
done
echo ""

# Check for forbidden files/directories
echo "🚫 Checking for Forbidden Files/Directories..."
echo "----------------------------------------------------------------------"

FORBIDDEN=(
    "src"
    "target"
    "Cargo.toml"
    "Cargo.lock"
    "DOCS"
)

for item in "${FORBIDDEN[@]}"; do
    if [ -e "$item" ]; then
        echo "  ⚠️  $item (SHOULD NOT BE IN PRE-RELEASE)"
        ((WARNINGS++))
    else
        echo "  ✅ $item (not present - good)"
    fi
done
echo ""

# Check for Rust source files
echo "🔍 Checking for Rust Source Files..."
echo "----------------------------------------------------------------------"

RUST_FILES=$(find . -name "*.rs" -not -path "./.git/*" 2>/dev/null | wc -l)
if [ "$RUST_FILES" -eq 0 ]; then
    echo "  ✅ No Rust source files (.rs) found"
else
    echo "  ⚠️  Found $RUST_FILES Rust source files (should be 0)"
    find . -name "*.rs" -not -path "./.git/*" 2>/dev/null | head -5
    ((WARNINGS++))
fi
echo ""

# Check Python package
echo "🐍 Checking Python Package..."
echo "----------------------------------------------------------------------"

if [ -f "ranex/__init__.py" ]; then
    echo "  ✅ ranex/__init__.py exists"
else
    echo "  ❌ ranex/__init__.py (MISSING)"
    ((ERRORS++))
fi

if [ -f "ranex/cli.py" ]; then
    echo "  ✅ ranex/cli.py exists"
else
    echo "  ❌ ranex/cli.py (MISSING)"
    ((ERRORS++))
fi

# Check FastAPI application
echo "🚀 Checking FastAPI Application..."
echo "----------------------------------------------------------------------"

if [ -f "app/main.py" ]; then
    echo "  ✅ app/main.py exists"
else
    echo "  ❌ app/main.py (MISSING)"
    ((ERRORS++))
fi

if [ -d "app/commons" ]; then
    COMMONS_FILES=$(find app/commons -name "*.py" 2>/dev/null | wc -l)
    echo "  ✅ app/commons/ exists ($COMMONS_FILES Python files)"
else
    echo "  ❌ app/commons/ (MISSING)"
    ((ERRORS++))
fi

if [ -d "app/features" ]; then
    FEATURES=$(find app/features -maxdepth 1 -type d 2>/dev/null | grep -v "^app/features$" | wc -l)
    echo "  ✅ app/features/ exists ($FEATURES features)"
else
    echo "  ❌ app/features/ (MISSING)"
    ((ERRORS++))
fi
echo ""

# Check Python syntax
echo ""
echo "🔍 Checking Python Syntax..."
echo "----------------------------------------------------------------------"

PYTHON_FILES=$(find ranex app examples -name "*.py" 2>/dev/null | wc -l)
echo "  Found $PYTHON_FILES Python files"

SYNTAX_ERRORS=0
for file in $(find ranex examples -name "*.py" 2>/dev/null); do
    if ! python3 -m py_compile "$file" 2>/dev/null; then
        echo "  ⚠️  Syntax error in $file"
        ((SYNTAX_ERRORS++))
    fi
done

if [ "$SYNTAX_ERRORS" -eq 0 ]; then
    echo "  ✅ All Python files have valid syntax"
else
    echo "  ⚠️  Found $SYNTAX_ERRORS Python files with syntax errors"
    ((WARNINGS++))
fi
echo ""

# Check examples
echo "📝 Checking Examples..."
echo "----------------------------------------------------------------------"

EXPECTED_DEMOS=(
    "basic_contract.py"
    "state_machine_demo.py"
    "security_scan_demo.py"
    "antipattern_demo.py"
    "dependency_scan_demo.py"
    "unified_security_demo.py"
    "structure_enforcement_demo.py"
    "layer_enforcement_demo.py"
    "import_validation_demo.py"
    "database_schema_demo.py"
    "sql_validation_demo.py"
    "schema_validation_demo.py"
    "ffi_validation_demo.py"
    "workflow_management_demo.py"
    "intent_airlock_demo.py"
    "semantic_atlas_demo.py"
    "circular_imports_demo.py"
    "fastapi_contract_demo.py"
    "fastapi_middleware_demo.py"
    "cli_demo.sh"
)

FOUND_DEMOS=0
for demo in "${EXPECTED_DEMOS[@]}"; do
    if [ -f "examples/$demo" ]; then
        ((FOUND_DEMOS++))
    fi
done

echo "  Found $FOUND_DEMOS/${#EXPECTED_DEMOS[@]} expected demos"
if [ "$FOUND_DEMOS" -eq "${#EXPECTED_DEMOS[@]}" ]; then
    echo "  ✅ All expected demos present"
else
    echo "  ⚠️  Missing some demos"
    ((WARNINGS++))
fi
echo ""

# Check wheels directory
echo "📦 Checking Wheels Directory..."
echo "----------------------------------------------------------------------"

if [ -d "wheels" ]; then
    WHEEL_COUNT=$(find wheels -name "*.whl" 2>/dev/null | wc -l)
    if [ "$WHEEL_COUNT" -eq 0 ]; then
        echo "  ⚠️  No wheels found (expected - need to build)"
        echo "     Run: maturin build --release"
    else
        echo "  ✅ Found $WHEEL_COUNT wheel(s)"
    fi
else
    echo "  ❌ wheels/ directory missing"
    ((ERRORS++))
fi
echo ""

# Check bin directory
echo "🔧 Checking Binary Directory..."
echo "----------------------------------------------------------------------"

if [ -d "bin" ]; then
    if [ -f "bin/ranex_mcp" ]; then
        echo "  ✅ ranex_mcp binary found"
        ls -lh bin/ranex_mcp
    else
        echo "  ⚠️  ranex_mcp binary not found (expected - need to build)"
        echo "     Run: cargo build --release --bin ranex_mcp"
    fi
else
    echo "  ❌ bin/ directory missing"
    ((ERRORS++))
fi
echo ""

# Summary
echo "======================================================================"
echo "Summary"
echo "======================================================================"
echo ""

if [ "$ERRORS" -eq 0 ] && [ "$WARNINGS" -eq 0 ]; then
    echo "✅ Structure verification PASSED"
    echo "   Pre-Release-v0.1 is ready (wheels and binary need to be built)"
    exit 0
elif [ "$ERRORS" -eq 0 ]; then
    echo "⚠️  Structure verification PASSED with warnings"
    echo "   Warnings: $WARNINGS"
    echo "   Pre-Release-v0.1 is mostly ready"
    exit 0
else
    echo "❌ Structure verification FAILED"
    echo "   Errors: $ERRORS"
    echo "   Warnings: $WARNINGS"
    exit 1
fi

