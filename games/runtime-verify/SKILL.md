---
name: runtime-verify
description: >-
  Verify a game's RUNTIME behavior after a code change, engine migration, or asset
  regeneration — launch it, capture screenshots/clips, run a migration sanity checklist,
  and only then declare the change done. Use whenever a game change is about to be reported
  as complete, after any Godot version migration or renderer/input/camera change, when the
  user says "verify the game runs", "check it in-game", "does it still play", "playtest it",
  "se ve bien el juego", "verifica que corre", "pruébalo en el juego" — and proactively
  before any release skill. Code that compiles but misbehaves is found by RUNNING, not by
  reading the diff.
---

# Runtime verify — run the game before saying "done"

The most expensive game bug is the one the developer finds while playing: it compiled,
tests passed, and it's still wrong (a camera zoomed to nowhere, a pickup that teleports,
a silent input). This skill closes that gap: after a change, **observe the running game**
and keep the evidence.

## Language / Idioma
Report in the user's language (EN/ES).

## Model & effort
| Phase | Model | Effort | Why |
|---|---|---|---|
| Boot/script checks, capture scripting | haiku | low | mechanical launches |
| Reading the screenshots + judging behavior | sonnet | medium | the judgment is visual — actually look |

Never skip the visual read to save tokens — an unexamined screenshot proves nothing.

## Step 1 — Pick the verification tier (cheapest that would catch the failure)

1. **Boot check** — does it launch clean? For Godot:
   `godot --headless --quit` (or `--quit-after 60` frames) from the project dir; read
   stderr for script errors, missing resources, parse failures. Zero output ≠ zero bugs,
   but nonzero output = stop here.
2. **Visual check** — does it look right? Capture a screenshot of the affected scene(s).
3. **Behavioral check** — does it act right? Drive the affected flow (scripted input,
   an integration/test scene, or a short recorded clip) and capture the result.

A change to gameplay/camera/input/rendering needs tier 2–3, not tier 1.

## Step 2 — Capture (prefer the project's own harness)

- Many projects ship a screenshot/capture harness under `tools/` — look first and use it.
- Godot fallback: a temporary autoload or test scene that waits N frames then
  `get_viewport().get_texture().get_image().save_png("user://verify_<name>.png")` and quits.
- Short clips: Godot `--write-movie out.avi` (fixed-fps movie writer), or an OS recorder;
  convert with `ffmpeg` to a small gif/mp4.
- For **before/after** changes, capture both sides (stash/checkout the pre-change state
  for the "before") — a pair is far stronger evidence than a lone "after".
- Save to a scratch/`artifacts/` dir; don't commit binaries unless asked.

## Step 3 — LOOK at what you captured

Open/read the image. Judge it against the *expectation*, not against "a file exists":
is the play area framed correctly, is the UI readable, is the thing you changed visible
and behaving? If you can't judge from the artifact, the artifact is wrong — capture better.

## Step 4 — Migration sanity checklist

After an engine upgrade (e.g. Godot 3→4) or renderer/input/camera rework, check the known
semantic flips even if nothing "errored":

- **Camera zoom semantics** — Godot 3→4 inverted `Camera2D.zoom` meaning (0.3 went from
  "zoomed in" to "zoomed way out"). Check actual on-screen framing, not the number.
- **Input map** — every action still bound and firing (log or on-screen debug).
- **Anchors/scale/stretch** — UI at 2–3 window sizes.
- **Signals** — renamed/renumbered connections still connected (watch for runtime warnings).
- **Resource paths** — `.tscn`/`.tres` loads, no `load()` returning null.
- **Physics layers/masks** — collisions that silently stopped colliding.
- **Shaders/renderer** — materials render (not magenta/black), particles emit.

One screenshot per checklist row you can't verify from logs.

## Step 5 — Report with evidence

Use the `quality/prove-it-validation` evidence block: claim, check, verbatim output,
artifact path(s), verdict. **PARTIAL/UNVERIFIED beats a false VERIFIED** — if you couldn't
run it (no display, no engine binary), say exactly that and hand the checklist to the user
to eyeball in 2 minutes.

## Rules
- ⚠ "It compiles / tests pass" is tier 0 — it never closes a gameplay/visual claim.
- ⚠ Never describe a screenshot you didn't capture this run.
- ✅ Run this before `release-itch` / `release-play` when the release includes untested changes.
