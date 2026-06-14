# skills

A curated, **generic** set of [Claude Code](https://docs.claude.com/en/docs/claude-code) skills you can drop into any project. Each one is self-contained, works for anyone (no private paths or hardcoded clients), and degrades gracefully — the ones that talk to a third-party service (e.g. Trello) **also work fully offline**.

> 🌍 **Bilingual / Bilingüe.** Every skill is usable in **English and Spanish**. Trigger phrases are listed in both languages and the skill always replies in the language you wrote in. *Cada skill funciona en inglés y español: responde en el idioma en que le escribas.*

---

## How to install a skill

A "skill" is just a folder with a `SKILL.md` (plus optional `scripts/`, `templates/`, `.env.example`). To use one:

```bash
# Clone, then copy the skill folder into your skills directory
git clone https://github.com/jachana/skills.git

# Per-user (all projects):
cp -r skills/2nd-brain/brain-sync  ~/.claude/skills/
# Or per-project:
cp -r skills/project-management/ship  <your-repo>/.claude/skills/
```

In Claude Code, invoke a skill with the `Skill` tool or `/skill-name`. If a skill ships a `.env.example`, copy it to `.env`, fill in your own values, and **never commit the `.env`** (the repo's `.gitignore` already blocks it).

### Secrets policy

No credentials live in this repo. Skills that need keys (Trello, email, etc.) ship a `.env.example` listing **which** variables are required and where to get them — never the values. Each skill's README repeats the requirement.

---

## Categories

| Folder | What's inside |
|---|---|
| [`2nd-brain/`](2nd-brain/) | **Obsidian "second brain" protocol.** Register a repo with a central Obsidian vault and keep a bidirectional `.brain/` bridge in sync (tasks down, status/log/answers up). |
| [`project-management/`](project-management/) | **Provider-agnostic kanban.** ship · triage · breakdown · refine (groom/enrich) · prune. Runs **locally**, on **Trello**, or **Jira** — same skills, auto-detected provider. |
| [`reporting/`](reporting/) | **Human-readable reports** and **proposal writing** — turn raw work/data into something a person actually wants to read. |
| [`email/`](email/) | **Email assistant** — draft replies grounded in your second-brain, and track multi-message threads so context never gets lost. |
| [`quality/`](quality/) | **`prove-it` validation discipline** — forces the model to *programmatically verify* claims and show the evidence instead of asserting "done ✅". |

Each category folder has its own `README.md` with setup details.

---

## Recommended companion skills

These pair well with everything here. Install them too:

- **caveman** — strips filler/hedging from the model's prose so output stays terse and scannable. Great with the reporting + validation skills. → [caveman plugin](https://github.com/obra/superpowers) ecosystem.
- **frontend-design** — opinionated UI/UX guidance; pair with `reporting/` when a report or proposal becomes a web page. → `claude-plugins-official/frontend-design`.
- **Matt Pocock "grill me"** — adversarial self-review that interrogates your reasoning before you commit. Pairs naturally with `quality/prove-it-validation` (one demands proof, the other pokes holes in it).

> The skills here *reference* these companions where relevant but never hard-depend on them — everything works standalone.

---

## Design principles

1. **Generic, not personal.** No private absolute paths, no client names. Anything machine-specific is an env var.
2. **Offline-capable.** A third-party outage (or no account at all) must not brick the skill. Online is an enhancement, not a requirement.
3. **Bilingual.** EN + ES triggers; reply in the user's language.
4. **Show your work.** Skills prefer evidence (command output, file diffs, test runs) over assertions.
5. **Self-documenting.** Every skill folder explains its own setup, env, and scripts.

## License

MIT — see [LICENSE](LICENSE). Use freely.
