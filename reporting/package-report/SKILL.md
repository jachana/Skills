---
name: package-report
description: >-
  Assemble and VALIDATE a client deliverable package — verify every artifact actually
  renders/parses (HTML reports draw their graphs, PDFs render, CSVs parse, scripts
  compile), generate a manifest/README, and zip only after every check passes. Use when
  the user says "package the deliverable", "prepare the zip for the client", "bundle the
  report", "empaqueta el entregable", "arma el zip para el cliente", "prepara la entrega",
  "/package-report" — or whenever a set of reports/models/scripts is about to be sent to
  a client. Never ship an artifact you didn't open.
---

# Package a client deliverable — validate, then zip

A deliverable with one blank graph or one CSV that doesn't parse undoes the credibility
of everything else in the zip. The rule here: **every artifact gets opened/executed before
it gets packaged** — the zip is the last step, not the first.

## Language / Idioma
Work in the user's language (EN/ES). The package README is written in the client's language.

## Model & effort
| Phase | Model | Effort | Why |
|---|---|---|---|
| Validation scripts (parse checks, zip listing) | haiku | low | mechanical |
| Judging rendered output + writing the README | sonnet | medium | "does this graph actually show the data" is judgment |

Escalate only if the deliverable includes a written analysis — that part is
`human-readable-report` territory (opus for exec/client-strategic).

## Step 1 — Inventory (the manifest)

List what goes in: reports (HTML/PDF/DOCX), graphs/images, data tables (CSV/XLSX),
scripts, model files, README. Confirm with the user if the set is ambiguous — and ask
what must NOT go in (internal notes, prices on a technical copy, raw creds).

## Step 2 — Validate every artifact by type

| Type | Check | Watch for |
|---|---|---|
| HTML report | Open it (headless browser or render + screenshot) and **look**: do the graphs draw? | An uninvoked IIFE / missing JS = a structurally-valid page with blank charts. A parse-check alone misses this. |
| PDF | Render; page count > 0; spot-check pages as images | Missing images/fonts render as blanks — look at a page, don't just `ls` the file. |
| CSV / tables | Parse programmatically (python/pandas); row+column counts vs expectation | Encoding (UTF-8 vs Latin-1 for ES text), delimiter, truncated last row. |
| Scripts | Syntax check (`python -m py_compile`, `node --check`, …) + README says how to run them | A script that imports a file NOT in the zip. Check its imports/paths against the manifest. |
| Images / graphs as files | Open; nonzero size; **fresher than their source data** (mtime) | Stale regenerated assets — the old-halo problem. Regenerate if in doubt. |
| Model files | Load headers / expected size; the loading script in the zip can read them | Shipping the wrong (non-best) checkpoint — verify against the error table. |

Fix or flag each failure, then **re-validate the fixed artifact** — don't assume the fix took.

## Step 3 — README / manifest

Generate a short README in the package root: what this delivery contains (one line per
file/folder), how to run any scripts (exact commands + requirements), the date and
version/period covered. In the client's language.

## Step 4 — Zip + verify the zip

- Zip with a clean name: `<client>-<deliverable>-<YYYY-MM-DD>.zip`.
- **List the zip's contents** and diff against the manifest — nothing missing, nothing extra.
- Junk sweep: no `.env`/secrets, `__pycache__`, `.pyc`, `node_modules`, editor droppings,
  internal scratch files.
- Size sanity vs expectation (a 2 KB "model" or a 900 MB "report" = something's wrong).

## Step 5 — Evidence block

Report completion with the `quality/prove-it-validation` format: the validation log
(each artifact → check → result), the zip listing, and the final path. If any check
could not run, the package is **not ready** — say what's unverified instead of shipping it.

## Rules
- ⚠ Never zip first and validate later — order is the whole point.
- ⚠ Never ship an HTML/PDF you didn't visually open this session.
- ✅ Pair with `human-readable-report` for the narrative and `frontend-design` if a report page needs to look client-grade.
