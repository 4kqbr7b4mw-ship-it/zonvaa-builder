# Codex Execution Operative Policy

Version: 1.0
Status: active
Normstufe: C3

## Capacity retries

- A new confirmed prompt may be started once automatically.
- Only `WAITING_FOR_CAPACITY` may be retried automatically.
- At most two automatic retries are permitted.
- Automatic retries wait at least 900 seconds after the previous attempt.
- `FAILED` and `BLOCKED` require an explicit retry.
- `CANCELLED` and `SUCCEEDED` are never retried.
- The same workflow is never executed concurrently.

These values are operative C3 settings. They do not change Chief-Architect
authority, prompt approval, security boundaries or the prohibition on push.
