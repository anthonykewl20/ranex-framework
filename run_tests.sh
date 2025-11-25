#!/bin/bash
# Test Runner for Ranex Framework
# Runs all available tests and verification scripts

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Running Ranex Framework Tests${NC}"
echo "================================="
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Set PYTHONPATH
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"
echo "📂 PYTHONPATH set to: $PYTHONPATH"
echo ""

# Counter
PASSED=0
FAILED=0

# 1. Run verification scripts
echo -e "${BLUE}1. Running verification scripts...${NC}"
echo "----------------------------------------------------------------------"
if [ -f "scripts/verify_installation.sh" ]; then
    if bash scripts/verify_installation.sh; then
        ((PASSED++))
    else
        ((FAILED++))
    fi
else
    echo -e "${YELLOW}⚠️  verify_installation.sh not found${NC}"
fi
echo ""

# 2. Run pytest tests (if they exist)
if [ -d "tests" ] && [ "$(ls -A tests/*.py 2>/dev/null)" ]; then
    echo -e "${BLUE}2. Running pytest tests...${NC}"
    echo "----------------------------------------------------------------------"
    if command -v pytest &> /dev/null; then
        if pytest tests/ -v; then
            ((PASSED++))
        else
            ((FAILED++))
        fi
    else
        echo -e "${YELLOW}⚠️  pytest not installed. Install with: pip install pytest${NC}"
    fi
    echo ""
fi

# 3. Run demo examples as integration tests
echo -e "${BLUE}3. Running demo examples as integration tests...${NC}"
echo "----------------------------------------------------------------------"
if [ -d "examples" ]; then
    cd examples
    DEMO_COUNT=0
    DEMO_PASSED=0
    DEMO_FAILED=0
    
    for demo in *.py; do
        if [ -f "$demo" ]; then
            ((DEMO_COUNT++))
            echo -n "  Testing $demo... "
            if python3 "$demo" > /dev/null 2>&1; then
                echo -e "${GREEN}✅ passed${NC}"
                ((DEMO_PASSED++))
            else
                echo -e "${RED}❌ failed${NC}"
                ((DEMO_FAILED++))
            fi
        fi
    done
    
    cd ..
    echo ""
    echo "  Demo results: $DEMO_PASSED/$DEMO_COUNT passed"
    if [ $DEMO_FAILED -eq 0 ]; then
        ((PASSED++))
    else
        ((FAILED++))
    fi
    echo ""
fi

# Summary
echo "================================="
echo -e "${BLUE}Test Summary${NC}"
echo "================================="
echo -e "${GREEN}✅ Passed: $PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}❌ Failed: $FAILED${NC}"
fi
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed.${NC}"
    exit 1
fi

