# GitHub Actions Workflows - Pre-Release

This directory contains CI/CD workflows for Ranex Framework Pre-Release.

## Workflows

### 1. `ci.yml` - Continuous Integration
**Triggers:** Push, Pull Request, Manual

**Jobs:**
- **Rust Build & Test** - Compiles and tests Rust code
- **Python Lint & Format** - Lints and checks Python code formatting
- **Python Tests** - Runs Python tests and example scripts
- **Security Scan** - Scans for security issues and secrets
- **Build Verification** - Verifies wheel builds and installs correctly
- **Documentation Check** - Verifies documentation exists
- **CI Summary** - Summarizes all job results

### 2. `security.yml` - Security Pipeline
**Triggers:** Push, Pull Request, Weekly Schedule, Manual

**Jobs:**
- **Dependency Vulnerability Scan** - Scans Python and Rust dependencies
- **Code Security Scan** - Scans code for security issues
- **SBOM Generation** - Generates Software Bill of Materials
- **Security Policy Check** - Verifies security documentation

### 3. `release-check.yml` - Pre-Release Validation
**Triggers:** Manual Dispatch, Tag Push

**Checks:**
- Version consistency
- Required files verification
- Wheel build and installation
- Smoke tests
- Documentation links

## Path Configuration

All workflows use `working-directory` to ensure correct paths:

- **Rust operations:** `${{ github.workspace }}` (repo root where Cargo.toml is)
- **Python operations:** `${{ github.workspace }}/Pre-Release-v0.1` (Pre-Release directory)

## Common Issues Fixed

1. ✅ **Cargo.toml not found** - Fixed by using `working-directory: ${{ github.workspace }}` for Rust operations
2. ✅ **Wheel paths incorrect** - Fixed by using relative paths from Pre-Release-v0.1
3. ✅ **Python imports fail** - Fixed by setting PYTHONPATH correctly
4. ✅ **Cache paths** - Fixed by using absolute paths with `${{ github.workspace }}`

## Testing Locally

To test workflows locally, use [act](https://github.com/nektos/act):

```bash
# Install act
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Run CI workflow
act -j rust
act -j python-test
act -j security
```

## Workflow Status

Check workflow status at: `https://github.com/your-org/ranex/actions`

---

**Last Updated:** 2025-11-25

