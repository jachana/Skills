# devops — Coolify control from Claude Code

Three skills over one stdlib-only API helper (`scripts/coolify.py`) that drives a
self-hosted [Coolify](https://coolify.io) PaaS (v4, API `v1`).

| Skill | What it does |
|---|---|
| `coolify` | Resource management — apps, databases, services, servers, projects, env vars. Reads free; writes **dry-run until `--apply`**, deletes need `--confirm <name>`. |
| `coolify-deploy` | Deploy → poll build to terminal → health-check → **PASS/FAIL**. Never reports success on a red build. |
| `coolify-audit` | Read-only inventory + env/secret hygiene + exposed ports + servers needing validation. |

## Setup

1. Copy `.env.example` to `.env` and fill in `COOLIFY_BASE_URL` + `COOLIFY_API_TOKEN`.
   - Base URL ends with `/api/v1`.
   - Token: Coolify dashboard → **Keys & Tokens → API Tokens** (shown once).
   - Abilities: `read`, plus `read:sensitive` to see env **values**, plus `write`/`deploy` for mutations.
2. `python scripts/coolify.py ping` to confirm connectivity.

## Safety model

- **Reads** (list/get/logs/inventory) run immediately.
- **Writes** (create/update/delete/start/stop/restart/deploy) are **dry-run by default** — they print `WOULD …` and change nothing. Add `--apply` to perform.
- **Destructive** ops (delete) additionally require `--confirm <exact-resource-name>`.

## Offline / no-creds

Without creds the helper still runs `--self-test`, prints dry-run previews, and explains
what's missing — it is never bricked by a missing server.

## Test

`python scripts/coolify.py --self-test`  (or `python -m unittest -v` in `scripts/`)

## Secrets policy

No credentials live in this repo. `.env` is gitignored; only `.env.example` is tracked.
