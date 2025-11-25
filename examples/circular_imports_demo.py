#!/usr/bin/env python3
"""
Ranex Framework - Circular Import Detection Demo

This demo showcases circular dependency detection.
It demonstrates:
1. Import graph analysis
2. Cycle detection
3. Cycle reporting
4. Architecture violations

Run: python examples/circular_imports_demo.py
"""

import os
import tempfile
import shutil


def demo_circular_imports():
    """Demonstrate circular import detection."""
    print("=" * 70)
    print("Ranex Framework - Circular Import Detection Demo")
    print("=" * 70)
    print()
    
    # Demo 1: What are circular imports?
    print("📝 Demo 1: Understanding Circular Imports")
    print("-" * 70)
    print("Circular imports occur when modules import each other:")
    print()
    print("Example cycle:")
    print("  app/features/payment/service.py")
    print("    ↓ imports")
    print("  app/features/payment/models.py")
    print("    ↓ imports")
    print("  app/features/payment/routes.py")
    print("    ↓ imports")
    print("  app/features/payment/service.py  ← Back to start (CYCLE!)")
    print()
    print("Problems:")
    print("  • Tight coupling")
    print("  • Hard to test")
    print("  • Prevents independent deployment")
    print("  • Violates vertical slice architecture")
    print()
    
    # Demo 2: How Ranex detects cycles
    print("📝 Demo 2: Cycle Detection Algorithm")
    print("-" * 70)
    print("Ranex uses Kosaraju's algorithm:")
    print("  • Finds strongly connected components (SCCs)")
    print("  • Identifies cycles (SCCs with >1 node)")
    print("  • Reports all files in the cycle")
    print()
    print("Performance:")
    print("  • Time: O(V + E) - linear time")
    print("  • Space: O(V) - linear space")
    print("  • Scales to large codebases")
    print()
    
    # Demo 3: Example cycles
    print("📝 Demo 3: Common Circular Import Patterns")
    print("-" * 70)
    print("""
# Pattern 1: Service ↔ Models
# app/features/payment/service.py
from app.features.payment.models import Payment

# app/features/payment/models.py
from app.features.payment.service import PaymentService  # ❌ CYCLE!

# Fix: Models should not import services
# Keep models pure data structures

# Pattern 2: Routes ↔ Service
# app/features/payment/routes.py
from app.features.payment.service import PaymentService

# app/features/payment/service.py
from app.features.payment.routes import get_payment_context  # ❌ CYCLE!

# Fix: Extract shared logic to commons
# Use dependency injection

# Pattern 3: Commons ↔ Features
# app/commons/database.py
from app.features.payment.models import Payment  # ❌ CYCLE!

# app/features/payment/models.py
from app.commons.database import Base

# Fix: Commons should not import features
# Use dependency inversion
""")
    print()
    
    # Demo 4: Prevention strategies
    print("📝 Demo 4: Prevention Strategies")
    print("-" * 70)
    print("Follow Ranex architecture rules:")
    print()
    print("✅ Correct Dependency Flow:")
    print("  routes → service → models → commons")
    print()
    print("❌ Avoid:")
    print("  • Models importing services")
    print("  • Services importing routes")
    print("  • Commons importing features")
    print("  • Features importing commons (use dependency injection)")
    print()
    print("Best Practices:")
    print("  • Keep models pure (no business logic)")
    print("  • Use dependency injection")
    print("  • Extract shared logic to commons")
    print("  • Follow vertical slice architecture")
    print()
    
    # Demo 5: Integration example
    print("📝 Demo 5: Integration Example")
    print("-" * 70)
    print("""
# Example: Detect cycles in codebase

# Note: Cycle detection requires graph-atlas feature
# This is a conceptual example

from ranex_core import ImportGraph, detect_cycles

# Build import graph from codebase
graph = ImportGraph()
# ... add nodes and edges from codebase analysis ...

# Detect cycles
cycles = detect_cycles(graph)

if cycles:
    print(f"❌ Found {len(cycles)} circular dependencies:")
    for cycle in cycles:
        print(f"  Cycle:")
        for file_path in cycle.cycle:
            print(f"    • {file_path}")
else:
    print("✅ No circular dependencies found")
""")
    print()
    
    # Demo 6: Benefits
    print("📝 Demo 6: Benefits of Cycle Detection")
    print("-" * 70)
    print("Cycle detection provides:")
    print("  • Early detection of architectural violations")
    print("  • Prevents tight coupling")
    print("  • Enables independent deployment")
    print("  • Improves testability")
    print()
    print("Use cases:")
    print("  • Pre-commit hooks")
    print("  • CI/CD pipeline checks")
    print("  • Architecture validation")
    print("  • Refactoring assistance")
    print()
    
    print("=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)
    print()
    print("Key Takeaways:")
    print("  • Circular imports violate architecture")
    print("  • Ranex detects cycles automatically")
    print("  • Follow dependency flow rules")
    print("  • Use dependency injection to break cycles")
    print()
    print("Next Steps:")
    print("  • Try examples/semantic_atlas_demo.py for code discovery")
    print("  • Run 'ranex arch' to check for cycles")
    print("  • Follow vertical slice architecture")


if __name__ == "__main__":
    demo_circular_imports()

