#!/bin/bash
# Ranex Framework - CLI Demo
#
# This demo showcases all CLI commands available in Ranex Framework.
# It demonstrates:
# 1. Project initialization
# 2. Security scanning
# 3. Architecture validation
# 4. Workflow management
# 5. Database utilities
# 6. Performance benchmarking
#
# Run: bash examples/cli_demo.sh

set -e

echo "======================================================================"
echo "Ranex Framework - CLI Demo"
echo "======================================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Demo 1: Help command
echo -e "${BLUE}📝 Demo 1: Help Command${NC}"
echo "----------------------------------------------------------------------"
echo "Command: ranex --help"
echo ""
ranex --help || echo "⚠️  ranex command not found (install ranex package first)"
echo ""

# Demo 2: Initialize project
echo -e "${BLUE}📝 Demo 2: Initialize Project${NC}"
echo "----------------------------------------------------------------------"
echo "Command: ranex init"
echo ""
echo "This command initializes a new Ranex project with:"
echo "  • .ranex/ directory structure"
echo "  • config.toml configuration"
echo "  • Feature templates"
echo "  • State machine templates"
echo ""
echo "Example:"
echo "  ranex init"
echo "  ranex init --feature payment"
echo ""

# Demo 3: Security scanning
echo -e "${BLUE}📝 Demo 3: Security Scanning${NC}"
echo "----------------------------------------------------------------------"
echo "Command: ranex scan"
echo ""
echo "This command performs security scanning:"
echo "  • SAST (Static Application Security Testing)"
echo "  • Dependency vulnerability scanning"
echo "  • Antipattern detection"
echo "  • Unified security report"
echo ""
echo "Example:"
echo "  ranex scan                    # Scan current directory"
echo "  ranex scan --path app/        # Scan specific path"
echo "  ranex scan --severity critical # Only critical issues"
echo ""

# Demo 4: Architecture validation
echo -e "${BLUE}📝 Demo 4: Architecture Validation${NC}"
echo "----------------------------------------------------------------------"
echo "Command: ranex arch"
echo ""
echo "This command validates architecture:"
echo "  • Layer enforcement"
echo "  • Structure validation"
echo "  • Import validation"
echo "  • Architecture report"
echo ""
echo "Example:"
echo "  ranex arch                    # Validate architecture"
echo "  ranex arch --fix              # Auto-fix violations"
echo "  ranex arch --strict           # Strict mode"
echo ""

# Demo 5: Workflow management
echo -e "${BLUE}📝 Demo 5: Workflow Management${NC}"
echo "----------------------------------------------------------------------"
echo "Command: ranex task"
echo ""
echo "This command manages project workflow:"
echo "  • Phase management (Requirements, Design, Implementation)"
echo "  • Task tracking"
echo "  • Phase locking/unlocking"
echo ""
echo "Example:"
echo "  ranex task list               # List tasks"
echo "  ranex task build              # Move to Implementation phase"
echo "  ranex task lock               # Lock current phase"
echo ""

# Demo 6: Verification
echo -e "${BLUE}📝 Demo 6: Verification${NC}"
echo "----------------------------------------------------------------------"
echo "Command: ranex verify"
echo ""
echo "This command verifies code:"
echo "  • Contract validation"
echo "  • State machine validation"
echo "  • Schema validation"
echo ""
echo "Example:"
echo "  ranex verify                  # Verify all contracts"
echo "  ranex verify --feature payment # Verify specific feature"
echo ""

# Demo 7: Database utilities
echo -e "${BLUE}📝 Demo 7: Database Utilities${NC}"
echo "----------------------------------------------------------------------"
echo "Command: ranex db"
echo ""
echo "This command provides database utilities:"
echo "  • Schema inspection"
echo "  • SQL validation"
echo "  • Database connection testing"
echo ""
echo "Example:"
echo "  ranex db schema               # Show database schema"
echo "  ranex db validate <query>    # Validate SQL query"
echo "  ranex db test                 # Test database connection"
echo ""

# Demo 8: Performance benchmarking
echo -e "${BLUE}📝 Demo 8: Performance Benchmarking${NC}"
echo "----------------------------------------------------------------------"
echo "Command: ranex bench"
echo ""
echo "This command runs performance benchmarks:"
echo "  • Contract performance"
echo "  • Validation performance"
echo "  • Security scan performance"
echo ""
echo "Example:"
echo "  ranex bench                   # Run all benchmarks"
echo "  ranex bench --contract        # Benchmark contracts only"
echo ""

# Demo 9: Stress testing
echo -e "${BLUE}📝 Demo 9: Stress Testing${NC}"
echo "----------------------------------------------------------------------"
echo "Command: ranex stress"
echo ""
echo "This command runs stress tests:"
echo "  • Logic gauntlet testing"
echo "  • Edge case testing"
echo "  • Performance under load"
echo ""
echo "Example:"
echo "  ranex stress                  # Run stress tests"
echo "  ranex stress --feature payment # Stress test specific feature"
echo ""

# Demo 10: Graph generation
echo -e "${BLUE}📝 Demo 10: Graph Generation${NC}"
echo "----------------------------------------------------------------------"
echo "Command: ranex graph"
echo ""
echo "This command generates architecture diagrams:"
echo "  • Dependency graphs"
echo "  • Layer diagrams"
echo "  • Feature maps"
echo ""
echo "Example:"
echo "  ranex graph                   # Generate dependency graph"
echo "  ranex graph --format mermaid  # Mermaid format"
echo "  ranex graph --output graph.png # Save to file"
echo ""

# Demo 11: Auto-remediation
echo -e "${BLUE}📝 Demo 11: Auto-Remediation${NC}"
echo "----------------------------------------------------------------------"
echo "Command: ranex fix"
echo ""
echo "This command auto-fixes violations:"
echo "  • Architecture violations"
echo "  • Structure violations"
echo "  • Import violations"
echo ""
echo "Example:"
echo "  ranex fix                     # Fix all violations"
echo "  ranex fix --dry-run           # Preview fixes"
echo ""

echo "======================================================================"
echo -e "${GREEN}✅ Demo Complete!${NC}"
echo "======================================================================"
echo ""
echo "Key Takeaways:"
echo "  • Ranex CLI provides comprehensive tooling"
echo "  • All commands support --help for detailed usage"
echo "  • Commands can be integrated into CI/CD pipelines"
echo "  • Auto-remediation available for many violations"
echo ""
echo "Next Steps:"
echo "  • Run 'ranex --help' to see all commands"
echo "  • Try 'ranex init' to initialize a project"
echo "  • Run 'ranex scan' to check your codebase"
echo "  • Use 'ranex arch' to validate architecture"
echo ""

