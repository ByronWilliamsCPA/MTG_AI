# Security Check Command

Run security validation including environment checks, vulnerability scanning, and secrets detection.

## Usage

```
/security [scope]
```

**Arguments:**
- `scope` (optional): `all`, `env`, `scan`, `deps` (default: `all`)

## Workflow

1. **Environment Validation**: Check GPG/SSH keys and signing configuration
2. **Code Scanning**: Run Bandit security analysis
3. **Dependency Audit**: Check for vulnerable dependencies
4. **Secrets Detection**: Scan for exposed secrets

## Commands Executed

### Environment Validation
```bash
# Check GPG key
gpg --list-secret-keys

# Check SSH key
ssh-add -l

# Check git signing
git config --get user.signingkey
```

### Code Scanning
```bash
# Bandit security scanner
uv run bandit -r src/ -c pyproject.toml

# Semgrep (if available)
uv run semgrep scan --config auto src/
```

### Dependency Audit
```bash
# Check for vulnerable dependencies
uv run pip-audit

# OSV-Scanner (alternative vulnerability scanner)
osv-scanner --recursive .
```

### Secrets Detection
```bash
# Gitleaks scan
gitleaks detect --source .

# TruffleHog (if available)
trufflehog filesystem .
```

## Security Standards

- **No hardcoded secrets**: All secrets in environment variables
- **Dependencies scanned**: No known vulnerabilities
- **Signed commits**: GPG signing enabled
- **SSH keys**: Secure authentication

## OWASP Compliance

Focus on preventing:
- A01: Broken Access Control
- A03: Injection
- A07: Authentication Failures
- A09: Logging Failures
