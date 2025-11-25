#!/usr/bin/env python3
"""
Ranex Framework - Antipattern Detection Demo

This demo showcases code quality and antipattern detection.
It demonstrates:
1. God class detection
2. Magic number detection
3. Mutable default arguments
4. Bare except clauses
5. Ranex architecture violations

Run: python examples/antipattern_demo.py
"""

import tempfile
import os
try:
    from ranex_core import AntipatternDetector
    _antipattern_available = True
except ImportError:
    _antipattern_available = False
    AntipatternDetector = None


def demo_antipattern_detection():
    """Demonstrate antipattern detection capabilities."""
    print("=" * 70)
    print("Ranex Framework - Antipattern Detection Demo")
    print("=" * 70)
    print()
    
    if not _antipattern_available or AntipatternDetector is None:
        print("⚠️  AntipatternDetector not available in this build.")
        print("   This feature is optional and may not be included.")
        return
    
    detector = AntipatternDetector()
    print("✅ Antipattern detector initialized")
    print()
    
    # Demo 1: God class detection
    print("📝 Demo 1: God Class Detection")
    print("-" * 70)
    
    god_class_code = """
class PaymentProcessor:
    def process_payment(self): pass
    def validate_payment(self): pass
    def send_email(self): pass
    def generate_invoice(self): pass
    def update_database(self): pass
    def log_transaction(self): pass
    def calculate_tax(self): pass
    def apply_discount(self): pass
    def check_inventory(self): pass
    def notify_shipping(self): pass
    def handle_refund(self): pass
    def process_chargeback(self): pass
    def generate_report(self): pass
    def export_data(self): pass
    def import_data(self): pass
    def backup_data(self): pass
    def restore_data(self): pass
    def audit_log(self): pass
    def security_check(self): pass
    def rate_limit(self): pass
    def cache_result(self): pass
    def retry_failed(self): pass
"""
    
    violations = detector.scan_content(god_class_code)
    print(f"Found {len(violations)} antipattern violations:")
    for v in violations:
        print(f"  [{v.severity.upper()}] {v.pattern}")
        print(f"    Line {v.line}: {v.code.strip()}")
        print(f"    Issue: {v.message}")
        print(f"    Fix: {v.fix_suggestion}")
        if v.ranex_rule:
            print(f"    Ranex Rule: {v.ranex_rule}")
        print()
    print()
    
    # Demo 2: Magic numbers
    print("📝 Demo 2: Magic Number Detection")
    print("-" * 70)
    
    magic_number_code = """
def calculate_interest(principal):
    return principal * 0.05 * 365  # Magic numbers!
    
def retry_request():
    for i in range(3):  # Magic number
        try:
            make_request()
            break
        except:
            time.sleep(5)  # Magic number
"""
    
    violations = detector.scan_content(magic_number_code)
    print(f"Found {len(violations)} antipattern violations:")
    for v in violations:
        print(f"  [{v.severity.upper()}] {v.pattern}")
        print(f"    Line {v.line}: {v.code.strip()}")
        print(f"    Issue: {v.message}")
        print(f"    Fix: {v.fix_suggestion}")
        print()
    print()
    
    # Demo 3: Mutable default arguments
    print("📝 Demo 3: Mutable Default Arguments")
    print("-" * 70)
    
    mutable_default_code = """
def process_items(items=[]):  # BAD: Mutable default
    items.append("new_item")
    return items

def update_cache(key, value, cache={}):  # BAD: Mutable default
    cache[key] = value
    return cache
"""
    
    violations = detector.scan_content(mutable_default_code)
    print(f"Found {len(violations)} antipattern violations:")
    for v in violations:
        print(f"  [{v.severity.upper()}] {v.pattern}")
        print(f"    Line {v.line}: {v.code.strip()}")
        print(f"    Issue: {v.message}")
        print(f"    Fix: {v.fix_suggestion}")
        print()
    print()
    
    # Demo 4: Bare except clauses
    print("📝 Demo 4: Bare Except Clauses")
    print("-" * 70)
    
    bare_except_code = """
def risky_operation():
    try:
        do_something()
    except:  # BAD: Catches everything
        pass

def another_operation():
    try:
        process_data()
    except:  # BAD: Silent failure
        return None
"""
    
    violations = detector.scan_content(bare_except_code)
    print(f"Found {len(violations)} antipattern violations:")
    for v in violations:
        print(f"  [{v.severity.upper()}] {v.pattern}")
        print(f"    Line {v.line}: {v.code.strip()}")
        print(f"    Issue: {v.message}")
        print(f"    Fix: {v.fix_suggestion}")
        print()
    print()
    
    # Demo 5: Ranex architecture violations
    print("📝 Demo 5: Ranex Architecture Violations")
    print("-" * 70)
    
    architecture_violation_code = """
# BAD: Importing from forbidden folders
from app.utils.helpers import validate_email
from app.helpers.common import format_currency
from app.lib.utils import parse_json

# BAD: Utility classes
class StringUtils:
    @staticmethod
    def capitalize(s): pass

class HelperFunctions:
    @staticmethod
    def format_date(d): pass
"""
    
    violations = detector.scan_content(architecture_violation_code)
    print(f"Found {len(violations)} architecture violations:")
    for v in violations:
        print(f"  [{v.severity.upper()}] {v.pattern}")
        print(f"    Line {v.line}: {v.code.strip()}")
        print(f"    Issue: {v.message}")
        print(f"    Fix: {v.fix_suggestion}")
        if v.ranex_rule:
            print(f"    Ranex Rule: {v.ranex_rule}")
        print()
    print()
    
    # Demo 6: Clean code (no violations)
    print("📝 Demo 6: Clean Code (No Violations)")
    print("-" * 70)
    
    clean_code = """
from app.commons.validators import validate_email
from app.features.payment.service import process_payment

# Constants instead of magic numbers
INTEREST_RATE = 0.05
DAYS_PER_YEAR = 365
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5

def calculate_interest(principal: float) -> float:
    return principal * INTEREST_RATE * DAYS_PER_YEAR

def retry_request(max_retries: int = MAX_RETRIES):
    for i in range(max_retries):
        try:
            make_request()
            break
        except ConnectionError:
            time.sleep(RETRY_DELAY_SECONDS)

def process_items(items=None):
    if items is None:
        items = []
    items.append("new_item")
    return items
"""
    
    is_clean = detector.is_clean(clean_code)
    violations = detector.scan_content(clean_code)
    
    if is_clean and len(violations) == 0:
        print("✅ Code is clean - no antipatterns detected")
    else:
        print(f"⚠️  Found {len(violations)} violations:")
        for v in violations:
            print(f"  [{v.severity.upper()}] {v.pattern}: {v.message}")
    print()
    
    # Demo 7: File scanning
    print("📝 Demo 7: File Scanning")
    print("-" * 70)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(god_class_code)
        temp_file = f.name
    
    try:
        result = detector.scan_file(temp_file)
        print(f"Scanned file: {temp_file}")
        print(f"Clean: {result.clean}")
        print(f"Violations: {len(result.violations)}")
        print(f"Scan time: {result.scan_time_ms}ms")
        
        if result.violations:
            print("\nViolations found:")
            for v in result.violations:
                print(f"  [{v.severity.upper()}] {v.pattern}: {v.message}")
    except Exception as e:
        print(f"⚠️  File scanning error: {e}")
    finally:
        os.unlink(temp_file)
    print()
    
    print("=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)
    print()
    print("Key Takeaways:")
    print("  • Antipattern detection improves code quality")
    print("  • Enforces Ranex architecture rules")
    print("  • Provides actionable fix suggestions")
    print("  • Prevents technical debt before it accumulates")
    print()
    print("Next Steps:")
    print("  • Try examples/security_scan_demo.py for security scanning")
    print("  • Try examples/structure_enforcement_demo.py for architecture enforcement")
    print("  • Integrate into CI/CD pipeline for automated checks")


if __name__ == "__main__":
    demo_antipattern_detection()

