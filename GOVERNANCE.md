# Governance

This document describes how MTG AI is governed, who makes decisions, and how contributors can participate in those decisions.

## Maintainers

The current maintainer is:

- **Byron Williams** (byronawilliams@gmail.com)

Maintainers have commit access and are responsible for reviewing and merging pull requests, triaging issues, and cutting releases.

## Decision Model

This project uses a single-maintainer with consensus model:

- The maintainer has final say on all decisions.
- For substantive changes (breaking API changes, security policy changes, major dependencies), the maintainer will seek input from active contributors via GitHub Discussions or issue comments before deciding.
- Routine changes (bug fixes, documentation updates, dependency bumps, refactors that preserve behavior) do not require external consensus.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full contributor workflow.

In summary:

1. Open an issue describing the change before sending a PR for non-trivial work.
2. Follow the project's coding standards (ruff, basedpyright, conventional commits).
3. Include tests for behavior changes.
4. Respond to review feedback within a reasonable window.

## Conflict Resolution

If a contributor disagrees with a maintainer decision:

1. Discuss in the PR or issue thread first.
2. If unresolved, open a new issue summarizing the disagreement and proposed alternatives.
3. The maintainer makes the final call after considering the discussion.

## Adding Maintainers

The maintainer may invite trusted long-term contributors to join as additional maintainers. There is no automatic promotion process; invitations are issued at the maintainer's discretion based on demonstrated judgment and sustained contributions.
