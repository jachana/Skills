---
name: triage
description: >-
  Sort a pile of incoming/unsorted items on a project board — route each to the right list, set priority,
  flag duplicates, and surface what needs a human decision. Provider-agnostic (local board.json, Trello, Jira)
  via board.py. Use when the user says "/triage", "triage the backlog", "sort the inbox", "what should I work on",
  "tria las tarjetas", "ordena el backlog", "clasifica lo que entró". Bilingual (EN/ES).
---

# Triage — sort the board

Turn an undifferentiated pile into a prioritized, routed board. Decide; don't just describe.

## Language / Idioma
Work and report in the user's language (EN/ES).

## Steps
1. **Sync first.** `python board.py status`; if online, `python board.py pull` (remote wins).
2. **Read the unsorted items** — cards in `Backlog`/inbox without a priority or clear home.
3. **For each item decide:**
   - **Route** — which list it belongs in (`To Do` if ready, stays `Backlog` if not, `Done`/remove if obsolete).
   - **Priority** — p0 (drop everything) / p1 (this week) / p2 (later). Justify in one phrase.
   - **Duplicate?** — if it restates an existing card, flag it for `prune` rather than keeping both.
   - **Too big / vague?** — flag for `breakdown` (needs splitting) or `refine` (needs detail/acceptance criteria).
   - **Blocked / needs human input?** — surface it explicitly; don't silently bury it.
4. **Apply** via board.py (`move … --to`, `add`, etc.). For provider boards, `push` after.
5. **Report** a short triage summary: counts per bucket, the top 3 to do next, and anything that needs the user's call.

## Rules
- ⚠ Don't invent priorities from nothing — base them on stated impact/urgency, or ask when genuinely unclear.
- ⚠ Don't delete here — route obvious junk to `prune`'s judgment, not straight to the bin.
- ✅ Hand off: tag items for `breakdown` (too big), `refine` (too thin), `prune` (dead/dupe).
