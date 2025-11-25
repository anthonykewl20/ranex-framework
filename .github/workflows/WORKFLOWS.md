# GitHub Actions Workflows - Technical Documentation

**Documentation Status:** Implementation-Based  
**Last Audited:** 2025-01-27  
**Audit Method:** Direct code inspection of `.github/workflows/*.yml`

---

## Table of Contents

1. [CI Workflow (`ci.yml`)](#ci-workflow-ciyml)
2. [Security Workflow (`security.yml`)](#security-workflow-securityyml)
3. [Release Check Workflow (`release-check.yml`)](#release-check-workflow-release-checkyml)
4. [Action SHA Update Script (`get-action-shas.sh`)](#action-sha-update-script-get-action-shassh)

---

## CI Workflow (`ci.yml`)

### Component Overview

Executes a multi-job continuous integration pipeline that compiles Rust code, lints Python code, runs Python tests, performs security scanning, verifies wheel builds, checks documentation, and aggregates results.

### Workflow Triggers

**Input Events:**
- **Push:** Triggers on pushes to branches matching `main`, `develop`, or `pre-release/**` patterns
- **Pull Request:** Triggers on PRs targeting `main` or `develop` branches
- **Manual Dispatch:** `workflow_dispatch` event (no input parameters)

**Concurrency Control:**
- **Group Key:** `${{ github.workflow }}-${{ github.ref }}`
- **Cancel Behavior:** `cancel-in-progress: true` **only** when `github.event_name == 'pull_request'`
- **Effect:** On PRs, newer commits cancel older runs. On pushes, runs proceed concurrently.

**Environment Variables:**
- `RUST_BACKTRACE: 1` (enables full Rust backtraces on panic)
- `PYTHON_VERSION: '3.12'` (hardcoded Python version)

### Job Specifications

#### Job: `rust`

**Purpose:** Compiles Rust library, runs clippy lints, executes unit tests, and builds release artifacts.

**Permissions:**
- `contents: read`
- `checks: write`

**Execution Flow:**

1. **Checkout** (`actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11`)
   - No parameters specified (defaults to full checkout)

2. **Cargo.toml Detection** (lines 31-41)
   - **Shell:** `bash` with `set -euo pipefail`
   - **Logic:** Checks for `Cargo.toml` in current directory OR `../Cargo.toml` (parent directory)
   - **Output:** Sets `steps.check_cargo.outputs.cargo_exists` to `'true'` or `'false'`
   - **Edge Case:** If neither file exists, outputs warning but sets `cargo_exists=false` (does not fail)

3. **Rust Installation** (conditional on `cargo_exists == 'true'`)
   - **Action:** `dtolnay/rust-toolchain@0b1efabc08b657293548b77fb76cc02d26091c7e`
   - **Toolchain:** `stable` (hardcoded)

4. **Cargo Cache** (conditional on `cargo_exists == 'true'`)
   - **Action:** `actions/cache@0057852bfaa89a56745cba8c7296529d2fc39830`
   - **Cache Paths:**
     - `~/.cargo/bin/`
     - `~/.cargo/registry/index/`
     - `~/.cargo/registry/cache/`
     - `~/.cargo/git/db/`
     - `${{ github.workspace }}/target/`
   - **Cache Key:** `${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}`
   - **Restore Keys:** `${{ runner.os }}-cargo-` (fallback to any OS-specific cargo cache)

5. **Rust Check** (lines 63-70)
   - **Working Directory:** `${{ github.workspace }}`
   - **Commands:** 
     - `cargo check --lib` (type checking only, no tests)
     - `cargo clippy --lib -- -D warnings` (lints with warnings treated as errors)
   - **Failure Mode:** Job fails if clippy warnings exist

6. **Rust Tests** (lines 72-78)
   - **Command:** `cargo test --lib --no-fail-fast`
   - **Behavior:** Runs all tests even if one fails (`--no-fail-fast`)

7. **Rust Build** (lines 80-86)
   - **Command:** `cargo build --release --lib`
   - **Artifact:** Built to `target/release/` (not explicitly uploaded)

8. **Skip Message** (lines 88-93, conditional on `cargo_exists == 'false'`)
   - **Output:** Prints success message indicating Python-only project

**Implementation Notes:**
- Rust job **does not fail** if `Cargo.toml` is missing; it gracefully skips all Rust steps
- `working-directory` is explicitly set to `${{ github.workspace }}` for all Rust commands
- Cache key depends on `Cargo.lock` hash; if lockfile changes, cache is invalidated
- Clippy warnings are treated as errors (`-D warnings`), causing job failure

**Discrepancy Alerts:**
- Line 36: Checks for `../Cargo.toml` but all subsequent commands use `${{ github.workspace }}` as working directory. If `Cargo.toml` exists in parent, Rust commands may fail because they run in workspace root, not parent directory.
- Line 86: Release build artifact is not uploaded or verified; build may succeed but produce no usable output.

---

#### Job: `python-lint`

**Purpose:** Validates Python code formatting (Black), runs Ruff linter, and performs type checking (mypy).

**Permissions:**
- `contents: read` (no write permissions)

**Execution Flow:**

1. **Checkout** (same as rust job)

2. **Python Setup** (`actions/setup-python@82c7e631bb3cdc910f68e0081d67478d79c6982d`)
   - **Version:** `${{ env.PYTHON_VERSION }}` (resolves to `'3.12'`)
   - **Cache:** Disabled (comment indicates explicit `actions/cache` used instead)

3. **Pip Cache** (`actions/cache@0057852bfaa89a56745cba8c7296529d2fc39830`)
   - **Path:** `~/.cache/pip`
   - **Key:** `${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt', '**/pyproject.toml', '**/setup.py') }}`
   - **Continue on Error:** `true` (cache failure does not fail job)

4. **Install Linting Tools** (lines 120-124)
   - **Packages:** `ruff`, `black`, `mypy`
   - **Installation:** `pip install --no-cache-dir` (bypasses pip cache, forces fresh download)

5. **Black Format Check** (lines 126-131)
   - **Command:** `black --check --diff ranex/ app/ examples/*.py`
   - **Failure Handling:** `|| true` (job does NOT fail on formatting violations)
   - **Output:** Prints diff if files are not formatted

6. **Ruff Lint** (lines 133-138)
   - **Command:** `ruff check ranex/ app/ examples/*.py`
   - **Failure Handling:** `|| true` (job does NOT fail on lint errors)

7. **Mypy Type Check** (lines 140-145)
   - **Command:** `mypy ranex/ --ignore-missing-imports`
   - **Scope:** Only checks `ranex/` directory (not `app/` or `examples/`)
   - **Failure Handling:** `|| true` (job does NOT fail on type errors)

**Implementation Notes:**
- **Critical:** All linting steps use `|| true`, meaning the job **always succeeds** regardless of linting failures
- Black and Ruff scan `ranex/`, `app/`, and `examples/*.py` (wildcard expansion)
- Mypy only scans `ranex/` directory
- Pip cache uses `continue-on-error: true`, so cache misses don't fail the job

**Discrepancy Alerts:**
- **Line 131, 138, 145:** All linting steps use `|| true`, making this a "soft check" that never fails the CI pipeline. The job name suggests it enforces linting, but it only reports violations.
- **Line 145:** `--ignore-missing-imports` flag means mypy will not report errors for missing imports, potentially hiding real type errors.

---

#### Job: `python-test`

**Purpose:** Builds Python wheel from Rust code (if Cargo.toml exists), installs dependencies, runs pytest tests, and executes example scripts as integration tests.

**Dependencies:**
- **Needs:** `rust` job (line 151) - waits for Rust job to complete, but does not use its artifacts

**Permissions:**
- `contents: read`

**Execution Flow:**

1. **Checkout** (same as previous jobs)

2. **Python Setup** (same as python-lint)

3. **Cargo.toml Detection** (lines 164-173)
   - Same logic as rust job (checks current dir or parent)

4. **Rust Toolchain** (conditional on `cargo_exists == 'true'`)
   - Same action and toolchain as rust job

5. **Cargo Cache** (conditional on `cargo_exists == 'true'`)
   - Same cache configuration as rust job

6. **Pip Cache** (same as python-lint)

7. **Build Wheel** (lines 204-214)
   - **Condition:** Checks for `Cargo.toml` again (redundant check)
   - **If Cargo.toml exists:**
     - Installs `maturin` (no version pinning)
     - Runs `maturin build --release --out wheels`
   - **If Cargo.toml missing:** Prints warning, continues (does not fail)

8. **Install Dependencies** (lines 216-233)
   - **Wheel Install:** `pip install --no-cache-dir wheels/ranex_core-0.0.1-*.whl`
     - **Failure Handling:** `|| echo "⚠️ Wheel not found, skipping"` (does not fail)
     - **Wildcard Pattern:** Matches any wheel with version `0.0.1-*` (e.g., `0.0.1-cp312-cp312-linux_x86_64.whl`)
   - **Test Dependencies:** `pytest`, `pytest-asyncio`, `pytest-cov`
   - **Package Installation:**
     - **If Cargo.toml exists:** `pip install --no-cache-dir -e .` (editable install)
     - **If Cargo.toml missing:** Installs `typer`, `rich`, `PyYAML` directly, sets `PYTHONPATH=$PWD`
   - **App Requirements:** `pip install --no-cache-dir -r app/requirements.txt || true` (does not fail if file missing)

9. **Run Python Tests** (lines 235-241)
   - **Command:** `pytest tests/ -v --tb=short`
   - **PYTHONPATH:** Set to `$PWD` (workspace root)
   - **Failure Handling:** `|| echo "No tests found"` (does not fail if `tests/` directory missing)

10. **Run Example Scripts** (lines 243-253)
    - **Working Directory:** `examples/`
    - **Logic:** Iterates over all `*.py` files in `examples/`
    - **Execution:** `timeout 10 python3 "$script" > /dev/null 2>&1`
      - **Timeout:** 10 seconds per script
      - **Output:** Suppressed (redirected to `/dev/null`)
    - **Success Criteria:** Exit code 0 = success, non-zero = warning (does not fail job)

**Implementation Notes:**
- Job depends on `rust` job but does not use Rust build artifacts; it rebuilds the wheel independently
- Wheel version is hardcoded to `0.0.1-*` pattern; will fail if version changes
- Example scripts run with 10-second timeout; scripts requiring server startup may timeout
- All failure modes use `|| true` or `|| echo`, making this job effectively non-blocking

**Discrepancy Alerts:**
- **Line 221:** Hardcoded version `0.0.1-*` in wheel filename. If `pyproject.toml` version changes, this step will fail silently (due to `|| echo`).
- **Line 252:** Example scripts that require external services (databases, APIs) will timeout after 10 seconds and be marked as warnings, not failures.
- **Line 241:** If `tests/` directory is missing, job succeeds with "No tests found" message, potentially hiding missing test suite.

---

#### Job: `security`

**Purpose:** Builds ranex package, runs `ranex scan` command, and performs TruffleHog secret scanning on git diff.

**Permissions:**
- `contents: read`
- `security-events: write` (allows uploading security findings to GitHub Security tab)

**Execution Flow:**

1. **Checkout** (same as previous jobs)

2. **Python Setup** (`continue-on-error: true`)
   - Python setup failure does not stop the job

3. **Rust Toolchain** (unconditional, no Cargo.toml check)
   - Installs Rust even if project is Python-only

4. **Cargo Cache** (unconditional)
   - Attempts to cache Cargo even if Cargo.toml doesn't exist

5. **Build ranex_core** (lines 290-300)
   - Same logic as python-test wheel build
   - Prints warning if Cargo.toml missing, continues

6. **Install ranex** (lines 302-314)
   - Same installation logic as python-test job
   - Sets `PYTHONPATH` if Cargo.toml missing

7. **Run ranex scan** (lines 316-322)
   - **Command:** `ranex scan`
   - **PYTHONPATH:** Set to workspace root
   - **Failure Handling:** `|| echo "Scan completed with warnings"` (does not fail job)

8. **Check Commits Differ** (lines 324-339)
   - **Purpose:** Determines if TruffleHog should run (only scans diffs, not entire history)
   - **Logic:**
     - Gets `BASE_REF` from `github.event.repository.default_branch` (typically `main`)
     - Gets `HEAD_REF` as `HEAD` (current commit)
     - Compares SHA hashes
   - **Output:** Sets `steps.check_commits.outputs.commits_differ` to `'true'` or `'false'`
   - **Edge Cases:**
     - If `git rev-parse` fails, sets empty string and `commits_differ=false`
     - If BASE == HEAD (e.g., push to main with no new commits), skips TruffleHog

9. **TruffleHog Scan** (lines 341-347, conditional on `commits_differ == 'true'`)
   - **Action:** `trufflesecurity/trufflehog@35a5bf210f44d70a149b39d4db254abc7580cf6d`
   - **Parameters:**
     - `path: .` (scans entire repository)
     - `base: ${{ github.event.repository.default_branch }}`
     - `head: HEAD`
   - **Behavior:** Scans git diff between base and head for hardcoded secrets

10. **Skip Message** (lines 349-356, conditional on `commits_differ != 'true'`)
    - Prints informational message explaining why scan was skipped

**Implementation Notes:**
- Rust toolchain and Cargo cache are installed unconditionally, even for Python-only projects (wasteful but non-blocking)
- `ranex scan` command failure does not fail the job (soft check)
- TruffleHog only runs when BASE != HEAD, meaning pushes to main with no new commits skip secret scanning
- Git rev-parse failures are silently handled (empty string comparison)

**Discrepancy Alerts:**
- **Line 322:** `ranex scan` failures are masked with `|| echo`, meaning security scan failures do not block CI.
- **Line 331-332:** `git rev-parse` failures are caught with `2>/dev/null || echo ""`, but empty string comparison `[ -n "$BASE_SHA" ]` may still evaluate incorrectly if git command fails in unexpected ways.
- **Line 272-275:** Rust toolchain installation is unconditional, but should be conditional on Cargo.toml existence (matches pattern from other jobs but wastes resources).

---

#### Job: `build-verify`

**Purpose:** Verifies that wheel builds successfully, can be installed, and ranex_core module can be imported. Also verifies CLI is accessible.

**Permissions:**
- `contents: read`

**Execution Flow:**

1. **Checkout** (same as previous jobs)

2. **Python Setup** (`continue-on-error: true`)

3. **Cargo.toml Detection** (lines 374-383)
   - Same detection logic as other jobs

4. **Rust Toolchain** (conditional on `cargo_exists == 'true'`)

5. **Cargo Cache** (conditional on `cargo_exists == 'true'`)

6. **Pip Cache** (`continue-on-error: true`)

7. **Install maturin** (lines 414-419, conditional on `cargo_exists == 'true'`)
   - **Note:** Maturin is installed twice if Cargo.toml exists (here and in Build wheel step)

8. **Build Wheel** (lines 421-431)
   - Same logic as python-test job
   - Prints warning if Cargo.toml missing, continues

9. **Verify Wheel Exists** (lines 433-439)
   - **Command:** `ls -lh wheels/*.whl` (lists all wheels)
   - **Verification:** `test -f wheels/ranex_core-0.0.1-*.whl || exit 1`
   - **Failure Mode:** Job **fails** if wheel pattern does not match (hard failure, no `|| true`)

10. **Install from Wheel** (lines 441-447)
    - **Install:** `pip install --no-cache-dir wheels/ranex_core-0.0.1-*.whl`
    - **Verification:** `python3 -c "import ranex_core; print('✅ ranex_core imported successfully')"`
    - **Failure Mode:** Job **fails** if import fails (hard failure)

11. **Verify CLI Works** (lines 449-471)
    - **Installation:** Same logic as python-test (editable install or direct dependencies)
    - **CLI Detection:**
      - **Method 1:** `command -v ranex` (checks if `ranex` is in PATH)
        - If found: `ranex --help || exit 1` (hard failure)
      - **Method 2:** `python3 -m ranex.cli --help` (module execution)
        - If succeeds: prints success message, continues
      - **Method 3:** Fallback to module import check
        - `python3 -c "import ranex; print('✅ ranex module importable')" || exit 1` (hard failure)

**Implementation Notes:**
- This is the **only job** that hard-fails on wheel build/install issues (no `|| true` or `|| echo`)
- Wheel version is hardcoded to `0.0.1-*` pattern (same issue as python-test)
- CLI verification tries three methods, but only Method 1 and Method 3 are hard failures
- Maturin is installed redundantly if Cargo.toml exists

**Discrepancy Alerts:**
- **Line 439:** Hardcoded version `0.0.1-*` in wheel filename pattern. If version changes in `pyproject.toml`, this step will fail even if wheel builds successfully with new version.
- **Line 427:** Maturin installation happens in both "Install maturin" step (line 419) and "Build wheel" step (line 427) if Cargo.toml exists, causing redundant pip install.

---

#### Job: `docs`

**Purpose:** Performs basic documentation checks: searches for markdown links and verifies security documentation files exist.

**Permissions:**
- `contents: read`

**Execution Flow:**

1. **Checkout** (same as previous jobs)

2. **Check for Broken Links** (lines 483-489)
   - **Command:** `find docs/ -name "*.md" -exec grep -l "\.md" {} \; | head -5`
   - **Logic:** Finds markdown files in `docs/` that contain the string `".md"` (literal dot-M-D)
   - **Output:** Prints first 5 matching files OR "Link check completed" if no matches
   - **Failure Handling:** `|| echo "Link check completed"` (does not fail)
   - **Limitation:** Only checks if files contain `.md` string, does not verify links are valid

3. **Verify Security Docs Exist** (lines 491-500)
   - **Required Files:**
     - `docs/security/THREAT_MODEL.md`
     - `docs/security/SECURITY_AUDIT.md`
     - `docs/security/SBOM.md`
     - `.github/SECURITY.md`
   - **Verification:** `test -f <file> || exit 1` (hard failure if any file missing)

**Implementation Notes:**
- Link check is a placeholder implementation; it only finds files containing `.md` string, not actual broken links
- Security doc check is the only hard failure in this job
- Link check uses `head -5`, limiting output to first 5 files

**Discrepancy Alerts:**
- **Line 489:** "Check for broken links" step does not actually validate links; it only finds markdown files containing the literal string `.md`. This is misleadingly named.
- **Line 488:** `grep -l "\.md"` searches for literal dot-M-D, which will match any markdown file that references another markdown file, but does not verify the referenced file exists.

---

#### Job: `ci-summary`

**Purpose:** Aggregates results from all previous jobs and determines overall CI pass/fail status.

**Dependencies:**
- **Needs:** `[rust, python-lint, python-test, security, build-verify, docs]` (line 506)
- **Condition:** `if: always()` (runs even if other jobs fail)

**Permissions:**
- `contents: read`

**Execution Flow:**

1. **Check Job Status** (lines 511-522)
   - **Logic:** Checks `needs.<job>.result` for three jobs:
     - `needs.rust.result`
     - `needs.python-test.result`
     - `needs.build-verify.result`
   - **Success Criteria:** All three must equal `"success"`
   - **Failure Mode:** Exits with code 1 if any of the three jobs failed
   - **Note:** Does NOT check `python-lint`, `security`, or `docs` job results

**Implementation Notes:**
- Only checks 3 out of 6 dependency jobs (`rust`, `python-test`, `build-verify`)
- Ignores `python-lint`, `security`, and `docs` job failures
- Uses `always()` condition, so summary always runs regardless of dependency job status

**Discrepancy Alerts:**
- **Line 515-517:** Summary job only checks 3 out of 6 jobs. If `python-lint`, `security`, or `docs` jobs fail, the summary will still report success as long as the other 3 pass. This contradicts the `needs:` declaration which lists all 6 jobs.

---

## Security Workflow (`security.yml`)

### Component Overview

Executes security-focused scanning jobs: dependency vulnerability scanning (Python/Rust), code security scanning using ranex_core, SBOM generation, and security policy verification.

### Workflow Triggers

**Input Events:**
- **Push:** Triggers on pushes to `main`, `develop`, or `pre-release/**` branches
- **Pull Request:** Triggers on PRs targeting `main` or `develop`
- **Schedule:** Weekly on Mondays at 9:00 AM UTC (`cron: '0 9 * * 1'`)
- **Manual Dispatch:** `workflow_dispatch` event (no input parameters)

**Concurrency Control:**
- **Group Key:** `${{ github.workflow }}-${{ github.ref }}`
- **Cancel Behavior:** `cancel-in-progress: true` **only** when `github.event_name == 'pull_request'`

### Job Specifications

#### Job: `dependency-scan`

**Purpose:** Scans Python and Rust dependencies for known vulnerabilities using `safety` (Python) and `cargo-audit` (Rust).

**Permissions:**
- `contents: read`
- `security-events: write`

**Execution Flow:**

1. **Checkout** (same action SHA as ci.yml)

2. **Python Setup** (Python 3.12)

3. **Pip Cache** (`continue-on-error: true`)

4. **Rust Toolchain** (unconditional installation)

5. **Cargo Cache** (unconditional)

6. **Build ranex_core** (lines 63-73)
   - Same wheel build logic as ci.yml jobs
   - Prints warning if Cargo.toml missing, continues

7. **Install Dependencies** (lines 75-88)
   - Same installation logic as ci.yml python-test job
   - Sets PYTHONPATH if Cargo.toml missing

8. **Run Dependency Scan** (lines 90-96)
   - **Command:** `ranex scan`
   - **Failure Handling:** `|| echo "Scan completed"` (does not fail job)

9. **Check Python Vulnerabilities** (lines 98-104)
   - **Tool:** `safety` (installed via pip, no version pinning)
   - **Command:** `safety check --file pyproject.toml`
   - **Failure Handling:** `|| echo "⚠️ Some vulnerabilities found"` (does not fail job)
   - **Input:** Reads from `pyproject.toml` (not `requirements.txt`)

10. **Check Rust Vulnerabilities** (lines 106-112)
    - **Tool:** `cargo-audit` (installed via `cargo install`, no version pinning)
    - **Command:** `cargo audit`
    - **Installation:** `cargo install cargo-audit || true` (does not fail if install fails)
    - **Failure Handling:** `|| echo "⚠️ Some vulnerabilities found"` (does not fail job)

**Implementation Notes:**
- All vulnerability checks use `|| echo`, meaning the job **never fails** on vulnerabilities
- `safety` tool reads from `pyproject.toml`, not `requirements.txt` (may miss dependencies listed elsewhere)
- `cargo-audit` installation failure is ignored (`|| true`), so audit may silently fail
- Rust toolchain installed unconditionally even if project is Python-only

**Discrepancy Alerts:**
- **Line 96, 104, 112:** All vulnerability scanning steps use `|| echo`, making this a reporting-only job that never fails CI, even when critical vulnerabilities are found.
- **Line 111:** `cargo install cargo-audit || true` means if cargo-audit installation fails, the audit step will also fail silently (cargo-audit command won't exist).

---

#### Job: `code-scan`

**Purpose:** Scans Python source files for security issues using `ranex_core.UnifiedSecurityScanner`.

**Permissions:**
- `contents: read`
- `security-events: write`

**Execution Flow:**

1. **Checkout** (same as dependency-scan)

2. **Python Setup** (Python 3.12)

3. **Pip Cache** (`continue-on-error: true`)

4. **Rust Toolchain** (unconditional)

5. **Cargo Cache** (unconditional)

6. **Build ranex_core** (lines 157-167)
   - Same wheel build logic

7. **Install ranex** (lines 169-182)
   - Same installation logic

8. **Run Security Scan on Codebase** (lines 184-202)
   - **Logic:** Uses `find` to locate all `*.py` files in `ranex/`, `app/`, `examples/` directories
   - **Per-File Execution:** For each Python file, runs inline Python script:
     ```python
     from ranex_core import UnifiedSecurityScanner
     scanner = UnifiedSecurityScanner.new()
     result = scanner.scan_content(content)
     if not result.secure:
         print(f'⚠️ Security issues in {file}')
         for v in result.violations:
             print(f'  - {v.severity}: {v.message}')
     ```
   - **Failure Handling:** `|| echo "Security scan completed"` (does not fail job)
   - **Output:** Prints violations to stdout, but does not fail on violations

**Implementation Notes:**
- Scans files by executing Python inline script via `python3 -c` for each file (inefficient for large codebases)
- Violations are printed but do not cause job failure
- Scanner is instantiated fresh for each file (no shared state)

**Discrepancy Alerts:**
- **Line 202:** `|| echo "Security scan completed"` means security violations are reported but do not fail the job. The job name suggests it enforces security, but it's reporting-only.
- **Line 191:** Inline Python script execution via `find -exec` is inefficient; creates new Python process for each file.

---

#### Job: `sbom`

**Purpose:** Generates Software Bill of Materials (SBOM) in CycloneDX format for Python and Rust dependencies, then uploads as artifacts.

**Conditional Execution:**
- **Runs Only When:** `github.event_name == 'push' && github.ref == 'refs/heads/main'`
- **Effect:** Does not run on PRs, scheduled runs, or manual dispatch (only on pushes to main)

**Permissions:**
- `contents: read`
- `actions: write` (required for artifact upload)

**Execution Flow:**

1. **Checkout** (same as previous jobs)

2. **Python Setup** (Python 3.12)

3. **Pip Cache** (`continue-on-error: true`)

4. **Generate Python SBOM** (lines 230-243)
   - **Tool Installation:** Tries `cyclonedx-bom` first, falls back to `cyclonedx-py`, else prints warning
   - **Execution Methods:**
     - **Method 1:** `cyclonedx-py -o sbom-python.json -pb` (if `cyclonedx-py` command exists)
     - **Method 2:** `cyclonedx py -o sbom-python.json` (if `cyclonedx` command exists)
   - **Output:** Sets `steps.python_sbom.outputs.python_sbom` to `'true'` or `'false'`
   - **Failure Handling:** If no tool available, sets `python_sbom=false`, continues

5. **Check for Cargo.toml** (lines 245-254)
   - Same detection logic as other jobs

6. **Generate Rust SBOM** (lines 256-269, conditional on `cargo_exists == 'true'`)
   - **Tool Installation:** `cargo install cargo-cyclonedx --quiet`
     - **Failure Handling:** `|| echo "⚠️ cargo-cyclonedx installation failed"` (does not fail)
   - **Command:** `cargo cyclonedx -o sbom-rust.json`
   - **Verification:** Checks if command exists via `command -v` or `cargo cyclonedx --help`
   - **Output:** Sets `steps.rust_sbom.outputs.rust_sbom` to `'true'` or `'false'`

7. **Upload SBOM Artifacts** (lines 271-279, conditional on SBOM generation success)
   - **Action:** `actions/upload-artifact@c7d193f32edcb7bfad88892161225aeda64e9392`
   - **Artifact Name:** `sbom`
   - **Paths:** `sbom-*.json` (matches both Python and Rust SBOMs)
   - **Retention:** 90 days
   - **Continue on Error:** `true` (upload failure does not fail job)

8. **Skip Message** (lines 281-287, conditional on no SBOMs generated)
   - Prints informational message

**Implementation Notes:**
- SBOM generation is best-effort; failures are logged but do not fail the job
- Python SBOM tool has fallback logic (tries two different command names)
- Rust SBOM installation failure is ignored, so generation may silently fail
- Artifact upload uses `continue-on-error: true`, so upload failures are ignored

**Discrepancy Alerts:**
- **Line 263:** `cargo install cargo-cyclonedx --quiet || echo` means if installation fails, the subsequent `cargo cyclonedx` command will fail, but the failure is masked.
- **Line 274:** `continue-on-error: true` on artifact upload means SBOM files may be generated but not uploaded, and the job will still succeed.
- **Line 208:** Job only runs on pushes to main branch, so PRs and scheduled runs do not generate SBOMs (may be intentional for performance).

---

#### Job: `security-policy`

**Purpose:** Verifies that required security documentation files and Dependabot configuration exist.

**Permissions:**
- `contents: read`

**Execution Flow:**

1. **Checkout** (same as previous jobs)

2. **Verify Security Documentation** (lines 299-308)
   - **Required Files:**
     - `.github/SECURITY.md`
     - `docs/security/THREAT_MODEL.md`
     - `docs/security/SECURITY_AUDIT.md`
     - `docs/security/SBOM.md`
   - **Verification:** `test -f <file> || exit 1` (hard failure if any missing)

3. **Verify Dependabot Config** (lines 310-316)
   - **Required File:** `.github/dependabot.yml`
   - **Verification:** `test -f <file> || exit 1` (hard failure if missing)

**Implementation Notes:**
- This is the only job in security.yml that hard-fails on missing files
- Does not verify file content, only existence
- Same file list as ci.yml docs job

**Discrepancy Alerts:**
- **Line 304-307:** Only checks file existence, not content validity. Empty or malformed files will pass this check.

---

## Release Check Workflow (`release-check.yml`)

### Component Overview

Performs pre-release validation checks: version consistency across files, required file verification, wheel build/install verification, smoke tests, and documentation link checks.

### Workflow Triggers

**Input Events:**
- **Manual Dispatch:** `workflow_dispatch` with required `version` input (string type)
- **Tag Push:** Triggers on pushes of tags matching pattern `v*` (e.g., `v0.0.1`, `v1.2.3`)

**Concurrency Control:**
- **Group Key:** `${{ github.workflow }}-${{ github.ref }}`
- **Cancel Behavior:** `cancel-in-progress: false` (never cancels in-progress runs)

### Job Specifications

#### Job: `release-checklist`

**Purpose:** Validates release readiness by checking version consistency, required files, wheel build/install, smoke tests, and documentation.

**Permissions:**
- `contents: read` (no write permissions)

**Execution Flow:**

1. **Checkout** (same action SHA as other workflows)

2. **Python Setup** (`continue-on-error: true`, Python 3.12)

3. **Pip Cache** (`continue-on-error: true`)

4. **Rust Toolchain** (unconditional installation)

5. **Cargo Cache** (unconditional)

6. **Check Version Consistency** (lines 62-78)
   - **Version Source:** `${{ github.event.inputs.version || github.ref_name }}`
     - **Manual Dispatch:** Uses `github.event.inputs.version`
     - **Tag Push:** Uses `github.ref_name` (tag name, e.g., `v0.0.1`)
   - **Version Normalization:** `VERSION="${VERSION#v}"` (strips leading `v` if present)
   - **Checks:**
     - `grep -q "version = \"$VERSION\"" pyproject.toml || exit 1`
     - `grep -q "version = \"$VERSION\"" ../Cargo.toml || exit 1` (checks parent directory)
   - **Failure Mode:** Hard failure if version mismatch

7. **Verify Required Files** (lines 80-111)
   - **Required Files List:**
     - `README.md`
     - `LICENSE`
     - `CHANGELOG.md`
     - `pyproject.toml`
     - `docs/security/THREAT_MODEL.md`
     - `docs/security/SECURITY_AUDIT.md`
     - `docs/security/SBOM.md`
     - `.github/SECURITY.md`
     - `.github/dependabot.yml`
   - **Verification:** `test -f "$file" || exit 1` (hard failure if any missing)
   - **Wheel Check:** `ls wheels/ranex_core-*.whl` (warning if missing, does not fail)

8. **Build Wheel** (lines 113-123)
   - Same wheel build logic as other workflows
   - Prints warning if Cargo.toml missing, continues

9. **Verify Wheel Installation** (lines 125-132)
   - **Install:** `pip install --no-cache-dir wheels/ranex_core-*.whl` (wildcard pattern)
   - **Import Checks:**
     - `import ranex_core` (hard failure)
     - `from ranex_core import SchemaValidator` (soft check: `|| echo "⚠️ SchemaValidator import check skipped"`)

10. **Run Basic Smoke Tests** (lines 134-156)
    - **Installation:** Same logic as other workflows (editable install or direct dependencies)
    - **CLI Test:** `ranex --help || exit 1` (hard failure)
    - **Import Tests:**
      - `from ranex import Contract` (soft check: `|| echo "⚠️ Contract import check skipped"`)
      - `from ranex_core import StateMachine` (soft check: `|| echo "⚠️ StateMachine import check skipped"`)

11. **Check Documentation Links** (lines 158-166)
    - **Checks:** Uses `grep -q` to verify README.md contains references to:
      - `THREAT_MODEL.md`
      - `SECURITY_AUDIT.md`
      - `SBOM.md`
    - **Failure Handling:** `|| echo "⚠️ ..."` (warnings only, does not fail)

12. **Release Checklist Summary** (lines 168-181)
    - **Output:** Writes markdown to `$GITHUB_STEP_SUMMARY`
    - **Content:** Pre-formatted checklist with all items marked as `[x]` (completed)
    - **Status:** Always reports "Ready for Pre-Release" regardless of actual results

**Implementation Notes:**
- Version check uses parent directory (`../Cargo.toml`) but all other commands use workspace root (potential path issue)
- Summary always reports success, even if previous steps failed (misleading)
- Most import checks are soft (`|| echo`), only CLI test is hard failure
- Documentation link check is warning-only, does not block release

**Discrepancy Alerts:**
- **Line 76:** Checks `../Cargo.toml` (parent directory) but all other steps use `${{ github.workspace }}` as working directory. If Cargo.toml is in parent, version check may fail even if file exists.
- **Line 172-180:** Summary step always writes success message regardless of actual job status. If previous steps failed, summary will still say "Ready for Pre-Release".
- **Line 132, 153-154:** Critical import checks (`SchemaValidator`, `Contract`, `StateMachine`) use soft failure (`|| echo`), meaning missing imports do not block release.

---

## Action SHA Update Script (`get-action-shas.sh`)

### Component Overview

Bash script that queries GitHub API to fetch latest commit SHAs for GitHub Actions used in workflows, for the purpose of updating pinned SHAs in workflow files.

### Execution Environment

**Shell:** `bash` with `set -euo pipefail` (exits on error, undefined variables, pipe failures)

### Script Logic

**Actions Queried:**

1. **actions/checkout@v4** (line 12)
   - **API Endpoint:** `https://api.github.com/repos/actions/checkout/git/refs/tags/v4`
   - **Extraction:** `jq -r '.object.sha'`
   - **Failure Handling:** `|| echo "Failed"` (prints "Failed" but does not exit script)

2. **actions/setup-python@v5** (line 15)
   - **API Endpoint:** `https://api.github.com/repos/actions/setup-python/git/refs/tags/v5`
   - **Extraction:** `jq -r '.object.sha'`
   - **Failure Handling:** `|| echo "Failed"`

3. **actions/cache@v4** (line 18)
   - **API Endpoint:** `https://api.github.com/repos/actions/cache/git/refs/tags/v4`
   - **Extraction:** `jq -r '.object.sha'`
   - **Failure Handling:** `|| echo "Failed"`

4. **actions/upload-artifact@v4** (line 21)
   - **API Endpoint:** `https://api.github.com/repos/actions/upload-artifact/git/refs/tags/v4`
   - **Extraction:** `jq -r '.object.sha'`
   - **Failure Handling:** `|| echo "Failed"`

5. **dtolnay/rust-toolchain@stable** (line 25)
   - **API Endpoint:** `https://api.github.com/repos/dtolnay/rust-toolchain/git/refs/heads/master`
   - **Note:** Queries `master` branch, not `stable` tag
   - **Extraction:** `jq -r '.object.sha'`
   - **Failure Handling:** `|| echo "Failed"`

6. **trufflesecurity/trufflehog@main** (line 28)
   - **API Endpoint:** `https://api.github.com/repos/trufflesecurity/trufflehog/git/refs/heads/main`
   - **Extraction:** `jq -r '.object.sha'`
   - **Failure Handling:** `|| echo "Failed"`

### Implementation Notes

- Script uses `set -euo pipefail` but all API calls use `|| echo "Failed"`, which prevents script exit on API failures
- Script prints SHAs to stdout but does not update workflow files automatically (manual copy-paste required)
- `dtolnay/rust-toolchain` queries `master` branch, but workflow uses `stable` toolchain parameter (may not match)
- Script requires `jq` to be installed (not checked or installed by script)
- Script requires `curl` to be installed (not checked or installed by script)

### Discrepancy Alerts

- **Line 25:** Queries `master` branch for `rust-toolchain`, but workflow uses `toolchain: stable` parameter. The SHA from `master` branch may not correspond to the `stable` toolchain version.
- **Line 2:** `set -euo pipefail` is set, but all API calls use `|| echo "Failed"`, which prevents the script from exiting on failures. The `-e` flag is effectively disabled by the error handling.
- **Dependencies:** Script requires `curl` and `jq` but does not check for their existence or provide installation instructions.

---

## Cross-Workflow Patterns

### Common Implementation Patterns

1. **Cargo.toml Detection:** All workflows use identical detection logic:
   ```bash
   if [ -f "Cargo.toml" ] || [ -f "../Cargo.toml" ]; then
     echo "cargo_exists=true"
   else
     echo "cargo_exists=false"
   fi
   ```
   - **Issue:** Checks parent directory but all commands run in workspace root

2. **Wheel Build Pattern:** Consistent across all workflows:
   ```bash
   if [ -f "Cargo.toml" ] || [ -f "../Cargo.toml" ]; then
     pip install --no-cache-dir maturin
     maturin build --release --out wheels
   else
     echo "⚠️ No Cargo.toml found - skipping wheel build"
   fi
   ```

3. **Package Installation Pattern:** Two paths based on Cargo.toml existence:
   - **If Cargo.toml exists:** `pip install --no-cache-dir -e .`
   - **If Cargo.toml missing:** Install `typer rich PyYAML` directly, set `PYTHONPATH=$PWD`

4. **Hardcoded Version:** Wheel filename pattern `ranex_core-0.0.1-*.whl` appears in multiple jobs
   - **Impact:** Will fail if version changes in `pyproject.toml`

5. **Soft Failure Pattern:** Most security/scanning steps use `|| echo` or `|| true`, making them reporting-only

### Action SHA Consistency

All workflows use the same pinned action SHAs:
- `actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11` (v4.1.1)
- `actions/setup-python@82c7e631bb3cdc910f68e0081d67478d79c6982d` (v5.1.0)
- `actions/cache@0057852bfaa89a56745cba8c7296529d2fc39830` (v4)
- `actions/upload-artifact@c7d193f32edcb7bfad88892161225aeda64e9392` (v4.0.0)
- `dtolnay/rust-toolchain@0b1efabc08b657293548b77fb76cc02d26091c7e` (stable)
- `trufflesecurity/trufflehog@35a5bf210f44d70a149b39d4db254abc7580cf6d` (main)

---

## Summary of Critical Issues

1. **Hardcoded Version:** Wheel filename pattern `0.0.1-*` will break if version changes
2. **Soft Failures:** Security and linting jobs never fail, only report violations
3. **Path Inconsistency:** Cargo.toml detection checks parent directory, but commands run in workspace root
4. **Summary Job:** Only checks 3 out of 6 dependency jobs
5. **SBOM Job:** Only runs on pushes to main, not on PRs or scheduled runs
6. **Release Summary:** Always reports success regardless of actual results

---

**Documentation Generated:** 2025-01-27  
**Method:** Direct code inspection and execution flow analysis  
**Assumptions:** None - all claims verified against actual workflow YAML files

