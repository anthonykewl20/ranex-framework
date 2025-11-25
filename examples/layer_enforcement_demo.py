#!/usr/bin/env python3
"""
Ranex Framework - Layer Enforcement Demo

This demo showcases architectural layer validation.
It demonstrates:
1. Layer dependency checking
2. Violation detection
3. Architecture reports
4. Fix suggestions

Run: python examples/layer_enforcement_demo.py
"""

import os
from ranex_core import LayerEnforcer


def demo_layer_enforcement():
    """Demonstrate layer enforcement capabilities."""
    print("=" * 70)
    print("Ranex Framework - Layer Enforcement Demo")
    print("=" * 70)
    print()
    
    enforcer = LayerEnforcer.new()
    print("✅ Layer enforcer initialized")
    print()
    
    # Demo 1: Scan project
    print("📝 Demo 1: Scan Project Architecture")
    print("-" * 70)
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"Scanning project: {project_root}")
    
    try:
        report = enforcer.scan(project_root)
        print(f"✅ Scan completed")
        print(f"   Valid: {report.valid}")
        print(f"   Violations: {len(report.violations)}")
        print(f"   Suggestions: {len(report.suggestions)}")
        print()
        
        if report.violations:
            print("Architecture Violations:")
            for i, violation in enumerate(report.violations[:5], 1):
                print(f"  {i}. {violation}")
            if len(report.violations) > 5:
                print(f"  ... and {len(report.violations) - 5} more")
            print()
        
        if report.suggestions:
            print("Fix Suggestions:")
            for i, suggestion in enumerate(report.suggestions[:5], 1):
                print(f"  {i}. {suggestion}")
            if len(report.suggestions) > 5:
                print(f"  ... and {len(report.suggestions) - 5} more")
        else:
            print("✅ No violations found - architecture is valid!")
    except Exception as e:
        print(f"⚠️  Scan error: {e}")
    print()
    
    # Demo 2: Layer architecture rules
    print("📝 Demo 2: Ranex Layer Architecture Rules")
    print("-" * 70)
    print("Ranex enforces layered architecture:")
    print()
    print("Layer Hierarchy (top to bottom):")
    print("  1. routes/     → Can import: service, commons")
    print("  2. service/    → Can import: models, commons")
    print("  3. models/     → Can import: commons")
    print("  4. commons/    → Cannot import from other layers")
    print()
    print("✅ Valid Dependencies:")
    print("  routes.py → service.py")
    print("  routes.py → commons/database.py")
    print("  service.py → models.py")
    print("  service.py → commons/validators.py")
    print()
    print("❌ Invalid Dependencies:")
    print("  routes.py → models.py  (must go through service)")
    print("  service.py → routes.py  (circular dependency)")
    print("  models.py → service.py  (circular dependency)")
    print("  commons/ → routes.py  (commons cannot import features)")
    print()
    
    # Demo 3: Common violations
    print("📝 Demo 3: Common Architecture Violations")
    print("-" * 70)
    print("""
# Violation 1: Routes importing models directly
# File: app/features/payment/routes.py
from app.features.payment.models import Payment  # ❌ VIOLATION

# Fix: Use service layer
from app.features.payment.service import PaymentService  # ✅ CORRECT

# Violation 2: Service importing routes
# File: app/features/payment/service.py
from app.features.payment.routes import get_payment  # ❌ CIRCULAR DEPENDENCY

# Fix: Extract shared logic to commons
from app.commons.payment_utils import validate_payment  # ✅ CORRECT

# Violation 3: Commons importing features
# File: app/commons/database.py
from app.features.payment.models import Payment  # ❌ VIOLATION

# Fix: Keep commons independent
# Use dependency injection or pass models as parameters
""")
    print()
    
    # Demo 4: Configuration
    print("📝 Demo 4: Architecture Configuration")
    print("-" * 70)
    print("Layer rules can be configured in .ranex/config.toml:")
    print("""
[architecture]
layers = {
    "routes" = ["service", "commons"],
    "service" = ["models", "commons"],
    "models" = ["commons"],
    "commons" = []
}

[architecture.hints]
"routes->models" = "💡 Use service layer instead"
"service->routes" = "💡 Circular dependency detected"
""")
    print()
    
    # Demo 5: Integration example
    print("📝 Demo 5: CI/CD Integration Example")
    print("-" * 70)
    print("""
# Example: Fail build on architecture violations

from ranex_core import LayerEnforcer

enforcer = LayerEnforcer.new()
report = enforcer.scan(".")

if not report.valid:
    print(f"❌ Build failed: {len(report.violations)} architecture violations")
    for violation in report.violations:
        print(f"  - {violation}")
    sys.exit(1)
else:
    print("✅ Architecture is valid")
""")
    print()
    
    print("=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)
    print()
    print("Key Takeaways:")
    print("  • Layer enforcement prevents architectural violations")
    print("  • Enforces dependency direction (top-down)")
    print("  • Prevents circular dependencies")
    print("  • Provides actionable fix suggestions")
    print()
    print("Next Steps:")
    print("  • Try examples/structure_enforcement_demo.py for structure validation")
    print("  • Try examples/import_validation_demo.py for import safety")
    print("  • Configure layers in .ranex/config.toml")


if __name__ == "__main__":
    demo_layer_enforcement()

