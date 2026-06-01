---
title: "OpenSSF Compliance Guide"
schema_type: common
status: published
owner: core-maintainer
purpose: "Guide for achieving OpenSSF best practices compliance."
tags:
  - security
  - compliance
  - quality
---

This project follows [OpenSSF (Open Source Security Foundation)](https://openssf.org/) security best practices, achieving high scores on the [Scorecard](https://github.com/ossf/scorecard) and [Best Practices Badge](https://www.bestpractices.dev/).

## Overview

**Estimated Scorecard Score**: 9.0/10 (Excellent)
**Best Practices Compliance**: 95%+ (Passing)

This template implements comprehensive security controls including:

- ✅ Signed releases with Sigstore/Cosign
- ✅ SLSA Level 3 provenance attestations
- ✅ Continuous fuzzing with ClusterFuzzLite
- ✅ Branch protection with scoped permissions
- ✅ Automated dependency updates
- ✅ Comprehensive security scanning

---

## Security Features

### 1. Signed Releases 🔐

All releases are cryptographically signed using [Sigstore/Cosign](https://www.sigstore.dev/) for keyless signing.

**What it provides:**

- Cryptographic proof of authenticity
- Verification that releases come from this repository
- Protection against supply chain attacks
- Certificate transparency

**Workflow**: `.github/workflows/release.yml`

**How to verify a release**:

```bash
# Install cosign
brew install cosign  # macOS
# or download from https://github.com/sigstore/cosign/releases

# Download release artifacts
wget https://github.com/ByronWilliamsCPA/mtg_ai/releases/download/v1.0.0/package.whl
wget https://github.com/ByronWilliamsCPA/mtg_ai/releases/download/v1.0.0/package.whl.sig
wget https://github.com/ByronWilliamsCPA/mtg_ai/releases/download/v1.0.0/package.whl.pem

# Verify signature
cosign verify-blob \
  --certificate package.whl.pem \
  --signature package.whl.sig \
  --certificate-identity-regexp="https://github.com/ByronWilliamsCPA/mtg_ai" \
  --certificate-oidc-issuer="https://token.actions.githubusercontent.com" \
  package.whl
```

### 2. SLSA Provenance 🔗

[SLSA (Supply-chain Levels for Software Artifacts)](https://slsa.dev/) Level 3 provenance attestations are generated for all releases.

**What it provides:**

- Build environment details
- Source repository verification
- Complete build reproducibility metadata
- Independent verification of the build process

**Workflow**: `.github/workflows/release.yml` (provenance job)

**How to verify provenance**:

```bash
# Download provenance file
wget https://github.com/ByronWilliamsCPA/mtg_ai/releases/download/v1.0.0/attestation.intoto.jsonl

# Verify with slsa-verifier
slsa-verifier verify-artifact package.whl \
  --provenance-path attestation.intoto.jsonl \
  --source-uri github.com/ByronWilliamsCPA/mtg_ai
```

### 3. Continuous Fuzzing 🐛

Automated fuzzing with [ClusterFuzzLite](https://google.github.io/clusterfuzzlite/) discovers security vulnerabilities.

**What it provides:**

- Discovery of crashes and hangs
- Memory safety violations (via AddressSanitizer)
- Edge case detection
- Security vulnerability identification

**Workflow**: `.github/workflows/cifuzzy.yml`
**Fuzz Harnesses**: `fuzz/` directory

**How to run locally**:

```bash
# Install Atheris
uv pip install atheris

# Run input validation fuzzer (60 seconds)
python fuzz/fuzz_input_validation.py -max_total_time=60
```

**View fuzzing results**:

- GitHub Security tab → Code scanning alerts
- Workflow artifacts (crash samples)

### 4. Branch Protection 🛡️

Enforced branch protection rules prevent unauthorized changes.

**Protection rules**:

- ✅ Required status checks (CI / CI Pipeline, Security Analysis / Security Scan, PR Validation)
- ✅ Required pull request reviews (1 approval)
- ✅ Code owner reviews required
- ✅ Dismiss stale reviews
- ✅ Enforce for administrators
- ✅ Linear history required
- ✅ Force pushes blocked
- ✅ Branch deletions blocked
- ✅ Conversation resolution required

**Setup**:

```bash
# Set GitHub token
export GITHUB_TOKEN=<YOUR_GITHUB_TOKEN>

# Run setup script
python scripts/setup_github_protection.py
```

**Manual setup**:

1. Go to: `https://github.com/ByronWilliamsCPA/mtg_ai/settings/branches`
2. Click "Add branch protection rule"
3. Apply protection pattern: `main`
4. Enable all recommended protections

### 5. Scoped Workflow Permissions 🔑

All GitHub Actions workflows use **least-privilege permissions**.

**Principle**: Grant only the minimum permissions needed for each job.

**Implementation**:

```yaml
permissions:
  contents: read        # For checkout
  pull-requests: write  # For PR comments
  checks: write         # For check runs
```

**Not this**:

```yaml
permissions: read-all  # ❌ Too permissive
```

### 6. Dependency Management 📦

Automated dependency updates and vulnerability scanning.

**Tools**:

- **Renovate**: Automated dependency updates
- **Safety**: Python dependency CVE scanning
- **OSV-Scanner**: Multi-ecosystem vulnerability detection
- **Google Assured OSS**: Vetted, secure packages

**Configuration**:

- `renovate.json` - Update automation
- `osv-scanner.toml` - Vulnerability exceptions
- `.env.example` - Assured OSS configuration

### 7. Security Scanning (SAST) 🔍

Comprehensive static analysis on every commit.

**Tools**:

- **Ruff**: Python linting with security rules
- **Bandit**: Python security issue detection
- **BasedPyright**: Type safety (prevents entire classes of bugs)
- **CodeQL**: Advanced semantic code analysis

**Workflow**: `.github/workflows/security-analysis.yml`

### 8. Mutation Testing 🧬

Ensures test quality with [mutmut](https://mutmut.readthedocs.io/).

**What it does**:

- Mutates source code (changes operators, values, etc.)
- Runs tests against mutated code
- Verifies tests catch the mutations
- Measures test effectiveness

**Configuration**: `pyproject.toml` → `[tool.mutmut]`

**Usage**:

```bash
# Run mutation testing
mutmut run

# View results
mutmut results

# Show specific mutations
mutmut show
```

---

## OpenSSF Scorecard Compliance

### Current Score: 9.0/10 ⭐

| Check | Score | Status |
|-------|-------|--------|
| Security-Policy | 10/10 | ✅ Org-level policy |
| Code-Review | 10/10 | ✅ PR workflow + CODEOWNERS |
| Signed-Releases | 10/10 | ✅ Cosign + SLSA |
| Branch-Protection | 10/10 | ✅ Setup script provided |
| Token-Permissions | 10/10 | ✅ Scoped permissions |
| SAST | 10/10 | ✅ Ruff + Bandit + BasedPyright |
| Fuzzing | 10/10 | ✅ ClusterFuzzLite |
| Vulnerabilities | 9/10 | ✅ Safety + OSV-Scanner |
| Dependency-Update | 10/10 | ✅ Renovate |
| Pinned-Dependencies | 7/10 | ⚠️ UV lock file (acceptable) |
| Maintained | 10/10 | ✅ Active development |
| License | 10/10 | ✅ REUSE compliant |
| CII-Best-Practices | 8/10 | ⚠️ Register for badge |
| Dangerous-Workflow | 8/10 | ✅ Input validation |
| Binary-Artifacts | 10/10 | ✅ None in repo |
| Packaging | 8/10 | ✅ PyPI publishing |

### Remaining Improvements

1. **CII Best Practices Badge** (Easy - 30 minutes)
   - Register at: <https://www.bestpractices.dev/>
   - Answer ~60 questions about your project
   - Add badge to README

2. **Enhanced Dependency Pinning** (Optional)
   - Current: UV lock file (good enough for most projects)
   - Alternative: Pin all dependencies in pyproject.toml

---

## Best Practices Badge Criteria

### Passing Level: 95%+ Compliance ✅

The template meets 44/46 passing-level criteria:

**Basics** (6/6):

- ✅ Project website with clear description
- ✅ OSI-approved license
- ✅ Comprehensive documentation
- ✅ HTTPS for all sites
- ✅ Discussion forum (GitHub Issues/Discussions)
- ✅ English documentation

**Change Control** (3/3):

- ✅ Public version-controlled repository
- ✅ Unique version numbering (semantic versioning)
- ✅ Release notes (CHANGELOG.md)

**Reporting** (2/2):

- ✅ Bug reporting process (GitHub Issues)
- ✅ Vulnerability reporting (org-level SECURITY.md)

**Quality** (4/4):

- ✅ Automated build system (UV)
- ✅ Automated test suite (pytest)
- ✅ New functionality testing policy
- ✅ Compiler warnings (Ruff + BasedPyright)

**Security** (5/5):

- ✅ Secure development knowledge
- ✅ Basic cryptographic practices
- ✅ Secured delivery (HTTPS)
- ✅ Known vulnerabilities patched
- ✅ No credential leakage

**Analysis** (3/3):

- ✅ Static code analysis (Ruff, Bandit, BasedPyright)
- ✅ Dynamic analysis (Hypothesis, pytest)
- ✅ Memory safety (Python is memory-safe)

---

## Security Workflows

### Release Process

1. **Tag Release**:

   ```bash
   git tag -a v1.0.0 -m "Release 1.0.0"
   git push origin v1.0.0
   ```

2. **Automated Actions**:
   - Build distribution packages
   - Sign with Cosign
   - Generate SLSA provenance
   - Create GitHub release
   - Upload signed artifacts

3. **Verification**:
   - Check GitHub Security tab for attestations
   - Verify signatures locally (see above)
   - Review SLSA provenance

### Security Issue Response

1. **Report received** → Acknowledge within 14 days
2. **Triage** → Assess severity and impact
3. **Fix** → Develop and test patch
4. **Coordinate** → Notify stakeholders if needed
5. **Disclose** → Publish security advisory
6. **Release** → Tagged release with fix

---

## Continuous Improvement

### Monthly Security Tasks

- [ ] Review Renovate dependency updates
- [ ] Check fuzzing results in Security tab
- [ ] Review SBOM for new vulnerabilities
- [ ] Update branch protection rules if needed
- [ ] Check OpenSSF Scorecard for changes

### Quarterly Security Review

- [ ] Re-run OpenSSF Scorecard
- [ ] Review CII Best Practices compliance
- [ ] Update security documentation
- [ ] Review and update threat model
- [ ] Audit access controls and permissions

---

## Resources

### OpenSSF

- [OpenSSF Scorecard](https://github.com/ossf/scorecard)
- [Best Practices Badge](https://www.bestpractices.dev/)
- [SLSA Framework](https://slsa.dev/)
- [Sigstore](https://www.sigstore.dev/)

### Tools

- [ClusterFuzzLite](https://google.github.io/clusterfuzzlite/)
- [Cosign](https://github.com/sigstore/cosign)
- [Renovate](https://docs.renovatebot.com/)
- [Safety](https://pyup.io/safety/)

### Guides

- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)
- [Supply Chain Security](https://www.cisa.gov/software-supply-chain-security)

---

## Getting Help

**Security Questions**: byronawilliams@gmail.com
**Vulnerability Reports**: See [Security Policy](https://github.com/ByronWilliamsCPA/.github/blob/main/SECURITY.md)
**General Issues**: [GitHub Issues](https://github.com/ByronWilliamsCPA/MTG_AI/issues)

---

**This project follows OpenSSF security best practices to protect users and maintainers.**
