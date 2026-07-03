---
name: coolify-audit
description: >-
  Read-only audit of a Coolify instance — full resource inventory, env-var hygiene
  (plaintext secrets), exposed ports, and servers that need validation. Writes NOTHING.
  Use when the user says "/coolify-audit", "audit my coolify", "review coolify config",
  "any exposed ports in coolify", "check coolify secrets", "audita mi coolify",
  "revisa la configuración de coolify", "¿hay puertos expuestos en coolify?",
  "revisa los secretos de coolify". Requires scripts/coolify.py + configured creds
  (token needs `read:sensitive` for the env-value checks to be meaningful).
---

# Coolify read-only audit

Never writes. Reply in the user's language (EN/ES). `CO` = the `coolify.py` shipped with the
companion **coolify** skill (`coolify/scripts/coolify.py` in your skills dir — install it alongside).

## Model & effort
| Phase | Model | Effort | Why |
|---|---|---|---|
| Inventory pulls (steps 1–2 commands) | haiku | low | script work |
| Hygiene/exposure judgment + report (steps 2–5) | sonnet | medium | deciding what's a secret or a risky port is judgment |

Session above sonnet → pull the inventory in a `model: haiku` subagent, judge in the session.

## 1. Inventory
- `python $CO resources --json` → everything on the instance.
- Cross-check `python $CO apps list`, `db list`, `svc list`, `server list`.

## 2. Env-var hygiene
- For each app/db/svc of interest: `python $CO env list <uuid> --target <app|db|svc> --json`.
- Flag values that look like plaintext secrets (long random strings, `KEY=`, `TOKEN=`,
  `PASSWORD=`, private keys). NOTE: values are masked unless the token has `read:sensitive`
  — if they come back empty, say so rather than reporting "no secrets".

## 3. Exposure
- From `apps get <uuid>` read `ports_exposes` / `ports_mappings`; list anything publicly mapped.
- Confirm each app's `fqdn` is intended.

## 4. Server health
- `python $CO server list` → for any unvalidated server, note its uuid and tell the
  user/operator to run `python $CO server validate <uuid>` themselves (or hand off to
  the `coolify` skill). Do NOT run `server validate` here — it triggers a server-side
  validation pipeline and is therefore a side effect, not a read.

## 5. Report
- Produce a short, skimmable report (pairs with reporting/human-readable-report):
  inventory counts, hygiene findings, exposed ports, servers needing attention. Lead with
  anything risky.

## Rules
- ⚠ Read-only: never run a command with `--apply`. If a fix is needed, hand off to the `coolify` skill.
- ⚠ Don't paste full secret values into the report — reference the key and the finding.
