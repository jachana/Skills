---
name: release-play
description: >-
  Publish a Godot (or other) Android game to Google Play — bump versionCode, build the
  SIGNED release AAB, validate package id and signing, prepare bilingual (EN/ES) store
  listing assets and screenshots, and stage the upload. Use when the user says
  "release to play", "publish to google play", "ship the android build", "sube a play",
  "publica en google play", "saca la versión de android", "/release-play". Sibling of
  release-itch (same bump/commit/push discipline, Play-specific build + listing + upload).
---

# Release to Google Play — Procedure

> [!important]
> Outward-facing and effectively irreversible once a track is rolled out. Default target
> is the **internal testing** track; promoting to **production** always needs the user's
> explicit confirmation, even when everything is green.

## Language / Idioma
Report in the user's language (EN/ES). Store listings are produced in **both** EN and ES
unless the user says otherwise.

## Model & effort
| Phase | Model | Effort | Why |
|---|---|---|---|
| Bump, build, validate (scripts) | sonnet | low | script work, but billed + outward-facing — don't run below sonnet |
| Listing copy (EN/ES) | sonnet | medium | store text sells the game; character limits bite |

Never haiku; never needs opus.

## Prerequisites (verify before touching anything)

- **Release keystore** configured in the export preset (not the debug keystore — Play
  rejects debug-signed AABs). Keystore path/passwords come from the project's env/preset,
  never hardcoded here.
- **versionCode** must exceed the highest code ever uploaded to Play for this package —
  check the project's version file/preset and, if in doubt, ask the user what Play shows.
- **Package id** in the preset matches the Play listing exactly (`com.x.y`) — a mismatch
  uploads cleanly and then fails at review/rollout.
- Project release scripts (`tools/bump_version.ps1` or equivalent) exist — prefer them.
- Godot Android export: 64-bit (`arm64-v8a`) enabled; target SDK per current Play policy.

## The procedure

### 1. Bump version
Use the project's bump script (patch by default; minor/major on user signal). It must
update both `versionCode` (+1) and `versionName`.
> BOM gotcha (Windows): PowerShell `Set-Content -Encoding UTF8` writes a BOM that Godot
> rejects in `export_presets.cfg` / `project.godot`. Use the no-BOM .NET write pattern;
> strip BOMs if the Android export suddenly can't find its preset.

### 2. Commit + push
Same discipline as release-itch: stage explicitly (no blanket `git add -A`), conventional
commit explaining the why, push to the release branch. Never `--force`.

### 3. Build the signed AAB (background — 5–15 min)
Project script if present; else:
```
godot --headless --export-release "Android" dist/<game>-<version>.aab
```
Run in background; on completion read the tail of the log.

### 4. Validate the artifact — before any upload
- Package id + versionCode inside the bundle:
  `bundletool dump manifest --bundle dist/<game>.aab | grep -E 'package|versionCode'`
  (or unzip and read `base/manifest/`). Must match step 1 and the Play listing.
- Signing: `jarsigner -verify dist/<game>.aab` (or keytool on the embedded cert) —
  confirm it's the **release** cert.
- Size sanity vs the previous release (a 10× jump = packed junk; a 10× drop = missing assets).

### 5. Store assets (first release or listing changes only)
Respect Play's hard limits — validate lengths before handing over:
- Title ≤ 30 chars · short description ≤ 80 · full description ≤ 4000 (EN + ES).
- Screenshots: use the project's capture harness (pair with `runtime-verify`); phone
  minimum 2, plus 7/10-inch if tablets targeted.
- Feature graphic 1024×500; icon 512×512 (32-bit PNG).

### 6. Upload / stage
- **Default:** stage everything in `dist/play-<version>/` (AAB + listings + assets) and
  tell the user exactly what to drag into Play Console → internal testing.
- If `fastlane supply` is configured in the project, offer it — still to internal testing.
- **Production rollout: only on explicit user confirmation**, and mention staged rollout %.

## Common failure modes
| Symptom | Cause | Fix |
|---|---|---|
| "Version code already used" | versionCode ≤ a previously uploaded one | bump again; codes are forever, even from deleted drafts |
| Upload rejected: debug certificate | debug keystore in preset | point preset at the release keystore, rebuild |
| `Invalid export preset` on build | UTF-8 BOM in cfg files | strip BOM, patch the bump script (step 1 note) |
| Rejected: missing 64-bit | only armeabi-v7a exported | enable arm64-v8a in the preset, rebuild |
| Listing rejected at review | text over limits / asset sizes wrong | re-check step 5 limits |

## What this skill does NOT do
- Does not run gameplay tests — run `runtime-verify` first if the release contains untested changes.
- Does not create the Play Console app entry or handle account/policy setup.
- Does not promote to production on its own. Ever.

## Cross-refs
- `release-itch` — same bump/commit/push spine, itch.io butler pipeline.
- `runtime-verify` — pre-release runtime check.
- `quality/prove-it-validation` — evidence discipline for the PASS/FAIL report.
