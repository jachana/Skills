---
# Project note — the single source of truth the brain syncs from.
# Lives in your vault under Projects/<Slug>.md. brain-init fills this in.
title: "{{title}}"
type:                 # client-delivery | client-support | internal-tool | research | legacy | admin
status: planning      # planning | active | on-hold | archived
priority: p2          # p0 | p1 | p2
client:               # leave blank if internal
attention:            # optional integer rank for your top-active list
folder: ""            # repo path RELATIVE to this Projects/ folder, e.g. "../../my-repo"
started: {{date}}
last-activity: {{date}}
phase: kickoff        # kickoff | discovery | design | build | uat | delivered | maintenance | closed
progress: 0           # 0-100, updated by sync from the repo's STATUS.md
next-milestone:
next-milestone-label:
---

# {{title}}

## Scope
<!-- One or two sentences: what this project delivers and why. Synced to CONTEXT.md. -->

## Milestones
<!-- - [ ] M1 — ...  (synced to CONTEXT.md) -->

## Team
<!-- Who's involved. Synced to CONTEXT.md. -->

## Brain → Repo · Tasks
<!-- Tasks you delegate to the repo agent. Synced to the repo's TASKS.md.
     The agent ticks [x] when done; the next sync reflects it back here. -->
- [ ] Example task — replace me

## Brain → Repo · Asks
<!-- Questions for the repo agent. Synced to ASKS.md. Answers come back paired here as "→ A:". -->
- Q: Example question — replace me

## Log
<!-- Append-only. The repo agent's LOG.md entries are merged in here, newest first. -->
