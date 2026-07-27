# Talk Track — Cursor Development Framework

---

## 1. What I Built

**Cue:** “I built an in-repo Cursor framework for scikit-image.”

- Goal: help people (and AI agents) contribute correctly — right files, right commands, fewer risky mistakes
- Constraint: **repo + Cursor only** — no third-party security products or external tool config
- Outcome: a **layered** system — guidance where agents need it, enforcement where mistakes are costly
- Not a rewrite of CONTRIBUTING — we **link** to it; Cursor layers stay thin

---

## 2. What I Focused On

**Cue:** “The MVP focuses on five themes.”

- **Functional Value Across SDLC** - Does it help teams complete work faster without sacrificing quality?
- **Collaboration** - Can it reduce handoff friction and improve shared understanding across roles and teams?
- **Governance & Auditability** - Can we establish clear usage guidelines and demonstrate what actions were taken?
- **Security** - Because agents can execute shell commands, modify files, and access networks, what local safeguards are required?
- **Maintainability & Reusability** - Can the framework be maintained efficiently and adapted to other projects?

---

## 3. Design Principles

**Cue:** “Three principles drove every choice.”

1. **Stay minimal** — rules only when agents pick the wrong file/command or make repo-specific mistakes CI won’t catch
2. **Link, don’t paste** — CONTRIBUTING stays authoritative; AGENTS/skills/rules point there instead of copying policy
3. **Guidance vs enforcement**
   - Rules + skills = how to behave
   - Hooks + scripts = what actually gets blocked or approved
   - One canonical place per concern (hooks for deny/ask; rules summarize)

---

## 4. Architecture

**Cue:** “Think of it as a stack, top to bottom.”

```
AGENTS.md (always on)
  → Persona (Developer / PM / QA)
  → Routing rules → workflow skills (first PR, pre-PR, tests)
  → File-scoped rules when editing src/ or tests/
  → Security rule + hooks (shell / file edits / MCP)
```

| Layer                        | What it does                                                                   |
| ---------------------------- | ------------------------------------------------------------------------------ |
| **AGENTS.md**                | Charter: sources of truth, package layout, `spin`, verify before claiming done |
| **Personas**                 | One mode per chat — Developer codes; PM/QA don’t implement                     |
| **Skills**                   | Step-by-step playbooks (first contribution, pre-PR gate, scaffold tests)       |
| **Scoped rules**             | Conventions only when editing `src/**` or `tests/**`                           |
| **Hooks**                    | Hard guardrails: destructive git/shell, protected paths, network asks          |
| **validate-contribution.sh** | Local pre-PR check: heuristics + pre-commit + `spin test --test-modified`      |

**Maintainer map:** `.cursor/README.md` — where to put future changes.

---

## 5. Governance Choices

**Cue:** “We deliberately shipped a small set.”

**Shipped:**

- AGENTS.md — always-on routing
- `skimage-source.mdc` — `src/**` (API, deprecations, Cython)
- `skimage-tests.mdc` — `tests/**` (RNG, threading, matching test trees)

**Skipped for now** (unless pain shows up):

- Separate meson / gallery / Cython-only / wrapper-only rules
- Always-on “baseline” rule duplicating AGENTS
- Copying full stylistic guidelines into agent files

**Reliability habits baked into AGENTS:**

- Sources of truth = **this repo + stable docs only** (no guessing APIs)
- Read before edit; minimal diffs; verify with `spin` before claiming tests pass

**Why dual-package layout is called out:** `_skimage2` = implementations; `skimage` = v1 wrappers; tests split the same way — agents otherwise edit the wrong layer.

---

## 6. Security

**Cue:** “Guardrails are local and layered.”

| Layer                    | When it runs                                  |
| ------------------------ | --------------------------------------------- |
| Cursor hooks             | In the agent session (shell, file edits, MCP) |
| pre-commit + secret scan | At commit                                     |
| CODEOWNERS               | At PR (needs org branch protection)           |

**What hooks do:**

- **Deny** destructive git/shell, hook bypass (`--no-verify`), audit/`.git` edits
- **Ask** (approval card) for git writes, direct network (`curl`/`wget`), protected-path edits
- **Not** blocking indirect network (`pip`, `spin install`, `git pull`) — by design

**Protected paths:** framework files, CI, deps manifests, entire `.cursor/skills/**` — canonical list in `protected_paths.py`

**Soft Admin:** Admin persona may _intend_ to edit governance files; hooks still **ask everyone**. Persona ≠ authentication; hooks don’t see chat persona.

---

## 7. Audit

**Cue:** “We log signal, not noise.”

- Append-only JSONL at `.cursor/audit/` (gitignored, local only)
- Log **deny + ask only** — not every allow (`spin test` doesn’t spam the log)
- Records **attempts that hit guardrails**, not whether the user clicked Approve
- Shared helper `audit_log.py`; failures must not break hooks

---

## 8. Personas & Workflows

**Cue:** “Same framework serves different roles.”

**Personas** (explicit only — agent asks once, then sticks):

