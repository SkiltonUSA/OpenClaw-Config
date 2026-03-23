# GSD Guardrails for HAL Agentic Stack

Status: Active (Pilot)
Owner: HAL
Last Updated: 2026-03-23

## Purpose

Adopt `get-shit-done` (GSD) as a planning/execution framework **without** weakening safety, approval, or change-control standards in this workspace.

---

## 1) Allowed Use (Green)

Use GSD for:

- Spec artifacts and planning structure:
  - `PROJECT.md`
  - `REQUIREMENTS.md`
  - `ROADMAP.md`
  - phase context/plans/research docs
- Phase-based implementation for medium/large projects
- Verification/UAT loops prior to merge
- Codex skill-style workflow where supported

---

## 2) Controlled Use (Yellow)

Allowed with constraints:

- Parallel execution/subagents:
  - default max concurrency: **2 writers at a time**
- Per-task commits:
  - required on feature branches only
  - commit messages must be explicit and reviewable
- Global installs:
  - only after local pilot passes and is approved

---

## 3) Prohibited Use (Red)

Do **not** use:

- `--dangerously-skip-permissions`
- blanket permission escalation in primary environments
- unattended production infra changes
- auto-deploy without explicit human approval

---

## 4) Mandatory Approval Gates

Human approval required before:

1. configuration changes
2. secret or credential changes
3. environment variable changes affecting runtime behavior
4. external side effects (deployments, outbound notifications, destructive commands)
5. edits to OpenClaw gateway config/runtime unless explicitly requested

---

## 5) Pilot Implementation Policy

Pilot scope:

- one non-critical project
- feature branch only
- local/project-scoped setup only

Execution policy during pilot:

- tests + lint required before completion
- no direct deploy commands
- all changes must be commit-traceable

Exit criteria:

- reduced rework vs current flow
- clean and understandable commit history
- no safety regressions
- predictable quality across at least 2 phases

---

## 6) Operational Defaults

- OpenClaw approvals remain source-of-truth policy.
- GSD is a workflow layer, **not** a policy authority.
- If workflow instructions conflict with local safety policy, local safety policy wins.

---

## 7) Quick Runbook

1. Start with planning artifacts (requirements/roadmap).
2. Discuss and lock phase context before execution.
3. Execute in small waves, max 2 writing tasks in parallel.
4. Verify and run UAT before calling phase complete.
5. Commit with clear messages; no push/deploy without approval.

---

## 8) Change Control

Any change to this file requires:

- rationale in commit message
- explicit mention of risk impact
- rollback note when behavior changes are significant
