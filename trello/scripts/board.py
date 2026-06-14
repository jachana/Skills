#!/usr/bin/env python3
"""
board.py — an offline-first kanban that *optionally* syncs to Trello.

The whole point: the `ship` skill works the same whether or not you have a
Trello account. With no credentials it's a pure local board (board.json).
With TRELLO_API_KEY / TRELLO_TOKEN / TRELLO_BOARD_ID set, `pull` / `push`
mirror that local board to/from Trello (matching cards by name).

Stdlib only — no pip install. Reads creds from the environment (or a sibling
.env file); NEVER stores them in board.json.

Usage:
  python board.py init [--lists "Backlog,To Do,In progress,In review,Done"]
  python board.py show
  python board.py add "Card name" [--list "Backlog"] [--desc "..."]
  python board.py move "Card name" --to "In progress"
  python board.py claim "Card name"          # -> In progress
  python board.py ship  "Card name"          # -> In review
  python board.py pick                        # print top card of the first non-empty backlog list
  python board.py rm   "Card name"
  python board.py pull                         # Trello -> local (online wins)
  python board.py push                         # local -> Trello
  python board.py status                       # online/offline + counts

All commands accept --file <path> (default: ./board.json).
Spanish flags also accepted as aliases (see --help).
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path

DEFAULT_LISTS = ["Backlog", "To Do", "In progress", "In review", "Done"]
CLAIM_LIST = "In progress"
SHIP_LIST = "In review"
TRELLO_API = "https://api.trello.com/1"


# ── env / creds ────────────────────────────────────────────────────────────
def load_env(start: Path):
    """Best-effort: load a sibling/ancestor .env into os.environ (without overwriting)."""
    for d in [start, *start.parents]:
        envf = d / ".env"
        if envf.is_file():
            for line in envf.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
            break


def creds():
    return (
        os.environ.get("TRELLO_API_KEY"),
        os.environ.get("TRELLO_TOKEN"),
        os.environ.get("TRELLO_BOARD_ID"),
    )


def online():
    return all(creds())


# ── local board ────────────────────────────────────────────────────────────
def load(path: Path):
    if not path.is_file():
        sys.exit(f"No board at {path}. Run: python board.py init")
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, board: dict):
    path.write_text(json.dumps(board, indent=2, ensure_ascii=False), encoding="utf-8")


def find_card(board, name):
    for c in board["cards"]:
        if c["name"].strip().lower() == name.strip().lower():
            return c
    return None


# ── Trello API ─────────────────────────────────────────────────────────────
def _req(method, path, params=None, data=None):
    key, token, _ = creds()
    params = dict(params or {})
    params.update({"key": key, "token": token})
    url = f"{TRELLO_API}{path}?{urllib.parse.urlencode(params)}"
    body = urllib.parse.urlencode(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode("utf-8")
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        sys.exit(f"Trello API error {e.code}: {e.read().decode('utf-8', 'replace')}")
    except urllib.error.URLError as e:
        sys.exit(f"Network error talking to Trello: {e.reason}. (Work offline — your local board still works.)")


def trello_lists(board_id):
    return _req("GET", f"/boards/{board_id}/lists", {"cards": "none"})


def trello_cards(board_id):
    return _req("GET", f"/boards/{board_id}/cards", {"fields": "name,desc,idList"})


# ── commands ───────────────────────────────────────────────────────────────
def cmd_init(args, path):
    if path.is_file() and not args.force:
        sys.exit(f"{path} already exists. Use --force to overwrite.")
    lists = [s.strip() for s in args.lists.split(",")] if args.lists else DEFAULT_LISTS
    save(path, {"lists": lists, "cards": []})
    print(f"Initialized board at {path} with lists: {', '.join(lists)}")


def cmd_show(args, path):
    board = load(path)
    mode = "ONLINE (Trello)" if online() else "OFFLINE (local only)"
    print(f"# Board — {mode}\n")
    for lst in board["lists"]:
        cards = [c for c in board["cards"] if c["list"] == lst]
        print(f"## {lst} ({len(cards)})")
        for c in cards:
            print(f"  - {c['name']}")
        if not cards:
            print("  (empty)")
        print()


def cmd_add(args, path):
    board = load(path)
    if find_card(board, args.name):
        sys.exit(f"Card already exists: {args.name}")
    lst = args.list or board["lists"][0]
    if lst not in board["lists"]:
        sys.exit(f"Unknown list '{lst}'. Known: {', '.join(board['lists'])}")
    board["cards"].append({"name": args.name, "list": lst, "desc": args.desc or ""})
    save(path, board)
    print(f"Added '{args.name}' to {lst}")


def cmd_move(args, path):
    board = load(path)
    card = find_card(board, args.name)
    if not card:
        sys.exit(f"No card named: {args.name}")
    if args.to not in board["lists"]:
        sys.exit(f"Unknown list '{args.to}'. Known: {', '.join(board['lists'])}")
    card["list"] = args.to
    save(path, board)
    print(f"Moved '{card['name']}' -> {args.to}")


def cmd_claim(args, path):
    args.to = CLAIM_LIST
    cmd_move(args, path)


def cmd_ship(args, path):
    args.to = SHIP_LIST
    cmd_move(args, path)


def cmd_pick(args, path):
    board = load(path)
    # "Most ready" = the pre-progress list closest to In progress (rightmost),
    # e.g. prefer a "To Do" card over a "Backlog" one. Iterate right-to-left.
    backlog_lists = [l for l in board["lists"] if l not in (CLAIM_LIST, SHIP_LIST, "Done")][::-1]
    for lst in backlog_lists:
        for c in board["cards"]:
            if c["list"] == lst:
                print(c["name"])
                return
    print("(no eligible cards)")


def cmd_rm(args, path):
    board = load(path)
    card = find_card(board, args.name)
    if not card:
        sys.exit(f"No card named: {args.name}")
    board["cards"].remove(card)
    save(path, board)
    print(f"Removed '{args.name}'")


def cmd_status(args, path):
    if online():
        _, _, bid = creds()
        print(f"ONLINE — synced board id {bid}")
    else:
        print("OFFLINE — no TRELLO_* env vars set. Local board is fully usable; "
              "set credentials (see .env.example) to enable pull/push.")
    if path.is_file():
        board = load(path)
        print(f"{len(board['cards'])} cards across {len(board['lists'])} lists at {path}")


def cmd_pull(args, path):
    if not online():
        sys.exit("Cannot pull: TRELLO_API_KEY / TRELLO_TOKEN / TRELLO_BOARD_ID not set. "
                 "You can keep working offline.")
    _, _, bid = creds()
    lists = trello_lists(bid)
    id2name = {l["id"]: l["name"] for l in lists}
    cards = trello_cards(bid)
    board = {
        "lists": [l["name"] for l in lists],
        "cards": [{"name": c["name"], "list": id2name.get(c["idList"], "Backlog"), "desc": c.get("desc", "")}
                  for c in cards],
    }
    save(path, board)
    print(f"Pulled {len(board['cards'])} cards / {len(board['lists'])} lists from Trello (online wins).")


def cmd_push(args, path):
    if not online():
        sys.exit("Cannot push: Trello credentials not set. Working offline.")
    _, _, bid = creds()
    board = load(path)
    remote_lists = {l["name"]: l["id"] for l in trello_lists(bid)}
    # create any missing lists
    for lst in board["lists"]:
        if lst not in remote_lists:
            new = _req("POST", "/lists", data={"name": lst, "idBoard": bid})
            remote_lists[lst] = new["id"]
            print(f"  created Trello list: {lst}")
    remote_cards = {c["name"].strip().lower(): c for c in trello_cards(bid)}
    created = moved = 0
    for c in board["cards"]:
        target_list_id = remote_lists[c["list"]]
        existing = remote_cards.get(c["name"].strip().lower())
        if existing:
            if existing["idList"] != target_list_id:
                _req("PUT", f"/cards/{existing['id']}", data={"idList": target_list_id})
                moved += 1
        else:
            _req("POST", "/cards", data={"name": c["name"], "desc": c.get("desc", ""), "idList": target_list_id})
            created += 1
    print(f"Pushed to Trello: {created} created, {moved} moved.")


COMMANDS = {
    "init": cmd_init, "show": cmd_show, "list": cmd_show, "add": cmd_add,
    "move": cmd_move, "claim": cmd_claim, "ship": cmd_ship, "pick": cmd_pick,
    "rm": cmd_rm, "status": cmd_status, "pull": cmd_pull, "push": cmd_push,
}


def main():
    p = argparse.ArgumentParser(description="Offline-first kanban with optional Trello sync.")
    p.add_argument("command", choices=COMMANDS.keys())
    p.add_argument("name", nargs="?", help="Card name (for add/move/claim/ship/rm)")
    p.add_argument("--file", default="board.json", help="Board JSON path (default: board.json)")
    p.add_argument("--list", "--lista", help="Target list for 'add'")
    p.add_argument("--to", "--a", help="Destination list for 'move'")
    p.add_argument("--desc", "--desc-es", help="Card description for 'add'")
    p.add_argument("--lists", "--listas", help="Comma-separated lists for 'init'")
    p.add_argument("--force", action="store_true", help="Overwrite on 'init'")
    args = p.parse_args()

    path = Path(args.file).expanduser().resolve()
    load_env(path.parent)

    if args.command in ("add", "move", "claim", "ship", "rm") and not args.name:
        sys.exit(f"'{args.command}' needs a card name.")
    if args.command == "move" and not args.to:
        sys.exit("'move' needs --to <list>.")

    COMMANDS[args.command](args, path)


if __name__ == "__main__":
    main()
