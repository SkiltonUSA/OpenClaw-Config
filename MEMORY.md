# MEMORY.md - Long-Term Memory

## 2026-03-08

- Reviewed OpenClaw docs for:
  - Multi-Agent Routing (`/concepts/multi-agent`)
  - Gateway Architecture (`/concepts/architecture`)
  - Agent Runtime (`/concepts/agent`)
  - Agent Loop (`/concepts/agent-loop`)
- Key understanding captured:
  - Multi-agent isolation depends on separate workspace + `agentDir` + session store per `agentId`.
  - Routing is deterministic and “most-specific wins” (peer > parentPeer > roles/guild/team > account > channel > default).
  - Omitting `accountId` in a binding matches default account only; `accountId: "*"` is channel-wide across accounts.
  - Workspace is default cwd, not a hard sandbox unless sandboxing is enabled.
  - Gateway is the central long-lived daemon and WS control plane; first frame must be `connect`.
  - Idempotency keys are required for side-effecting methods like `send`/`agent` for safe retries.
  - Events are not replayed; clients must refresh on gaps.
  - Agent runtime injects bootstrap files (`AGENTS.md`, `SOUL.md`, `TOOLS.md`, `BOOTSTRAP.md`, `IDENTITY.md`, `USER.md`) on first turn, with truncation/missing-file markers.
  - Core tools are policy-controlled; `TOOLS.md` is guidance only (not tool enablement).
  - Skills resolve from bundled + `~/.openclaw/skills` + `<workspace>/skills` (workspace wins on name conflicts).
  - Agent loop is serialized per session lane; queue modes (`steer`/`followup`/`collect`) control interruption behavior.
  - Stream model: `assistant`, `tool`, `lifecycle`; `agent.wait` waits for lifecycle end/error only.
  - `NO_REPLY` is treated as a silent token; duplicate messaging confirmations are suppressed.
  - Runtime timeout and wait timeout are distinct (`agent.wait` timeout does not stop the running agent).
  - System prompt is OpenClaw-owned per run, supports `full|minimal|none` prompt modes, and injects bootstrap/workspace context with configurable truncation caps.
  - Context budget is dominated by system prompt + tool schemas + injected files + history/tool results; `/context list` and `/context detail` are the primary diagnostics.
  - Workspace is memory/home but not a hard boundary; true isolation is enforced by sandboxing/tool policy, not cwd defaults.
  - Presence is a best-effort in-memory view of gateway + connected clients/nodes; stable `instanceId` is required to avoid duplicate presence rows.
  - User rule: before modifying `~/.openclaw/openclaw.json`, always create a backup first using suffix convention `openclaw.json-bak-<name><DDMMYYYY>` (example: `openclaw.json-bak-hal03082026`, using DSK-style date convention).

## 2026-03-19

- Confirmed Skylight integration pattern in this workspace/runtime:
  - Direct API access works reliably when `env.vars` includes `SKYLIGHT_URL`, `SKYLIGHT_EMAIL`, `SKYLIGHT_PASSWORD`, and `SKYLIGHT_FRAME_ID`.
  - After adding these via OpenClaw `config.patch`, gateway restart is required for runtime availability.
  - Browser Relay is not required for Skylight when API env vars are configured.
  - In Discord, generic prompts may still fall back to Browser Relay messaging; explicitly instructing API/env-var usage resolves it.

## 2026-03-09

- User completed OpenClaw npm upgrade and restart; instructed me to run post-upgrade check with `openclaw doctor --non-interactive`.
- Diagnosed post-upgrade token mismatch: gateway service had embedded stale `OPENCLAW_GATEWAY_TOKEN` after onboarding/restart, causing CLI unauthorized probe failures.
- Confirmed model split requirement and current config:
  - default model remains OpenAI Codex (`openai-codex/gpt-5.3-codex`)
  - `mathew` agent uses Anthropic (moved from `claude-sonnet-4-5` to `claude-sonnet-4-6` during troubleshooting).
- Ran repeated live tests against `mathew` (`2+2`) while user watched logs:
  - initial failures: Anthropic billing/credit error
  - intermediate failures: invalid authentication credentials / invalid `x-api-key`
  - after user fixed key/account issue, test succeeded and returned `4` on Anthropic Sonnet 4.6.
- Important safety note reinforced: API keys were pasted in chat during setup; treat as exposed and rotate after successful configuration.

## 2026-03-20

- Added model failover for main defaults to reduce impact of OpenAI Codex OAuth refresh outages:
  - `agents.defaults.model.primary`: `openai-codex/gpt-5.3-codex`
  - `agents.defaults.model.fallbacks`: `anthropic/claude-sonnet-4-6`, `gemini_api/gemini-2.5-pro`
- Established operational response pattern for codex OAuth failures:
  - Discord alert target: channel `1481012976688431224`
  - Re-auth sequence: `openclaw configure --section model` → browser OAuth for `openai-codex` → `openclaw doctor --non-interactive`
- Added heartbeat-driven OAuth failure detector instructions to `HEARTBEAT.md` with de-dup state file `memory/oauth-monitor-state.json`.
