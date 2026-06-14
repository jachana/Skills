---
name: prove-it-validation
description: >-
  Discipline skill: before claiming any task succeeded, VERIFY it programmatically and SHOW the evidence
  (real command output, test runs, diffs, queries — and for anything visual, a screenshot / preview /
  short screen recording, attached to the PR or surfaced to the user) — never assert "done" on faith. Use whenever you're
  about to report a change as working, finished, fixed, or passing, and whenever the user says
  "prove it", "verify this actually works", "show me proof", "don't just tell me it's done",
  "demuéstralo", "verifica que de verdad funciona", "muéstrame la evidencia", "no me digas que sí sin probar".
  Rigid skill — follow it exactly; do not rationalize skipping verification. Bilingual (EN/ES).
---

# Prove it — programmatic validation before claiming success

The rule: **a claim of success is not done until it's verified with evidence the user can see and reproduce.** "It should work", "I've fixed it", "tests will pass" are not acceptable terminal statements.

## Language / Idioma
Explain and report in the user's language (EN/ES). Command output stays verbatim.

## The core loop — for every success claim
1. **State the claim precisely.** What, specifically, is supposed to be true now? ("The login endpoint returns 401 on a bad password.")
2. **Pick the cheapest test that would FALSIFY it.** Think like a skeptic: what observation would prove the claim wrong?
3. **Run it.** Actually execute — test, script, query, build, curl, file read. Don't simulate or predict the output.
4. **Show the evidence.** Paste the real output (or the relevant lines). Point at the part that proves the claim. For anything visual or behavioral that text can't capture, produce a **visible artifact** — screenshot, preview, or short recording (see "Show the proof as an artifact").
5. **Judge honestly.** Output matches claim → report success *with* the evidence. Doesn't match → the claim is false; fix or report the gap. Never round a partial pass up to "done".

## What counts as proof (strongest → weakest)
- An automated **test** that exercises the exact behavior, passing in a real run.
- A **command / script** whose output directly demonstrates the property (e.g. `curl` showing the status code, a SQL count, a diff).
- A **build / typecheck / lint** completing clean.
- A **file read** showing the change is actually present where it needs to be.
- (Weak — flag as such) Reasoning about why it should work, with no execution.

If you can only offer the weakest level, **say so explicitly**: "Unverified — I could not run X because Y."

## Show the proof as an artifact
Text output proves logic; it can't prove "the page renders right" or "the flow works end to end". When the claim is **visual or behavioral**, capture something the user can look at — and put it where they'll see it.

**When to capture what:**
- **UI / page / layout / styling** → a **screenshot** (or before/after pair for a change).
- **A flow, animation, or interaction** → a **short screen recording** (a few seconds; a GIF or mp4).
- **A generated page/report/build** → a **rendered preview** (open the file, screenshot it, or serve it locally and capture).
- **A CLI/terminal behavior** → a captured terminal session (asciinema cast) or just the pasted output if static.

**How (use whatever the project already has; these are defaults):**
- Web UI: drive it headless and snapshot — **Playwright** (`page.screenshot()`, `page.video`) or Puppeteer. They run in CI too.
- Native desktop / arbitrary screen: OS capture (macOS `screencapture`, Windows Snipping/`Win+Shift+S`, Linux `scrot`/`grim`), or `ffmpeg` to record a region to mp4/gif.
- Trim/convert video to a lightweight GIF with `ffmpeg` so it embeds anywhere.
- Save artifacts to a temp/`artifacts/` dir — don't commit large binaries into the repo unless asked.

**Where to surface it:**
- **PR exists / relevant** → attach it. `gh pr comment <pr> --body "Proof: <what it shows>"` with the image embedded (drag-drop in the GitHub UI, or upload and reference the URL). Put before/after shots in the PR description so the reviewer sees the change working without checking out the branch.
- **No PR** → show it directly to the user (inline image / send the file). Caption it with what it proves.
- Always **caption the artifact** with the claim it backs ("login rejects bad password — note the red 401 toast"), so a picture isn't left to interpretation.

⚠ The artifact must be **real** — actually captured from the running thing, this run. Never mock up, edit, or describe a screenshot you didn't take.

## Verify the right thing
- Test the **behavior the user cares about**, not a proxy. "Code compiles" ≠ "feature works".
- Cover the **failure path**, not just the happy path (the bad-password case, the empty input, the permission denial).
- Check **side effects** you claimed: row written? file created? cache invalidated? Show it.
- Re-run after the "fix" — confirm it actually changed the result, and that you didn't break a neighbor (regression check).

## Reporting format
When you report completion, include a short **Evidence** block:
```
Claim:    <what should be true>
Check:    <command / test you ran>
Result:   <verbatim output, trimmed to the relevant lines>
Artifact: <path/link to screenshot · recording · preview — for visual/behavioral claims; else "n/a">
Verdict:  VERIFIED ✅ | PARTIAL ⚠ (what's left) | UNVERIFIED ❌ (why)
```
Use `VERIFIED` only when the output (and, for visual claims, the artifact) genuinely demonstrates the claim.

## Red flags — STOP if you catch yourself thinking:
| Thought | Reality |
|---|---|
| "This is too simple to need testing" | Simple changes break things too. Run the check. |
| "The tests would pass" | Then running them costs nothing — run them. |
| "I'll say it's done and they'll tell me if not" | Shipping an unverified claim is the failure. |
| "I can't run it, so I'll assume it works" | Then label it UNVERIFIED, don't claim success. |
| "The output is probably fine" | Read it. "Probably" is not evidence. |

## Anti-fabrication
- ⚠ Never invent or paraphrase command output. Paste what actually printed.
- ⚠ If a check can't run (no env, no creds, no network), say exactly why and mark the claim UNVERIFIED — do not substitute optimism.
- ✅ Prefer one real falsifying test over three paragraphs explaining why it should work.
