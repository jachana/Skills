# Workflow template — adapt and run

A ready-to-edit `Workflow` script for the fan-out → synthesis analysis. Replace the
game-specific bits (`GAME_DIR`, the game blurb, the per-dimension `focus`, the file
lists) and the priority order if the user gave a different one. If the `Workflow`
tool isn't available, run the same shape as parallel subagents: spawn one analyst
per dimension in a single message (each with the shared context + schema), collect
their structured findings, then do the synthesis yourself using the report template
in SKILL.md.

Notes when adapting:
- Keep the `meta` block a pure literal (no variables/among its fields).
- Don't put the literal token `Math` + `.random(` or `new Date(` / `Date.now(` in any
  string — the workflow validator rejects scripts containing those substrings (even
  inside prompt text). Paraphrase if you need to mention RNG.
- Weight every analyst's impact judgement by the priority order, and repeat the order
  in the synthesis prompt so the ranking is strict.

```javascript
export const meta = {
  name: 'game-improvement-analysis',
  description: 'Analyze a game across experience dimensions and produce a ranked improvement report',
  phases: [
    { title: 'Analyze', detail: 'one parallel analyst per dimension reads the code' },
    { title: 'Synthesize', detail: 'dedup + rank by the priority order into one report' },
  ],
}

const GAME_DIR = '<ABSOLUTE/PATH/TO/GAME/CODE>'   // e.g. C:/proj/game/scripts

const PRIORITY = `PRIORITY ORDER (most to least important): Fun > Feel > Performance > Challenge > Consistency.
Weight every finding's impact by this order — a Fun win outranks a Consistency win at equal impact.`

const GAME_BLURB = `<2-3 sentences: core loop, controls, win/lose, key systems>`

const COMMON = `You are analyzing a game. ${GAME_BLURB}

${PRIORITY}

Read the actual code under ${GAME_DIR} (and its subfolders) plus the central config/
tuning file and the main loop. Also check the asset folder for art/assets that may
hint at planned or unfinished features (sprite sheets not animated, textures with no
code references) — verify whether they are actually wired in.

Be CONCRETE: cite files/functions/constants. No generic advice. Each finding must be
actionable with a one-line concrete change. Tag effort S (<1h), M (a few hrs), L (bigger).`

const SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        properties: {
          title: { type: 'string' },
          kind: { type: 'string', enum: ['problem', 'idea', 'improvement'] },
          impact: { type: 'string', enum: ['high', 'medium', 'low'] },
          effort: { type: 'string', enum: ['S', 'M', 'L'] },
          where: { type: 'string' },
          detail: { type: 'string' },
          suggestion: { type: 'string' },
        },
        required: ['title', 'kind', 'impact', 'effort', 'where', 'detail', 'suggestion'],
      },
    },
  },
  required: ['findings'],
}

phase('Analyze')

const dims = [
  { label: 'fun',         focus: 'DIMENSION: FUN (highest priority). Core-loop engagement, decisions, variety, reward loops, progression/meta, novelty deeper in, "one more run" pull. Read the loop, generators/levels, scoring, economy.' },
  { label: 'feel',        focus: 'DIMENSION: FEEL/JUICE. Input responsiveness + clarity, animation/particles/shake/hit-stop, audio + haptics coverage, and readability (safe vs dangerous, what is selected, what just happened). Read input, render, juice, audio.' },
  { label: 'performance', focus: 'DIMENSION: PERFORMANCE. Per-frame allocations/garbage, draw-call counts, hot-path scans, redundant work, load time + asset/build weight. Cite exact hot spots and concrete fixes.' },
  { label: 'challenge',   focus: 'DIMENSION: CHALLENGE/BALANCE. Difficulty-curve shape, fairness + solvability, dead or contradictory mechanics, risk/reward, economy pacing. Read the tuning constants and generation/balance code.' },
  { label: 'consistency', focus: 'DIMENSION: CONSISTENCY/POLISH (lowest). Code consistency, half-wired/unfinished features, dead code, latent bugs, test gaps. Keep these lower-impact unless they cause real bugs.' },
]

const results = await parallel(dims.map(d => () =>
  agent(`${COMMON}\n\n=== ${d.focus}`, { label: d.label, phase: 'Analyze', schema: SCHEMA })
))

phase('Synthesize')

const all = dims.map((d, i) => ({ dimension: d.label, findings: (results[i] && results[i].findings) || [] }))

const report = await agent(
  `You are the lead designer writing one improvement report. ${PRIORITY}

De-duplicate overlapping findings, resolve contradictions, and produce a single
prioritized markdown report with these sections:
1. "## Top 5 — do these first" — highest-leverage overall, ranked strictly by the
   priority order, each one line: **title** (dimension · impact · effort) — change + why.
2. "## By dimension" — group the rest under Fun / Feel / Performance / Challenge /
   Consistency, each a tight bullet: **title** (impact·effort) — suggestion.
3. "## Quick wins" — the S-effort items worth batching.
4. "## Bigger bets" — the L-effort ideas, each with one sentence on the payoff.

Keep file/function references. Cut vague or low-value items. Make it skimmable — the
dev should know exactly what to build next.

FINDINGS JSON:
${JSON.stringify(all)}`,
  { label: 'synthesis', phase: 'Synthesize' }
)

return report
```
