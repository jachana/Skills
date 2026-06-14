---
name: refine
description: >-
  Backlog refinement / grooming / enrichment — make a backlog ready to work: enrich thin cards with
  context and acceptance criteria, estimate, order by priority, and flag what's blocked, duplicated, or
  needs splitting. The umbrella for "refine", "groom", "enrich", "backlog refinement". Provider-agnostic
  (local board.json, Trello, Jira) via board.py. Use when the user says "/refine", "/groom", "/enrich",
  "refine the backlog", "groom the board", "enrich this card", "refina el backlog", "enriquece esta tarjeta",
  "deja el backlog listo". Bilingual (EN/ES).
---

# Refine — make the backlog ready (groom / enrich)

A refined backlog means the next person can pick the top card and start with zero questions. Two modes, same skill:

- **Enrich (one card)** — flesh out a single thin card.
- **Groom (whole backlog)** — a health pass over the top of the backlog.

## Language / Idioma
Work and report in the user's language (EN/ES).

## Enrich a single card
Bring a thin card up to "ready":
1. **Context** — what and why, in plain terms; link the relevant repo / second-brain notes.
2. **Acceptance criteria** — bulleted, testable ("returns 401 on bad password"). Pairs with `quality/prove-it-validation`.
3. **Scope edges** — what's explicitly out.
4. **Size signal** — rough effort; if it's clearly too big, hand to `breakdown`.
5. Write it back to the card description (`--desc`) and `push` if online.

## Groom the whole backlog
A pass over the top ~10–15 cards:
1. **Sync.** `python board.py status`; if online, `python board.py pull`.
2. **For each top card, judge readiness:** has context + acceptance criteria + priority? If not, enrich it (above).
3. **Re-order** by priority/value so the top of the backlog is genuinely the next-best work.
4. **Route the exceptions:** too big → `breakdown`; dead/dupe → `prune`; unsorted inbox → `triage`.
5. **Apply** changes via board.py; `push` if online.
6. **Report** "Definition of Ready" status: how many top cards are ready vs. need work, and the ordered top 5.

## Rules
- ⚠ Don't fabricate acceptance criteria or estimates — derive from the card/context, or ask. A confidently-wrong criterion is worse than a flagged gap.
- ⚠ Enrich, don't redesign — refinement clarifies intent, it doesn't quietly change scope. Surface scope changes to the user.
- ✅ "Ready" = clear goal + acceptance criteria + priority + right-sized. Anything missing one is not ready; say so.
