# Coolify `devops/` skill category — design

**Date:** 2026-06-17
**Status:** Approved (design), pending implementation plan
**Repo:** `jachana/skills` (this repo)

## Summary

A new `devops/` skill category that drives a self-hosted **Coolify** PaaS through its
REST API (v4, API path `v1`). One shared Python CLI helper (`scripts/coolify.py`,
stdlib only) does all HTTP, safety-gating, and deployment polling; three thin skills
wrap it:

- **`coolify`** — resource management (CRUD over apps, databases, services, servers, projects, env vars). Primary skill.
- **`coolify-deploy`** — trigger a deploy, poll the build to a terminal state, validate health, report PASS/FAIL.
- **`coolify-audit`** — read-only inventory + config/secret hygiene audit.

Design follows the repo's principles: **generic** (no private paths/clients),
**bilingual** (EN/ES triggers, reply in the user's language), **offline-capable**
(degrades gracefully without creds), **secrets via `.env.example`** (never committed),
**self-documenting**.

## Architecture decision

**Chosen:** one shared `coolify.py` CLI; all three skills shell out to it (same pattern
as `project-management/scripts/board.py`).

Rejected alternatives:
- Raw `curl` snippets per SKILL.md — every skill would re-implement auth, the dry-run
  gate, and build-polling; drifts fast.
- Per-skill scripts — triplicates the HTTP client and the safety engine.

Rationale: auth, the dry-run/confirm safety engine, and the deployment-status state
machine must live in exactly one place. Three skills, one driver.

## Layout

```
devops/
  pack.json                  bilingual category manifest (EN/ES), order = next free
  README.md                  setup, env, token-ability notes, security policy
  .env.example               COOLIFY_BASE_URL, COOLIFY_API_TOKEN (+ comments)
  scripts/
    coolify.py               the shared API driver (Python 3, stdlib only)
  coolify/SKILL.md           resource management (CRUD)  ← primary
  coolify-deploy/SKILL.md    deploy + build validation
  coolify-audit/SKILL.md     read-only audit / inventory
```

## The `coolify.py` driver

Pure Python 3 stdlib (`urllib.request`, `json`, `argparse`) — **no pip installs**.
Resources are addressed by `uuid` everywhere (API convention; numeric `id` exists in
payloads but is never used in paths).

### Command surface

```
coolify.py ping                          GET /version    (init/health check)

coolify.py apps    list | get <uuid> | logs <uuid>          (reads)
coolify.py apps    create <variant> ... | update <uuid> ... (writes)
coolify.py apps    delete <uuid>                            (destructive write)
coolify.py apps    start|stop|restart <uuid>                (writes)

coolify.py db      list | get <uuid> | create <engine> ... | delete <uuid>
coolify.py db      start|stop|restart <uuid>
coolify.py svc     list | get <uuid> | create ... | delete <uuid>
coolify.py svc     start|stop|restart <uuid>

coolify.py server  list | get <uuid> | validate <uuid> | resources <uuid>
coolify.py project list | get <uuid> | create ... | update <uuid> ... | delete <uuid>

coolify.py env     list <uuid> | set <uuid> KEY=VAL | set-bulk <uuid> <file>
coolify.py env     delete <uuid> <env_uuid>
                   (all env subcommands take --target app|db|svc, default app, since the
                    endpoint differs: /applications|databases|services/{uuid}/envs)
                   (set-bulk <file> = .env-style KEY=VAL lines OR a JSON object; uses
                    PATCH .../envs/bulk)

coolify.py deploy      <uuid|--tag T> [--force]      -> prints deployment_uuid
coolify.py deployment  get <dep_uuid>                -> status + logs tail
coolify.py deployment  wait <dep_uuid> [--timeout S] -> polls to terminal; exit 0/1
coolify.py deployment  history <app_uuid>            -> paginated (skip/take)

coolify.py resources                                 whole-instance inventory
```

- Output: `--json` for machine-readable; human-readable table by default.
- App create variants (API has **no** generic `POST /applications`): `public`,
  `private-github-app`, `private-deploy-key`, `dockerfile`, `dockerimage`. The
  `apps create <variant>` subcommand picks the right endpoint and validates required
  fields per variant (wrong variant → 422).
- DB create engines: `postgresql`, `mysql`, `mariadb`, `mongodb`, `redis`, `keydb`,
  `dragonfly`, `clickhouse` (distinct POST endpoints).

### Safety engine (dry-run by default + confirm writes)

Implemented once in the HTTP layer so every subcommand inherits it:

- **Reads** (`GET`) run freely.
- **Writes** (`POST/PATCH/DELETE`, plus the GET-but-mutating start/stop/restart/deploy)
  are **dry-run by default**: print `WOULD <METHOD> <path>` + a body/field diff, perform
  no network mutation, exit 0.
- `--apply` performs the write for real.
- **Destructive** ops (`delete` on apps/db/svc/server/project) require, in addition to
  `--apply`, a `--confirm <name>` that must exactly match the target resource's name —
  typo-proof. Mismatch → refuse, exit non-zero.
- No skill can bypass the gate; it lives below the subcommand dispatch.

### Auth & config

- Env first: `COOLIFY_BASE_URL`, `COOLIFY_API_TOKEN`. Fallback: a `.env` file in cwd.
- `COOLIFY_BASE_URL` shape: `https://<instance>/api/v1` (Coolify Cloud:
  `https://app.coolify.io/api/v1`).
- Header: `Authorization: Bearer <id>|<secret>` — the pipe-form Sanctum token used whole.
- Token abilities matter and are documented in README + `.env.example`:
  - `read` — basic reads.
  - `read:sensitive` — required to see env **values** (otherwise masked/empty).
  - `write` / `deploy` — required for mutations / deploys.
- Missing/invalid creds → clean, actionable error (not a stack trace).

### Deployment polling / build validation (the heart of `coolify-deploy`)

Verified two-stage truth: **`finished` ≠ healthy**.

1. `deploy <uuid>` (or `--tag`) → capture `deployment_uuid` from the response.
2. Poll `GET /deployments/{deployment_uuid}` every ~3s until `status` is terminal.
   Status enum (from Coolify source `ApplicationDeploymentStatus.php`):
   - non-terminal: `queued`, `in_progress`
   - terminal SUCCESS: `finished`
   - terminal FAILURE: `failed`, `cancelled-by-user`
   - Guard against unexpected strings (OpenAPI types this as bare `string`).
   - Honor `429 Retry-After`; respect `--timeout`.
3. On `finished`, if the app has `health_check_enabled`, poll `GET /applications/{uuid}`
   for `running:healthy` (vs `running:unhealthy`).
4. Print **PASS/FAIL** verdict + tail of the deployment `logs` on failure. Exit code
   0 (pass) / 1 (fail) so callers "don't call it done while red"
   (ties into `quality/prove-it-validation`).

## The three skills (thin wrappers)

### `coolify` (resource management — primary)
List/inspect any resource; create (variant-aware for apps, engine-aware for db);
guarded update/delete; env get/set (bulk-aware via `set-bulk`). Always previews writes
(dry-run) and asks the user to confirm before re-running with `--apply`. Destructive ops
surface the `--confirm <name>` requirement.

### `coolify-deploy` (deploy + build validation)
Flow: `deploy` → `deployment wait` → health check → report. **Refuses to report success**
on a non-`finished` or unhealthy build; shows failing logs. Supports redeploy and
`--force` (no-cache rebuild). Single in-flight deploy at a time; surfaces queue 429s.

### `coolify-audit` (read-only)
Never writes. Full inventory via `/resources`; env hygiene (flag plaintext values that
look like secrets — requires `read:sensitive` to be meaningful, else says so); exposed
ports list; servers that need `server validate`. Produces a short human-readable report
(pairs with `reporting/human-readable-report` style).

## Cross-cutting

- **Error mapping → actionable messages:** 401 (token/abilities), 409 (domain conflict →
  hint `force_domain_override=true`), 422 (wrong app-create variant / missing fields),
  429 (back off, honor `Retry-After`), API-disabled (hint `/enable` with a root token).
- **Bilingual:** EN + ES trigger phrases in each SKILL.md; reply in the user's language.
- **Pagination:** only deployment history paginates (`skip`/`take`, default `take=10`);
  all other lists return plain JSON arrays.
- **Testing:** `coolify.py --self-test` runs offline against recorded fixtures — verifies
  arg parsing, the dry-run gate (no network on writes without `--apply`), the
  destructive `--confirm` guard, and the deployment-status state machine (queued →
  in_progress → finished/failed). No live instance required.
- **Offline degradation:** with no creds, reads/`ping` explain what's missing; the
  dry-run preview and `--self-test` still work, so the skill is never bricked without a
  server.

## Out of scope (v1)

- Backups, preview/PR deployments, MCP toggle, Hetzner provisioning, team management —
  the driver may expose `resources`/version but these flows are not wrapped by skills yet.
- A long-running watch/daemon mode. Polling is per-invocation with `--timeout`.

## API reference (verified 2026-06-17)

- Base: `https://<instance>/api/v1`. Bearer `id|secret`. uuid-addressed.
- Sources: OpenAPI `raw.githubusercontent.com/coollabsio/coolify/main/openapi.yaml`;
  `coolify.io/docs/api-reference/*`; status enum
  `github.com/coollabsio/coolify/blob/main/app/Enums/ApplicationDeploymentStatus.php`.
- Key gotchas: GET can mutate (start/stop/restart/deploy); no generic app-create;
  sensitive fields redacted without `read:sensitive`; `finished` ≠ healthy.
