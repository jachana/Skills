# quality — discipline skills

Skills that change *how* the model works, not what it builds.

| Skill | Use it when… |
|---|---|
| [`prove-it-validation`](prove-it-validation/) | You want the model to **programmatically verify** its claims and **show the evidence** — actual command output, test runs, diffs, and for anything visual a **screenshot / preview / short recording** attached to the PR or shown to you — instead of asserting "done ✅". |

## Why
The single most expensive AI failure mode is the confident false "it works". This skill makes verification a required, visible step: a claim of success must be backed by reproducible proof, or it's labeled unverified.

It pairs naturally with the **Matt Pocock "grill me"** companion skill — `prove-it` demands the evidence, "grill me" pokes holes in it. Run both for high-stakes changes.

Bilingual (EN/ES). No env vars, no scripts.
