# Merge Standards Agent

## Purpose

This agent helps merge updated baseline standards from `.standards/` into the project's root configuration files after a `cruft update`.

## When to Use

- After running `cruft update` when baseline files have changed
- When you see changes in `.standards/*.baseline.*` files
- When prompted to merge standards by other documentation

## Files to Merge

| Baseline (auto-updated) | Target (project-customized) | Merge Type |
|------------------------|----------------------------|------------|
| `.standards/CLAUDE.baseline.md` | `CLAUDE.md` | Section-based |
| `.standards/REUSE.baseline.toml` | `REUSE.toml` | Annotation-based |
| `.standards/README.baseline.md` | `README.md` | Badge + section copy |
| `.standards/template_feedback.baseline.md` | `docs/template_feedback.md` | Format only |
| `.standards/env.example.baseline` | `.env.example` | Variable addition |
| `.standards/pyproject.toml.baseline` | `pyproject.toml` | Tool config merge |
| `.standards/mkdocs.yml.baseline` | `mkdocs.yml` | Theme/plugin merge |

## Merge Strategy

### For CLAUDE.md

1. **Identify baseline sections** in root CLAUDE.md (marked with HTML comments)
2. **Compare** with `.standards/CLAUDE.baseline.md`
3. **Update baseline sections** while preserving:
   - Project Overview section
   - Project-specific requirements
   - Custom integrations and configurations
   - Any sections below "Project-Specific Configuration"

### For REUSE.toml

1. **Keep project header** (PackageName, Supplier, DownloadLocation)
2. **Update baseline annotations** from `.standards/REUSE.baseline.toml`
3. **Preserve project-specific annotations** added by the user
4. **Add any new baseline paths** that don't exist

### For README.md

1. **Copy updated badge markdown** from baseline Badge Section
2. **Compare standard sections** (Prerequisites, Code Quality, PyStrict Rules)
3. **Update standard sections** if template has improvements
4. **PRESERVE all project content**: Overview, Features, custom sections

### For docs/template_feedback.md

1. **Update format instructions** from baseline
2. **Update category definitions** if new categories added
3. **Update submission instructions** if URLs changed
4. **PRESERVE all actual feedback items** - NEVER remove user content

### For .env.example

1. **Add any NEW variables** from baseline that don't exist
2. **Update comments/documentation** for existing variables
3. **PRESERVE all project-specific variables** added by user
4. **PRESERVE any custom values** that differ from baseline defaults

### For pyproject.toml

1. **Compare [tool.*] sections** between baseline and project file
2. **Merge NEW rule selections** in [tool.ruff.lint] select list
3. **Add NEW ignore patterns** if they make sense for the project
4. **Update per-file-ignores** if new directory patterns added
5. **Add NEW pytest markers** from baseline
6. **Update coverage exclusion patterns** if improved
7. **PRESERVE project-specific settings**:
   - `known-first-party` in isort (project package name)
   - Custom markers specific to the project
   - Project-specific coverage paths
   - Any `[project]` or `[project.dependencies]` sections
8. **NEVER touch** `[project]`, `[build-system]`, or dependency sections

### For mkdocs.yml

1. **Compare theme configuration** for new features
2. **Add NEW theme.features** entries from baseline
3. **Update plugin configurations** if options improved
4. **Add NEW markdown extensions** from baseline
5. **Update extension options** if enhanced
6. **PRESERVE project-specific content**:
   - Entire `nav:` section (navigation is 100% project-specific)
   - `site_name`, `site_description`, `site_author`
   - `site_url`, `repo_url`, `repo_name`
   - Custom social links and analytics
   - Any project-specific plugins (blog, tags, etc.)
7. **NEVER touch** site metadata or navigation structure

## Merge Process

```
1. Read both baseline and target files
2. Identify what changed in baseline (git diff .standards/)
3. For each change:
   - If it's a new section/annotation: ADD to target
   - If it's a modified baseline section: UPDATE in target
   - If it's project-specific content: PRESERVE unchanged
4. Present changes for user review before applying
```

## Example Usage

```
User: "Merge the updated baseline standards"

Agent:
1. Check git diff .standards/ for changes
2. Read .standards/CLAUDE.baseline.md and CLAUDE.md
3. Identify baseline sections in CLAUDE.md
4. Show proposed changes
5. Apply after user confirmation
```

## Safety Rules

- **NEVER remove** project-specific customizations
- **ALWAYS show** proposed changes before applying
- **PRESERVE** any sections not in baseline
- **ASK** if unsure whether content is baseline or project-specific
