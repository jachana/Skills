# project-management — kanban that works anywhere

A disciplined set of board-management skills built on a **provider-agnostic** kanban engine. The core idea: the workflow is the same whether your board lives **locally**, in **Trello**, in **Jira**, or somewhere else — only the sync adapter changes.

| | Local (default) | Trello | Jira |
|---|---|---|---|
| Trigger | no provider env set | `TRELLO_*` set | `JIRA_*` set |
| Store | `board.json` | Trello board (mirrored locally) | Jira project (mirrored locally) |
| Override | `PM_PROVIDER=local` | `PM_PROVIDER=trello` | `PM_PROVIDER=jira` |

Adding another tool = implement `pull()`/`push()` in a provider class in `scripts/board.py`. Local always works with zero setup.

## Skills

| Skill | Does |
|---|---|
| [`ship`](ship/) | Take the top card all the way to shipped — claim, verify it isn't already done, build + test, commit, move to *In review*, keep the board in sync. |
| [`triage`](triage/) | Sort an unsorted pile — route each item to the right list, set priority, flag dupes/oversized/blocked. |
| [`breakdown`](breakdown/) | Split an oversized/vague card into 3–7 small, ordered, independently-shippable subtasks with acceptance criteria. |
| [`refine`](refine/) | **Backlog refinement / groom / enrich** (umbrella) — bring thin cards to "ready" (context + acceptance criteria + priority + right-sized); health-pass the top of the backlog. |
| [`prune`](prune/) | Remove dead weight — duplicates, done-but-open, obsolete, zombie cards — with confirmation before deleting. |

They hand off to each other: `triage` flags items for `breakdown` (too big), `refine` (too thin), or `prune` (dead/dupe).

## The engine — `scripts/board.py`

Pure stdlib Python, no install. Reads provider creds from env or a sibling `.env`; never writes them to disk.

```bash
python scripts/board.py init
python scripts/board.py add "Card" --list "To Do"
python scripts/board.py pick           # top "ready" card
python scripts/board.py claim "Card"   # -> In progress
python scripts/board.py ship  "Card"   # -> In review
python scripts/board.py show | status
python scripts/board.py pull            # remote -> local (remote wins)
python scripts/board.py push            # local  -> remote
```
Spanish flag aliases work (`--lista`, `--a`, `--listas`). **Conflict rule: remote wins** — `pull` before claiming, `push` after shipping.

## Setup (optional — only for a remote provider)
Copy `.env.example` → `.env`, fill in one provider's block (Trello or Jira), then `python scripts/board.py pull` to seed the mirror. No `.env` → local-only board, nothing lost.

## Status of providers
- **local** — fully implemented + tested.
- **trello** — implemented (lists + cards, create/move). 
- **jira** — implemented against Jira Cloud REST v3 (status↔list mapping, create + transition). Verify against your instance before relying on it.

## Companion skills
- **caveman** — terse commit messages + status notes.
- **quality/prove-it-validation** (this repo) — don't move a card to *In review* on an unproven claim; show the passing run.
