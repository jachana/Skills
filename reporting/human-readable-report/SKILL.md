---
name: human-readable-report
description: >-
  Write a report a human actually wants to read — status update, summary, analysis, retro, or briefing.
  Leads with the conclusion, structures for skimming, backs claims with evidence, and cuts filler.
  Use when the user says "write a report", "summarize this for <audience>", "status update",
  "haz un reporte", "resúmeme esto para el cliente", "informe de avance", or asks to turn raw
  notes/data/logs into something presentable. Output adapts to the audience and the user's language.
---

# Write a human-readable report

Default failure mode of AI reports: a flat wall of text that buries the answer. This skill forces the opposite.

## Language / Idioma
Write the report in the user's language (EN/ES). If the audience differs from the user (e.g. user writes Spanish but the report is for an English client), ask which language the **report** should be in.

## Before writing — get three things
1. **Audience** — who reads this? (exec / client / teammate / your future self). Drives depth and jargon.
2. **Purpose** — decision needed, status reassurance, or a record? Drives what leads.
3. **Source material** — the raw input. If thin, pull from the user's second-brain (`.brain/` files, vault notes) or ask.

If any is unclear and it changes the output, ask **one** sharp question. Otherwise infer and state your assumption.

## Structure (adapt, don't pad)
1. **TL;DR / Resumen** — 1–3 sentences with the actual answer or headline. The reader could stop here and be informed.
2. **Key points** — 3–6 bullets, each a claim + its evidence (number, link, file, quote). No claim without backing.
3. **Detail** — only the sections the audience needs. Use headings; keep paragraphs ≤4 lines.
4. **Risks / open questions** — what's unknown or could go wrong. Honesty here builds trust.
5. **Next steps / Ask** — concrete actions + owner. If the report needs a decision, state the options and your recommendation.

Drop any section that's empty — don't write "N/A" filler.

## Style rules
- **Lead with the conclusion**, then support it (inverted pyramid).
- **Evidence over assertion** — "deploys dropped to 4 min (from 11)" not "deploys are much faster". If you can't back a claim, label it an estimate or cut it.
- **Skimmable** — bold the load-bearing phrase in each bullet; tables for comparisons; short paragraphs.
- **No filler** — cut "it's worth noting", "in order to", "as we can see". (The **caveman** companion skill enforces this.)
- **Quantify** — dates, counts, deltas, money. Vague = useless.
- **Match the register** to the audience: execs get outcomes + money; engineers get specifics.

## Formats
- Default: Markdown. Offer to render to a styled HTML page (pair with **frontend-design**) or paste-ready email/Slack block if the user wants to send it.
- Long data → a table, not prose.

## Anti-patterns to avoid
- Restating the prompt back as an intro paragraph.
- Hedging every sentence ("might", "could potentially", "seems to").
- A 6-paragraph preamble before the actual finding.
- Claiming results you didn't verify — if it's from a test/run, show the output; if not, say "unverified".