- **Developer** — implement, test, contribute
- **PM** — issues / acceptance criteria; no code
- **QA** — test plans / verification checklists
- **Admin** — soft governance (policy intent; hooks still ask)

**Key workflows:**

1. **First contribution** — prefers `:beginner: Good first issue`; scoped change; handoff to pre-PR
2. **Pre-PR gate** — runs `validate-contribution.sh`; PR metadata checklist (AI disclosure, labels)
3. **Scaffold tests** — right test tree + weak-test checklist

First contribution requires **Developer** — we don’t let PM/QA drive a code PR path by accident.

---

## 9. Design Choices

**Cue:** “These are the tradeoffs I’d highlight.”

| Choice                                     | Why                                                 |
| ------------------------------------------ | --------------------------------------------------- |
| Minimal rules, not a CONTRIBUTING mirror   | Less drift; agents stay focused                     |
| Routing rules stay thin → load a skill     | Procedures live in one place for maintainability    |
| Deny destructive; ask on network/protected | Safety without blocking normal work                 |
| Soft Admin, not hard persona enforcement   | Hooks can’t see persona without extra session state |
| Audit deny/ask only, no after-hooks        | Simpler; still useful for compliance review         |
| Cursor-only first contribution path        | Fast MVP; no bots/Zulip/issue-form work             |

---

## 10. What’s Next

**Cue:** “MVP is in place; a few ops and optional hardenings remain.”

- Create a reusable package that can recreate a similar framework in other projects
- Add guided onboarding capability to make sure new developers have the necessary base understanding of the project
- Tighten security (hard deny protected changes, network allow lists, configure CODE_OWNERS with GH rules, etc...)
- Add additional personas like SecOps for policies and Admin for framework changes, etc...

---

## Demo runbook (~8–12 min)

Audience cares about **business value**: SDLC friction, security/governance, onboarding speed — not architecture deep-dives. Narrate outcomes at each step.

### Prep

- Branch with the framework loaded; Cursor hooks enabled
- Prefer **fresh chats** so persona ask is visible
- Optional: side pane ready for `.cursor/audit/audit.jsonl`
- Don’t implement a full feature live — show routing, guardrails, and the local gate

### Sequence

| Step                           | Do                                                                                                                    | Say / highlight                                                                                                                                                                    |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **0. Frame** (60–90s)          | No click — set context                                                                                                | AI helps velocity _and_ creates risk (wrong files, skipped checks, destructive shell). This is a **thin in-repo control plane** so AI follows how we already ship.                 |
| **1. Personas** (1–2 min)      | New chat → agent asks Dev / PM / QA                                                                                   | Same IDE, role-appropriate work. Cuts handoff friction; explicit mode = light governance. Optional: choose **PM**, ask for acceptance criteria — show it doesn’t jump into `src/`. |
| **2. Onboarding** (2–3 min)    | As **Developer**: “Help me with my first PR”                                                                          | Playbook, not blank chat. Prefers `:beginner: Good first issue`. Guides setup → scoped change → verify → PR. **Value:** faster time-to-first-PR, less senior babysitting.          |
| **3. SDLC friction** (1–2 min) | One prompt only: “Where should a new algorithm live?” _or_ “Add tests for …”                                          | Right layer (`_skimage2` vs `skimage`), right test tree, `spin` not raw pytest. **Value:** less rework in review/CI.                                                               |
| **4. Security** (2–3 min)      | (a) Agent edits `AGENTS.md` / a skill without you asking → **ask** card. (b) Destructive or `--no-verify` → **deny**. | In-session guardrails. Deny vs ask. Layered with pre-commit + CODEOWNERS. Soft Admin still needs human approve. **Value:** AI coding without a blank check.                        |
| **5. Audit** (45–60s)          | Open audit log after deny/ask                                                                                         | High-signal trail only (deny/ask), not every allow. **Value:** reviewable AI-assisted activity.                                                                                    |
| **6. Pre-PR gate** (1–2 min)   | “Validate my branch” / “ready to open a PR”                                                                           | Runs `validate-contribution.sh` (heuristics + pre-commit + `spin test --test-modified`). **Value:** checks left; cleaner PRs before human review.                                  |
| **7. Close** (30–45s)          | Roll up the table below                                                                                               | MVP is repo-owned; next is reuse across projects (§10), not a new platform.                                                                                                        |

### Value roll-up (close)

| They care about | What you showed                                |
| --------------- | ---------------------------------------------- |
| Onboarding      | First-PR skill + persona + repo routing        |
| SDLC friction   | Right layer, tests, pre-PR validate            |
| Security        | Deny/ask hooks, protected paths                |
| Governance      | Personas, protected framework files, audit log |
| Maintainability | Thin layers over CONTRIBUTING                  |

### Short room (~6 min)

**Must-show:** persona ask → first-PR prompt → protected-path **ask** → peek audit → one-liner on validate script. Skip architecture unless asked.

### Don’t demo live

- Full feature implementation or long test runs
- Deep dive into hook Python / every `.mdc`
- Hard Admin-only enforcement (not shipped — soft ask by design)
