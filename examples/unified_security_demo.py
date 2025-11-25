#!/usr/bin/env python3
"""
Ranex Framework - Unified Security Scanner Demo

This demo showcases the unified security scanner that combines:
1. SAST (Static Application Security Testing)
2. Dependency vulnerability scanning
3. Antipattern detection
4. Unified reporting and prioritization

Run: python examples/unified_security_demo.py
"""

import os
import tempfile
# Note: SecurityScanner is internal, not directly exposed
try:
    from ranex_core import UnifiedSecurityScanner, AntipatternDetector, DependencyScannerOSV
    _security_available = True
except ImportError:
    _security_available = False
    UnifiedSecurityScanner = None
    AntipatternDetector = None
    DependencyScannerOSV = None


def demo_unified_security():
    """Demonstrate unified security scanning."""
    print("=" * 70)
    print("Ranex Framework - Unified Security Scanner Demo")
    print("=" * 70)
    print()
    
    # Initialize unified scanner
    if not _security_available or UnifiedSecurityScanner is None:
        print("⚠️  UnifiedSecurityScanner not available in this build.")
        print("   This feature is optional and may not be included.")
        print("   See examples/security_scan_demo.py for fallback demonstration.")
        return
    
    try:
        scanner = UnifiedSecurityScanner.new()
        print("✅ Unified security scanner initialized")
    except Exception as e:
        print(f"⚠️  Failed to initialize unified scanner: {e}")
        print("   Falling back to individual scanners...")
        scanner = None
    print()
    
    # Demo 1: Unified scanning
    if scanner:
        print("📝 Demo 1: Unified Security Scan")
        print("-" * 70)
        
        vulnerable_code = """
import os
import pickle

# Hardcoded secret
api_key = "sk-1234567890abcdefghijklmnopqrstuvwxyz"

# SQL injection vulnerability
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return execute_query(query)

# Insecure deserialization
def load_data(file_path):
    with open(file_path, 'rb') as f:
        return pickle.load(f)

# Mutable default argument
def process_items(items=[]):
    items.append("new_item")
    return items
"""
        
        try:
            result = scanner.scan_content(vulnerable_code)
            print(f"✅ Unified scan completed")
            print(f"   Violations found: {len(result.violations)}")
            print(f"   Pattern scans: {result.stats.pattern_scans}")
            print(f"   ML scans: {result.stats.ml_scans}")
            print(f"   Total scan time: {result.performance.total_ms}ms")
            print()
            
            if result.violations:
                print("Violations by severity:")
                severity_counts = {}
                for v in result.violations:
                    severity_counts[v.severity] = severity_counts.get(v.severity, 0) + 1
                
                for severity in ["critical", "high", "medium", "low"]:
                    count = severity_counts.get(severity, 0)
                    if count > 0:
                        print(f"  {severity.upper()}: {count}")
                print()
                
                print("Top violations:")
                for v in result.violations[:5]:
                    print(f"  [{v.severity.upper()}] {v.category}")
                    print(f"    Line {v.line}: {v.message}")
                    print(f"    Fix: {v.fix_suggestion}")
                    print()
        except Exception as e:
            print(f"⚠️  Unified scan error: {e}")
        print()
    
    # Demo 2: Individual scanners (fallback)
    print("📝 Demo 2: Individual Scanner Comparison")
    print("-" * 70)
    
    test_code = """
api_key = "sk-test1234567890abcdefghijklmnopqrstuvwxyz"
def process(items=[]): pass
"""
    
    # SAST scanner
    print("SAST Scanner:")
    # SecurityScanner is internal - UnifiedSecurityScanner includes SAST scanning
    # sast_scanner = SecurityScanner()  # Not available - use UnifiedSecurityScanner instead
    print("  ⚠️  SAST scanning is included in UnifiedSecurityScanner")
    print()
    
    # Antipattern detector
    print("Antipattern Detector:")
    if AntipatternDetector is None:
        print("  ⚠️  AntipatternDetector not available in this build")
    else:
        try:
            antipattern_detector = AntipatternDetector()
            antipattern_violations = antipattern_detector.scan_content(test_code)
            print(f"  Violations: {len(antipattern_violations)}")
            for v in antipattern_violations:
                print(f"    [{v.severity.upper()}] {v.pattern}: {v.message}")
        except Exception as e:
            print(f"  ⚠️  Antipattern scan error: {e}")
    print()
    
    # Dependency scanner
    print("Dependency Scanner:")
    if DependencyScannerOSV is None:
        print("  ⚠️  DependencyScannerOSV not available in this build")
    else:
        try:
            dep_scanner = DependencyScannerOSV.new_offline()
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            dep_result = dep_scanner.scan_project(project_root)
            print(f"  Dependencies scanned: {dep_result.total_dependencies}")
            print(f"  Vulnerabilities: {len(dep_result.vulnerabilities)}")
        except Exception as e:
            print(f"  ⚠️  Dependency scan error: {e}")
    print()
    
    # Demo 3: Severity prioritization
    print("📝 Demo 3: Severity Prioritization")
    print("-" * 70)
    print("Unified scanner prioritizes violations by severity:")
    print("  1. CRITICAL - Immediate action required")
    print("     • Hardcoded secrets")
    print("     • SQL injection")
    print("     • Insecure deserialization")
    print()
    print("  2. HIGH - Address soon")
    print("     • Weak cryptography")
    print("     • Mutable defaults")
    print("     • God classes")
    print()
    print("  3. MEDIUM - Review and fix")
    print("     • Magic numbers")
    print("     • Bare excepts")
    print()
    print("  4. LOW - Best practices")
    print("     • Print statements")
    print("     • Code style issues")
    print()
    
    # Demo 4: Integration example
    print("📝 Demo 4: CI/CD Integration Example")
    print("-" * 70)
    print("""
# Example: Fail build on critical vulnerabilities

scanner = UnifiedSecurityScanner.new()
result = scanner.scan_content(code)

critical_vulns = [v for v in result.violations if v.severity == "critical"]
if critical_vulns:
    print(f"❌ Build failed: {len(critical_vulns)} critical vulnerabilities")
    for v in critical_vulns:
        print(f"  - {v.category}: {v.message}")
    sys.exit(1)
else:
    print("✅ No critical vulnerabilities found")
""")
    print()
    
    # Demo 5: Performance comparison
    print("📝 Demo 5: Performance Benefits")
    print("-" * 70)
    print("Unified scanner provides:")
    print("  • Single API for all security checks")
    print("  • Optimized performance (shared resources)")
    print("  • Unified reporting format")
    print("  • Better prioritization across scan types")
    print("  • Reduced false positives through cross-validation")
    print()
    
    print("=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)
    print()
    print("Key Takeaways:")
    print("  • Unified scanner combines all security checks")
    print("  • Provides severity-based prioritization")
    print("  • Optimized for performance")
    print("  • Easy to integrate into CI/CD pipelines")
    print()
    print("Next Steps:")
    print("  • Integrate into pre-commit hooks")
    print("  • Add to CI/CD pipeline")
    print("  • Set up automated vulnerability alerts")
    print("  • Review individual scanner demos for details")


if __name__ == "__main__":
    demo_unified_security()

