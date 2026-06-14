---
name: dependency-graph
description: >-
  Print the dependency graph of board cards — recently closed + currently open — as a Mermaid diagram,
  an ASCII tree (roots first), plus cycle and dangling-reference diagnostics. Reads `depends-on:` lines
  from card descriptions. Provider-agnostic (local board.json, Trello, Jira) via board.py.
  Use when the user says "/dependency-graph", "show the dependency graph", "what blocks what",
  "print dependencies", "muestra el grafo de dependencias", "qué bloquea a qué", "qué depende de qué".
  Bilingual (EN/ES). Requires this category's scripts/board.py + scripts/dep_graph.py.
---

# Dependency graph of open + closed cards

Show how the work connects: what must finish before what, what's already done, and where the
chain is broken (cycles, references to cards that don't exist). Decision aid, not decoration.

## Language / Idioma
Work and report in the user's language (EN/ES).

## Dependency convention
A card declares its blockers with a single line in its description:

```
depends-on: Auth API; Login UI
```

Comma- or semicolon-separated, matched to card **names** (case-insensitive). `triage` writes these;
you can also add them by hand. A card in a **done** list (`Done`/`Shipped`/`Closed` by default) renders as closed.

## Steps
1. **Sync first.** `python board.py status`; if online, `python board.py pull` (remote wins) so the
   graph reflects the live board, not a stale mirror.
2. **Render.** Run the helper against the board file:
   - All cards (open + recently closed): `python scripts/dep_graph.py --file board.json`
   - Open only (hide finished work): `python scripts/dep_graph.py --file board.json --open-only`
   - Custom done lists: add `--done-list Done --done-list "Live 1.0"` (repeatable).
3. **Read it back to the user.** Paste the Mermaid block (renders in any Markdown/Mermaid viewer or a
   GitHub PR) and the ASCII tree. Then **interpret**, don't just dump:
   - Roots = unblocked, start-here work. Deep leaves = most-blocked.
   - `[x]` = closed, `[ ]` = open.
4. **Act on the diagnostics — these are the point:**
   - **⚠ Cycles** → a dependency loop that can never resolve. Flag for `triage`/`breakdown` to break it
     (usually one edge is wrong or two cards should merge).
   - **⚠ Dangling** → `depends-on` names a card that isn't on the board (typo, or it was pruned).
     Fix the name or drop the dependency.
5. **Optional: save it.** Offer to write the Mermaid to a `.md` so it can be committed / attached to a PR
   (pairs with `reporting/` and `quality/prove-it-validation`).

## Rules
- ⚠ The graph is only as good as the `depends-on:` lines. If cards clearly depend on each other but say
  nothing, note it and hand off to `triage` (its dependency-detection pass) rather than guessing silently.
- ⚠ Don't "fix" a cycle by deleting a card here — surface it; breaking it is a `triage`/`breakdown` decision.
- ✅ Closed cards stay in the graph by default so you can see what a now-open card was waiting on.
  Use `--open-only` when the user just wants the live frontier.
