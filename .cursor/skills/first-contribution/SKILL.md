---
name: first-contribution
description: >-
  Guides a newcomer's first scikit-image pull request, preferring GitHub issues
  labeled ":beginner: Good first issue". Use when the user asks for a first
  contribution, first PR, starter issue, onboarding as a new contributor, or
  help picking an easy issue to work on.
---

# First contribution

Help someone land a **first** PR on **`egarelnabi/scikit-image`**. Stay inside this
playbook; do not invent a parallel onboarding path.

**Contribution target:** all branches, commits, and PRs go to
`egarelnabi/scikit-image`. Never push or open a PR against
`scikit-image/scikit-image`. Upstream is **issue discovery only**.

Norms for layout, `spin`, pre-commit, and PR policy: **AGENTS.md** (always applied). Deep reference: **CONTRIBUTING.md** — link, do not paste.

## Issue selection

**Default:** open issues labeled `:beginner: Good first issue` on **upstream**
`scikit-image/scikit-image` (list with `gh` below). Prefer these strongly for a first PR.

If the user names an issue **without** that label (or with different labels):

1. Say clearly that labeled issues are the recommended first-contribution path and why (scoped, curated for newcomers).
2. Show a short list of `:beginner: Good first issue` alternatives.
3. Ask whether they want to switch to a labeled issue **or** proceed with their choice anyway.
4. **Do not edit code** until they explicitly confirm. Silence or ambiguity is not confirmation.
5. If they confirm proceeding off-label, continue this playbook on that issue, and note in the PR handoff that it was not a `:beginner: Good first issue`.

Do not expand scope beyond the chosen issue. No drive-by refactors, renames, or unrelated cleanups.

## When to use Plan mode

**Default: stay in Agent** and follow this playbook. Most `:beginner: Good first issue` work is already scoped — Plan adds friction without benefit.

**Switch to Plan** (Cursor Plan mode) only when, after `gh issue view`, the next step is still ambiguous, for example:

- User confirmed an **off-label** or larger issue
- Issue text is vague (no files / acceptance criteria)
- Several valid approaches (API shape, where tests live)
- Change would span many modules (e.g. Cython + wrappers + both test trees)

Do **not** require Plan as a step of every first contribution. After a short plan is agreed, switch back to Agent to implement.

## Agent Review (optional)

**Offer** Cursor **Agent Review** of the diff when the change is ready to hand off — after tests / verify (pre-pr-gate), or when the user is about to open a PR. Useful for missing tests, wrong layer (`skimage` vs `_skimage2`), and scope creep.

**Skip** for docs-only or still in-progress work, pure issue listing with no code, or while still in Plan.

Agent Review does **not** replace **pre-pr-gate** (`validate-contribution.sh` / `spin`), QA test plans, or maintainer review. Do not auto-launch Bugbot or security-review unless the user explicitly asks.

## Workflow

Copy and track:

```
First contribution:
- [ ] List / pick an upstream issue (prefer :beginner: Good first issue)
- [ ] If off-label: strongly suggest labeled alternatives; get explicit confirmation
- [ ] If scope/approach still unclear: Plan mode, then return to Agent
- [ ] Dev setup (if needed) — AGENTS.md § Build and test
- [ ] Branch from origin/main (egarelnabi/scikit-image)
- [ ] Summarize planned code changes; get explicit approval before editing
- [ ] Implement only what the issue asks
- [ ] Add or update tests — read and follow [scaffold-test](../scaffold-test/SKILL.md)
- [ ] Verify — [pre-pr-gate skill](../pre-pr-gate/SKILL.md) / `./tools/cursor/validate-contribution.sh`
- [ ] Offer Agent Review (optional; skip docs-only / WIP)
- [ ] Summarize for PR on egarelnabi/scikit-image (link upstream issue, AI disclosure)
```

### 1. List and pick

Discover issues on upstream only (do not modify them):

```bash
gh issue list -R scikit-image/scikit-image --label ":beginner: Good first issue" --state open --limit 20
```

Show the user the list (number, title, URL). Help them choose; do not start coding until they confirm an issue number.

To inspect one issue:

```bash
gh issue view <number> -R scikit-image/scikit-image
```

If labels include `:beginner: Good first issue`, proceed after the user confirms the issue number.

If not, follow **Issue selection** above (suggest labeled alternatives → wait for explicit confirmation before coding).

If the issue asks contributors to comment before starting, remind the user — do **not** comment on upstream unless they explicitly ask. Prefer linking the upstream URL in the fork PR body instead.

