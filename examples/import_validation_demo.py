#!/usr/bin/env python3
"""
Ranex Framework - Import Validation Demo

This demo showcases import security validation.
It demonstrates:
1. Package security checking
2. Typosquatting detection
3. Dependency validation
4. Import safety scoring

Run: python examples/import_validation_demo.py
"""

import os
from ranex_core import ImportValidator


def demo_import_validation():
    """Demonstrate import validation capabilities."""
    print("=" * 70)
    print("Ranex Framework - Import Validation Demo")
    print("=" * 70)
    print()
    
    validator = ImportValidator()
    print("✅ Import validator initialized")
    print(f"   Allowed packages: {len(validator.allowed_packages)}")
    print()
    
    # Demo 1: Valid packages
    print("📝 Demo 1: Valid Package Imports")
    print("-" * 70)
    
    valid_packages = [
        "fastapi",
        "pydantic",
        "sqlalchemy",
        "ranex_core",
    ]
    
    print("Testing valid packages:")
    for package in valid_packages:
        try:
            result = validator.check_package(package)
            if result.is_safe:
                print(f"  ✅ {package}: Safe (score: {result.security_score})")
                print(f"     Reason: {result.reason}")
            else:
                print(f"  ⚠️  {package}: Not safe")
                print(f"     Reason: {result.reason}")
                if result.alternatives:
                    print(f"     Alternatives: {', '.join(result.alternatives)}")
        except Exception as e:
            print(f"  ❌ {package}: Error - {e}")
    print()
    
    # Demo 2: Typosquatting detection
    print("📝 Demo 2: Typosquatting Detection")
    print("-" * 70)
    
    suspicious_packages = [
        "requets",      # Typo of "requests"
        "pythom",       # Typo of "python"
        "numpy",        # Valid but checking
        "django",       # Valid but checking
    ]
    
    print("Testing for typosquatting:")
    for package in suspicious_packages:
        try:
            result = validator.check_package(package)
            if not result.is_safe:
                print(f"  ⚠️  {package}: Suspicious")
                print(f"     Reason: {result.reason}")
                if result.alternatives:
                    print(f"     Did you mean: {', '.join(result.alternatives)}")
            else:
                print(f"  ✅ {package}: Safe")
        except Exception as e:
            print(f"  ❌ {package}: Error - {e}")
    print()
    
    # Demo 3: Unknown packages
    print("📝 Demo 3: Unknown Package Detection")
    print("-" * 70)
    
    unknown_packages = [
        "malicious-package",
        "unknown-library",
        "suspicious-module",
    ]
    
    print("Testing unknown packages:")
    for package in unknown_packages:
        try:
            result = validator.check_package(package)
            if not result.is_safe:
                print(f"  ⚠️  {package}: Not in dependencies")
                print(f"     Reason: {result.reason}")
                print(f"     Security score: {result.security_score}")
                if result.alternatives:
                    print(f"     Similar packages: {', '.join(result.alternatives)}")
            else:
                print(f"  ✅ {package}: Safe")
        except Exception as e:
            print(f"  ❌ {package}: Error - {e}")
    print()
    
    # Demo 4: Security scoring
    print("📝 Demo 4: Security Scoring")
    print("-" * 70)
    print("Import validator provides security scores:")
    print("  • 100: Package is in dependencies (safe)")
    print("  • 80-99: Package is similar to known package (typosquatting risk)")
    print("  • 50-79: Package is unknown (medium risk)")
    print("  • 0-49: Package is suspicious (high risk)")
    print()
    print("Example scores:")
    print("  fastapi → 100 (in dependencies)")
    print("  requets → 85 (typo of 'requests')")
    print("  unknown-pkg → 50 (not in dependencies)")
    print()
    
    # Demo 5: Typosquatting examples
    print("📝 Demo 5: Common Typosquatting Attacks")
    print("-" * 70)
    print("Typosquatting is when attackers create packages with similar names:")
    print()
    print("Real Examples:")
    print("  • requests → requets (malicious)")
    print("  • urllib3 → urllib (malicious)")
    print("  • django → djang (malicious)")
    print()
    print("Protection:")
    print("  • Ranex detects similar package names")
    print("  • Suggests correct package names")
    print("  • Warns about unknown packages")
    print("  • Validates against dependency list")
    print()
    
    # Demo 6: Integration example
    print("📝 Demo 6: Integration Example")
    print("-" * 70)
    print("""
# Example: Pre-commit hook for import validation

from ranex_core import ImportValidator
import ast
import sys

validator = ImportValidator()

def check_imports(file_path):
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                package = alias.name.split('.')[0]
                result = validator.check_package(package)
                if not result.is_safe:
                    print(f"❌ {file_path}: Unsafe import '{package}'")
                    print(f"   {result.reason}")
                    if result.alternatives:
                        print(f"   Did you mean: {result.alternatives[0]}")
                    return False
    return True

# Check all Python files
all_safe = True
for file_path in sys.argv[1:]:
    if not check_imports(file_path):
        all_safe = False

sys.exit(0 if all_safe else 1)
""")
    print()
    
    print("=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)
    print()
    print("Key Takeaways:")
    print("  • Import validation prevents typosquatting attacks")
    print("  • Validates packages against dependency list")
    print("  • Provides security scores for risk assessment")
    print("  • Suggests correct package names")
    print()
    print("Next Steps:")
    print("  • Try examples/structure_enforcement_demo.py for structure validation")
    print("  • Try examples/layer_enforcement_demo.py for layer validation")
    print("  • Integrate into pre-commit hooks")


if __name__ == "__main__":
    demo_import_validation()

