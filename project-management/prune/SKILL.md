---
name: prune
description: >-
  Clean dead weight off a project board — duplicates, stale/obsolete cards, things already done, and
  zombie items no one will ever do. Proposes removals with reasons and gets confirmation before deleting.
  Provider-agnostic (local board.json, Trello, Jira) via board.py. Use when the user says "/prune",
  "clean up the board", "remove dead cards", "kill duplicates", "limpia el tablero", "elimina tarjetas muertas",
  "saca los duplicados". Bilingual (EN/ES).
---

# Prune — remove dead weight (carefully)

A board full of zombie cards hides the real work. Cut what's dead — but confirm before deleting, because deletion is hard to reverse.

## Language / Idioma
Work and report in the user's language (EN/ES).

## Steps
1. **Sync first.** `python board.py status`; if online, `python board.py pull`.
2. **Scan for removal candidates:**
   - **Duplicates** — two cards for the same work (keep the better-described one).
   - **Already done** — work shipped but the card never moved to Done.
   - **Obsolete** — superseded by a decision, no longer relevant.
   - **Stale zombies** — sat untouched a long time with no priority and no owner; nobody will do it.
3. **Classify, don't nuke.** For each candidate, propose: **delete**, **archive/Done**, or **keep** — each with a one-line reason.
4. **Confirm before destructive action.** Present the list and get the user's go-ahead. Deletion via `python board.py rm "<name>"` (local) / archived on the provider after `push`. **Never bulk-delete without confirmation.**
5. **Report** what was removed/archived/kept and the board's new card count.

## Rules
- ⚠ Removal is hard to undo — when unsure whether a card is dead, default to **keep** and flag it, don't delete.
- ⚠ Confirm before deleting anything you didn't create. Show the user the exact list first.
- ✅ Prefer archive/Done over hard delete when the card has any historical value.
