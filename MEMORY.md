# MEMORY.md - Long-Term Memory

## 2026-03-08

- Reviewed OpenClaw docs for:
  - Multi-Agent Routing (`/concepts/multi-agent`)
  - Gateway Architecture (`/concepts/architecture`)
- Key understanding captured:
  - Multi-agent isolation depends on separate workspace + `agentDir` + session store per `agentId`.
  - Routing is deterministic and “most-specific wins” (peer > parentPeer > roles/guild/team > account > channel > default).
  - Omitting `accountId` in a binding matches default account only; `accountId: "*"` is channel-wide across accounts.
  - Workspace is default cwd, not a hard sandbox unless sandboxing is enabled.
  - Gateway is the central long-lived daemon and WS control plane; first frame must be `connect`.
  - Idempotency keys are required for side-effecting methods like `send`/`agent` for safe retries.
  - Events are not replayed; clients must refresh on gaps.
