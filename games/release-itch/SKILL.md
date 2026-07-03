---
name: release-itch
description: >-
  Use when the user asks to release/publish/ship to itch.io (any of: "release to itch",
  "publish", "ship the build", "push to itch", "bump and publish", "/release-itch").
  Bumps the version, commits the working tree, pushes to remote, then runs the
  multi-platform itch build + butler push pipeline. Works in any Godot project that ships
  the matching `tools/bump_version.ps1` + `tools/release_itch.ps1` pair and sets
  `ITCH_TARGET` in its `.env`.
---

# Release to itch.io — Procedure

> [!important]
> This skill is **billed** (itch butler patches go live). Confirm with the user before running if the request was ambiguous. If they typed something explicit like "publish" or "ship", proceed without re-confirmation.

## Model & effort
| Phase | Model | Effort | Why |
|---|---|---|---|
| Whole pipeline (bump, commit, push, butler) | sonnet | low | scripts do the work — but this is billed and outward-facing, so don't run below sonnet: the commit message and the failure-mode calls need a competent model |

Never haiku here; never needs opus.

## When to invoke

- Direct: `/release-itch`, "release to itch", "publish to itch", "ship the demo", "bump and release"
- Implicit: "deploy", "push to itch", "publish the build", "send to itch"
- Hybrid: "commit, push, and publish" (this skill covers the whole chain)

## Prerequisites (verify before bumping)

- Working tree is in a clean enough state to commit (uncommitted changes are OK — they get bundled into the release commit).
- Current branch is the project's release branch (`master`/`main` — whatever releases come from). If on a feature branch, stop and ask the user.
- `tools/bump_version.ps1`, `tools/release_itch.ps1`, and `tools/build_*.ps1` exist.
- `.env` contains `ITCH_TARGET=<user>/<game>` (the butler push target).
- Butler binary present (release_itch.ps1 checks `$env:BUTLER_BIN` or `$env:USERPROFILE\android-tools\butler\butler.exe`).

## The 5-step procedure

### 1. Bump version

```powershell
powershell -ExecutionPolicy Bypass -File tools/bump_version.ps1
```

Defaults to a patch bump (`0.1.33 → 0.1.34`, code +1). Pass `-SemVer minor` or `-SemVer major` when the user signals a milestone bump (e.g., demo gating, big feature). The user usually just wants patch — don't overthink.

The script writes:
- `project.godot` — `config/version="X.Y.Z"`
- `export_presets.cfg` — Android `version/code` and `version/name`

> [!warning] BOM gotcha
> Older versions of `bump_version.ps1` wrote files via `Set-Content -Encoding UTF8`, which under Windows PowerShell 5.1 adds a UTF-8 BOM that Godot rejects (`Invalid export preset name: Android` → Android build fails). The fixed version uses `[System.IO.File]::WriteAllLines(... , [System.Text.UTF8Encoding]::new($false))`. If you see this error, verify `tools/bump_version.ps1` uses the no-BOM .NET write pattern and strip BOMs from the affected files before retrying.

### 2. Inspect changes

```bash
git status --short
git log --oneline -5
```

Identify:
- What files are modified (use this to write a meaningful commit message)
- Recent commit style (Conventional Commits: `feat(scope):`, `fix(scope):`, `chore(scope):`)
- Any orphan untracked files (random PNGs, .ase scratch files) that should NOT be staged

### 3. Stage + commit

Stage explicitly — never blanket `git add -A` because the repo accumulates orphan scratch art. Group by directory if there are many files.

Commit message follows the project's Conventional Commits style. Include:
- Subject line ≤ 60 chars
- Body explaining the WHY of each meaningful change (not just what)
- `Co-Authored-By: Claude <noreply@anthropic.com>` footer (or the exact footer your
  harness mandates — don't hardcode a model name that will go stale)

```bash
git commit -m "$(cat <<'EOF'
{type}({scope}): {short subject}

{body — group by area, explain why}

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### 4. Push to remote

```bash
git push origin master
```

Never `--force` push. If the push is rejected, stop and tell the user — likely a remote drift that needs human attention.

### 5. Run release pipeline (background)

```powershell
powershell -ExecutionPolicy Bypass -File tools/release_itch.ps1
```

Always launch via `run_in_background: true` — the build + 3 butler pushes take 5–15 minutes. The pipeline:
1. Builds Android APK → `dist/`
2. Builds Web → `dist/web/`
3. Builds Windows → `dist/windows/`
4. Butler-pushes each to `$ITCH_TARGET:{android,html5,windows}`

When the background task completes, read the tail of the output file (path returned by the launch) and report:
- Final line should be `[release_itch] PASS - all platforms pushed at {version}`
- Failures usually look like `[release_itch] FAIL during {step}`

## Common failure modes

| Symptom | Cause | Fix |
|---|---|---|
| `Invalid export preset name: Android` | UTF-8 BOM in `export_presets.cfg` | Strip BOM from `export_presets.cfg` AND `project.godot`, re-run release. Patch `bump_version.ps1` if not already done. |
| `butler not found at ...` | Butler binary missing | Tell user to install butler or set `$env:BUTLER_BIN`. |
| `version/code (N) must exceed current (N)` | Tried to set the same code twice | Run bump_version normally (it auto-increments). |
| Android build hangs >5 min | Java/SDK config issue | Check `tools/build_android.ps1` first. Don't blindly retry. |
| Butler push 0% stalled >5 min | Network or itch outage | Read the output, wait ~2 min, ask user before retrying. |

## Outputs to report back

After the background pipeline completes:
1. Read the tail of the output file (last ~40 lines).
2. Report the final PASS/FAIL line.
3. If PASS, mention the version (e.g., "shipped v0.1.34") and the three channels updated.
4. If FAIL, identify which step failed and propose a fix.

## What this skill does NOT do

- Does not run tests or smoke checks first — assume the user already verified locally.
- Does not bump the demo flag or any feature flags — purely build/publish.
- Does not generate marketing assets (gif, screenshots) — separate skill for that.
- Does not change branches.

## Cross-refs

- `tools/release_itch.ps1` — the actual pipeline script
- `tools/bump_version.ps1` — version bump script
- `tools/build_{android,web,windows}.ps1` — per-platform builders
- `.env` — must contain `ITCH_TARGET=<user>/<game>`
- `docs/release/demo-plan.md` — current demo scope (filter what gets shipped)
