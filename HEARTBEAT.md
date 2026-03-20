# HEARTBEAT.md

# Quota warning monitor

- Check `/status` usage (session_status) on each heartbeat.
- If **day remaining < 25%** OR **week remaining < 25%**, send an alert in this channel with current remaining % and ETA.

# OAuth failure detector (openai-codex)

- On each heartbeat, check recent gateway logs for this error text:
  - `OAuth token refresh failed for openai-codex`
- Keep de-dup state in `memory/oauth-monitor-state.json` so the same failure is not posted repeatedly.
- If a *new* failure is detected, send a Discord alert to channel `1481012976688431224` with:
  - what failed
  - likely reason: provider-side token/session rotation or invalidation
  - re-auth steps:
    1) `openclaw configure --section model`
    2) complete browser OAuth for `openai-codex`
    3) `openclaw doctor --non-interactive`
  - reassurance that this is usually provider-session churn, not user prompt quality.

- If no quota alert and no new OAuth failure alert is needed, reply `HEARTBEAT_OK`.
