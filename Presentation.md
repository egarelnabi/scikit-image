# Presentation

## Governance

### What we started from

You asked what from the scikit-image repo would make good **Cursor rules** and **AGENTS.md** material. The first pass was a long menu (architecture, `spin`, Cython, meson, gallery, deprecations, dispatching, etc.).

### Main decision: stay minimal

We agreed **not** to mirror CONTRIBUTING or add many scoped rules.

**Ship set:**

| Artifact                             | Role                                                                 |
| ------------------------------------ | -------------------------------------------------------------------- |
| **AGENTS.md**                        | Repo-wide routing: sources of truth, workflow, `spin`, PR/AI policy  |
| **`.cursor/rules/skimage-core.mdc`** | `src/**` — layout, style, API changes, warnings/deprecations, Cython |
| **`.cursor/rules/tests.mdc`**        | `tests/**` — layout, helpers, RNG, threading, `spin test`            |

**Deferred / skipped (unless pain shows up later):**

- Separate rules for meson, gallery, deprecations, Cython-only, wrappers-only
- **alwaysApply** baseline rule (only if agents still guess with no repo files open)
- Backend dispatching, full benchmark/ASV copy in rules
- Duplicating stylistic guidelines or env setup in AGENTS.md

**Principle:** Put guidance in rules only when agents **pick the wrong file/command** or make **repo-specific** mistakes CI won’t prevent.

### Content decisions (by topic)

#### Sources of truth

