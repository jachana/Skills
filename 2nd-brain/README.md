# 2nd-brain — Obsidian "second brain" protocol

Turn an [Obsidian](https://obsidian.md) vault into a **central brain** that delegates work to, and collects status from, every code repo you work in. Each repo gets a small `.brain/` bridge folder; a sync script reconciles it with the vault.

```
   ┌────────────────────────────┐         ┌──────────────────────────────┐
   │  Obsidian vault (the Brain)│         │  your-repo/                  │
   │  Projects/<Name>.md  ◀────────sync───▶│  .brain/                     │
   │   · Scope / Milestones     │         │   CONTEXT.md   (brain → repo)│
   │   · Brain → Repo · Tasks   │  push   │   TASKS.md     (brain → repo)│
   │   · Brain → Repo · Asks    │ ───────▶│   ASKS.md      (brain → repo)│
   │   · Log                    │         │   STATUS.md    (repo → brain)│
   │                            │  pull   │   LOG.md       (repo → brain)│
   │                            │ ◀───────│   ANSWERS.md   (repo → brain)│
   └────────────────────────────┘         └──────────────────────────────┘
```

## Skills in this category

**Single-project skills** (run inside one repo):

| Skill | Use it when… |
|---|---|
| [`brain-init`](brain-init/) | You want to **register the current repo** with the central brain — creates the vault project note and scaffolds `.brain/`. |
| [`brain-sync`](brain-sync/) | You're **working inside a repo that already has a `.brain/` folder** — defines exactly what to read, what to update, and what to never touch. Triggers automatically. Enforces **project isolation**: never act on other projects' info unless prompted; instead log a `[CROSS-REF]` signal up to the brain. |

**Root-brain skills** (run over the whole vault — cross-project):

| Skill | Use it when… |
|---|---|
| [`brain-report`](brain-report/) | You want a **generalized progress report** across all projects — movement over a time period, completed work, pending tasks, overall states, what needs attention. Runs `scripts/Brain-Report.ps1` (deterministic) then adds narrative. |
| [`brain-connect`](brain-connect/) | You want to **find reuse across projects** — where something from one project is useful in another. Runs `scripts/Brain-Connect.ps1` to surface candidate pairs, then reasons over the notes for concrete recommendations. |

> **Isolation model:** a local project agent reasons only from *its own* `.brain/` files. The root brain is the only thing that looks across projects — it does so on demand (`brain-report`, `brain-connect`) and by harvesting the `[CROSS-REF]` signals local agents log up. Clean per-project reasoning, global awareness at the center.

## Setup

1. **Pick (or create) an Obsidian vault** to be your brain. It needs two folders: `Projects/` and `Templates/`. Copy the starter files from [`templates/`](templates/) into your vault's `Templates/`.
2. **Set environment variables** (copy `.env.example` → `.env`, or export them in your shell / Claude Code settings):

   | Variable | Required | Meaning |
   |---|---|---|
   | `BRAIN_PATH` | ✅ | Absolute path to your Obsidian vault root (the brain). e.g. `D:/Vaults/Brain` or `/home/me/Brain`. |
   | `BRAIN_REPOS_ROOT` | optional | Root folder the sync auto-scans for orphan `.brain/` dirs. Defaults to the vault's parent. |

3. **Install the sync script** from [`scripts/Sync-Project-Brains.ps1`](scripts/) into your vault (e.g. `BRAIN_PATH/Scripts/`). Run it manually or on a schedule:

   ```powershell
   pwsh scripts/Sync-Project-Brains.ps1 -BrainRoot "$env:BRAIN_PATH"
   pwsh scripts/Sync-Project-Brains.ps1 -BrainRoot "$env:BRAIN_PATH" -DryRun   # preview
   ```

> The skills read `BRAIN_PATH` to locate the vault. If it isn't set, they ask you for the path once and remember it for the session. **No path is hardcoded.**

## The `.brain/` file contract (7 files)

| File | Direction | Repo agent may write? |
|---|---|---|
| `CONTEXT.md` | brain → repo | No (regenerated each sync) |
| `TASKS.md` | brain → repo | Tick `[x]` only |
| `ASKS.md` | brain → repo | No |
| `INSTRUCTIONS.md` | brain → repo (once) | No |
| `STATUS.md` | repo → brain | Yes |
| `LOG.md` | repo → brain | Append only |
| `ANSWERS.md` | repo → brain | Append only |

`brain-sync` documents the full protocol. `Sync-Project-Brains.ps1` is the engine that moves data both ways.
