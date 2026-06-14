---
name: email-assistant
description: >-
  Draft email replies and new messages grounded in the user's second-brain (project context, prior decisions),
  and track multi-message threads so a long back-and-forth stays coherent. Use when the user says
  "reply to this email", "draft an email to <x>", "answer this client", "track this thread",
  "responde este correo", "redacta un email para <x>", "contesta al cliente", "haz seguimiento a este hilo".
  Grounds facts in the brain — asks instead of inventing. Drafts only; never sends without explicit approval.
  Bilingual (EN/ES); writes in the recipient's language.
---

# Email assistant (brain-grounded, thread-aware)

Two jobs: write a good reply grounded in real context, and keep a record of the thread so the next reply doesn't lose the plot.

## Language / Idioma
Detect the incoming email's language and draft the reply in **that** language. Mirror the sender's formality (tú/usted, first-name vs. formal). If the user wants a different language, follow their instruction.

## Step 1 — Identify or open the thread
A thread is tracked as one Markdown file at `${EMAIL_THREADS_DIR:-./email-threads}/<slug>.md`, where `<slug>` derives from the subject (strip `Re:`/`RE:`/`Fwd:`, slugify).
- If the file exists, **read it first** — it holds the running summary, open asks, and commitments.
- If not, create it with the template below after drafting.

Thread file template:
```markdown
---
subject: <clean subject>
participants: [you, <them>]
status: open        # open | waiting-on-them | closed
last-update: YYYY-MM-DD
---

## Summary
<2-4 lines: what this thread is about, where it stands>

## Open asks
- [ ] <thing they asked you> (owner: you)
- [ ] <thing you asked them> (owner: them)

## Commitments
- YYYY-MM-DD — <who> promised <what> by <when>

## Message log
- YYYY-MM-DD ← them: <one-line gist>
- YYYY-MM-DD → you: <one-line gist>
```

## Step 2 — Ground the reply in the brain
Before answering anything factual (status, dates, scope, decisions):
1. Pull context from the second-brain — vault `Projects/<name>.md`, the repo's `.brain/CONTEXT.md` / `STATUS.md` / `LOG.md`, or notes the user points to.
2. Use those facts in the reply.
3. **If a needed fact isn't in the brain and you can't derive it — ASK the user. Never invent dates, numbers, names, or commitments.** A wrong fact in a client email is worse than a question.

## Step 3 — Draft the reply
- **Answer their actual questions first**, in order. Don't bury answers under pleasantries.
- Be concise and specific: concrete dates, next steps, owners.
- Match tone to the relationship and their message's register.
- If you're making a commitment on the user's behalf (a deadline, a deliverable), flag it explicitly so they can approve before sending.
- Structure: greeting → direct answers → any asks of them → clear next step → sign-off.

## Step 4 — Update the thread file
After drafting, update the thread Markdown:
- Append both the incoming and your draft to `## Message log` (one-line gists).
- Tick/added items in `## Open asks`; record any new `## Commitments`.
- Set `status` (`waiting-on-them` after you reply and need something back) and `last-update`.

## Step 5 — Hand off (don't auto-send)
- Present the draft for the user to review. **Do not send by default.**
- Only if SMTP env vars are configured AND the user explicitly says "send it" do you send. Even then, show the final version first.

## Guardrails
- ⚠ Never fabricate facts, prices, dates, or commitments. Ground in the brain or ask.
- ⚠ Don't send without explicit approval, even with SMTP wired up.
- ⚠ Keep the thread file truthful — it's the memory the next reply depends on.
- ✅ Surface open asks owned by the user ("they're still waiting on the spec from you") so nothing silently drops.
