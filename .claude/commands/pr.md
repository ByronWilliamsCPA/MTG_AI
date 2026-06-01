# Prepare Pull Request

Analyze the current branch and prepare a PR description following the project template.

## Instructions

1. **Gather context** by running these commands:
   - `git status` - see uncommitted changes
   - `git log $(git merge-base HEAD main)..HEAD --oneline` - commits on this branch
   - `git diff $(git merge-base HEAD main)..HEAD --stat` - files changed summary
   - `git diff $(git merge-base HEAD main)..HEAD` - actual changes (if not too large)

2. **Analyze the changes**:
   - What components were modified?
   - What is the purpose/motivation?
   - Are there breaking changes?
   - What testing was done or is needed?

3. **Generate PR description** using this template:

````markdown
## Summary

<!-- Brief description: what changed and why -->

## Changes

- **Component**: What changed and why

## Impact

- ✅ [Key benefit or outcome]
- ✅ No breaking changes

## Testing

- [ ] Tests pass (`uv run pytest`)
- [ ] Linting passes (`uv run ruff check`)

## Notes

<!-- Optional: known issues, follow-up work -->
````

4. **Output the PR description** ready to copy-paste into GitHub.

5. **Suggest a PR title** following conventional commits:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation
   - `refactor:` for code restructuring
   - `test:` for test additions
   - `chore:` for maintenance

## Example Output

**Title**: `feat: add user authentication with OAuth2`

**Description**:
```
## Summary

Add OAuth2 authentication flow supporting Google and GitHub providers.

## Changes

- **auth/oauth.py**: New OAuth2 client implementation
- **api/routes/auth.py**: Login/logout endpoints
- **config.py**: OAuth provider configuration

## Impact

- ✅ Users can now sign in with Google or GitHub
- ✅ Session management with secure cookies
- ✅ No breaking changes to existing API

## Testing

- [x] Tests pass (`uv run pytest`)
- [x] Linting passes (`uv run ruff check`)
- [x] Manual testing with both providers

## Notes

Follow-up: Add Microsoft provider support (tracked in Linear)
```
