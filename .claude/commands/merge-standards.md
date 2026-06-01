# Merge Baseline Standards

After running `cruft update`, merge any changes from `.standards/` into project files.

## Task

1. Check for changes in baseline files:
   ```bash
   git diff .standards/
   ```

2. If changes exist, merge them into the corresponding root files:
   - `.standards/CLAUDE.baseline.md` → `CLAUDE.md`
   - `.standards/REUSE.baseline.toml` → `REUSE.toml`

3. For CLAUDE.md:
   - Update the "BASELINE DEVELOPMENT STANDARDS" section (between HTML comment markers)
   - Preserve all project-specific sections

4. For REUSE.toml:
   - Add any new baseline annotation paths
   - Update existing baseline annotations
   - Preserve any project-specific annotations the user added

5. Show the proposed changes and ask for confirmation before applying.

## Important

- NEVER remove project-specific customizations
- ALWAYS preserve sections not in the baseline
- If unsure, ASK the user before making changes
