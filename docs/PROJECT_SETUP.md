---
title: "Project Setup Guide"
schema_type: common
status: published
owner: core-maintainer
purpose: "Step-by-step guide for setting up the development environment."
tags:
  - guide
  - installation
  - development
---

This guide covers everything you need to know after generating your project from the cookiecutter template. It includes manual setup steps, keeping your project updated, and managing your repository structure.

## Table of Contents

- [Initial Setup](#initial-setup)
- [Project Planning with Claude Code](#project-planning-with-claude-code)
- [Manual Registrations Required](#manual-registrations-required)
- [Keeping Your Project Updated](#keeping-your-project-updated)
- [CI/CD Workflow Configuration](#cicd-workflow-configuration)
- [Badge Configuration](#badge-configuration)
- [Security Configuration](#security-configuration)
- [Repository Management](#repository-management)

---

## Initial Setup

After generating your project, complete these steps:

### 1. Review Generated Files

Your project was generated with the following configuration:

- **Project Name**: MTG AI
- **Python Version**: 3.12
- **License**: MIT

### 2. Create GitHub Repository

```bash
# Create a new repository on GitHub, then:
git remote add origin https://github.com/ByronWilliamsCPA/MTG_AI.git
git push -u origin main
```

### 3. Install Dependencies

```bash
# Install UV if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync --all-extras

# Install pre-commit hooks
uv run pre-commit install
```

### 4. Verify Setup

```bash
# Run tests
uv run pytest -v

# Run linting
uv run ruff check .

# Run type checking
uv run basedpyright src/
```

### 5. Generate Project Planning Documents

Use Claude Code to generate comprehensive planning documents for your project:

```bash
# Open Claude Code and describe your project, then run:
/plan <your detailed project description>
```

See [Project Planning with Claude Code](#project-planning-with-claude-code) below for the complete workflow.

---

## Project Planning with Claude Code

This template includes an integrated AI-assisted project planning workflow that transforms your project concept into actionable development plans with proper git branch strategy.

### Overview

The planning workflow generates 4 core documents, then synthesizes them into a comprehensive project plan:

```text
Project Description
        │
        ▼
┌───────────────────────────────────────┐
│   Step 1: Generate Planning Docs      │
│   (project-planning skill)            │
└───────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│   project-vision.md (PVS)             │  What & Why
│   tech-spec.md                        │  How (architecture)
│   roadmap.md                          │  When (phases)
│   adr/adr-001-*.md                    │  Key decisions
└───────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│   Step 2: Synthesize Project Plan     │
│   (project-plan-synthesizer agent)    │
└───────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│   PROJECT-PLAN.md                     │  Actionable plan
│   - Git branch strategy               │  with semantic
│   - Phase deliverables                │  release alignment
│   - TodoWrite checklist               │
└───────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│   Step 3: Start Development           │
│   /git/milestone start                │
└───────────────────────────────────────┘
```

### Step 1: Generate Planning Documents

Describe your project and generate the 4 core documents:

```bash
# Using the /plan command (recommended)
/plan I want to build a CLI tool for managing personal finances.
The main users are individuals tracking expenses.
Core features: expense tracking, budget categories, monthly reports.
Technical constraints: must work offline, SQLite for storage.
```

**Or provide a more detailed description:**

```text
Generate planning documents for this project:

I'm building a REST API for inventory management. Target users are
small business owners. Core features include product CRUD, stock
tracking, low-stock alerts, and reporting. Must integrate with
existing PostgreSQL database and support OAuth2 authentication.
```

**What gets created:**

| Document | Location | Purpose |
|----------|----------|---------|
| Project Vision & Scope | `docs/planning/project-vision.md` | Problem, solution, scope, success metrics |
| Technical Specification | `docs/planning/tech-spec.md` | Architecture, data model, APIs, security |
| Development Roadmap | `docs/planning/roadmap.md` | Phased implementation plan |
| Architecture Decision Records | `docs/planning/adr/adr-001-*.md` | Key technical decisions with rationale |

**The project-planning skill will:**
1. Analyze your project description
2. Generate each document using templates
3. Validate each document with AI consensus review
4. Ensure documents cross-reference correctly
5. Flag any assumptions needing your validation

### Step 2: Synthesize into Project Plan

After the 4 documents are generated, synthesize them into an actionable plan:

```bash
# Request synthesis
"Synthesize my planning documents into a project plan"
```

**The project-plan-synthesizer agent will:**
1. Read and validate all 4 source documents
2. Extract key information from each document
3. Lookup best practices via Context7 for your tech stack
4. Map phases to semantic release-aligned git branches
5. Validate with tiered consensus (multi-model AI review)
6. Generate `docs/planning/PROJECT-PLAN.md`
7. Create initial TodoWrite checklist for Phase 0

**Output:** `docs/planning/PROJECT-PLAN.md` containing:
- Git branch strategy for each phase
- Consolidated risk register
- Cross-referenced architecture decisions
- Success criteria per phase
- TodoWrite checklist for Phase 0

### Git Branch Strategy (Semantic Release)

Phases are automatically mapped to semantic release branch types:

| Phase Focus | Branch Type | Version Impact | Example |
|-------------|-------------|----------------|---------|
| Foundation/Setup | `feat/` | Minor (0.X.0) | `feat/phase-0-foundation` |
| Core Features | `feat/` | Minor (0.X.0) | `feat/phase-1-core` |
| Additional Features | `feat/` | Minor (0.X.0) | `feat/phase-2-advanced` |
| Performance | `perf/` | Patch (0.0.X) | `perf/phase-3-optimization` |
| Documentation | `docs/` | None | `docs/phase-4-documentation` |
| Bug Fixes | `fix/` | Patch (0.0.X) | `fix/phase-X-bugfixes` |

### Step 3: Review and Start Development

**Review the synthesized plan:**

```bash
# Review the generated plan
cat docs/planning/PROJECT-PLAN.md

# Verify:
# - Phase deliverables match your expectations
# - Git branch types align with semantic release
# - Success criteria are measurable
```

**Start development with the milestone workflow:**

```bash
# Start Phase 0 (creates branch, sets up tracking)
/git/milestone start feat/phase-0-foundation
```

**This will:**
- Create the feature branch from main
- Set up git worktree if parallel development is needed
- Show semantic release impact for this branch type
- Create TodoWrite list from phase deliverables

### Phase Completion Workflow

When you complete a phase:

```bash
# 1. Validate all commits match branch type
/git/milestone complete

# 2. Create PR with What the Diff summary
/git/pr-prepare --include_wtd=true

# 3. Merge PR (triggers semantic release if applicable)

# 4. Start next phase
/git/milestone start feat/phase-1-core
```

### Using Planning Documents During Development

**Load context for a task:**

```text
Load context from project-vision.md sections 2-3 and adr/adr-001-*.md,
then implement [feature] per tech-spec.md section [X].
```

**Validate code against specs:**

```text
Review this code against tech-spec.md section 6 (security).
Flag any violations.
```

**Check phase progress:**

```text
Review PROJECT-PLAN.md Phase 1 deliverables and update status.
```

### Document Update Guidelines

| Document | Update When |
|----------|-------------|
| **Roadmap** | After completing tasks, adjusting timelines |
| **ADR** | When making new architectural decisions |
| **Tech Spec** | When architecture changes significantly |
| **PVS** | When scope changes (rare) |
| **PROJECT-PLAN.md** | After each phase completion |

### Planning Resources

- **Skill Reference**: `.claude/skills/project-planning/SKILL.md`
- **Document Templates**: `.claude/skills/project-planning/templates/`
- **Detailed Guidance**: `.claude/skills/project-planning/reference/`
- **Git Milestone Workflow**: `.claude/skills/git/workflows/milestone.md`
- **Project Plan Template**: `docs/planning/project-plan-template.md`

---

## Manual Registrations Required

Some features require manual registration on external services:

### OpenSSF Best Practices Badge

The OpenSSF Best Practices badge requires manual project registration:

1. **Register your project**: Visit [https://www.bestpractices.dev/en](https://www.bestpractices.dev/en)
2. **Click "Get Your Badge Now"**
3. **Enter your repository URL**: `https://github.com/ByronWilliamsCPA/mtg_ai`
4. **Complete the questionnaire** answering questions about your project's security practices
5. **Get your badge ID** (e.g., `12345`)
6. **Add the badge to your README**:

````markdown
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/YOUR_PROJECT_ID/badge)](https://www.bestpractices.dev/en/projects/YOUR_PROJECT_ID)
````

**Tip**: Many questions can be answered "Met" based on this template's default configuration (CI/CD, security scanning, documentation, etc.).

### Codecov Configuration

1. **Sign up/Login**: Visit [https://codecov.io](https://codecov.io) and authenticate with GitHub
2. **Add repository**: Navigate to your organization and add the repository
3. **Copy the upload token** (optional for public repos, required for private)
4. **Add as GitHub secret**: Repository Settings > Secrets > `CODECOV_TOKEN`

---

## Keeping Your Project Updated

This template uses [Cruft](https://cruft.github.io/cruft/) for template management, allowing you to receive updates.

### Check for Template Updates

```bash
# Check if updates are available
cruft check

# See what would change
cruft diff
```

### Apply Template Updates

```bash
# Update to the latest template version
cruft update

# If there are conflicts, resolve them manually
# Then mark as resolved:
cruft update --skip
```

### Best Practices for Updates

1. **Create a branch** before updating: `git checkout -b template-update`
2. **Review all changes** carefully with `cruft diff`
3. **Test thoroughly** after updating: `uv run pytest && uv run ruff check .`
4. **Commit with clear message**: `git commit -m "chore: update from cookiecutter template"`

### Handling Merge Conflicts

When conflicts occur:

```bash
# After cruft update shows conflicts
git status  # See conflicted files

# Edit files to resolve conflicts
# Then stage resolved files
git add <resolved-files>

# Complete the update
cruft update --skip
```

---

## CI/CD Workflow Configuration

Your project includes several GitHub Actions workflows:

### Core Workflows

| Workflow | File | Purpose |
|----------|------|---------|
| CI Pipeline | `ci.yml` | Tests, linting, type checking |
| Security Analysis | `security-analysis.yml` | Dependency scanning, CodeQL |
| PR Validation | `pr-validation.yml` | Lock file and requirements sync validation |
| OpenSSF Scorecard | `scorecard.yml` | Supply chain security assessment |
| SBOM & Security Scan | `sbom.yml` | Software Bill of Materials generation |
| Documentation | `docs.yml` | Build and deploy MkDocs |

### Required GitHub Secrets

Set these in Repository Settings > Secrets and variables > Actions:

| Secret | Required For | How to Get |
|--------|--------------|------------|
| `CODECOV_TOKEN` | Codecov uploads | codecov.io > Settings > Upload Token |
| `SCORECARD_TOKEN` | Scorecard (optional) | GitHub PAT with repo scope |
| `QLTY_COVERAGE_TOKEN` | Qlty coverage upload | qlty.sh > project Settings > Coverage token |

### Qlty Code Quality

Qlty aggregates code quality metrics (complexity scores, code smell detection, and
coverage trends) and surfaces them as PR comments via the `qlty.yml` workflow. It does
not replace Ruff, BasedPyright, or pytest; those tools run directly in CI and Qlty
consumes their output to build trend data.

**Setup**:

1. Create a project at [qlty.sh](https://qlty.sh) and link your GitHub repository.
2. Copy the `QLTY_COVERAGE_TOKEN` from the Qlty project Settings page.
3. Add it as a repository secret named `QLTY_COVERAGE_TOKEN` (see [Required GitHub Secrets](#required-github-secrets)).

The `.qlty/qlty.toml` configuration file is already generated. No manual tool
configuration is required beyond the token.

---

## Badge Configuration

### Automatic Badges (No Setup Required)

These badges work automatically once your repository is public:

- **OpenSSF Scorecard**: Updates weekly after first workflow run
- **CI Pipeline**: Shows status after first push
- **Security Analysis**: Shows status after first push
- **SBOM & Security Scan**: Shows status after dependency changes

### Badges Requiring Registration

| Badge | Service | Registration URL |
|-------|---------|-----------------|
| OpenSSF Best Practices | bestpractices.dev | [Register Project](https://www.bestpractices.dev/en) |
| Codecov | codecov.io | [Add Repository](https://codecov.io) |

### Adding OpenSSF Best Practices Badge

After registration, add this badge to your README's "Quality & Security" section:

````markdown
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/YOUR_ID/badge)](https://www.bestpractices.dev/en/projects/YOUR_ID)
````

---

## Security Configuration

### Branch Protection Rules

You can configure branch protection either via script (recommended) or manually through the GitHub UI.

#### Option 1: Automated Setup (Recommended)

Use the included script to configure comprehensive branch protection:

```bash
# Set up branch protection with default settings
uv run python scripts/setup_github_protection.py

# Or specify custom settings
uv run python scripts/setup_github_protection.py --enforce-admins --require-code-owner-reviews
```

The script configures:
- Required pull request reviews before merging
- Required status checks to pass
- Enforce rules for administrators
- Require signed commits
- Dismiss stale reviews on new commits

#### Option 2: Manual UI Setup

1. Go to Repository Settings > Branches > Add rule
2. Apply to: `main`
3. Enable:
   - [x] Require a pull request before merging
   - [x] Require status checks to pass
   - [x] Require branches to be up to date
   - [x] Include administrators

#### Automated Setup Script

The template includes `scripts/setup_github_protection.py`, which configures branch
protection via the GitHub API with the project's required status checks, required
signatures, code-owner reviews, and the chosen approval count (controlled by the
`sole_contributor` cookiecutter flag). Selecting `sole_contributor=yes` also disables
required code-owner reviews, because the GitHub API rejects the combination of zero
required approvers and required code-owner review with HTTP 422.

Manual invocation after creating the GitHub repo:

```bash
export GITHUB_TOKEN=ghp_your_token_with_admin_repo_scope
uv run python scripts/setup_github_protection.py
```

Prerequisites:

- GitHub repository must exist (create it via `gh repo create` or the web UI).
- `GITHUB_TOKEN` must have the `repo` scope (or repository admin permission for fine-grained PATs).
- The local `origin` remote must point at the new GitHub repo.

If you set the `auto_setup_branch_protection` cookiecutter variable to `yes` when
generating the project, and you supply `GITHUB_TOKEN` in your environment, and the
project has a configured remote, the post-gen hook runs this script automatically.
The auto-run is non-fatal: if any precondition fails or the API call errors out,
generation completes with a printed warning and you can run the script manually later.

##### Prerequisites for auto-run

The post-gen hook runs `git init` against the freshly generated project, which
creates a repo with **no** `origin` remote. The auto-run therefore only succeeds
when all of the following are true at generation time:

1. `auto_setup_branch_protection` is set to `yes` in your cookiecutter answers.
2. `GITHUB_TOKEN` is exported in the shell that runs `cruft create` (or
   `cookiecutter`), with `repo` scope (or repo-admin permission for a
   fine-grained PAT).
3. An `origin` remote is configured on the generated project before the auto-run
   reaches the helper. In the default flow this is not the case, so the auto-run
   prints a hint and skips. Two ways to satisfy the requirement:

   - **Pre-create the GitHub repo and the local remote.** Create the empty
     GitHub repo first (`gh repo create <name> --public`), then add the remote
     manually after generation completes:

     ```bash
     cd <project_slug>
     git remote add origin git@github.com:<owner>/<name>.git
     GITHUB_TOKEN=ghp_xxx uv run python scripts/setup_github_protection.py
     ```

   - **Skip auto-run and use the manual command later.** Leave
     `auto_setup_branch_protection=no` (the default) and run the script
     manually once the remote is in place. This is the documented happy path
     for most users.

When the auto-run is skipped because a precondition is missing, the hook prints
a one-line hint identifying the missing piece (token, remote, or script) along
with the exact command to recover. No `GITHUB_TOKEN` value is ever echoed back.

### Required Status Checks

Add these as required checks:
- `CI / Test` (from CI workflow)
- `CI / Lint` (from CI workflow)
- `codecov/patch`

### Security Policy
Your `SECURITY.md` file is already configured. Update these sections:

1. **Supported Versions**: Update as you release new versions
2. **Security Contact**: Change `security@example.com` if needed
3. **PGP Key**: Add your security team's PGP key for encrypted reports

---

## Repository Management

### Release Process

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md** with release notes
3. **Create a tag**:
   ```bash
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push origin v1.0.0
   ```
4. **Create GitHub Release** from the tag

### Dependency Updates
Renovate is configured to automatically create PRs for dependency updates. Review and merge these regularly.

### Code Quality Standards

This project enforces:

- **80%+ test coverage** (enforced via pytest-cov)
- **Zero linting errors** (enforced via Ruff)
- **Type safety** (enforced via BasedPyright)
- **Security scanning** (enforced via Bandit, pip-audit, OSV-Scanner)

### Project Structure

```text
mtg_ai/
├── src/mtg_ai/    # Main package
│   ├── core/                               # Core functionality
│   ├── utils/                              # Utility functions
│   └── cli.py                              # CLI entrypoint
├── tests/                                  # Test suite
├── docs/                                   # Documentation
├── .github/workflows/                      # CI/CD workflows
├── pyproject.toml                          # Project configuration
└── README.md                               # Project readme
```

---

## Getting Help

- **Template Issues**: [cookiecutter-python-template issues](https://github.com/ByronWilliamsCPA/cookiecutter-python-template/issues)
- **Cruft Documentation**: [cruft.github.io/cruft](https://cruft.github.io/cruft/)
- **UV Documentation**: [docs.astral.sh/uv](https://docs.astral.sh/uv/)
- **OpenSSF Scorecard**: [securityscorecards.dev](https://securityscorecards.dev/)
- **OpenSSF Best Practices**: [bestpractices.dev](https://www.bestpractices.dev/)
