# trello — kanban ship workflow (online **or** offline)

A disciplined "pick → verify → implement → test → ship" loop over a kanban board. The key design choice: **it doesn't require Trello.** With no credentials it drives a local `board.json`; with `TRELLO_*` env vars set, the same workflow mirrors to a real Trello board.

## Skill

| Skill | Use it when… |
|---|---|
| [`ship`](ship/) | You want to take the top backlog card all the way to shipped — claim it, confirm it isn't already done, implement + test, commit, and move it to **In review**, keeping the board in sync. |

## Two modes, one workflow

| | Offline (default) | Online (Trello) |
|---|---|---|
| Trigger | no `TRELLO_*` vars set | `TRELLO_API_KEY` + `TRELLO_TOKEN` + `TRELLO_BOARD_ID` set |
| Board store | local `board.json` | real Trello board (mirrored to `board.json`) |
| Commands | `board.py …` | `board.py pull` / `push` wrap the same commands |

The `ship` skill auto-detects the mode via `board.py status` and behaves identically either way — only the final "sync" step differs (a `push` to Trello vs. a local save).

## The board helper — `scripts/board.py`

Pure stdlib Python, no install. Reads Trello creds from the environment or a sibling `.env`; never writes them to disk.

```bash
python scripts/board.py init                       # create board.json (default 5 lists)
python scripts/board.py add "Card name" --list "To Do"
python scripts/board.py pick                        # top "ready" card
python scripts/board.py claim "Card name"           # -> In progress
python scripts/board.py ship  "Card name"           # -> In review
python scripts/board.py show
python scripts/board.py status                      # ONLINE vs OFFLINE + counts

# Online only (no-op message if creds missing):
python scripts/board.py pull                         # Trello -> local (online wins)
python scripts/board.py push                         # local  -> Trello
```

Spanish flag aliases work too (`--lista`, `--a`, `--listas`).

## Setup (optional — only for online mode)

1. Copy `.env.example` → `.env`, fill in `TRELLO_API_KEY`, `TRELLO_TOKEN`, `TRELLO_BOARD_ID`. See the comments in that file for where to get each.
2. `python scripts/board.py pull` to seed the local mirror from Trello.
3. From then on, `ship` keeps both in sync. **Conflict rule: online wins** — a `pull` overwrites local.

No `.env`? You lose nothing — you just get a local-only board.

## Companion skills
- **caveman** — keeps your commit messages and status notes terse.
- **quality/prove-it-validation** (this repo) — pairs with step "run tests": don't move a card to *In review* on an unproven claim; show the passing run.
