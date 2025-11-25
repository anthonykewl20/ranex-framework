#!/usr/bin/env python3
"""
Ranex Framework - Security Scan Demo (SAST)

This demo showcases Static Application Security Testing (SAST) capabilities.
It demonstrates:
1. Hardcoded secrets detection
2. SQL injection vulnerability detection
3. XSS vulnerability detection
4. Insecure deserialization detection
5. Weak cryptography detection

Run: python examples/security_scan_demo.py
"""

import tempfile
import os

# Note: SecurityScanner is internal. Use UnifiedSecurityScanner instead.
try:
    from ranex_core import UnifiedSecurityScanner
    SECURITY_SCANNER_AVAILABLE = True
except ImportError:
    print("⚠️  UnifiedSecurityScanner not available. Using fallback demonstration.")
    SECURITY_SCANNER_AVAILABLE = False


def demo_security_scanning():
    """Demonstrate security scanning capabilities."""
    print("=" * 70)
    print("Ranex Framework - Security Scan Demo (SAST)")
    print("=" * 70)
    print()
    
    if not SECURITY_SCANNER_AVAILABLE:
        print("⚠️  Security scanning not available in this build.")
        print("   This demo requires UnifiedSecurityScanner.")
        print("   See examples/unified_security_demo.py for working example.")
        return
    
    scanner = UnifiedSecurityScanner.new()
    print(f"✅ Security scanner initialized")
    print()
    
    # Demo 1: Hardcoded secrets
    print("📝 Demo 1: Hardcoded Secrets Detection")
    print("-" * 70)
    
    vulnerable_code_1 = """
# BAD: Hardcoded API key
api_key = "sk-1234567890abcdefghijklmnopqrstuvwxyz"
password = "super_secret_password_123"

# GOOD: Using environment variables
import os
api_key = os.getenv("API_KEY")
"""
    
    result = scanner.scan_content(vulnerable_code_1)
    violations = result.violations if hasattr(result, 'violations') else []
    print(f"Found {len(violations)} security violations:")
    for v in violations:
        severity = getattr(v, 'severity', 'unknown')
        category = getattr(v, 'category', 'unknown')
        line = getattr(v, 'line', 0)
        code = getattr(v, 'code', '').strip()
        message = getattr(v, 'message', 'Security issue detected')
        fix = getattr(v, 'fix_suggestion', 'Review code')
        print(f"  [{severity.upper()}] {category}")
        print(f"    Line {line}: {code}")
        print(f"    Issue: {message}")
        print(f"    Fix: {fix}")
        print()
    print()
    
    # Demo 2: SQL injection
    print("📝 Demo 2: SQL Injection Detection")
    print("-" * 70)
    
    vulnerable_code_2 = """
def get_user(user_id):
    # BAD: SQL injection vulnerability
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return execute_query(query)
    
    # GOOD: Parameterized query
    query = "SELECT * FROM users WHERE id = ?"
    return execute_query(query, (user_id,))
"""
    
    result = scanner.scan_content(vulnerable_code_2)
    violations = result.violations if hasattr(result, 'violations') else []
    print(f"Found {len(violations)} security violations:")
    for v in violations:
        severity = getattr(v, 'severity', 'unknown')
        category = getattr(v, 'category', 'unknown')
        line = getattr(v, 'line', 0)
        code = getattr(v, 'code', '').strip()
        message = getattr(v, 'message', 'Security issue detected')
        fix = getattr(v, 'fix_suggestion', 'Review code')
        print(f"  [{severity.upper()}] {category}")
        print(f"    Line {line}: {code}")
        print(f"    Issue: {message}")
        print(f"    Fix: {fix}")
        print()
    print()
    
    # Demo 3: XSS vulnerability
    print("📝 Demo 3: XSS Vulnerability Detection")
    print("-" * 70)
    
    vulnerable_code_3 = """
from flask import Flask, request

app = Flask(__name__)

@app.route("/search")
def search():
    # BAD: XSS vulnerability
    query = request.args.get("q", "")
    return f"<h1>Search results for: {query}</h1>"
    
    # GOOD: Escape user input
    from markupsafe import escape
    return f"<h1>Search results for: {escape(query)}</h1>"
"""
    
    result = scanner.scan_content(vulnerable_code_3)
    violations = result.violations if hasattr(result, 'violations') else []
    print(f"Found {len(violations)} security violations:")
    for v in violations:
        severity = getattr(v, 'severity', 'unknown')
        category = getattr(v, 'category', 'unknown')
        line = getattr(v, 'line', 0)
        code = getattr(v, 'code', '').strip()
        message = getattr(v, 'message', 'Security issue detected')
        fix = getattr(v, 'fix_suggestion', 'Review code')
        print(f"  [{severity.upper()}] {category}")
        print(f"    Line {line}: {code}")
        print(f"    Issue: {message}")
        print(f"    Fix: {fix}")
        print()
    print()
    
    # Demo 4: Insecure deserialization
    print("📝 Demo 4: Insecure Deserialization Detection")
    print("-" * 70)
    
    vulnerable_code_4 = """
import pickle

# BAD: Insecure deserialization
def load_data(file_path):
    with open(file_path, 'rb') as f:
        return pickle.load(f)
    
    # GOOD: Use JSON or safe serialization
    import json
    with open(file_path, 'r') as f:
        return json.load(f)
"""
    
    result = scanner.scan_content(vulnerable_code_4)
    violations = result.violations if hasattr(result, 'violations') else []
    print(f"Found {len(violations)} security violations:")
    for v in violations:
        severity = getattr(v, 'severity', 'unknown')
        category = getattr(v, 'category', 'unknown')
        line = getattr(v, 'line', 0)
        code = getattr(v, 'code', '').strip()
        message = getattr(v, 'message', 'Security issue detected')
        fix = getattr(v, 'fix_suggestion', 'Review code')
        print(f"  [{severity.upper()}] {category}")
        print(f"    Line {line}: {code}")
        print(f"    Issue: {message}")
        print(f"    Fix: {fix}")
        print()
    print()
    
    # Demo 5: Secure code (no violations)
    print("📝 Demo 5: Secure Code (No Violations)")
    print("-" * 70)
    
    secure_code = """
import os
from sqlalchemy import text

def get_user(user_id: int):
    api_key = os.getenv("API_KEY")
    query = text("SELECT * FROM users WHERE id = :user_id")
    return db.execute(query, {"user_id": user_id})
"""
    
    result = scanner.scan_content(secure_code)
    violations = result.violations if hasattr(result, 'violations') else []
    
    if len(violations) == 0:
        print("✅ Code is secure - no violations detected")
    else:
        print(f"⚠️  Found {len(violations)} violations")
        for v in violations:
            severity = getattr(v, 'severity', 'unknown')
            category = getattr(v, 'category', 'unknown')
            message = getattr(v, 'message', 'Security issue detected')
            print(f"  [{severity.upper()}] {category}: {message}")
    print()
    
    # Demo 6: File scanning
    print("📝 Demo 6: File Scanning")
    print("-" * 70)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(vulnerable_code_1)
        temp_file = f.name
    
    try:
        result = scanner.scan_file(temp_file)
        print(f"Scanned file: {temp_file}")
        secure = getattr(result, 'secure', True)
        violations = getattr(result, 'violations', [])
        scan_time = getattr(result, 'scan_time_ms', 0)
        print(f"Secure: {secure}")
        print(f"Violations: {len(violations)}")
        print(f"Scan time: {scan_time}ms")
        
        if violations:
            print("\nViolations found:")
            for v in violations:
                severity = getattr(v, 'severity', 'unknown')
                line = getattr(v, 'line', 0)
                message = getattr(v, 'message', 'Security issue detected')
                print(f"  [{severity.upper()}] Line {line}: {message}")
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
    print("  • SAST scanning detects vulnerabilities before deployment")
    print("  • Multiple severity levels (critical, high, medium, low)")
    print("  • Provides fix suggestions for each violation")
    print("  • Can scan both file content and files on disk")
    print()
    print("Next Steps:")
    print("  • Try examples/antipattern_demo.py for code quality checks")
    print("  • Try examples/dependency_scan_demo.py for dependency vulnerabilities")
    print("  • Try examples/unified_security_demo.py for comprehensive scanning")


if __name__ == "__main__":
    demo_security_scanning()

