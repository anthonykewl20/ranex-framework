# Upgrade to Team Edition

Team Edition unlocks the full power of Ranex.

---

## Feature Comparison

| Feature | Community | Team |
|---------|:---------:|:----:|
| **Security Scanning** | | |
| SAST Patterns | 7 | 30+ |
| Antipatterns | 5 | 15+ |
| Custom Rules | ❌ | ✅ |
| CVE Database | ❌ | ✅ |
| **State Machine** | | |
| Basic Transitions | ✅ | ✅ |
| Guard Conditions | ❌ | ✅ |
| Nested States | ❌ | ✅ |
| Multiple per Feature | ❌ | ✅ |
| **MCP Tools** | | |
| Basic Tools | 10 | 43 |
| ARBITER Tools | ❌ | ✅ |
| Drift Tools | ❌ | ✅ |
| RAG Tools | ❌ | ✅ |
| Governance Tools | ❌ | ✅ |
| **CLI Commands** | | |
| Basic Commands | 8 | 22 |
| Holodeck Simulation | ❌ | ✅ |
| Attestation | ❌ | ✅ |
| **Features** | | |
| Atlas (TF-IDF) | ✅ | ✅ |
| Atlas (RAG/Semantic) | ❌ | ✅ |
| ARBITER Test Integrity | ❌ | ✅ |
| Drift Detection | ❌ | ✅ |
| Phase Gates | ❌ | ✅ |
| Audit Trail | Basic | Full |
| **Support** | | |
| Community Support | ✅ | ✅ |
| Priority Support | ❌ | ✅ |
| Onboarding Session | ❌ | ✅ |

---

## Key Team Features

### RAG Semantic Search

Find existing code by meaning, not just keywords:

```python
# Community (TF-IDF)
atlas.search("calculate tax")  # Keyword match only

# Team (RAG)
atlas.search("compute sales tax for orders")  
# Finds: calculate_tax(), apply_tax_rate(), get_tax_percentage()
```

### ARBITER Test Integrity

Detects useless tests:

```python
# ARBITER catches this:
def test_payment():
    result = process_payment(mock)
    assert result is not None  # Tautological - always passes!

# ARBITER Report:
# ❌ Tautological assertion at line 3
# Mutation score: 12% (tests don't catch bugs)
```

### Drift Detection

Catches scope creep:

```
You asked: "Create login endpoint"
AI generated:
  ✅ Login endpoint
  ⚠️ OAuth integration (not requested)
  ⚠️ Password reset (not requested)
  ⚠️ 2FA setup (not requested)

Drift Score: 45% compliant
```

### Advanced Security

30+ patterns including:
- Second-order SQL injection
- Blind SQL injection
- XSS variants
- CSRF
- SSRF
- XXE
- JWT vulnerabilities
- Race conditions
- And more...

### Guard Conditions

Conditional state transitions:

```yaml
# Team Edition
transitions:
  - from: Processing
    to: Paid
    guard:
      - amount <= credit_limit
      - fraud_score < 0.3
```

---

## Pricing

| Plan | Price | Use Case |
|------|-------|----------|
| Community | Free | Individual developers |
| Team | Contact us | Small teams (2-10) |
| Enterprise | Contact us | Large organizations |

---

## Migration Path

Upgrading is seamless:

1. **Install Team Edition wheel**
   ```bash
   pip install ranex_core_team-*.whl
   ```

2. **Your code works unchanged**
   - Same @Contract decorator
   - Same state.yaml format
   - Same CLI commands (plus more)

3. **Enable new features**
   ```toml
   # .ranex/config.toml
   [features]
   rag = true
   arbiter = true
   drift = true
   ```

---

## Contact

**Email:** sales@ranex.dev

**What to include:**
- Team size
- Use case (startup, enterprise, etc.)
- Current pain points
- Questions about features

**Response time:** 24-48 hours

---

## FAQ

### Can I try Team Edition before buying?

Yes! We offer 14-day trials for qualified teams. Contact sales@ranex.dev.

### Is there a discount for startups?

Yes! Contact us with your startup details.

### Do you offer annual billing?

Yes, with a discount. Contact sales for pricing.

### What's the onboarding process?

1. Install Team Edition
2. 1-hour onboarding call with engineer
3. Configure for your project
4. Ongoing priority support

---

**Ready to upgrade?** Contact sales@ranex.dev

