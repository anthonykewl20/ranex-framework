#!/usr/bin/env python3
"""
Ranex Framework - Structure Enforcement Demo

This demo showcases architectural structure enforcement.
It demonstrates:
1. Forbidden folder detection (utils/, helpers/, lib/)
2. Feature structure validation (4-file structure)
3. Auto-remediation capabilities
4. Quarantine system

Run: python examples/structure_enforcement_demo.py
"""

import os
import tempfile
from ranex_core import StructureSentinel


def demo_structure_enforcement():
    """Demonstrate structure enforcement capabilities."""
    print("=" * 70)
    print("Ranex Framework - Structure Enforcement Demo")
    print("=" * 70)
    print()
    
    # Initialize sentinel
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sentinel = StructureSentinel(project_root)
    print(f"✅ Structure sentinel initialized")
    print(f"   Project root: {project_root}")
    print()
    
    # Demo 1: Forbidden folders
    print("📝 Demo 1: Forbidden Folder Detection")
    print("-" * 70)
    
    forbidden_paths = [
        "app/utils/helpers.py",
        "app/helpers/common.py",
        "app/lib/utils.py",
        "app/core/config.py",
        "app/shared/constants.py",
    ]
    
    print("Testing forbidden folder paths:")
    for path in forbidden_paths:
        try:
            sentinel.check_file(path)
            print(f"  ⚠️  Unexpected: {path} was allowed")
        except Exception as e:
            print(f"  ✅ Blocked: {path}")
            print(f"     Error: {str(e)[:80]}...")
    print()
    
    # Demo 2: Valid feature structure
    print("📝 Demo 2: Valid Feature Structure")
    print("-" * 70)
    
    valid_paths = [
        "app/features/payment/routes.py",
        "app/features/payment/service.py",
        "app/features/payment/models.py",
        "app/features/payment/state.yaml",
        "app/features/payment/schemas.py",
        "app/commons/database.py",
        "app/commons/validators.py",
    ]
    
    print("Testing valid paths:")
    for path in valid_paths:
        try:
            sentinel.check_file(path)
            print(f"  ✅ Allowed: {path}")
        except Exception as e:
            print(f"  ❌ Unexpectedly blocked: {path}")
            print(f"     Error: {str(e)[:80]}...")
    print()
    
    # Demo 3: Invalid feature files
    print("📝 Demo 3: Invalid Feature Files")
    print("-" * 70)
    
    invalid_feature_paths = [
        "app/features/payment/helpers.py",  # Not in 4-file structure
        "app/features/payment/utils.py",    # Not in 4-file structure
        "app/features/payment/helpers.py", # Not in 4-file structure
    ]
    
    print("Testing invalid feature files:")
    for path in invalid_feature_paths:
        try:
            sentinel.check_file(path)
            print(f"  ⚠️  Unexpected: {path} was allowed")
        except Exception as e:
            print(f"  ✅ Blocked: {path}")
            print(f"     Error: {str(e)[:80]}...")
    print()
    
    # Demo 4: Ranex architecture rules
    print("📝 Demo 4: Ranex Architecture Rules")
    print("-" * 70)
    print("Ranex enforces vertical slice architecture:")
    print()
    print("✅ Allowed Structure:")
    print("  app/")
    print("    commons/          # Shared utilities")
    print("      database.py")
    print("      validators.py")
    print("    features/          # Feature modules")
    print("      payment/")
    print("        routes.py      # API endpoints")
    print("        service.py     # Business logic")
    print("        models.py      # Data models")
    print("        state.yaml     # State machine")
    print("        schemas.py     # Pydantic schemas (optional)")
    print()
    print("❌ Forbidden Structure:")
    print("  app/")
    print("    utils/             # ❌ FORBIDDEN")
    print("    helpers/           # ❌ FORBIDDEN")
    print("    lib/               # ❌ FORBIDDEN")
    print("    core/              # ❌ FORBIDDEN")
    print("    shared/            # ❌ FORBIDDEN")
    print()
    print("Benefits:")
    print("  • Prevents architectural drift")
    print("  • Enforces consistent structure")
    print("  • Makes codebase easier to navigate")
    print("  • Supports vertical slice architecture")
    print()
    
    # Demo 5: Auto-remediation
    print("📝 Demo 5: Auto-Remediation")
    print("-" * 70)
    print("Structure sentinel can auto-remediate violations:")
    print("  • Move files from utils/ to commons/")
    print("  • Restructure features to 4-file format")
    print("  • Quarantine invalid files")
    print()
    print("Example:")
    print("  # Before:")
    print("  app/utils/helpers.py")
    print()
    print("  # After auto-remediation:")
    print("  app/commons/helpers.py")
    print()
    
    # Demo 6: Integration example
    print("📝 Demo 6: Integration Example")
    print("-" * 70)
    print("""
# Example: Pre-commit hook integration

from ranex_core import StructureSentinel
import sys

sentinel = StructureSentinel(".")
changed_files = sys.argv[1:]  # Files changed in commit

for file_path in changed_files:
    try:
        sentinel.check_file(file_path)
        print(f"✅ {file_path} passes structure validation")
    except Exception as e:
        print(f"❌ {file_path} violates structure rules")
        print(f"   {e}")
        sys.exit(1)
""")
    print()
    
    print("=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)
    print()
    print("Key Takeaways:")
    print("  • Structure enforcement prevents architectural drift")
    print("  • Enforces vertical slice architecture")
    print("  • Blocks forbidden folders automatically")
    print("  • Validates feature structure (4-file format)")
    print()
    print("Next Steps:")
    print("  • Try examples/layer_enforcement_demo.py for layer validation")
    print("  • Try examples/import_validation_demo.py for import safety")
    print("  • Integrate into pre-commit hooks")


if __name__ == "__main__":
    demo_structure_enforcement()

