---
name: client-comms
description: >-
  Umbrella for ANY client-facing message — email, Teams chat, WhatsApp, LinkedIn. Confirms
  the CHANNEL and tone before drafting, applies per-client style notes from a local registry,
  and defaults to "work is active" framing. Use whenever the user asks to write/reply to a
  client or colleague in any medium: "reply to the client", "answer Juan on Teams",
  "write to <client>", "respóndele al cliente", "contéstale por Teams", "escríbele a <cliente>",
  "mándale un whatsapp" — and ESPECIALLY when the channel is not stated (never assume email).
  Full email threads hand off to email-assistant; this skill owns channel choice, tone, and
  per-client style.
---

# Client comms — right channel, right tone, first time

The two ways a technically-correct message still fails: it's in the wrong **medium**
(an email when the conversation lives in Teams), or the wrong **register** ("resuming
work" when work never stopped; usted for a tú client). Both cost a rework round with a
human who already read the bad draft. This skill front-loads those two decisions.

## Language / Idioma
Draft in the **recipient's** language and formality (tú/usted, first-name vs formal).
Interact with the user in their language (EN/ES).

## Model & effort
| Phase | Model | Effort | Why |
|---|---|---|---|
| Channel/registry lookup | any | low | mechanical |
| Drafting client-facing text | **sonnet — hard floor, never haiku** | medium | register misses are the top rework cause |
| Delicate thread (upset client, money, scope disputes) | opus | high | one wrong sentence costs more than the tokens |

Session below sonnet → stop and tell the user before drafting.

## Step 0 — Channel FIRST (never assume email)

If the user didn't state the medium, ask one question — channel? — before writing a word.
The channel dictates the whole shape:

| Channel | Shape |
|---|---|
| **Email** | Full structure (greeting → answers → asks → next step → sign-off). Hand the drafting + thread tracking to **email-assistant**; this skill supplies tone + style notes. |
| **Teams / Slack chat** | Short. No "Dear X", no signature block. Lead with the answer; bullets over paragraphs; links inline. Reads like a message, not a letter. |
| **WhatsApp** | Brief, warm-professional, recipient's register. No corporate boilerplate. Emojis only if the client uses them first. |
| **LinkedIn** | Public-adjacent: assume it could be screenshotted. |

Wrong-channel drafts read wrong even with perfect content — a Teams message formatted
as an email feels like a form letter.

## Step 1 — Tone defaults (override only on user instruction)

- **Work is ACTIVE.** Never frame ongoing work as "resuming"/"retomando"/"picking back up"
  unless the user explicitly says it stalled. Default: "seguimos avanzando en…", "estamos
  trabajando en…", "here's where we are".
- Mirror the last message's register and formality; when first contact, err formal in ES
  (usted) and neutral-professional in EN, then note what the client uses.
- Commitments (dates, deliverables, prices) get flagged to the user before the draft is final.

## Step 2 — Per-client style registry

One Markdown note per client at `${CLIENT_COMMS_DIR:-./client-comms}/<client-slug>.md`:

```markdown
---
client: <name>
language: es      # what THEY write in
formality: tú     # tú | usted | first-name | formal
channels: {default: teams, formal: email}
---
- Prefers short messages, answers inline.
- Never mention price in chat — email only.
- <date> — corrected: don't say "retomar", work is continuous.
```

Read it **before** drafting. After the user corrects a draft, **offer to record the
correction** here — that's how the skill stops repeating mistakes. Keep the registry out
of public repos (it's client data): it lives in the user's workspace or brain vault,
never in this skill's folder.

## Step 3 — Ground the facts

Status, dates, scope, decisions come from the second-brain (vault note, `.brain/` files)
or the user — same rule as email-assistant: **ask instead of inventing**. A wrong fact
in a client message is worse than a question in chat.

## Step 4 — Draft, flag, hand over

Draft in the channel-native shape, flag any commitment made on the user's behalf,
present for approval. **Never send anything anywhere without explicit approval** —
not email, not chat, not DM.

## Guardrails
- ⚠ No channel stated → ask; don't default to email.
- ⚠ Never fabricate facts, dates, prices, names.
- ⚠ Never auto-send.
- ✅ Corrections are gold: offer to write each one into the client's registry note.

## Cross-refs
- `email-assistant` — full email drafting + thread files (this skill feeds it tone/style).
- `reporting/proposal-writer` — when the "message" is actually a proposal/quote.
