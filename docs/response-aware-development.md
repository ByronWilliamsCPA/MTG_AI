# Response-Aware Development (RAD)

> **Status**: Stub | See project `CLAUDE.md` for full inline RAD tagging standards.

RAD tagging standards, comment marker syntax, and verification workflow for this
project are documented in `CLAUDE.md` under the "Response-Aware Development (RAD)"
section.

The canonical tagging syntax and full examples for this project are in
[`CLAUDE.md`](../CLAUDE.md) under the "Response-Aware Development (RAD)" section.

## Quick Reference

Tag assumptions that could cause production failures using three markers:

- `#CRITICAL` - assumption that could cause outages or data loss
- `#ASSUME` - assumption that could cause bugs
- `#EDGE` - assumption about uncommon scenarios

Each marker must be paired with a `#VERIFY` instruction describing the defensive
code or validation required.

### Mandatory Categories

Tagging is mandatory for:

- Timing dependencies (state updates, async operations, race conditions)
- External resources (API availability, file existence, network connectivity)
- Data integrity (type safety at boundaries, null/undefined handling)
- Concurrency (shared state, transaction isolation, deadlock potential)
- Security (authentication, authorization, input validation)
- Payment and financial (transaction integrity, retry logic, rollback handling)
