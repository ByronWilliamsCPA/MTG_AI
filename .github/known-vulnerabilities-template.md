# Known Vulnerability Template

Use this template to document each unfixed CVE in `.github/known-vulnerabilities.md`.
Copy the block below and fill in all fields.

---

## CVE-XXXX-XXXXX | Package Name | Severity

| Field | Value |
|-------|-------|
| **CVE ID** | CVE-XXXX-XXXXX |
| **Package** | package-name |
| **Affected Version** | x.y.z |
| **Fixed Version** | x.y.z+1 (or "No fix available") |
| **Severity** | Critical / High / Medium / Low |
| **CVSS Score** | 0.0 |
| **Discovered** | YYYY-MM-DD |
| **Reassessment Due** | YYYY-MM-DD (must be within 60 days of Discovered) |
| **Blocking Release** | Yes / No |

### Description

Brief description of the vulnerability and what it affects.

### Impact on This Project

Explanation of whether and how this vulnerability affects this specific project and
its use cases. Be specific: is the vulnerable code path exercised? Is the input
trusted or untrusted?

### Remediation Plan

- [ ] Action item 1 (owner, due date)
- [ ] Action item 2 (owner, due date)

### Why Not Fixed Yet

Explanation of the blocker: upstream has not released a fix, fix introduces a
breaking change, awaiting vendor patch, etc.

### References

- [CVE Details](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-XXXX-XXXXX)
- [GitHub Advisory](https://github.com/advisories/GHSA-XXXX)
- [Upstream Issue](https://github.com/owner/repo/issues/XXX)
