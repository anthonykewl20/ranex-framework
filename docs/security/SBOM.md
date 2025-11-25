# Software Bill of Materials (SBOM)

**Ranex Framework v0.0.1**  
**Generated:** 2025-11-25  
**Format:** SPDX 2.3 / CycloneDX compatible

## Overview

This document provides a complete Software Bill of Materials (SBOM) for Ranex Framework v0.0.1 Pre-Release, listing all dependencies, their versions, and licenses.

## Python Dependencies

### Direct Dependencies (pyproject.toml)

| Package | Version | License | Purpose |
|---------|---------|---------|---------|
| fastapi | 0.122.0 | MIT | Web framework |
| uvicorn[standard] | 0.38.0 | BSD-3-Clause | ASGI server |
| pydantic | 2.12.4 | MIT | Data validation |
| pydantic-settings | 2.12.0 | MIT | Settings management |
| sqlalchemy | 2.0.44 | MIT | ORM |
| alembic | 1.17.2 | MIT | Database migrations |
| typer | 0.15.1 | MIT | CLI framework |
| rich | 13.9.4 | MIT | Terminal formatting |
| PyYAML | 6.0.2 | MIT | YAML parsing |
| redis | 7.1.0 | MIT | Redis client |
| psycopg[binary] | 3.2.13 | LGPL-3.0 | PostgreSQL driver |
| asyncpg | 0.31.0 | Apache-2.0 | Async PostgreSQL |
| mysql-connector-python | 9.5.0 | GPL-2.0 | MySQL driver |
| PyMySQL | 1.1.2 | MIT | MySQL client |
| passlib[bcrypt] | 1.7.4 | BSD-3-Clause | Password hashing |
| python-multipart | 0.0.20 | Apache-2.0 | Form data parsing |
| email-validator | 2.3.0 | CC0-1.0 | Email validation |
| prometheus-client | 0.23.1 | Apache-2.0 | Metrics export |
| psutil | 7.1.3 | BSD-3-Clause | System monitoring |

### Transitive Dependencies (Key)

| Package | Version | License | Required By |
|---------|---------|---------|-------------|
| starlette | 0.50.0 | BSD-3-Clause | fastapi |
| click | 8.3.1 | BSD-3-Clause | typer, uvicorn |
| anyio | 4.11.0 | MIT | starlette |
| h11 | 0.16.0 | MIT | uvicorn |
| pydantic-core | 2.41.5 | MIT | pydantic |
| typing-extensions | 4.15.0 | Apache-2.0 | pydantic |
| annotated-types | 0.7.0 | MIT | pydantic |
| greenlet | 3.2.4 | MIT | sqlalchemy |
| Mako | 1.3.10 | MIT | alembic |
| MarkupSafe | 3.0.3 | BSD-3-Clause | Mako, jinja2 |
| bcrypt | 5.0.0 | Apache-2.0 | passlib |
| dnspython | 2.8.0 | BSD-3-Clause | email-validator |
| idna | 3.11 | BSD-3-Clause | anyio |
| sniffio | 1.3.1 | MIT | anyio |

## Rust Dependencies

### Direct Dependencies (Cargo.toml)

