# email — assistant grounded in your second-brain

| Skill | Use it when… |
|---|---|
| [`email-assistant`](email-assistant/) | You're drafting a reply, composing a new email, or tracking a back-and-forth thread — and you want it grounded in real project context (your second-brain), with the conversation history kept so nothing gets dropped. |

## What makes it different
- **Grounded** — answers pull facts from your second-brain (`2nd-brain/` vault notes, `.brain/` context) instead of guessing. If a fact isn't there, it asks rather than inventing.
- **Thread-aware** — keeps a lightweight per-thread record (who said what, open asks, commitments made) so a long chain stays coherent across many replies.
- **Bilingual** — drafts in the recipient's language (EN/ES), mirrors their tone/formality.

## Storage
Thread tracking is **local Markdown** under `email-threads/` in your working dir (or your vault). No mail-server access is required — you paste the incoming email in and the skill drafts the reply. See the skill for the optional IMAP/SMTP env vars if you later want it to read/send directly.

## Privacy
The skill never sends anything itself by default — it drafts; you send. If you wire up SMTP (`.env.example`), sending still requires your explicit go-ahead.
