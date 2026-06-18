---
name: coolify
description: >-
  Manage a self-hosted Coolify PaaS over its API — list/inspect/create/update/delete
  applications, databases, services, servers, projects, and environment variables.
  Reads run freely; writes are DRY-RUN by default (preview only) until you pass --apply,
  and deletes require --confirm <name>. Use when the user says "/coolify", "manage my
  coolify", "list coolify apps", "set a coolify env var", "restart the coolify service",
  "gestiona mi coolify", "lista las apps de coolify", "reinicia el servicio en coolify",
  "cambia una variable de entorno en coolify". Requires scripts/coolify.py + a configured
  COOLIFY_BASE_URL/COOLIFY_API_TOKEN (.env).
---

# Coolify resource management

Drive Coolify resources through `scripts/coolify.py`. Reply in the user's language (EN/ES).

## 0. Locate the helper + confirm connectivity
- `CO = devops/scripts/coolify.py`.
- `python $CO ping` → confirms `COOLIFY_BASE_URL` + token work. If it errors about config,
  tell the user to copy `devops/.env.example` to `.env` and fill it in (token from
  Coolify → Keys & Tokens → API Tokens; add `read:sensitive` to see env values).

## 1. Inspect (reads — always safe)
- `python $CO apps list` / `db list` / `svc list` / `server list` / `project list`
- `python $CO apps get <uuid>` (same for db/svc/server/project)
- `python $CO apps logs <uuid>` · `python $CO server resources <uuid>` · `python $CO resources`
- Add `--json` for machine output.

## 2. Mutate — preview first, then --apply  ⟵ do not skip the preview
Every write is dry-run by default. **Show the user the `WOULD …` preview, get a yes, then
re-run with `--apply`.**
- Lifecycle: `python $CO apps restart <uuid>` → preview; `… apps restart <uuid> --apply` → do it.
- Env: `python $CO env set <uuid> KEY=VALUE --target app` (preview) → add `--apply`.
  - Bulk: `python $CO env set-bulk <uuid> path/to/vars.env --apply`.
- Create app: `python $CO apps create <variant> --json-body body.json --apply`
  (variants: public, private-github-app, private-deploy-key, dockerfile, dockerimage —
  pick by how the source is provided; a wrong variant returns 422).
- Create db: `python $CO db create <engine> --json-body body.json --apply`
  (postgresql/mysql/mariadb/mongodb/redis/keydb/dragonfly/clickhouse).

## 3. Delete — destructive, double-gated
`python $CO apps delete <uuid> --apply --confirm "<exact app name>"`. Without a matching
`--confirm` the helper refuses. Always read the resource (`apps get <uuid>`) and show the
user what will be deleted before running.

## Rules
- ⚠ Never invent a uuid — list/get first to obtain it.
- ⚠ Never pass `--apply` to a mutating command without first showing the dry-run preview and getting the user's go-ahead.
- ⚠ Secrets: don't print full env values into chat unless the user asks; note values are masked unless the token has `read:sensitive`.
- ✅ To deploy/validate a build, hand off to the `coolify-deploy` skill.
