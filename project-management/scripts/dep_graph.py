#!/usr/bin/env python3
"""
dep_graph.py — print the dependency graph of board cards (open + closed).

Dependencies are read from each card's description as a line:
    depends-on: Other Card; Another Card
(comma or semicolon separated; matched to card names, case-insensitive).
Cards in a "done" list count as closed; everything else is open.

Outputs Mermaid (paste into any Markdown/Mermaid renderer) + an ASCII tree,
and warns on cycles and dangling references.

  python dep_graph.py                      # open + closed, from ./board.json
  python dep_graph.py --open-only
  python dep_graph.py --file board.json --done-list Done
"""
import argparse, json, re, sys
from pathlib import Path

# Windows consoles default to cp1252 and crash on box-drawing/check glyphs.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DONE_DEFAULT = {"done", "shipped", "closed"}


def parse_deps(desc):
    m = re.search(r'(?im)^\s*depends-on\s*:\s*(.+)$', desc or "")
    if not m:
        return []
    return [d.strip() for d in re.split(r'[;,]', m.group(1)) if d.strip()]


def main():
    ap = argparse.ArgumentParser(description="Print the card dependency graph.")
    ap.add_argument("--file", default="board.json")
    ap.add_argument("--open-only", action="store_true")
    ap.add_argument("--done-list", action="append", help="List name(s) treated as closed (repeatable).")
    a = ap.parse_args()

    path = Path(a.file).expanduser().resolve()
    if not path.is_file():
        sys.exit(f"No board at {path}.")
    board = json.loads(path.read_text(encoding="utf-8"))
    done_lists = {s.lower() for s in (a.done_list or [])} or DONE_DEFAULT

    cards = {}
    for c in board["cards"]:
        closed = c["list"].lower() in done_lists
        if a.open_only and closed:
            continue
        cards[c["name"].strip().lower()] = {"name": c["name"], "closed": closed, "deps": parse_deps(c.get("desc", ""))}

    # edges + validation
    edges, dangling = [], []
    for key, c in cards.items():
        for d in c["deps"]:
            dk = d.strip().lower()
            if dk in cards:
                edges.append((dk, key))          # dependency -> dependent
            else:
                dangling.append((c["name"], d))

    # cycle detection (DFS)
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {k: WHITE for k in cards}
    adj = {k: [] for k in cards}
    for src, dst in edges:
        adj[src].append(dst)
    cycle = []
    def dfs(u, stack):
        color[u] = GRAY
        for v in adj[u]:
            if color[v] == GRAY:
                cycle.append(" -> ".join(cards[x]["name"] for x in stack[stack.index(v):] + [v]))
            elif color[v] == WHITE:
                dfs(v, stack + [v])
        color[u] = BLACK
    for k in cards:
        if color[k] == WHITE:
            dfs(k, [k])

    # ── Mermaid ──
    print("## Dependency graph (Mermaid)\n")
    print("```mermaid")
    print("graph TD")
    for key, c in cards.items():
        style = ":::closed" if c["closed"] else ""
        print(f'  {hash_id(key)}["{c["name"]}"]{style}')
    for src, dst in edges:
        print(f"  {hash_id(src)} --> {hash_id(dst)}")
    print("  classDef closed fill:#ddd,stroke:#999,color:#666;")
    print("```\n")

    # ── ASCII roots-first ──
    print("## Dependency tree (roots first)\n")
    indeg = {k: 0 for k in cards}
    for _, dst in edges:
        indeg[dst] += 1
    roots = [k for k in cards if indeg[k] == 0]
    seen = set()
    def show(u, depth):
        c = cards[u]
        mark = "[x]" if c["closed"] else "[ ]"
        print(f"{'  ' * depth}{mark} {c['name']}")
        if u in seen:
            return
        seen.add(u)
        for v in adj[u]:
            show(v, depth + 1)
    for r in sorted(roots, key=lambda k: cards[k]["name"]):
        show(r, 0)
    if not roots and cards:
        print("_(no roots — every card depends on something; see cycles below)_")

    # ── diagnostics ──
    if cycle:
        print("\n## ⚠ Cycles detected")
        for c in sorted(set(cycle)):
            print(f"- {c}")
    if dangling:
        print("\n## ⚠ Dangling dependencies (named card not on board / filtered out)")
        for who, dep in dangling:
            print(f'- "{who}" depends-on "{dep}" — not found')
    print(f"\n_{len(cards)} cards · {len(edges)} edges · "
          f"{sum(1 for c in cards.values() if c['closed'])} closed / {sum(1 for c in cards.values() if not c['closed'])} open_")


def hash_id(key):
    return "n" + str(abs(hash(key)) % (10 ** 8))


if __name__ == "__main__":
    main()
