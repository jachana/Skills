---
name: brain-sync
description: >-
  Protocol for working in a repo that contains a `.brain/` folder — the bridge to a central Obsidian
  "second brain" vault. Triggers automatically whenever the working directory or any ancestor contains
  a `.brain/` directory. Tells you what to read (CONTEXT/TASKS/ASKS), what to update (STATUS/LOG/ANSWERS),
  and what to NEVER touch. Also applies when the user says "/brain-sync", "sync with the brain",
  "sincroniza con el cerebro", or "qué dice el cerebro de este repo".
---

# Second-brain communication protocol

The `.brain/` folder in (or near) your working directory bridges this repo to a central Obsidian vault. Read this skill once per session when a `.brain/` exists.

## Language / Idioma
Reply in the user's language (EN/ES). `LOG.md` / `STATUS.md` / `ANSWERS.md` content may be written in whichever language the user works in; keep the **field names** (`phase:`, `progress:`, `Q:`, `A:`, etc.) exactly as below so the sync script parses them.

## Discover the .brain/ folder
It's usually at the repo root but may be up to ~3 levels up. Walk upward:
```bash
for i in . .. ../.. ../../..; do
  [ -d "$i/.brain" ] && { echo "found: $i/.brain"; break; }
done
```
If no `.brain/` exists, this skill doesn't apply — proceed normally.

## The 7 files

| File | Direction | Read | Write |
|---|---|---|---|
| `CONTEXT.md` | brain → here | YES | **NO** (overwritten on sync) |
| `TASKS.md` | brain → here | YES | Tick `[x]` only |
| `ASKS.md` | brain → here | YES | **NO** |
| `INSTRUCTIONS.md` | brain → here | YES | **NO** |
| `STATUS.md` | here → brain | YES | YES |
| `LOG.md` | here → brain | YES | YES (append) |
| `ANSWERS.md` | here → brain | YES | YES (append) |

## Session protocol

### 1. On start — read three first
- `.brain/CONTEXT.md` — scope, phase, milestones, team
- `.brain/TASKS.md` — tasks the brain delegated to this repo
- `.brain/ASKS.md` — questions the brain wants answered

### 2. As you work
- Execute TASKS items; tick `[x]` in `TASKS.md` when done.
- Answer ASKS by appending to `ANSWERS.md`:
  ```
  Q: <verbatim question text>
  A: <your answer>
  ```
- After meaningful work, append one line to `LOG.md`:
  ```
  - YYYY-MM-DD HH:MM — [TYPE] short description
  ```
  TYPES: `WORK` · `DECISION` · `MILESTONE` · `BLOCKER` · `LESSON` · `HANDOFF`

### 3. Periodically + at session end — update `STATUS.md` frontmatter
- `last-activity:` (today)
- `progress:` (0–100, best estimate)
- `phase:` (if changed: `kickoff | discovery | design | build | uat | delivered | maintenance | closed`)
- `blockers:` (array)
- `next-action:` (one-liner)

## NEVER
- ❌ Edit `CONTEXT.md`, `TASKS.md` (beyond ticking), `ASKS.md`, `INSTRUCTIONS.md` — the brain owns them.
- ❌ Reach into the vault directly — communicate only through your `.brain/` files.
- ❌ Mirror the task ledger into project docs (no duplication; the brain owns it).
- ❌ Create new files in `.brain/` beyond the 7 standard ones.

## Escalate to the human when
- A `TASKS.md` item is impossible without info you lack → `[BLOCKER]` in `LOG.md` **and** add to `blockers:` in `STATUS.md`.
- A `CONTEXT.md` assumption is materially wrong → log `[BLOCKER]` and explain.
- Scope changed beyond `CONTEXT.md` → log + tell the human.

## Sync mechanics (FYI — you don't trigger it)
A scheduled/manual run of `Sync-Project-Brains.ps1` from the vault:
1. Regenerates `CONTEXT.md`/`TASKS.md`/`ASKS.md` from the vault project note.
2. Merges your `STATUS.md` fields into the note frontmatter.
3. Appends new `LOG.md` entries to the note's `## Log`.
4. Ticks newly-`[x]`-ed `TASKS.md` boxes back in the note.
5. Pairs each `ANSWERS.md` `Q:/A:` block to the matching question.

Your job: keep `STATUS.md` honest, `LOG.md` truthful, `ANSWERS.md` responsive, `TASKS.md` ticked.
