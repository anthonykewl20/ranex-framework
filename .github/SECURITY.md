# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.0.1   | :white_check_mark: |
| < 0.0.1 | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability, please follow these steps:

### 1. **Do NOT** create a public GitHub issue

Security vulnerabilities should be reported privately to prevent exploitation.

### 2. Report via GitHub Security Advisory

1. Go to the [Security](https://github.com/your-org/ranex/security) tab
2. Click "Report a vulnerability"
3. Fill out the security advisory form
4. Provide detailed information about the vulnerability

### 3. What to Include

Please include the following information:

- **Description:** Clear description of the vulnerability
- **Impact:** Potential impact and severity
- **Steps to Reproduce:** Detailed steps to reproduce
- **Affected Versions:** Which versions are affected
- **Suggested Fix:** If you have a suggested fix (optional)

### 4. Response Timeline

- **Initial Response:** Within 48 hours
- **Triage:** Within 7 days
- **Fix:** 
  - Critical: Within 7 days
  - High: Within 30 days
  - Medium: Next release cycle
  - Low: Next release cycle

### 5. Disclosure Policy

- We will acknowledge receipt of your report within 48 hours
- We will keep you informed of the progress
- We will notify you when the vulnerability is fixed
- We will credit you in the security advisory (if you wish)
- We will coordinate public disclosure with you

## Security Best Practices

### For Users

1. **Keep Dependencies Updated**
   - Regularly update Ranex and its dependencies
   - Monitor security advisories
   - Use Dependabot alerts

2. **Secure Configuration**
   - Use environment variables for secrets
   - Enable log sanitization
   - Configure proper authentication
   - Use HTTPS in production

3. **Monitor Security**
   - Enable GitHub Security features
   - Review Dependabot alerts
   - Monitor security advisories
   - Review security audit reports

### For Developers

1. **Secure Development**
   - Follow secure coding practices
   - Review security documentation
   - Run security scans regularly
   - Keep dependencies updated

2. **Security Testing**
   - Run `ranex scan` regularly
   - Review security audit reports
   - Test security fixes thoroughly
   - Follow security roadmap

## Security Features

Ranex Framework includes several security features:

- ✅ **Static Analysis (SAST):** Detects vulnerabilities in code
- ✅ **Dependency Scanning:** OSV database integration
- ✅ **Import Validation:** Prevents typosquatting
- ✅ **Architecture Enforcement:** Prevents structural vulnerabilities
- ✅ **Log Sanitization:** Prevents sensitive data leakage
- ✅ **Contract System:** Enforces business logic

See [Security Documentation](docs/security/) for more details.

## Security Documentation

- [Threat Model](docs/security/THREAT_MODEL.md)
- [Security Audit Report](docs/security/SECURITY_AUDIT.md)
- [SBOM](docs/security/SBOM.md)
- [Security Best Practices](docs/security/BEST_PRACTICES.md) (planned)

## Security Contact

- **GitHub Security Advisory:** [Report here](https://github.com/your-org/ranex/security/advisories/new)
- **Email:** security@ranex.dev (to be established)

## Security Acknowledgments

We thank security researchers who responsibly disclose vulnerabilities. Contributors will be credited in security advisories (with permission).

---

**Last Updated:** 2025-11-25  
**Policy Version:** 1.0

