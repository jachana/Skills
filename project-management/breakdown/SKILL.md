---
name: breakdown
description: >-
  Split an oversized or vague card into small, independently-shippable subtasks with clear acceptance criteria.
  Provider-agnostic (local board.json, Trello, Jira) via board.py. Use when the user says "/breakdown",
  "break this card down", "split this into tasks", "this card is too big", "desglosa esta tarjeta",
  "divide esto en subtareas", "esta tarjeta es muy grande". Bilingual (EN/ES).
---

# Breakdown — split a big card into shippable pieces

A card you can't finish in one sitting hides risk. Break it until each piece is small, testable, and ordered.

## Language / Idioma
Work and report in the user's language (EN/ES).

## Steps
1. **Read the card** — its title, description, and any linked context (repo, second-brain notes).
2. **Restate the goal** in one sentence so the split stays anchored to the outcome.
3. **Decompose into 3–7 subtasks**, each:
   - **Independently shippable** — delivers value or is verifiable on its own.
   - **Small** — roughly a single focused work session.
   - **Acceptance criterion** — one line stating how you'll know it's done (pairs with `quality/prove-it-validation`).
   - **Ordered** — note dependencies; put the unblocking piece first.
4. **Surface the seams** — call out the riskiest/most-uncertain subtask so it can be tackled (or spiked) first.
5. **Apply** — either as a checklist on the parent card, or as child cards. With board.py:
   `python board.py add "<parent>: <subtask>" --list "To Do"` per piece; keep the parent as the umbrella. `push` if online.
6. **Report** the ordered list + which subtask to start with and why.

## Rules
- ⚠ Don't split into busywork — each subtask must move the goal, not just decompose for its own sake.
- ⚠ Don't lose the parent's intent; every subtask traces back to the restated goal.
- ✅ If the card is vague rather than big, send it to `refine` first — you can't split what isn't understood.
