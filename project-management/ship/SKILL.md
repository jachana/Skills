---
name: ship
description: >-
  Take the top kanban card all the way to the integration branch: claim it, verify it isn't already
  implemented, build + test on a branch, open a PR to the integration branch (develop) with evidence,
  merge it, and only THEN move the card to "shipped" (e.g. "En develop"). Never touches the release
  branch (master/main) — that is /release's job. No per-card human review queue.
  Provider-agnostic: works OFFLINE against a local board.json OR ONLINE against Trello / Jira / others.
  Use when the user says "/ship", "ship the next card", "pick and ship a card", "trabaja la siguiente tarjeta",
  "toma la próxima tarjeta y déjala en develop".
  Requires the board.py helper (project-management/scripts/board.py).
---

# Ship a card → integration branch

One card from backlog to **merged on the integration branch** (default `develop`). The human does not
review each card; they review once per release (`/release`). So the proof has to be in the PR.

## Language / Idioma
Reply in the user's language (EN/ES). Commit messages: conventional-commit English (`feat(area): …`) unless the repo says otherwise.

## Model & effort
| Phase | Model | Effort | Why |
|---|---|---|---|
| Board ops via board.py (steps 0, 1, 7, 8) | haiku | low | the script does the work |
| Already-done check (step 2) | haiku / Explore subagent | low | grep + read, no generation |
| Implement + tests (steps 3–4) | sonnet | medium | real coding |
| Architectural / multi-system card | opus | high | design tradeoffs before code |

Session below the peak this card needs → tell the user before implementing. Session above → run board ops and the step-2 check in a subagent with an explicit `model:`.

## 0. Read the repo's flow + locate the board
- Read the repo's CLAUDE.md / CONTRIBUTING for: integration branch (`INT`, default `develop`), release branch (`REL`, default `master`/`main`), list names, required test commands, regression-test rules. **Repo rules win over this skill.**
- Find `board.py` (`BOARD`). List names come from env (or the repo's `.env`):
  `PM_CLAIM_LIST` (default `In progress`), `PM_SHIP_LIST` (default `In review` — set it to the integration list, e.g. `En develop`), `PM_PICK_FROM` (comma list, priority order, e.g. `Bugs,Backlog`). Decision list: `PM_DECIDE_LIST` (e.g. `Necesita decisión`), used with `move --to`.
- Repo has its own board CLI (e.g. `tboard`)? Use it instead of board.py for the same steps.
- `python $BOARD status`. ONLINE → `python $BOARD pull` first (online wins). OFFLINE → local `board.json`.

## 1. Pick + claim
- `python $BOARD pick` → top ready card. Skip any card already in the claim list (another agent owns it).
- Claim **before** working: `python $BOARD claim "<name>"` + `push` if online.
- Branch from the **remote** integration tip: `git fetch origin && git switch -c feat/<slug> origin/$INT` (`fix/<slug>` for bugs). Prefer a separate worktree if the main checkout is busy.

## 2. VERIFY it isn't already done  ⟵ do not skip
Grep `origin/$INT` for the feature and check recent commits/PRs — the code, not just the card title. Already there →
note where (commit/PR), `ship` the card with that note, stop. Partially there → implement only the gap, say so.

## 3. Implement
Backend + frontend + **tests**, following repo patterns. Client-reported bug → regression test per repo rules (e.g. `REG-NNN`, fail→pass proven).

## 4. Test — prove it
- Targeted tests for what changed + the repo's fast regression suite + build if frontend changed. Paste real output.
- Red → fix or stop. Never open the merge with failing tests. Never run the full suite here unless the repo asks (that's `/release`).

## 5. PR to the integration branch, with evidence
- Commit (conventional), `git push -u origin <branch>`.
- `gh pr create --base $INT` — body = the evidence the release reviewer will rely on:
  - **Qué / por qué** (1–3 lines, link to the card).
  - **Pruebas**: commands run + pass counts; regression test ids with "falla→pasa" when applicable.
  - **UI**: screenshot or short recording if the change is visible.
  - **Migraciones**: new revision ids, single-head check output, up/down notes.
  - **Riesgo**: what could break, what the release walkthrough should click.
- Never target `$REL`. Never push to `$INT` or `$REL` directly.

## 6. Merge
- Merge per repo method (`gh pr merge <url> --merge|--squash|--rebase --delete-branch`). With required checks, wait for them (`--auto`) — don't bypass.
- Confirm: `gh pr view <url> --json state` → `MERGED`. Not merged (conflict, checks red, needs human) → step 8b.

## 7. Card → shipped (only after MERGED)
- `python $BOARD ship "<name>"` → `PM_SHIP_LIST` (e.g. *En develop*), `push` if online. Add the PR link as a comment/desc note.
- This list is **not** a review queue: it means "on the integration branch, waiting for the next release".

## 8. Confirm / fallbacks
a. Success: local branch deleted, `git status` clean, card on the shipped list. Report: what shipped, PR link, test proof.
b. Merge failed or a decision is needed (client question, business rule, prod action, conflict you can't resolve safely) →
   branch stays pushed, PR stays open, card → `python $BOARD move "<name>" --to "$PM_DECIDE_LIST"` with a one-line note of what's needed. **Never** move a card to the shipped list without a merged PR.

## Rules
- ⚠ The release branch is off-limits: no PRs, merges or tags to it. That's `/release`.
- ⚠ Never hand-edit `board.json` to fake a state — drive it through `board.py` (or the repo CLI).
- ⚠ Online conflict rule: **online wins**. `pull` before claiming; `push` after every move.
- ⚠ One card at a time through step 7 before claiming the next.
- ✅ New bug/idea found mid-flight → its own card (`board.py add "<name>" --list Backlog`/`Bugs`), don't scope-creep.