### 2. Setup (skip steps already done)

**Remotes** — this workspace contributes only to the fork:

```bash
git remote -v
# origin should be https://github.com/egarelnabi/scikit-image.git (or SSH equivalent)
```

- `origin` — **`egarelnabi/scikit-image`** (push and PR target)
- An `upstream` remote pointing at `scikit-image/scikit-image` may exist for reference; **do not** fetch/merge it for branching, and **never** push or open PRs there

Inspect with `git remote -v` and adapt commands; never run `git config`.

**Install, hooks, and spin commands:** follow **AGENTS.md** § Build and test (e.g. `spin install -v`, `pre-commit install`, `spin test -- …`, `spin build --clean` when adding Cython/source files).

### 3. Branch and implement

```bash
git switch main
git fetch origin main
git merge origin/main
git switch -c first-contribution-<issue-number>
```

Branch from **`origin/main`** (`egarelnabi/scikit-image`) so Cursor hooks and framework files stay on the branch. Do **not** `git fetch/merge upstream/main` or create `*-upstream` clean branches for contribution.

- Read the issue and the files it points at before editing.
- Follow **AGENTS.md** § Package layout and **Read before edit**.
- Match surrounding style. Change only what the issue requires.

#### Pre-edit change summary (required)

Before creating, modifying, or deleting code (or tests), present a short plan and **stop**.
Do not edit until the user explicitly approves. Silence or ambiguity is not approval.
(Issue pick / off-label confirmation still apply earlier; this gate is specifically about the patch.)

Include:

- **Goal** (upstream issue URL / title; fork `Fixes #N` only if a fork triage issue exists)
- **Files** to touch (paths)
- **What** you will change in each (1–2 bullets per file)
- **Out of scope** (what you will not change)
- **Verify** steps you intend (pre-pr-gate / narrowest tests)

If the user revises the plan, update the summary and wait again before editing.

### Tests

If the issue changes code under `src/`, **read and follow** **[scaffold-test](../scaffold-test/SKILL.md)** (scaffold from peer tests, weak-test checklist). While editing test files, **skimage-tests.mdc** applies automatically.

Doc-only issues: skip unless the issue requires tests.

### 4. Verify

Follow **[pre-pr-gate](../pre-pr-gate/SKILL.md)**:

1. Complete the **weak-test checklist** in [scaffold-test](../scaffold-test/SKILL.md) when tests were added or changed.
2. Run from the repository root:

   ```bash
   ./tools/cursor/validate-contribution.sh
   ```

3. Complete the PR metadata checklist in the pre-pr-gate skill before handoff.

Do not claim checks passed unless the script (or equivalent steps) succeeded. Report commands and outcomes.

After a successful verify (or when the user is about to open a PR), **offer Agent Review** per the section above — do not require it.

### 5. Hand off for PR

Do **not** commit, push, or open a PR unless the user explicitly asks.

When summarizing for the user, include:

- What changed (files + intent)
- Commands run and results
- Concise PR title
- Suggested PR body that follows [PULL_REQUEST_TEMPLATE.md](../../../.github/PULL_REQUEST_TEMPLATE.md) — short description; link the **upstream** issue URL; `Fixes #N` / `Closes #N` only for issues on **`egarelnabi/scikit-image`**; generative-tool disclosure per **AGENTS.md** § Pull requests / CONTRIBUTING AI policy; and the template's optional `release-note` block (see [pre-pr-gate](../pre-pr-gate/SKILL.md) § 5)
- PR target: **`egarelnabi/scikit-image`** base `main` — never `scikit-image/scikit-image`

When the user asks to open the PR:

```bash
gh pr create -R egarelnabi/scikit-image --base main --title "..." --body "$(cat <<'EOF'
...
EOF
)"
```

Do **not** invent `## Summary` / `## Test plan` (or similar) unless they explicitly ask.

## Getting unstuck

Point the user at:

- Zulip: https://skimage.zulipchat.com/
- Developer forum: https://discuss.scientific-python.org/c/contributor/skimage

## Out of scope for this skill

- Creating/relabeling GitHub issues (PM owns fork triage publish)
- Pushing or opening PRs against `scikit-image/scikit-image`
- Fetching/merging `upstream/main` to “clean” a contribution branch
- Proactively hunting unlabeled "looks easy" work (only consider off-label issues when the user asks for a specific one)
- Cython/API design/deprecation work unless the chosen issue explicitly requires it
- Editing protected paths (see `.cursor/rules/security.mdc`)