- **Decision:** Agents use **only** this repo + [scikit-image stable documentation](https://scikit-image.org/docs/stable/); no guessing or external sources.
- **Placement:** **AGENTS.md** only (not a duplicate always-on rule unless needed later).
- **Uncertainty:** Folded into that section — say what you checked, what's unknown, ask.

#### Architecture

- **`_skimage2`** = implementations; **`skimage`** = v1 wrappers; tests split **`tests/skimage/`** vs **`tests/skimage2/`**.
- **Decision:** Table + rule of thumb in **AGENTS.md**; “where code goes” again in **`skimage-core.mdc`** (on purpose — rule only loads for `src/**`).

#### Build & test

- **Decision:** **`spin`** only (not raw pytest/meson); `--test-modified` for PR-like runs; meson + rebuild note in AGENTS.md; **`src/` as test path** documented in **AGENTS.md only** (removed from `tests.mdc` after review).

#### Reliability additions (the “1–5” plan)

| Item                        | Decision | Where                                                     |
| --------------------------- | -------- | --------------------------------------------------------- |
| Verify before claiming done | Adopted  | AGENTS.md — Verification                                  |
| Read before edit            | Adopted  | AGENTS.md                                                 |
| Minimal / focused diffs     | Adopted  | AGENTS.md — Scope                                         |
| API change guardrails       | Adopted  | **`skimage-core.mdc` only** — not duplicated in AGENTS.md |
| Uncertainty protocol        | Adopted  | Merged into Sources of truth in AGENTS.md                 |

**Extra:** One line in **`tests.mdc`**: behavior changes need tests in the matching tree.

**Clarification:** API guardrails were partially already in `skimage-core` (deprecation helpers); we added the missing bullets (tests, wrappers + both trees, `__all__`) without repeating the full deprecation story in AGENTS.md beyond the PR one-liner + CONTRIBUTING link.

### Review & trim (final polish)

We reviewed all three files and concluded they were **ship-ready** with two small dedups:

1. Removed duplicate “breaking changes → deprecation cycle” from **API changes** (kept under **Warnings and deprecations**).
2. Removed **`src/` test path** from **`tests.mdc`** (kept in AGENTS.md).

**Left as acceptable overlap:** package layout in AGENTS + `skimage-core`; PR deprecation pointer vs implementation details in the rule; short `spin test` examples in `tests.mdc` for context when editing tests.

### Options we discussed but did not take (yet)

- **alwaysApply** rule bundling verify + read-before-edit + sources of truth
- **Rename “Scope”** → “Change scope” (cosmetic; not done)
- Merge Verification into Build and test (optional; kept separate)
- Merge API changes + Warnings sections in `skimage-core` (optional; kept separate)

### Outcome

A **small, layered** agent setup: one charter file (~80 lines) + two file-scoped rules, aligned with CONTRIBUTING via links instead of copying it, focused on scikit-image’s dual-package layout and agent failure modes (wrong layer, no `spin`, invented APIs, weak tests, claiming pass without running checks).

## Security

### What we set out to do

Reduce risk of **agents or developers** doing destructive or high-impact actions in scikit-image, using **repo-local Cursor hooks**, rules, pre-commit, and optionally **CODEOWNERS** — no third-party security products.

### Top priorities (agreed)

**Do first:** shell hooks, git policy in repo, secret scanning at commit.

**Do next:** protected paths, self-weakening guardrails, CI path protection.

**Later / situational:** dependency gates, MCP/browser, broad network allowlists.

| Layer        | Role                                  |
| ------------ | ------------------------------------- |
| Cursor hooks | In-session: shell, file edits, MCP    |
| pre-commit   | At commit: secrets, existing zizmor   |
| CODEOWNERS   | At PR merge (needs branch protection) |

**Decisions:** Cursor-only enforcement works without CODEOWNERS; **local machine** scope = hooks + pre-commit, minus CODEOWNERS only.

### What we built (implemented)

- **`.cursor/hooks.json`** — `beforeShellExecution`, `preToolUse`, `beforeMCPExecution` (`failClosed: true`)
- **`before-shell.py`** — deny destructive git/shell; **ask** git writes, clean, **direct network** (`curl`/`wget`/…)
- **`protect-paths.py`** + **`protected_paths.py`** — canonical globs; audit/git deny; protected + skills → **ask**
- **`before-mcp.py`** — **ask** on browser/fetch-like MCP tools
- **`security.mdc`** + **AGENTS.md** pointer
- **`tools/check_secrets.py`** + pre-commit **`detect-private-key`**
- **`.gitignore`** secret patterns
- **`CODEOWNERS`** on sensitive paths (`@scikit-image/core` placeholder)
- **Admin persona** + skills/routing in repo (framework evolved; see below)

**Bootstrap lesson:** Hook scripts must run via `python3 …/script.py` (not bare paths) to avoid `failClosed` lockout when files aren’t executable.

**`check_secrets.py` in `tools/`** — pre-commit runner, not a Cursor hook; same pattern as `generate_requirements.py`.

### Network policy (decisions)

- Scope: **direct** network only (`curl`, MCP fetch/browser) — **ask**, not deny (except existing `curl|sh` **deny**).
- **Not** in scope: `pip`, `spin install`, `git pull` (indirect network).
- Host **allow-list** deferred — hooks only see command strings, not sockets; implicit tools need extra rules.
- **Deny vs ask:** kept **deny** for destructive actions; direct network uses **ask** only.

### Audit logs (decisions)

- **Append-only** via hooks; agent **writes denied**.
- **Reads allowed** (reversed earlier “block reads” design); removed `deny-audit-read` / `beforeReadFile`.
- Shell no longer blocks `.cursor/audit` paths.
- **`.gitignore`** `.cursor/audit/` — local, not committed.

### Persona, skills, governance (decisions)

- **Hook-protected (ask):** hooks, `security.mdc`, persona/first-contribution/pre-pr-gate rules, **entire `.cursor/skills/**`, AGENTS, CI, CODEOWNERS, pre-commit, deps manifests.
- **Not hook-protected (by design):** `tools/cursor/validate-contribution.sh`, `skimage-source` / `skimage-tests` rules, `.cursor/README.md` (optional to add; **CODEOWNERS** still covers `/.cursor/`).
- **Personas:** Developer · PM · QA · **Admin** — routing in `persona.mdc`; Admin for governance edits in **policy**, hooks still **ask everyone** (**soft Admin**).

**Hard deny non-Admin on protected paths:** discussed; **not implemented** — hooks don’t see chat persona.

### Architecture / refactors (decisions)

- **Merged `repo_paths.py` into `protect-paths.py`** — fine; only one consumer.
- **Kept `protected_paths.py` separate** — data vs hook behavior; `security.mdc` links to it.
- **YAML under `.cursor/`** for path lists — discussed as cleaner later; **stayed Python** for MVP.

### Admin + persona enforcement (discussed, not built)

| Option                                                      | Tradeoff                                                         |
| ----------------------------------------------------------- | ---------------------------------------------------------------- |
| **Deny all protected edits** (no new files)                 | Hard enforcement; Admin also blocked via agent                   |
| **Rules only**                                              | No extra files; user can still approve non-Admin                 |
| **Session tracking** (`beforeSubmitPrompt` + per-chat JSON) | Enables Admin **ask**, others **deny**; needs extra hook + state |

**Parallel chats:** one global persona file = **shared**; per-`conversation_id` files = **one persona per chat** (preferred if you build tracking).

**Persona ≠ authentication** — session file is UX/enforcement hint, not identity.

### Still on you (ops)

- Replace **`@scikit-image/core`** in CODEOWNERS; enable **branch protection** + code-owner review.
- Run **`pre-commit install`** locally.
- Commit framework files when ready.
- Choose next step: **deny-all protected** MVP vs **track-persona** for Admin-only **ask**.

### Outcome (security arc)

We went from “what to protect” → **full local guardrail stack** → refined **network (ask)**, **audit (read OK, no agent writes)**, **persona/skills protection**, **simpler hook layout** — and ended on **how to enforce Admin-only governance** without hooks seeing persona unless you add session state or deny protected edits for everyone.

## Audit

### What we set out to do

Keep track of **notable user and agent actions** for audit and compliance, building on the existing Cursor hooks (`before-shell`, `protect-paths`, `before-mcp`) rather than a third-party product.

### Top events (agreed categories)

We mapped guardrails to roughly **ten event categories**, by risk tier:

| Tier                 | Examples                                                                                   |
| -------------------- | ------------------------------------------------------------------------------------------ |
| Security / integrity | Blocked shell commands, git mutations, protected-path edits, `.git/` edits, network egress |
| Secrets & bypass     | Pre-commit secret hits, `--no-verify` / hook bypass                                        |
| Governance / product | AI tool disclosure on PRs, public API / deprecation changes, clean builds                  |

**In scope for hooks:** deny/ask paths on shell, file edits, and MCP.

**Out of scope for hooks (policy / CI / review):** AI disclosure (CONTRIBUTING), secrets on push (pre-commit / GitHub), public API changes (review / diff).

### Storage and schema (decisions)

| Decision     | Choice                                                                                          |
| ------------ | ----------------------------------------------------------------------------------------------- |
| Format       | **Append-only JSONL** at `.cursor/audit/audit.jsonl`                                            |
| Commit       | **Gitignore** `.cursor/audit/` — local only                                                     |
| Shared code  | **`.cursor/hooks/audit_log.py`** imported by hook scripts                                       |
| Record shape | `event_type`, `hook`, `outcome`, `target`, optional `rule`, `messages`, `context` (cwd, branch) |

### Logging volume (main tradeoffs)

| Option                                                                                  | Decision                                  |
| --------------------------------------------------------------------------------------- | ----------------------------------------- |
| Log every **allow** (full trail)                                                        | **No** — too noisy                        |
| Log **deny** + **ask** only                                                             | **Yes** — signal-focused                  |
| **After-hooks** (`afterShellExecution`, etc.) to confirm execution or user Approve/Deny | **No** — simpler; UI outcome not recorded |
| **`sessionStart`** logging                                                              | **No** — not in final scope               |
| Pre-commit **`secrets.detected`** → audit log                                           | **Discussed, not implemented**            |
| Log high-risk allows only (e.g. `src/skimage/**`)                                       | **Dropped** once we skipped all allows    |

**Implication:** The log records **attempts** that hit guardrails (blocked or sent for approval), not whether the user approved or whether a command actually ran.

### Hook bypass (addition)

**Decision:** Deny and log **`--no-verify`** and **`--no-gpg-sign`** in `before-shell.py` (security rules already forbade them; hooks did not block them before).

Event type: `guardrail_bypass.attempted`.

### Event types implemented (deny / ask only)

| `event_type`                            | Hook                   |
| --------------------------------------- | ---------------------- |
| `shell.command.denied`                  | `beforeShellExecution` |
| `shell.git_mutation.approval_requested` | `beforeShellExecution` |
| `shell.network.approval_requested`      | `beforeShellExecution` |
| `shell.clean.approval_requested`        | `beforeShellExecution` |
| `guardrail_bypass.attempted`            | `beforeShellExecution` |
| `file.edit.protected_path`              | `preToolUse`           |
| `file.edit.git_internals`               | `preToolUse`           |
| `mcp.network.approval_requested`        | `beforeMCPExecution`   |

Routine allows (`spin test`, normal file edits, non-network MCP) produce **no** log line.

### What we built (implemented)

| File                   | Role                                                    |
| ---------------------- | ------------------------------------------------------- |
| **`audit_log.py`**     | Best-effort JSONL writer; failures must not break hooks |
| **`before-shell.py`**  | Audit on deny/ask; bypass deny for hook-skipping flags  |
| **`protect-paths.py`** | Audit on protected / `.git` edits                       |
| **`before-mcp.py`**    | Audit on network MCP ask                                |
| **`.gitignore`**       | `.cursor/audit/`                                        |

**`hooks.json` unchanged** — no after-hooks.

**Verification:** Smoke test — three deny/ask scenarios → three log lines; allow paths → zero lines.

### Querying (local)

```bash
cat .cursor/audit/audit.jsonl | python3 -m json.tool
grep '"outcome": "denied"' .cursor/audit/audit.jsonl
grep 'approval_requested' .cursor/audit/audit.jsonl
```

### Deferred / optional later

- Pre-commit integration in **`check_secrets.py`**
- **`public_api.change`** detection (matcher or CI)
- **`ai_tool.disclosure`** automation (PR metadata)
- Revisit **after-hooks** if execution or approval outcomes are required

### Outcome (audit arc)

We went from **“top 10 events to track”** → full design (schema, shared logger, optional after-hooks and allow logging) → **trimmed to deny/ask only, no after-hooks** → **implemented** the lean hook-based audit trail aligned with the security stack.

## Personas

### What we were building

A **chat persona system** for this repo’s Cursor framework: modes with different capabilities, **not** real authentication.

### Options we discussed

**Personas / structure**

- One mega-skill vs **one skill per persona** + thin router → chose the latter
- Nest `first-contribution` under Developer vs **keep it separate** → keep separate
- Infer persona from the task vs **explicit declare, else ask once** → no inference

**PM / non-dev use**

- Use Cursor for research, triage, issue drafts, product PR summaries — **not** implement/commit
- Dedicated PM skill: yes, as a **separate non-coding** skill (later folded into the persona set)

**Admin + protected paths**

- Soft Admin (skill says OK; hook still **ask**) vs hard allow (hook **allow**, no popup) → **soft only**
- Non-Admin: keep approve card vs **deny with no override** → explored; needs persona state for hooks
- Persona persistence via prompt parsing vs simpler approaches:
  - always **deny** protected paths (Admin drafts; human edits)
  - manual **arm file** (`.cursor/state/admin`) then ask
  - prompt-parsed state (tried, then **reverted**)

**Temporarily turning hooks off**

- No documented Settings “disable all hooks”
- Practical: rename/clear `.cursor/hooks.json` locally

**Removing an unpushed Admin commit**

- `git reset` (mixed or hard) vs `git revert` → **reset** is right; revert only if already pushed

### Main decisions

| Decision                      | Choice                                                                               |
| ----------------------------- | ------------------------------------------------------------------------------------ |
| Personas                      | Developer, PM, QA (+ Admin)                                                          |
| Selection                     | Explicit only; ask once if missing; stop until answered                              |
| Stickiness                    | Instruction-level for the chat; switch must be explicit                              |
| First contribution            | Separate skill; requires **Developer**                                               |
| Admin                         | Soft governance persona; may edit protected paths when user asks; **no hook bypass** |
| Protected-path hook           | **Ask for everyone** (persona-deny / persistence work reverted)                      |
| Hook “only Admin” enforcement | Not shipped; simpler patterns preferred if revisited                                 |

### End state (this chat)

- Soft **Admin** persona captured in routing/skills/docs (see also Security § Persona)
- Persona-deny / persistence hook experiments were **fully reverted**
- Protected edits still: **ask** (approve/deny), except audit / `.git` → **deny**

## Modularity & Maintenenace

### What we set out to build

An **8–12 hour MVP** Cursor framework in-repo (plus Cursor config) to:

1. Scaffold correct first contributions
2. Catch mistakes early (tests, conventions, deprecations)
3. Align with CI/guardrails and approved context
4. Stay **maintainable** as scikit-image evolves
5. Serve **Developer, PM, QA, DevOps** from one system

**Constraint:** repo + Cursor only — no external tool config.

### Architecture we converged on

| Layer                                       | Role                                                                                 |
| ------------------------------------------- | ------------------------------------------------------------------------------------ |
| **AGENTS.md**                               | Always-on **router**: sources of truth, layout, `spin`, verification, PR/AI pointers |
| **CONTRIBUTING.md**                         | **Authoritative policy** — Cursor layers link, don’t copy                            |
| **Always-on rules**                         | `persona.mdc`, `security.mdc`                                                        |
| **Routing rules**                           | `first-contribution.mdc`, `pre-pr-gate.mdc` → workflow skills                        |
| **File-scoped rules**                       | `skimage-source.mdc`, `skimage-tests.mdc`                                            |
| **Skills**                                  | Procedures, gates, checklists under `.cursor/skills/`                                |
| **Hooks + `protected_paths.py`**            | **Enforce** shell/MCP/file writes; rules **summarize**                               |
| **`.cursor/README.md`**                     | **Maintainer** map, layer contract, hook pipeline                                    |
| **`tools/cursor/validate-contribution.sh`** | Pre-PR heuristics + pre-commit + `spin test --test-modified`                         |

**Principle:** _Link, don’t paste_ — especially with AGENTS always applied.

### Main decisions

| Topic                                          | Decision                                                                                                            |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| **Skill location**                             | Project skills in **`.cursor/skills/`** (versioned, team-owned)                                                     |
| **Global vs rules**                            | **AGENTS + slim always-on rules** = boundaries/process; **file-scoped rules** = edit-time Python/test/Cython detail |
| **Phase 1 scope**                              | Entry + guardrails first; skills/scripts in Phase 2 (later added)                                                   |
| **`skimage-core.mdc`**                         | Renamed/evolved to **`skimage-source.mdc`** (`src/**` only, not a fake “always core”)                               |
| **`tests.mdc`**                                | Renamed **`skimage-tests.mdc`** for symmetry                                                                        |
| **Protected paths**                            | Central **`protected_paths.py`**; sync summary in **`security.mdc`**                                                |
| **`pre-pr-gate.mdc`**                          | Added to **`PROTECTED`** (same class as `first-contribution.mdc`)                                                   |
| **CONTRIBUTING pointer**                       | Discussed; **deferred** (~3/10 need vs framework function)                                                          |
| **Dedupe skills (#2)**                         | Applied — first-contribution, persona-dev/PM/QA, tests layout → **AGENTS links**                                    |
| **Routing duplication (#1)**                   | **Option A** — slim `.mdc` to “load skill”; gates stay in skills (**not** delete routing rules)                     |
| **Hook doc (#3 partial)**                      | **README “Hook pipeline”** + `protect-paths.py` comments — **did not** trim duplicate workflow globs                |
| **`sync-check.sh`**                            | Optional hygiene; **not built**                                                                                     |
| **Human behavior tour**                        | Optional AGENTS / OVERVIEW section — **discussed, not required**                                                    |
| **`protect-paths.py` vs `protected_paths.py`** | Hook script vs glob list; **`repo_paths.py` merged into `protect-paths.py`**                                        |

### Options we compared (and usual choice)

| Option                                  | When we picked it                                                                                                       |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| **AGENTS vs rules for conventions**     | Conventions in **scoped rules**; AGENTS = layout + `spin` + verification                                                |
| **Duplicate boundaries in core rule**   | **Compact mirror** in security/persona; full text in AGENTS/README                                                      |
| **Dedupe vs agent performance**         | Dedupe **reference** material only; keep **procedures** in skills                                                       |
| **#1 Option A vs B**                    | **A** — keep routing `.mdc`, slim bodies                                                                                |
| **Persona vs `first-contribution.mdc`** | **Conflicts in persona** owns Developer requirement; routing rule can slim further (**Option 2** noted, partially done) |
| **PR metadata**                         | **Single owner: pre-pr-gate skill** (first-contribution § 5 deduped)                                                    |

### What we implemented in this arc

1. **Phase 1:** `AGENTS.md` + core rule (later AGENTS became the main agent guide; source/tests split into scoped rules).
2. **Maintainability pass:** `.cursor/README.md`, `protected_paths.py`, skill dedupe, `skimage-tests.mdc` rename.
3. **Enforcement docs:** README “Enforcement vs guidance” + Hook pipeline; `pre-pr-gate` protected; AGENTS § Verification / Further reading links.
4. **#1 Option A:** Slim `first-contribution.mdc` and `pre-pr-gate.mdc`.
5. **Fixes 1 & 2:** README `_is_skill_path()` wording; first-contribution handoff → pre-pr-gate PR checklist.

Branch also gained **pre-pr-gate**, **scaffold-test**, **validate-contribution.sh**, personas, hooks — documented in `.cursor/README.md`.

### Still open (discussed, not done)

- **CONTRIBUTING** optional Cursor note
- **`sync-check`** for `protected_paths` ↔ `security.mdc`
- **Trim duplicate globs** in `protected_paths.py`
- **Pre-pr-gate skill:** shorten heuristic prose → link `tools/cursor/README` only
- **Slim `first-contribution.mdc`** to skill + Conflicts pointer only (persona overlap)
- **Slim `persona-developer`** in-scope bullets → AGENTS § Verification
- **README table merge** (layer contract + enforcement) — optional clarity pass

### Outcome (modularity & maintenance arc)

We built a **layered, repo-owned Cursor onboarding system** (AGENTS → personas → routing skills → scoped rules → hooks/script), decided **skills live in `.cursor/skills/`**, **enforce in hooks/scripts and procedure in skills**, and iteratively **deduped and documented** so maintainers have a single map in **`.cursor/README.md`** without duplicating CONTRIBUTING.

## First Contribution

### Options we discussed

**Broader first-contribution ideas (early):**

1. Curated starter issues
2. Short first-PR path (separate from full contribute guide)
3. Mentored tracks / office hours
4. Skill ladders (docs → tests → Python → harder)
5. Friendlier PR triage (labels, welcome bot)
6. In-repo starter kit / Sphinx page
7. External programs (GSoC, Outreachy, etc.)
8. Metrics on first-issue response/merge

We treated these as **separate levers**, not one mandatory package. Natural core was **1 + 2**.

**For (1) and (2), approaches considered:**

- GitHub-side: label hygiene, issue templates, seeded issues, Sphinx/CONTRIBUTING page, Zulip announce
- Cursor-side: project **skill** + **thin rule** (+ hooks later if we want hard gates)

### Main decisions

| Topic            | Options                                    | Decision                                                                             |
| ---------------- | ------------------------------------------ | ------------------------------------------------------------------------------------ |
| Issue source     | New taxonomy vs existing label             | Use existing `:beginner: Good first issue` only                                      |
| First-PR “page”  | Top of `CONTRIBUTING.md` vs separate page  | Separate page preferred — then narrowed to **Cursor skill**, not Sphinx              |
| Scope of build   | Full community workflow vs Cursor controls | **Cursor only** (rules/skills; no Zulip/bots/issue forms)                            |
| Skill packaging  | Skill only vs skill + thin rule            | **Skill + thin rule**, **project**-scoped                                            |
| Skill files      | `SKILL.md` + `reference.md` vs one file    | **One file** (merged)                                                                |
| Off-label issues | Hard refuse vs allow with friction         | **Strongly suggest labeled**; require **explicit confirmation** to proceed off-label |
| Enforcement      | Soft agent guidance vs hooks/CI            | Soft for now; we don’t force PR submission                                           |

### What we built

- `.cursor/skills/first-contribution/SKILL.md` — playbook (list/pick, setup, branch, scoped change, `spin` verify, PR handoff)
- `.cursor/rules/first-contribution.mdc` — routes first-contribution chats to that skill

**Invocation:** natural language (“first contribution / first PR / starter issue”), not a slash command.

**Retrieval test:** plain `good first issue` → 0 hits; real label is `:beginner: Good first issue` — skill/rule updated accordingly. `gh` wasn’t available in the test environment; list was fetched via GitHub API.