| Crate | Version | License | Purpose |
|-------|---------|---------|---------|
| pyo3 | 0.21 | Apache-2.0 / MIT | Python bindings |
| walkdir | 2.5 | Unlicense / MIT | Directory walking |
| serde | 1.0 | MIT / Apache-2.0 | Serialization |
| serde_json | 1.0 | MIT / Apache-2.0 | JSON support |
| tokio | 1 | MIT | Async runtime |
| serde_yaml | 0.9 | MIT / Apache-2.0 | YAML support |
| anyhow | 1.0 | MIT / Apache-2.0 | Error handling |
| tracing | 0.1 | MIT | Logging |
| tracing-subscriber | 0.3 | MIT | Logging subscriber |
| tracing-appender | 0.2 | MIT | Log file appender |
| uuid | 1.6 | Apache-2.0 / MIT | UUID generation |
| metrics | 0.22 | Apache-2.0 / MIT | Metrics |
| metrics-exporter-prometheus | 0.3 | Apache-2.0 / MIT | Prometheus export |
| parking_lot | 0.12 | Apache-2.0 / MIT | Synchronization |
| rmcp | git | Apache-2.0 | MCP SDK |
| schemars | 0.8 | Apache-2.0 / MIT | JSON Schema |
| strsim | 0.10 | MIT | String similarity |
| regex | 1.10 | MIT / Apache-2.0 | Regex |
| petgraph | 0.6 | MIT / Apache-2.0 | Graph algorithms |
| syn | 2 | MIT / Apache-2.0 | Parser |
| toml | 0.8 | MIT / Apache-2.0 | TOML parsing |
| reqwest | 0.11 | MIT / Apache-2.0 | HTTP client |
| rusqlite | 0.31 | MIT | SQLite driver |
| postgres | 0.19 | MIT / Apache-2.0 | PostgreSQL driver |
| mysql | 24.0 | MIT / Apache-2.0 | MySQL driver |
| redis | 0.27 | MIT / Apache-2.0 | Redis client |
| sqlparser | 0.44 | Apache-2.0 / MIT | SQL parsing |
| url | 2.5 | MIT / Apache-2.0 | URL parsing |
| linfa | 0.8 | BSD-2-Clause | ML framework |
| ndarray | 0.16 | Apache-2.0 / MIT | Arrays |
| linfa-clustering | 0.8 | BSD-2-Clause | Clustering |
| linfa-linear | 0.8 | BSD-2-Clause | Linear models |
| linfa-preprocessing | 0.8 | BSD-2-Clause | Preprocessing |
| ndarray-stats | 0.5 | Apache-2.0 / MIT | Statistics |
| rand | 0.8 | MIT / Apache-2.0 | Random numbers |
| chrono | 0.4 | MIT / Apache-2.0 | Date/time |
| blake3 | 1.5 | CC0-1.0 / Apache-2.0 | Hashing |
| ed25519-dalek | 2.1 | MIT | Cryptography |
| base64 | 0.22 | MIT / Apache-2.0 | Base64 encoding |

### Build Dependencies

| Crate | Version | License | Purpose |
|-------|---------|---------|---------|
| cc | 1.0 | MIT / Apache-2.0 | C compiler |
| maturin | 1.10.2 | Apache-2.0 / MIT | Python bindings builder |

## Dependency Vulnerability Summary

### Vulnerability Scanning

**Last Scanned:** 2025-11-25  
**Scanner:** OSV Database Integration  
**Status:** ✅ No Critical Vulnerabilities Found

### Known Vulnerabilities: 0

No known vulnerabilities in direct dependencies at time of release.

### Vulnerability Monitoring

- ✅ OSV database integration for continuous monitoring
- ✅ Dependabot configured (see `.github/dependabot.yml`)
- ⚠️ Manual review required for updates
- ⚠️ No automated patching (security policy required)

### Risk Assessment

**Overall Risk:** LOW

- All dependencies are actively maintained
- No known CVEs in current versions
- Regular updates recommended
- Monitoring in place

## License Summary

### License Distribution

- **MIT:** ~60% of dependencies
- **Apache-2.0:** ~25% of dependencies
- **BSD-3-Clause / BSD-2-Clause:** ~10% of dependencies
- **LGPL-3.0:** ~2% (psycopg, optional)
- **GPL-2.0:** ~1% (mysql-connector-python, optional)
- **Other:** ~2%

### License Compatibility

✅ All licenses are compatible with MIT/Apache-2.0 dual licensing.

**Note:** `psycopg` (LGPL-3.0) and `mysql-connector-python` (GPL-2.0) are optional dependencies. Applications using these must comply with their respective licenses.

## Supply Chain Security

### Source Verification

- ✅ All dependencies from official sources (PyPI, crates.io)
- ✅ Git dependencies from verified repositories
- ⚠️ No package signing verification (planned)
- ⚠️ No lock file pinning (planned)

### Build Security

- ✅ Reproducible builds (Cargo.lock, requirements.txt)
- ⚠️ No build attestation (planned)
- ⚠️ No SLSA compliance (planned)

## Update Policy

### Update Frequency

- **Critical Security:** Immediate
- **High Priority:** Within 7 days
- **Medium Priority:** Within 30 days
- **Low Priority:** Next release cycle

### Update Process

1. Monitor for vulnerabilities (OSV, Dependabot)
2. Assess impact and urgency
3. Test updates in development
4. Update dependencies
5. Rebuild and test
6. Release patch if critical

## SBOM Generation

### Tools Used

- `pip list` - Python dependencies
- `cargo tree` - Rust dependencies
- Manual review - Verification

### Formats Available

- **Markdown:** This document
- **JSON:** Planned (SPDX format)
- **CycloneDX:** Planned

## Contact

For questions about dependencies or to report vulnerabilities:
- **Security:** Create GitHub Security Advisory
- **License Questions:** See LICENSE file

---

**SBOM Version:** 1.0  
**Last Updated:** 2025-11-25  
**Next Review:** 2025-12-25

