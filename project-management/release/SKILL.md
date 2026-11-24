---
name: release
description: >-
  Promote the integration branch (develop) to the release branch (master/main) as a versioned release:
  pick the version, build an acceptance guide from the PRs/cards in range, run the full test suite once,
  check migrations, validate on the dev/staging deploy (incl. external integrations in sandbox mode),
  walk the human through the guide, then PR develop→master, merge, tag vX.Y.Z, verify the production
  deploy, and move the cards to the released list with the version label. This is the ONE human review
  point — /ship never touches master.
  Use when the user says "/release", "haz un release", "pasa develop a master", "release v0.9",
  "promote develop to main", "cut a release".
  Uses board.py (project-management/scripts/board.py) or the repo's own board CLI.
---

# Release: integration → release branch

`INT` = integration branch (default `develop`), `REL` = release branch (default `master`/`main`).
The repo's CLAUDE.md wins over this skill for branch names, test commands, deploy targets and list names.

## Language / Idioma
Reply in the user's language (EN/ES). Acceptance guide and release notes in the language the client/team reads (Conico: Chilean Spanish).

## Model & effort
| Phase | Model | Effort | Why |
|---|---|---|---|
| Range, version, board moves, tag (steps 1, 2, 9, 10) | haiku | low | mechanical |
| Full suite + migration check (steps 4, 5) | haiku | low | run + read output |
| Acceptance guide + release notes (steps 3, 11) | sonnet | medium | summarize real diffs into click-paths |
| Risk read of the diff (step 3, risky areas) | opus | high | money, tax docs, migrations, auth |

## Gates (all must be green, in order — stop at the first red)
| # | Gate | Evidence kept |
|---|---|---|
| G1 | Range is non-empty and `INT` contains `REL` | `git log` count |
| G2 | Full suite green, once, foreground | pass/fail counts |
| G3 | Migrations: one head, reviewed, upgrade tested on a prod copy | head id, notes |
| G4 | Dev/staging deploy of the exact `INT` sha is healthy | deploy id + sha |
| G5 | Integration smoke in sandbox (e.g. one doc per tax-doc type) | ids/folios |
| G6 | Human walkthrough of the acceptance guide | ✅/❌ per item |
| G7 | Prod deploy healthy on the tagged sha | deploy id + health |

## 1. Freeze the range
- `git fetch origin --tags`. Range = `origin/$REL..origin/$INT`.
- `git merge-base --is-ancestor origin/$REL origin/$INT` must succeed (no hotfix on `REL` missing from `INT`). If it fails → merge `REL` back into `INT` via PR first.
- Empty range → nothing to release, stop.
- Record `RC_SHA = git rev-parse origin/$INT`. Everything below tests **this sha**. Ask agents/the user to hold merges to `INT` until the tag; if `INT` moves, either re-freeze (repeat G2–G5 for the delta) or release `RC_SHA` exactly.

## 2. Pick the version
- Last tag: `git describe --tags --abbrev=0 origin/$REL` (or `git tag --sort=-creatordate | head -1`). Format `vMAJOR.MINOR.PATCH` (accept legacy `vX.Y` as `vX.Y.0`).
- **Minor** bump (`v0.8.9 → v0.9.0`) if the range has any new feature, schema migration, config/env change, or behavior change a user would notice.
- **Patch** bump (`v0.9.0 → v0.9.1`) if it's only bug fixes / copy / perf with no migration.
- **Major** only on the user's explicit call. State the choice + one-line reason; the user can override.

