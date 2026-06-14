---
name: ship
description: >-
  Take the top kanban card all the way to shipped: claim it, verify it isn't already implemented,
  build backend+frontend+tests, commit, and move it to "In review" — keeping the board in sync.
  Provider-agnostic: works OFFLINE against a local board.json OR ONLINE against Trello / Jira / others
  (auto-detected; no account required).
  Use when the user says "/ship", "ship the next card", "pick and ship a card", "trabaja la siguiente tarjeta",
  "toma la próxima tarjeta del tablero y déjala lista para revisión".
  Requires the board.py helper (this skill's category ships it under project-management/scripts/board.py).
---

# Ship a card (online or offline)

A disciplined loop from "top of backlog" to "In review". Never claims success without proof.

## Language / Idioma
Reply in the user's language (EN/ES). Commit messages stay in conventional-commit English (`feat(area): …`) unless the user's repo convention says otherwise.

## 0. Locate the board helper + detect mode
- Find `board.py` (this category's `scripts/board.py`; copy it into the repo's `scripts/` or reference it directly). Let `BOARD = path to board.py`.
- Run `python $BOARD status`.
  - **ONLINE** (Trello creds present) → start by `python $BOARD pull` so local mirrors the board (online wins).
  - **OFFLINE** → just use the local `board.json` (run `python $BOARD init` if none exists).
- Everything below uses the same `board.py` commands regardless of mode.

## 1. Pick + claim
- `python $BOARD pick` → the top ready card. Confirm with the user if ambiguous.
- **Claim it before working** (multi-agent signal): `python $BOARD claim "<name>"` (moves it to *In progress*).
- Create/switch to a working branch off the main branch, e.g. `git switch -c ship/<slug>`.

## 2. VERIFY it isn't already done  ⟵ do not skip
Before writing anything, grep the codebase for the feature. Check recent commits. If it's already implemented:
- Say so, ship the card straight to review (`python $BOARD ship "<name>"`), and stop. Don't re-implement.

## 3. Implement
- Build the change: backend + frontend + **tests**. Follow the repo's existing patterns and conventions.

## 4. Test — and prove it (see quality/prove-it-validation)
- Run the targeted tests for what you changed. Paste the real output.
- **Do not advance the card on an unproven claim.** If tests fail, fix or stop — never move to *In review* while red.

## 5. Commit
- Conventional message: `feat(area): …` / `fix(area): …`. Keep `board.json` changes in their own commit or let step 6 handle it.

## 6. Ship → In review (keep the board in sync)
- `python $BOARD ship "<name>"` (moves the card to *In review* locally).
- **If ONLINE:** `python $BOARD push` to mirror the move (and any new cards) to Trello.
- Open a PR / push the branch per the repo's flow.

## 7. Confirm clean state
- `git status` clean, the feat commit present, `python $BOARD show` shows the card under *In review*.
- Briefly report what shipped + the proof (test output, PR link).

## Rules
- ⚠ Never hand-edit `board.json` to fake a state — drive it through `board.py` so online/offline stay consistent.
- ⚠ Online conflict rule: **online wins**. Always `pull` before claiming; `push` after shipping.
- ⚠ One card at a time: finish through step 6 before claiming the next (avoids dangling branches/cards).
- ✅ New bug/idea discovered mid-flight? Add it as its own card (`board.py add "<name>" --list Backlog`) instead of scope-creeping the current one.
