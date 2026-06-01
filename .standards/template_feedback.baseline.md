# Template Feedback Baseline

> **Source**: ByronWilliamsCPA/cookiecutter-python-template
> **Version**: 0.1.0
> **Updated**: 2026-06-01
>
> This file contains the **baseline format** for template feedback documentation.
> Merge format changes into `docs/template_feedback.md` using: `/merge-standards`

---

## Standard Header Format

```markdown
# Template Feedback

> **Purpose**: Document issues discovered in this project that should be addressed
> in the [cookiecutter-python-template](https://github.com/ByronWilliamsCPA/cookiecutter-python-template).
>
> **Generated From**: cookiecutter-python-template v0.1.0
> **Project Created**: __PROJECT_CREATION_DATE__
```

---

## Feedback Item Format (REQUIRED)

All feedback items MUST use this format for consistency across projects:

```markdown
### [Short Descriptive Title]

- **Priority**: Critical / High / Medium / Low
- **Category**: [See categories below]
- **Discovered**: YYYY-MM-DD
- **Template Version**: 0.1.0

**Issue**: [Clear description of what's wrong or missing]

**Context**: [How was this discovered? What were you trying to do?]

**Suggested Fix**: [What should the template do differently?]

**Affected Files**: [List template files that need changes]
- `mtg_ai/path/to/file.ext`
- `hooks/post_gen_project.py`

**Workaround** (optional): [Steps to fix locally if applicable]
```

---

## Standard Categories

Use these categories for consistent classification:

| Category | Description | Examples |
|----------|-------------|----------|
| **Configuration** | Tool configs, settings files | pyproject.toml, .pre-commit-config.yaml |
| **Documentation** | Docs, README, guides | README.md, docs/*, CONTRIBUTING.md |
| **Tooling** | Dev tools, scripts, hooks | scripts/*, hooks/*, noxfile.py |
| **Structure** | Project layout, directories | src/, tests/, file organization |
| **CI/CD** | Workflows, pipelines | .github/workflows/*, CI configuration |
| **Security** | Security configs, scanning | Security tools, vulnerability handling |
| **Dependencies** | Package management | pyproject.toml deps, lock files |
| **Licensing** | REUSE, SPDX, license files | REUSE.toml, LICENSES/*, LICENSE |
| **Quality** | Linting, formatting, types | Ruff, BasedPyright, quality tools |
| **Testing** | Test framework, coverage | pytest config, test patterns |

---

## Priority Guidelines

| Priority | Criteria | Response Time |
|----------|----------|---------------|
| **Critical** | Blocks project creation or core functionality | Fix immediately |
| **High** | CI/CD fails, security issues, major UX problems | Fix in next release |
| **Medium** | Inconvenient but has workaround | Plan for future release |
| **Low** | Nice to have, cosmetic issues | Address when convenient |

---

## Submission Instructions Section

```markdown
## Submitting Feedback

Once you've collected feedback, you can:

1. **Create an issue** in the [cookiecutter-python-template repository](https://github.com/ByronWilliamsCPA/cookiecutter-python-template/issues)
   - Use the "Template Feedback" issue template if available
   - Include the project name and template version

2. **Submit a PR** if you have fixes for the template
   - Reference the feedback items addressed
   - Include test projects if applicable

3. **Share this file** with the template maintainers
   - Attach `docs/template_feedback.md` to the issue
   - Or copy relevant sections into the issue body

When submitting, always reference:
- This project name and repository
- Template version used (`0.1.0`)
- Date range of feedback collection
```

---

## Example Feedback Item

```markdown
### Missing Trailing Newline in Workflow Files

- **Priority**: Low
- **Category**: CI/CD
- **Discovered**: 2024-11-24
- **Template Version**: 0.1.0

**Issue**: Several GitHub workflow files are missing trailing newlines, causing
pre-commit hooks to fail on first run after project generation.

**Context**: After generating a new project and running `pre-commit run --all-files`,
the end-of-file-fixer hook modified multiple workflow files.

**Suggested Fix**: Add trailing newlines to all template workflow files in
`mtg_ai/.github/workflows/`.

**Affected Files**:
- `mtg_ai/.github/workflows/ci.yml`
- `mtg_ai/.github/workflows/release.yml`
- `mtg_ai/.github/workflows/docs.yml`

**Workaround**: Run `pre-commit run --all-files` after project generation to auto-fix.
```

---

## Merge Instructions

When `.standards/template_feedback.baseline.md` is updated by cruft:

1. **Compare format sections** - Update the "How to Use" section in your feedback file
2. **Review categories** - Add any new categories to your reference
3. **Check submission instructions** - Update links if they've changed
4. **Preserve your feedback** - NEVER overwrite actual feedback items

**What to merge:**
- Format template updates
- New categories or priority definitions
- Updated submission instructions
- Example improvements

**What NOT to merge:**
- Your actual feedback items
- Your project-specific notes
- Any local workarounds documented

---

*This baseline is automatically updated by cruft. Merge changes into docs/template_feedback.md.*
