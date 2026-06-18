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

Never writes. Reply in the user's language (EN/ES). `CO = devops/scripts/coolify.py`.

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
- `python $CO server list` → for any unvalidated server, recommend
  `python $CO server validate <uuid>` (that one is read-only; it runs Coolify's validation pipeline).

## 5. Report
- Produce a short, skimmable report (pairs with reporting/human-readable-report):
  inventory counts, hygiene findings, exposed ports, servers needing attention. Lead with
  anything risky.

## Rules
- ⚠ Read-only: never run a command with `--apply`. If a fix is needed, hand off to the `coolify` skill.
- ⚠ Don't paste full secret values into the report — reference the key and the finding.
