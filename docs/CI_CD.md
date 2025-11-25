# CI/CD Pipeline - Pre-Release

This document describes the CI/CD pipeline configuration for Ranex Framework Pre-Release.

## Overview

The Pre-Release CI/CD focuses on **quality assurance** and **validation** rather than deployment. The pipeline ensures code quality, security, and build correctness before distribution.

## Workflows

### 1. CI Pipeline (`.github/workflows/ci.yml`)

**Purpose:** Continuous Integration - validates code on every push/PR

**Triggers:**
- Push to `main`, `develop`, or `pre-release/**` branches
- Pull requests to `main` or `develop`
- Manual dispatch

**Jobs:**

#### Rust Build & Test
- ✅ Compiles Rust code (`cargo check`)
- ✅ Runs Clippy linter (`cargo clippy`)
- ✅ Runs Rust unit tests (`cargo test`)
- ✅ Builds release library (`cargo build --release`)

#### Python Lint & Format
- ✅ Checks code formatting (Black)
- ✅ Runs Ruff linter
- ✅ Type checking (mypy)

#### Python Tests
- ✅ Builds `ranex_core` wheel
- ✅ Installs dependencies
- ✅ Runs pytest tests
- ✅ Runs example scripts as integration tests

#### Security Scan
- ✅ Runs `ranex scan` command
- ✅ Checks for hardcoded secrets (TruffleHog)

#### Build Verification
- ✅ Builds wheel file
- ✅ Verifies wheel exists and installs correctly
- ✅ Verifies CLI works

#### Documentation Check
- ✅ Checks for broken links
- ✅ Verifies security documentation exists

---

### 2. Security Pipeline (`.github/workflows/security.yml`)

**Purpose:** Security-focused validation and monitoring

**Triggers:**
- Push to `main`, `develop`, or `pre-release/**` branches
- Pull requests to `main` or `develop`
- Weekly schedule (Monday 9 AM UTC)
- Manual dispatch

**Jobs:**

#### Dependency Vulnerability Scan
- ✅ Scans Python dependencies (safety)
- ✅ Scans Rust dependencies (cargo-audit)
- ✅ Runs `ranex scan` for dependency validation

#### Code Security Scan
- ✅ Scans Python code for security issues
- ✅ Uses UnifiedSecurityScanner

#### SBOM Generation
- ✅ Generates Software Bill of Materials (Python)
- ✅ Generates Software Bill of Materials (Rust)
- ✅ Uploads SBOM artifacts

#### Security Policy Check
- ✅ Verifies security documentation exists
- ✅ Verifies Dependabot configuration

---

### 3. Release Check (`.github/workflows/release-check.yml`)

**Purpose:** Pre-release validation checklist

**Triggers:**
- Manual dispatch (with version input)
- Tag push (`v*`)

**Jobs:**

#### Pre-Release Checklist
- ✅ Version consistency check (pyproject.toml, Cargo.toml)
- ✅ Required files verification
- ✅ Wheel build and installation test
- ✅ Smoke tests (CLI, imports)
- ✅ Documentation link checks
- ✅ Generates release checklist summary

---

## CI/CD Strategy for Pre-Release

### What We DO

✅ **Quality Assurance**
- Code linting and formatting
- Unit and integration tests
- Build verification
- Security scanning

✅ **Validation**
- Dependency checks
- Security policy compliance
- Documentation completeness
- Version consistency

✅ **Monitoring**
- Weekly security scans
- Dependency vulnerability monitoring
- SBOM generation

### What We DON'T Do (Pre-Release)

❌ **Deployment**
- No automatic releases
- No package publishing
- No deployment to production

❌ **Advanced Features**
- No performance benchmarking (planned for v0.1)
- No cross-platform builds (Linux only for pre-release)
- No code coverage reporting (planned for v0.1)

---

## Running CI Locally

### Pre-commit Checks

```bash
# Rust checks
cd ..
cargo check --lib
cargo clippy --lib -- -D warnings
cargo test --lib

# Python checks
black --check ranex/ app/
ruff check ranex/ app/
mypy ranex/ --ignore-missing-imports

# Build check
maturin build --release --out Pre-Release-v0.1/wheels
pip install wheels/ranex_core-0.0.1-*.whl
python3 -c "import ranex_core; print('✅ Build works')"

# Security scan
ranex scan
```

### Using act (GitHub Actions locally)

```bash
# Install act: https://github.com/nektos/act
act -j rust
act -j python-test
act -j security
```

---

## Workflow Status Badges

Add these to your README.md:

```markdown
![CI](https://github.com/your-org/ranex/workflows/CI%20-%20Pre-Release/badge.svg)
![Security](https://github.com/your-org/ranex/workflows/Security%20-%20Pre-Release/badge.svg)
```

---

## Future Enhancements (v0.1+)

### Planned Additions

- [ ] **Performance Benchmarks**
  - Benchmark critical paths
  - Performance regression detection

- [ ] **Code Coverage**
  - Coverage reporting
  - Coverage thresholds

- [ ] **Cross-Platform Builds**
  - Windows builds
  - macOS builds
  - Multiple Python versions

- [ ] **Release Automation**
  - Automated wheel building
  - GitHub Releases creation
  - PyPI publishing (optional)

- [ ] **Advanced Security**
  - Fuzzing
  - Penetration testing
  - Dependency update automation

---

## Troubleshooting

### CI Failures

**Rust build fails:**
- Check Cargo.toml syntax
- Verify all dependencies are available
- Check for breaking changes in dependencies

**Python tests fail:**
- Verify wheel is built correctly
- Check PYTHONPATH is set
- Verify dependencies are installed

**Security scan fails:**
- Review security findings
- Update dependencies if needed
- Check for false positives

### Manual Workflow Triggers

To manually trigger workflows:

1. Go to GitHub Actions tab
2. Select workflow
3. Click "Run workflow"
4. Select branch and options
5. Click "Run workflow"

---

## Best Practices

1. **Run CI Locally First**
   - Test changes before pushing
   - Fix linting issues locally
   - Verify tests pass

2. **Small, Focused PRs**
   - Easier to review
   - Faster CI runs
   - Clearer change history

3. **Monitor Security Scans**
   - Review weekly security reports
   - Address vulnerabilities promptly
   - Update dependencies regularly

4. **Keep CI Fast**
   - Use caching effectively
   - Parallelize jobs
   - Skip unnecessary checks

---

**Last Updated:** 2025-11-25  
**Maintained By:** Ranex DevOps Team

