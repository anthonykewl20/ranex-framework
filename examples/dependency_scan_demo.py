#!/usr/bin/env python3
"""
Ranex Framework - Dependency Vulnerability Scanning Demo

This demo showcases dependency vulnerability scanning using OSV.dev API.
It demonstrates:
1. CVE lookup for Python packages
2. Vulnerability severity assessment
3. Fixed version detection
4. Batch dependency queries
5. Offline mode support

Run: python examples/dependency_scan_demo.py
"""

import os
import sys
try:
    from ranex_core import DependencyScannerOSV
    _dependency_scanner_available = True
except ImportError:
    _dependency_scanner_available = False
    DependencyScannerOSV = None


def demo_dependency_scanning():
    """Demonstrate dependency vulnerability scanning."""
    print("=" * 70)
    print("Ranex Framework - Dependency Vulnerability Scanning Demo")
    print("=" * 70)
    print()
    
    # Initialize scanner
    if not _dependency_scanner_available or DependencyScannerOSV is None:
        print("⚠️  DependencyScannerOSV not available in this build.")
        print("   This feature is optional and may not be included.")
        return
    
    try:
        scanner = DependencyScannerOSV.new()
        print("✅ Dependency scanner initialized (OSV API enabled)")
    except Exception as e:
        print(f"⚠️  Failed to initialize OSV scanner: {e}")
        print("   Trying offline mode...")
        try:
            scanner = DependencyScannerOSV.new_offline()
            print("✅ Dependency scanner initialized (offline mode)")
        except Exception as e2:
            print(f"❌ Failed to initialize scanner: {e2}")
            print("   Skipping dependency scanning demo")
            return
    print()
    
    # Demo 1: Scan current project
    print("📝 Demo 1: Scan Project Dependencies")
    print("-" * 70)
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"Scanning project: {project_root}")
    
    try:
        result = scanner.scan_project(project_root)
        print(f"✅ Scan completed")
        print(f"   Total dependencies: {result.total_dependencies}")
        print(f"   Vulnerabilities found: {len(result.vulnerabilities)}")
        print(f"   Safe: {result.safe}")
        print(f"   Scan time: {result.scan_time_ms}ms")
        print(f"   OSV API used: {result.osv_api_used}")
        print()
        
        if result.vulnerabilities:
            print("Vulnerabilities:")
            for vuln in result.vulnerabilities:
                print(f"  [{vuln.severity.upper()}] {vuln.package} {vuln.version}")
                if vuln.cve_id:
                    print(f"    CVE: {vuln.cve_id}")
                print(f"    Description: {vuln.description[:100]}...")
                if vuln.fixed_in:
                    print(f"    Fixed in: {vuln.fixed_in}")
                if vuln.cvss_score:
                    print(f"    CVSS Score: {vuln.cvss_score}")
                if vuln.references:
                    print(f"    References: {vuln.references[0]}")
                print()
        else:
            print("✅ No vulnerabilities found!")
    except Exception as e:
        print(f"⚠️  Scan error: {e}")
        print("   This may be due to:")
        print("   - Network connectivity issues")
        print("   - Missing pyproject.toml")
        print("   - OSV API rate limiting")
    print()
    
    # Demo 2: Explain OSV integration
    print("📝 Demo 2: OSV.dev Integration")
    print("-" * 70)
    print("Ranex uses OSV.dev (Open Source Vulnerabilities) database:")
    print("  • 50,000+ real CVEs from multiple sources")
    print("  • Supports Python, npm, Go, Rust, and more")
    print("  • Real-time vulnerability data")
    print("  • Fixed version information")
    print("  • CVSS scores and severity ratings")
    print()
    print("Benefits:")
    print("  • More comprehensive than static databases")
    print("  • Always up-to-date vulnerability information")
    print("  • Supports multiple package ecosystems")
    print("  • Free and open source")
    print()
    
    # Demo 3: Offline mode
    print("📝 Demo 3: Offline Mode")
    print("-" * 70)
    print("The scanner supports offline mode for:")
    print("  • CI/CD environments without internet access")
    print("  • Air-gapped systems")
    print("  • Rate limit avoidance")
    print()
    print("To use offline mode:")
    print("  scanner = DependencyScannerOSV.new_offline()")
    print()
    
    # Demo 4: Best practices
    print("📝 Demo 4: Best Practices")
    print("-" * 70)
    print("1. Run dependency scans regularly:")
    print("   • Before each release")
    print("   • Weekly in CI/CD pipeline")
    print("   • After adding new dependencies")
    print()
    print("2. Act on vulnerabilities:")
    print("   • Update to fixed versions when available")
    print("   • Review critical/high severity issues immediately")
    print("   • Document exceptions for low-severity issues")
    print()
    print("3. Integrate with CI/CD:")
    print("   • Fail builds on critical vulnerabilities")
    print("   • Warn on high/medium severity")
    print("   • Generate reports for review")
    print()
    
    print("=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)
    print()
    print("Key Takeaways:")
    print("  • Dependency scanning prevents supply chain attacks")
    print("  • OSV.dev provides comprehensive vulnerability data")
    print("  • Regular scanning is essential for security")
    print("  • Offline mode supports restricted environments")
    print()
    print("Next Steps:")
    print("  • Try examples/unified_security_demo.py for comprehensive scanning")
    print("  • Integrate into CI/CD pipeline")
    print("  • Set up automated vulnerability alerts")


if __name__ == "__main__":
    demo_dependency_scanning()

