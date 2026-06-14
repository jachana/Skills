---
name: brain-connect
description: >-
  Find useful cross-project links in the central Obsidian "brain": where something built, learned, or
  decided in ONE project is reusable in ANOTHER. Surfaces candidate pairs heuristically, then reasons over
  the notes to produce concrete "reuse X from A in B" recommendations. Use when the user says "/brain-connect",
  "what can these projects share", "find reuse across projects", "are any of my projects similar",
  "qué pueden compartir estos proyectos", "encuentra cosas reutilizables entre proyectos", "proyectos parecidos".
  Reads the vault from BRAIN_PATH; read-only. Bilingual (EN/ES).
---

# Brain connect — cross-project reuse finder

A **root-brain** capability. It looks across all project notes to spot leverage: a component, decision, vendor, or lesson from one project that another could borrow. (Single-project agents never do this — see the isolation rule in `brain-sync`.)

## Language / Idioma
Report in the user's language (EN/ES).

## Step 1 — Get candidate pairs (don't eyeball the whole vault)
Run the heuristic finder so you start from grounded candidates, not a vibe:
```powershell
pwsh Brain-Connect.ps1 -BrainRoot "$env:BRAIN_PATH" -Top 20 -MinShared 2
```
It ranks project pairs by shared significant terms (frontmatter `tags`/`stack`/`tech` + `Scope`/`Milestones` keywords) and prints a table of candidates with the overlapping terms. **These are leads, not conclusions.**

## Step 2 — Judge each candidate against the actual notes
For the top candidate pairs (and any the user names), open both project notes and look for *real, actionable* reuse — not just shared words:
- **Component / code** — A built an auth flow, PDF export, websocket layer… B has the same need.
- **Decision / ADR** — A chose a library/approach after evaluation; B is about to make the same call.
- **Vendor / integration** — same external API, same credentials path, same gotcha.
- **Lesson (`[LESSON]` log entries)** — A hit a pitfall B can avoid.
- **Data / domain model** — overlapping entities worth a shared schema.

Discard shallow matches (two projects both say "dashboard" but share nothing usable).

## Step 3 — Recommend concretely
For each real link, write one tight recommendation:
> **Aclara → Medtracker:** Aclara's `pdf-export` module (built 2026-06, see its Log) covers Medtracker's pending "Export to PDF" task. Lift it instead of rebuilding — saves the open p1 task.

Include: source project + the specific artifact (cite where in the note), target project + the need it fills, and the action ("reuse", "copy the ADR", "talk to the same vendor"). Rank by payoff.

## Step 4 — Respect the boundary
- This skill runs at the **root brain**, with the user's intent to cross-reference. Local project agents must NOT pull other projects' info on their own — they only *report up* a `[CROSS-REF]` signal for the brain to act on (see `brain-sync`). 
- When you act on such a signal or make a new link, suggest the user record it (e.g. a note in each project's `## Log` or a `Patterns/` note) so the knowledge compounds.

## Notes
- Read-only: never edits project notes unless the user asks you to record a found link.
- The heuristic can miss semantic matches with no shared vocabulary — if the user suspects a link the script didn't surface, read the two notes directly and judge.
