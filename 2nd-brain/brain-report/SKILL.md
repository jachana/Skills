---
name: brain-report
description: >-
  Generate a generalized progress report across ALL projects in the central Obsidian "brain" vault —
  progress over a time period, what got done, pending tasks, overall project states, and what needs attention.
  Use when the user says "/brain-report", "give me a progress report", "what happened this week across projects",
  "status of everything", "reporte de avance", "qué se hizo esta semana", "estado general de los proyectos",
  "qué está pendiente". Runs a deterministic aggregator (Brain-Report.ps1) then writes a human narrative on top.
  Reads the vault from BRAIN_PATH. Bilingual (EN/ES).
---

# Brain progress report (root-brain, cross-project)

This is a **root-brain** capability: it reads every project note in the vault and rolls them up. (Contrast `brain-sync`, which is single-project and never looks across projects.)

## Language / Idioma
Write the narrative in the user's language (EN/ES). The aggregator's tables stay as generated.

## Step 1 — Run the deterministic aggregator
Locate `Brain-Report.ps1` (this category's `scripts/`). It does the parsing so you don't hallucinate numbers.
```powershell
pwsh Brain-Report.ps1 -BrainRoot "$env:BRAIN_PATH" -Since 7d
# or an explicit window:
pwsh Brain-Report.ps1 -BrainRoot "$env:BRAIN_PATH" -Since 2026-06-01 -Until 2026-06-14 -Out report.md
```
Ask the user for the **time window** if they didn't give one (default: last 7 days). It emits Markdown with these sections, already computed from the notes:
- **Overview** — table: status / phase / progress / priority / activity count / open tasks per project
- **Activity in period** — dated log entries per project, in window
- **Completed in period** — `[MILESTONE]`/`[DELIVERED]` log entries
- **Pending tasks** — all open `[ ]` tasks, grouped, priority-sorted
- **Needs attention** — active-but-stale projects + anything with blockers

## Step 2 — Add the narrative the script can't
The script gives facts; you add judgment. On top of (not replacing) the generated report, write:
- **Headline (TL;DR)** — 2–3 sentences: the period's net movement. What advanced, what stalled, the one thing that needs a decision.
- **Per-priority read** — call out p0/p1 projects explicitly; bury p2 noise.
- **Risks** — connect the "Needs attention" rows to consequences ("Medtracker blocked 25d on vendor keys → MVP date at risk").
- **Recommended focus** — where the user should spend the next cycle, with reasons.

Pair with `reporting/human-readable-report` for the writing style (lead with the conclusion, evidence over assertion, no filler).

## Step 3 — Ground every claim
- **Use only what the aggregator + notes contain.** Do not invent progress %, dates, or task counts — the script computed them; cite those.
- If a project's data looks wrong (e.g. `progress: 60` but no activity in 30d), flag the *data quality* issue rather than smoothing over it.
- If asked for a number the notes don't support, say it's not tracked.

## Step 4 — Deliver
- Default: post the report inline (generated sections + your narrative on top).
- Offer to save it into the vault (e.g. `Reports/<period>.md`) or render it (pair with `frontend-design`) if the user wants to share it.

## Notes
- This skill **reads** the vault; it does not modify project notes.
- Time windows: `-Since 7d` / `30d` or an ISO date. `-Until` defaults to today. `-IncludeArchived` to include archived projects.
- For *cross-project reuse* (not just status), use the sibling `brain-connect` skill.
