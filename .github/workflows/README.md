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
- **Python operations:** `${{ github.workspace }}` (repo root - Pre-Release-v0.1 IS the repo root)

## Governance Compliance

All workflows follow strict governance rules:

1. ✅ **Actions Pinned by SHA** - All 42 actions use full commit SHA (prevents supply chain attacks)
2. ✅ **Concurrency Control** - All workflows cancel outdated PR builds to save costs
3. ✅ **Least Privilege** - All 12 jobs have explicit permissions (no default permissions)
4. ✅ **Defensive Shell Scripting** - All run blocks use `shell: bash` with `set -euo pipefail`
5. ✅ **No Latest Tags** - No Docker images or actions use `:latest` or dynamic tags

## Common Issues Fixed

1. ✅ **Cargo.toml not found** - Fixed by using `working-directory: ${{ github.workspace }}` for Rust operations
2. ✅ **Wheel paths incorrect** - Fixed by using `wheels/` instead of `Pre-Release-v0.1/wheels`
3. ✅ **Python imports fail** - Fixed by setting PYTHONPATH correctly
4. ✅ **Cache paths** - Fixed by using absolute paths with `${{ github.workspace }}`
5. ✅ **Working directory paths** - Fixed by removing `/Pre-Release-v0.1` suffix (repo root IS Pre-Release-v0.1)

## Testing Locally

To test workflows locally, use [act](https://github.com/nektos/act):

```bash
# Install act (user-space installation)
mkdir -p ~/.local/bin
ACT_VERSION=$(curl -s https://api.github.com/repos/nektos/act/releases/latest | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')
curl -L -o /tmp/act.tar.gz "https://github.com/nektos/act/releases/download/${ACT_VERSION}/act_Linux_x86_64.tar.gz"
tar -xzf /tmp/act.tar.gz -C ~/.local/bin act
chmod +x ~/.local/bin/act
export PATH="$HOME/.local/bin:$PATH"

# Configure act (use medium image)
mkdir -p ~/.config/act
echo "-P ubuntu-latest=catthehacker/ubuntu:act-latest" > ~/.config/act/actrc

# Test individual jobs
act -j docs
act -j python-lint
act -j security-policy
```

**Tested Jobs:** ✅ docs, ✅ python-lint, ✅ security-policy (all passed)

## Workflow Status

Check workflow status at: `https://github.com/anthonykewl20/ranex-framework/actions`

## Action SHAs

All actions are pinned by SHA for security. To update SHAs, use the provided script:

```bash
./.github/workflows/get-action-shas.sh
```

Current pinned actions:
- `actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11` (v4.1.1)
- `actions/setup-python@82c7e631bb3cdc910f68e0081d67478d79c6982d` (v5.1.0)
- `actions/cache@13aacd865c20de90d75de3b17ebe84f7a17d57d2` (v4.0.0)
- `actions/upload-artifact@c7d193f32edcb7bfad88892161225aeda64e9392` (v4.0.0)
- `dtolnay/rust-toolchain@0b1efabc08b657293548b77fb76cc02d26091c7e` (stable)
- `trufflesecurity/trufflehog@35a5bf210f44d70a149b39d4db254abc7580cf6d` (main)

---

**Last Updated:** 2025-01-27  
**Status:** ✅ Production Ready - All governance rules enforced

