---
name: game-improvement-analysis
description: >-
  Analyze a game's codebase and produce a prioritized, actionable improvement
  report — concrete problems, ideas, and changes — ranked by player-experience
  priorities (default Fun > Feel > Performance > Challenge > Consistency, but
  honor any order the user states). Fan the analysis out across those dimensions
  with parallel subagents (or a Workflow if available), then synthesize one
  ranked report. Use this whenever the user wants to improve, review, critique,
  audit, or "make more fun" a game / prototype / level, asks "what should I
  build or fix next" for a game, or wants a read on game feel, balance, juice,
  or progression — even if they don't say the word "analyze". This is read-only
  analysis; offer to implement the picks afterward, don't change code as part of
  the analysis.
---

# Game Improvement Analysis

Turn a vague "make my game better" into a concrete, ranked build list. The value
comes from three things working together: **breadth** (cover every axis of player
experience, not just the one the dev is staring at), **specificity** (every finding
cites a file/function/constant and a concrete change — not "add more juice"), and
**prioritization** (rank by what actually moves the experience, so the dev knows
the single next thing to do).

You do this by fanning the analysis out — one focused analyst per dimension reads
the code in parallel — then synthesizing into a single ordered report. Parallel
analysts each go deep on their axis without the others' noise, which surfaces far
more than one pass trying to hold everything at once.

## Model & effort
| Phase | Model | Effort | Why |
|---|---|---|---|
| Scout pass (Step 2) | haiku / Explore subagent | low | locating structure, not judging it |
| Dimension analysts (Step 3) | subagents with explicit `model: sonnet` | medium | code reading + design judgment, ×5 in parallel — opus here quintuples cost for little gain |
| Synthesis + ranking (Step 4) | opus | high | cross-dimension tradeoffs are the deliverable |

A full audit of a very large game where every dimension interacts is a legitimate Fable exception; the default cap is opus. Session below opus at synthesis → say so in the report header.

## Step 1 — Lock the priority order

The ranking is the most important output, so get the lens right before looking at
code. Use the order the user gives. If they don't give one, default to:

**Fun > Feel > Performance > Challenge > Consistency**

Why this default: a game that isn't fun fails no matter how clean the code is, and
feel (how it responds to your hands) is what makes fun *land*; performance protects
both; challenge/balance shapes the experience for engaged players; consistency and
polish matter but rarely make or break the session. Higher-priority wins outrank
lower ones even at equal impact — a high-impact Fun item beats a high-impact
Consistency item.

Default dimension meanings (adapt to the specific game):
- **Fun** — moment-to-moment decisions, variety, reward loops, progression/meta,
  novelty as you go deeper, the "one more run" pull. Boredom and sameness are Fun bugs.
- **Feel / juice** — input responsiveness and clarity, animation/particles/screen
  shake/hit-stop, audio + haptics, and readability (can the player instantly tell
  what's safe vs dangerous, what's selected, what just happened).
- **Performance** — per-frame allocations/garbage, draw-call counts, hot-path scans,
  load time and build/asset weight, anything that drops frames or stalls startup.
- **Challenge / balance** — difficulty curve shape, fairness and solvability, dead
  or contradictory mechanics, risk/reward, economy pacing.
- **Consistency / polish** — code consistency, half-wired or unfinished features,
  dead code, latent bugs, test gaps.

If the user's game is a genre where a dimension means something specific (e.g.
"Feel" for a rhythm game is timing windows), fold that in.

## Step 2 — Scout the codebase first (inline)

Before fanning out, do a quick read so the analysts get pointed at real files, not
made to rediscover the structure five times. Find: the engine/stack, the main loop
and state machine, entities/structures, the central config/tuning constants, the
render path, and the asset folder. Note anything that looks **unfinished or
half-wired** — art or assets with no code referencing them, sprite sheets that
aren't animated, feature flags, TODOs. Those are often the highest-leverage Fun/Feel
opportunities (and a perf/consistency cost), so make sure an analyst checks them.

## Step 3 — Fan out one analyst per dimension

Prefer a **Workflow** if it's available (parallel analyze phase → synthesis phase);
otherwise spawn the analysts as parallel subagents in a single message, each with an
explicit `model: sonnet` (see Model & effort — analysts don't need more, and the
synthesis pass is where the big model earns its cost). There's a
ready-to-adapt workflow script in `references/workflow-template.md` — read it and
fill in the game-specific context.

Give every analyst the same shared context and one dimension to own:

- A 2–3 sentence description of the game (core loop, controls, win/lose, key systems)
  so they reason about player experience, not just code.
- The **priority order**, and an instruction to weight each finding's impact by it.
- The concrete files to read for their dimension (from your scout pass).
- The unfinished-feature note from Step 2 — tell them to check whether such art/assets
  are actually wired into code.

Demand findings that are **concrete and actionable**: each must cite a
file/function/constant and give a one-line concrete change. Reject generic advice
("add more polish"). Have each tag **impact** (high/medium/low) and **effort**
(S < ~1h, M a few hrs, L bigger), and classify as problem / idea / improvement.

Have analysts return structured findings (use a schema if your fan-out supports it):

```json
{
  "findings": [
    {
      "title": "short name",
      "kind": "problem | idea | improvement",
      "impact": "high | medium | low",
      "effort": "S | M | L",
      "where": "file / function / constant references",
      "detail": "what's going on and why it matters for THIS dimension",
      "suggestion": "the concrete change to make"
    }
  ]
}
```

Suggested analyst set (rename/merge to fit the game): `fun`, `feel`, `performance`,
`challenge`, `consistency`. Scale up only if the game is large.

## Step 4 — Synthesize into one ranked report

Collect all findings, de-duplicate overlaps (the same issue often surfaces under two
dimensions — merge and note both), and resolve contradictions. Rank **strictly by
the priority order**. Then produce the report using this structure:

```markdown
## Top 5 — do these first
<the highest-leverage changes overall, each one line:>
N. **Title** (dimension · impact · effort) — what to change and why it matters.

## By dimension
### Fun
- **Title** (impact · effort) — concrete suggestion.
### Feel
...
### Performance
...
### Challenge
...
### Consistency
...

## Quick wins
<the S-effort items worth batching into one commit>

## Bigger bets
<the L-effort ideas, each with one sentence on the payoff>
```

Keep it skimmable — the dev should finish reading and know exactly what to build
next. Cut vague or low-value items rather than padding. Preserve file/function refs
so each item is directly actionable. When a single change resolves an item that
appears as both a cost (perf/consistency) and an opportunity (fun/feel) — e.g.
unused art that could become a mechanic — say so and recommend the one resolution.

## Step 5 — Offer to implement, don't auto-implement

This skill produces a plan, not a diff. After presenting the report, offer a sensible
first move given the priority order — usually: batch the **Quick wins** into one
low-risk commit, then take the top **Feel** items, then a **Top 5** bet. Let the
user pick. Only start changing code once they choose.

## Notes

- Match effort to the ask: a quick "what's weak here?" wants a tight pass; "do a full
  audit" warrants more analysts and deeper reads.
- If you can run the game or its tests, do — observed behavior (a janky frame, a silent
  impact, an unsolvable level) beats inferring from code. But code analysis alone is a
  valid pass when you can't run it.
- This generalizes beyond games: the same fan-out-then-rank shape works for any
  artifact with competing quality axes. For games, the default dimensions above are
  the ones that matter.
