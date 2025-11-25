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
from ranex_core import SecurityScanner


def demo_security_scanning():
    """Demonstrate security scanning capabilities."""
    print("=" * 70)
    print("Ranex Framework - Security Scan Demo (SAST)")
    print("=" * 70)
    print()
    
    scanner = SecurityScanner()
    print(f"✅ Security scanner initialized")
    print(f"   Patterns loaded: {scanner.get_pattern_count()}")
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
    
    violations = scanner.scan_content(vulnerable_code_1)
    print(f"Found {len(violations)} security violations:")
    for v in violations:
        print(f"  [{v.severity.upper()}] {v.category}")
        print(f"    Line {v.line}: {v.code.strip()}")
        print(f"    Issue: {v.message}")
        print(f"    Fix: {v.fix_suggestion}")
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
    
    violations = scanner.scan_content(vulnerable_code_2)
    print(f"Found {len(violations)} security violations:")
    for v in violations:
        print(f"  [{v.severity.upper()}] {v.category}")
        print(f"    Line {v.line}: {v.code.strip()}")
        print(f"    Issue: {v.message}")
        print(f"    Fix: {v.fix_suggestion}")
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
    
    violations = scanner.scan_content(vulnerable_code_3)
    print(f"Found {len(violations)} security violations:")
    for v in violations:
        print(f"  [{v.severity.upper()}] {v.category}")
        print(f"    Line {v.line}: {v.code.strip()}")
        print(f"    Issue: {v.message}")
        print(f"    Fix: {v.fix_suggestion}")
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
    
    violations = scanner.scan_content(vulnerable_code_4)
    print(f"Found {len(violations)} security violations:")
    for v in violations:
        print(f"  [{v.severity.upper()}] {v.category}")
        print(f"    Line {v.line}: {v.code.strip()}")
        print(f"    Issue: {v.message}")
        print(f"    Fix: {v.fix_suggestion}")
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
    
    is_secure = scanner.is_secure(secure_code)
    violations = scanner.scan_content(secure_code)
    
    if is_secure and len(violations) == 0:
        print("✅ Code is secure - no violations detected")
    else:
        print(f"⚠️  Found {len(violations)} violations")
        for v in violations:
            print(f"  [{v.severity.upper()}] {v.category}: {v.message}")
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
        print(f"Secure: {result.secure}")
        print(f"Violations: {len(result.violations)}")
        print(f"Scan time: {result.scan_time_ms}ms")
        
        if result.violations:
            print("\nViolations found:")
            for v in result.violations:
                print(f"  [{v.severity.upper()}] Line {v.line}: {v.message}")
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