## 3. Acceptance guide (what the human will click)
- Collect PRs merged into `INT` in range: `gh pr list --base $INT --state merged --search "merged:>=<last tag date>" --json number,title,body,url,mergedAt` (cross-check with `git log --merges --first-parent origin/$REL..origin/$INT`). Collect the cards on the shipped list (e.g. *En develop*).
- Flag mismatches: card on the shipped list without a merged PR, or PR without a card → list them, don't hide them.
- Write `docs/releases/vX.Y.Z.md` (or the repo's place) grouped **by module/screen**, each item:
  `- [ ] <screen> → <action> → <expected result>  (PR #n, card)` — real click-paths taken from the PR evidence, not the titles.
- Put on top a **Riesgo** block: migrations, money/tax/totals, permissions, data deletes, anything touching external integrations. These get walked first.
- Target: 30–40 min of walkthrough. Too long → the release is too big; offer to split by releasing an earlier `RC_SHA`.

## 4. G2 — full suite, once, foreground
Run the repo's full suite at `RC_SHA` in a clean worktree (`git worktree add ../<repo>-rc <RC_SHA>`), **foreground**, wait for it:
backend in parallel if the repo supports it (e.g. `pytest -n auto`), frontend tests, frontend build, regression suite.
Red → stop, open a `Bugs` card per failure (or fix via `/ship` on `INT`), re-freeze. Never "known flaky" a failure without the user's OK.

## 5. G3 — migrations
- Single head (e.g. `alembic heads` → exactly one). List new revisions in range.
- Read each new migration: destructive ops (drop/rename column, data rewrites, NOT NULL on populated tables) → call out in Riesgo + confirm a backup/rollback note exists.
- Upgrade on a copy of prod data (the dev/staging DB if it's a prod copy) and confirm the app boots.

## 6. G4 — dev/staging deploy of `RC_SHA`
- Make sure the dev deploy runs exactly `RC_SHA` (e.g. Coolify dev app on `INT`; use the `coolify` / `coolify-deploy` skills to deploy + verify). Record deploy id and sha. Health endpoint green, app loads, login works.

## 7. G5 — integration smoke (sandbox)
The dev environment talks to **sandbox** credentials of external services, so test the real flows there, not mocks:
e.g. tax/e-invoicing — emit one document of each type in range (factura, boleta, NC/ND, guía…), check folio, PDF and provider status; payments/webhooks — one round trip. Record ids. A sandbox failure blocks the release unless the user explicitly waives it (write the waiver in the notes).

## 8. G6 — human walkthrough
Hand the user the guide (file path or rendered page) + dev URL. They tick items.
- ❌ item → new card in `Bugs` with the guide line, then: **fix now** (via `/ship` → `INT`, re-freeze, re-run G2–G5 for the delta) or **drop** (revert the PR on `INT` via PR, note it). The user decides; record which.
- Anything needing a client/business answer → card to the decision list; release without it only if it's isolated.
Don't proceed until every item is ✅, dropped, or waived by the user.

## 9. Promote: PR → merge → tag
- `gh pr create --base $REL --head $INT --title "Release vX.Y.Z" --body <summary + link to guide + gate evidence table>`.
- Verify the PR head sha == `RC_SHA` (else re-freeze). Merge with a **merge commit** (`gh pr merge --merge`, never delete `INT`).
- `git fetch origin && git tag -a vX.Y.Z <merge sha on REL> -m "Release vX.Y.Z: <one-line summary>" && git push origin vX.Y.Z`.
- Optional: `gh release create vX.Y.Z --notes-file <notes>` if the repo uses GitHub Releases.

## 10. G7 — production deploy
- Verify the prod deploy picked up the tagged sha (e.g. Coolify prod app: status running, commit == merge sha, fresh `last_online_at`, health green). Use `coolify-deploy` to trigger if it doesn't auto-deploy.
- Post-deploy smoke in prod: login + the Riesgo items that are safe to touch in prod (read-only where possible; no test tax docs in prod).
- Red → roll back to the previous tag's deploy first, then investigate. Never leave prod red while debugging.

## 11. Close out
- Board: every card in range → released list (e.g. *En master*) with label `vX.Y.Z` (create the label if missing); `push` if online. Cards dropped in step 8 → back to `Backlog`/`Bugs` with a note.
- Release notes (client-facing, short, in their language): what's new by module, what was fixed, anything they must do. Draft only — the user sends it.
- Update the repo's progress log (e.g. `PROGRESS.md`) with version, date, highlights; commit via PR to `INT`.
- `git worktree remove ../<repo>-rc`. Report: version, gate table with evidence, PR + tag links, prod deploy id.

## Rules
- ⚠ Only this skill merges into `REL` or creates tags. Hotfix = branch from `REL`, PR to `REL` with the same gates (scaled down: targeted + regression + sandbox smoke of the area), patch tag, then merge `REL` back into `INT`.
- ⚠ Release exactly what was tested: `RC_SHA` must equal the PR head and the tagged merge's second parent.
- ⚠ Full suite runs once per release, foreground — never left in background.
- ⚠ Never tag before G1–G6 are green; never mark cards released before G7.
- ✅ Keep evidence (counts, ids, shas) in the PR body: it is the audit trail of the human review.
