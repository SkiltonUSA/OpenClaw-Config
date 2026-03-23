# GSD Pilot Checklist

Status: Ready
Owner: HAL
Date: 2026-03-23

## Pilot Scope

- Project: ______________________________
- Branch: `feature/gsd-pilot-________________`
- Risk Level: Non-critical only
- Pilot Window: _________________________

---

## 1) Pre-Flight

- [ ] Confirm project is non-critical (no prod infra impact)
- [ ] Confirm working branch is created
- [ ] Confirm `GSD-GUARDRAILS.md` is present and current
- [ ] Confirm approval gates understood (config/secrets/external effects)
- [ ] Confirm max concurrency set to 2 writing tasks

---

## 2) Planning Setup

- [ ] Create/refresh `PROJECT.md`
- [ ] Create/refresh `REQUIREMENTS.md`
- [ ] Create/refresh `ROADMAP.md`
- [ ] Mark explicit v1 / v2 / out-of-scope boundaries
- [ ] Capture assumptions and open questions

---

## 3) Phase Execution Rules

- [ ] Run work in small waves
- [ ] Keep max 2 parallel writing tasks
- [ ] Require tests + lint before phase completion
- [ ] No deploy commands during pilot
- [ ] No gateway/config/runtime edits unless explicitly approved

---

## 4) Commit Hygiene

- [ ] Atomic commits per meaningful task
- [ ] Clear commit messages (intent + scope)
- [ ] No direct push to protected branches
- [ ] Include rollback notes for risky changes

---

## 5) Verification / UAT

- [ ] Generate or update verification notes per phase
- [ ] Run user-facing UAT checklist
- [ ] Log defects and create fix tasks/plans
- [ ] Re-verify after fixes

---

## 6) Pilot Exit Review

Score each 1–5 (5 is best):

- Rework reduction vs current workflow: __
- Output quality consistency: __
- Commit history clarity: __
- Safety/approval compliance: __
- Throughput/turnaround: __

Pass threshold (recommended):

- No safety regressions
- Average score >= 4
- At least 2 completed phases

Decision:

- [ ] Pass → propose broader adoption
- [ ] Partial → keep for selected project types only
- [ ] Fail → rollback to prior workflow

---

## 7) Notes / Evidence

- Links to PRs/branches:
  - ____________________________________
- Key lessons:
  - ____________________________________
- Follow-up actions:
  - ____________________________________
