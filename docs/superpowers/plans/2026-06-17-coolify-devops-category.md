# Coolify `devops/` Skill Category — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a `devops/` skill category that drives a self-hosted Coolify PaaS via its REST API — one shared `coolify.py` CLI helper plus three skills (`coolify`, `coolify-deploy`, `coolify-audit`).

**Architecture:** A single stdlib-only Python CLI (`devops/scripts/coolify.py`) owns all HTTP, the dry-run/confirm safety engine, and the deployment-status state machine. Three thin SKILL.md files shell out to it. Mirrors the existing `project-management/scripts/board.py` pattern.

**Tech Stack:** Python 3.12, standard library only (`urllib`, `json`, `argparse`, `unittest`). No pip installs. Tests via stdlib `unittest`; `coolify.py --self-test` runs the same suite for end users.

## Global Constraints

- **Stdlib only** — no third-party imports in `coolify.py` or its tests. Verbatim rule from the repo (`board.py`: "Stdlib only").
- **Secrets via env / `.env`** — read `COOLIFY_BASE_URL`, `COOLIFY_API_TOKEN` from environment, fallback to a `.env` walked up from cwd. NEVER write creds to disk. Only `.env.example` is committed (`.gitignore` already blocks `.env`).
- **Bilingual** — every SKILL.md lists EN + ES trigger phrases; the skill replies in the user's language.
- **Generic** — no private absolute paths, no client names, no hardcoded instance URLs.
- **Offline-capable** — no creds must not brick the tool: reads explain what's missing, dry-run preview and `--self-test` still work.
- **API facts (verified 2026-06-17):** base `https://<instance>/api/v1`; header `Authorization: Bearer <id>|<secret>`; resources addressed by `uuid`; deployment status enum `queued`/`in_progress`/`finished`/`failed`/`cancelled-by-user` (`finished` = success, `failed`+`cancelled-by-user` = failure); `finished` ≠ healthy (check app `status` for `running:healthy`); no generic `POST /applications` (5 create variants); env values masked without the `read:sensitive` token ability.
- **Run tests with:** `python -m unittest -v` from `devops/scripts/` (or `python coolify.py --self-test`).
- **Commit style:** conventional commits, `feat(devops): …` / `docs(devops): …`.

---

## File Structure

- `devops/pack.json` — bilingual category manifest (EN + `es` mirror).
- `devops/README.md` — setup, token abilities, security policy.
- `devops/.env.example` — `COOLIFY_BASE_URL`, `COOLIFY_API_TOKEN` with comments.
- `devops/scripts/coolify.py` — the driver. One file: errors → config → transport → `CoolifyClient` (safety engine + retries) → deployment state machine → resource routing tables → argparse + dispatch → `main`/`--self-test`.
- `devops/scripts/test_coolify.py` — stdlib `unittest` suite. Imports `coolify` and drives it with a recording fake transport (no network).
- `devops/coolify/SKILL.md` — resource management (primary).
- `devops/coolify-deploy/SKILL.md` — deploy + build validation.
- `devops/coolify-audit/SKILL.md` — read-only audit/inventory.
- `README.md` (repo root) — add a `devops/` row to the categories table.

---

### Task 1: Category scaffolding (manifest, README, env example)

**Files:**
- Create: `devops/pack.json`
- Create: `devops/README.md`
- Create: `devops/.env.example`

**Interfaces:**
- Consumes: nothing.
- Produces: the `devops/` category directory; `pack.json` keys `title`, `description`, `order`, `skills{coolify,coolify-deploy,coolify-audit}`, `es{title,description,skills{...}}`.

- [ ] **Step 1: Write `devops/pack.json`**

```json
{
  "title": "DevOps",
  "description": "Drive a self-hosted Coolify PaaS from Claude Code — resource management, build-validated deploys, and read-only config audits — via one stdlib-only API helper. Dry-run by default.",
  "order": 6,
  "skills": {
    "coolify": "Manage Coolify resources (apps, databases, services, servers, projects, env vars) over the API. Reads run freely; writes are dry-run until --apply.",
    "coolify-deploy": "Trigger a Coolify deploy, poll the build to a terminal state, verify health, and report PASS/FAIL. Never reports success on a red build.",
    "coolify-audit": "Read-only audit of a Coolify instance: resource inventory, env-var hygiene, exposed ports, servers needing validation."
  },
  "es": {
    "title": "DevOps",
    "description": "Controla un Coolify autoalojado desde Claude Code — gestión de recursos, despliegues validados por build y auditorías de configuración de solo lectura — con un ayudante de API sin dependencias. Modo simulación por defecto.",
    "skills": {
      "coolify": "Gestiona recursos de Coolify (apps, bases de datos, servicios, servidores, proyectos, variables de entorno) por la API. Las lecturas corren libres; las escrituras son simuladas hasta usar --apply.",
      "coolify-deploy": "Dispara un despliegue en Coolify, sondea el build hasta un estado terminal, verifica la salud y reporta PASS/FAIL. Nunca reporta éxito con un build en rojo.",
      "coolify-audit": "Auditoría de solo lectura de una instancia Coolify: inventario de recursos, higiene de variables de entorno, puertos expuestos y servidores que requieren validación."
    }
  }
}
```

- [ ] **Step 2: Write `devops/.env.example`**

```bash
# Coolify API credentials — copy to .env and fill in. NEVER commit .env (gitignored).
#
# Base URL INCLUDING the version path. Self-hosted: https://your-instance/api/v1
# Coolify Cloud: https://app.coolify.io/api/v1
COOLIFY_BASE_URL=https://your-instance/api/v1
#
# API token from the Coolify dashboard → Keys & Tokens → API Tokens (shown once).
# Format is "<id>|<secret>" — paste it whole. Grant abilities you need:
#   read            basic reads
#   read:sensitive  REQUIRED to see env-var VALUES (otherwise masked/empty)
#   write           create / update / delete
#   deploy          trigger deployments
COOLIFY_API_TOKEN=
```

- [ ] **Step 3: Write `devops/README.md`**

```markdown
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
```

- [ ] **Step 4: Verify the manifest is valid and complete**

Run:
```bash
cd C:/Otros/Skills && python -c "import json; d=json.load(open('devops/pack.json')); assert set(d['skills'])=={'coolify','coolify-deploy','coolify-audit'}; assert set(d['es']['skills'])==set(d['skills']); print('pack.json ok')"
```
Expected: `pack.json ok`

- [ ] **Step 5: Commit**

```bash
cd C:/Otros/Skills && git add devops/pack.json devops/README.md devops/.env.example && git commit -m "feat(devops): scaffold Coolify skill category (manifest, README, env example)"
```

---

### Task 2: Driver config loading

**Files:**
- Create: `devops/scripts/coolify.py`
- Test: `devops/scripts/test_coolify.py`

**Interfaces:**
- Produces:
  - `class CoolifyError(Exception)`, `class ConfigError(CoolifyError)`, `class ConfirmError(CoolifyError)`, `class APIError(CoolifyError)` with attrs `status:int, body:str, hint:str`.
  - `load_env(start: Path) -> None` — walks up from `start`, loads first `.env` via `os.environ.setdefault`.
  - `load_config(start: Path|None=None) -> tuple[str,str]` — returns `(base_url, token)`; raises `ConfigError` if either missing. Strips trailing `/` from base; warns on stderr if base does not end with `/api/v1`.

- [ ] **Step 1: Write the failing test**

Create `devops/scripts/test_coolify.py`:
```python
import os, sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import coolify  # noqa: E402


class TestConfig(unittest.TestCase):
    def setUp(self):
        for k in ("COOLIFY_BASE_URL", "COOLIFY_API_TOKEN"):
            os.environ.pop(k, None)

    def test_missing_raises_configerror(self):
        with self.assertRaises(coolify.ConfigError):
            coolify.load_config(start=Path(self.id()))  # nonexistent dir → no .env

    def test_reads_from_env_and_strips_slash(self):
        os.environ["COOLIFY_BASE_URL"] = "https://ex.test/api/v1/"
        os.environ["COOLIFY_API_TOKEN"] = "1|secret"
        base, token = coolify.load_config(start=Path(self.id()))
        self.assertEqual(base, "https://ex.test/api/v1")
        self.assertEqual(token, "1|secret")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd C:/Otros/Skills/devops/scripts && python -m unittest -v test_coolify.TestConfig`
Expected: FAIL — `ModuleNotFoundError: No module named 'coolify'` (file not created yet).

- [ ] **Step 3: Write minimal implementation**

Create `devops/scripts/coolify.py`:
```python
#!/usr/bin/env python3
"""coolify.py — drive a self-hosted Coolify (v4, API v1) from the command line.

Stdlib only. Creds from env (COOLIFY_BASE_URL, COOLIFY_API_TOKEN) or a sibling .env;
NEVER stored on disk. Writes are dry-run by default — add --apply to perform; deletes
also need --confirm <resource-name>.

Run `python coolify.py --self-test` to run the offline test suite.
"""
import json, os, sys, time, urllib.error, urllib.request
from pathlib import Path


# ── errors ──────────────────────────────────────────────────────────────────
class CoolifyError(Exception):
    pass


class ConfigError(CoolifyError):
    pass


class ConfirmError(CoolifyError):
    pass


class APIError(CoolifyError):
    def __init__(self, status, body, hint=""):
        self.status, self.body, self.hint = status, body, hint
        super().__init__(f"HTTP {status}: {hint or (body[:200] if body else '')}")


# ── config ──────────────────────────────────────────────────────────────────
def load_env(start: Path):
    for d in [start, *start.parents]:
        envf = d / ".env"
        if envf.is_file():
            for line in envf.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())
            break


def load_config(start: Path = None):
    load_env(start or Path.cwd())
    base = os.environ.get("COOLIFY_BASE_URL", "").strip().rstrip("/")
    token = os.environ.get("COOLIFY_API_TOKEN", "").strip()
    if not base or not token:
        raise ConfigError(
            "Set COOLIFY_BASE_URL and COOLIFY_API_TOKEN (env or .env). "
            "Base looks like https://<instance>/api/v1; token from Coolify → "
            "Keys & Tokens → API Tokens."
        )
    if not base.endswith("/api/v1"):
        print(f"warning: COOLIFY_BASE_URL usually ends with /api/v1 (got {base})",
              file=sys.stderr)
    return base, token
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd C:/Otros/Skills/devops/scripts && python -m unittest -v test_coolify.TestConfig`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
cd C:/Otros/Skills && git add devops/scripts/coolify.py devops/scripts/test_coolify.py && git commit -m "feat(devops): coolify.py config loading + errors"
```

---

### Task 3: HTTP transport + GET reads + error mapping

**Files:**
- Modify: `devops/scripts/coolify.py`
- Test: `devops/scripts/test_coolify.py`

**Interfaces:**
- Consumes: `APIError` from Task 2.
- Produces:
  - `real_transport(method, url, headers, body) -> (status:int, headers:dict, raw:bytes)`.
  - `HINTS: dict[int,str]` keyed by HTTP status.
  - `class CoolifyClient(base_url, token, apply=False, transport=None, sleeper=time.sleep, max_retries=4)` with `request(method, path, body=None, *, destructive=False, confirm=None, resource_name=None)` and `get/post/patch/delete` convenience methods. (In this task `request` performs GET; writes are added in Task 4.) Successful JSON returns a `dict`/`list`; empty body returns `{}`; non-JSON returns `{"raw": <text>}`. On `status >= 400` raises `APIError(status, body, HINTS.get(status, ""))`.

- [ ] **Step 1: Write the failing test**

Append to `devops/scripts/test_coolify.py` (before the `if __name__` line):
```python
class RecordingTransport:
    """Fake transport: returns queued (status, headers, body-dict) responses
    and records each (method, url, body) call. No network."""
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def __call__(self, method, url, headers, body):
        self.calls.append((method, url, body))
        status, hdrs, payload = self.responses.pop(0)
        raw = json.dumps(payload).encode() if not isinstance(payload, (bytes, type(None))) else (payload or b"")
        return status, hdrs, raw


import json  # noqa: E402  (used by RecordingTransport)


class TestReads(unittest.TestCase):
    def _client(self, responses, **kw):
        return coolify.CoolifyClient("https://ex.test/api/v1", "1|s",
                                     transport=coolify.RecordingTransport(responses)
                                     if False else coolify_rt(responses), **kw)

    def test_get_returns_parsed_json(self):
        t = RecordingTransport([(200, {}, [{"uuid": "a1", "name": "web"}])])
        c = coolify.CoolifyClient("https://ex.test/api/v1", "1|s", transport=t)
        out = c.get("/applications")
        self.assertEqual(out[0]["uuid"], "a1")
        self.assertEqual(t.calls[0][0], "GET")
        self.assertTrue(t.calls[0][1].endswith("/applications"))

    def test_http_error_maps_hint(self):
        t = RecordingTransport([(401, {}, {"message": "unauthorized"})])
        c = coolify.CoolifyClient("https://ex.test/api/v1", "1|s", transport=t)
        with self.assertRaises(coolify.APIError) as cm:
            c.get("/applications")
        self.assertEqual(cm.exception.status, 401)
        self.assertIn("ability", cm.exception.hint.lower())


def coolify_rt(responses):
    return RecordingTransport(responses)
```

> Note: keep the single `import json` at the top of the file if you prefer; the duplicate is harmless but you may remove it. The `_client` helper is unused scaffolding — leave it or delete it.

- [ ] **Step 2: Run test to verify it fails**

Run: `cd C:/Otros/Skills/devops/scripts && python -m unittest -v test_coolify.TestReads`
Expected: FAIL — `AttributeError: module 'coolify' has no attribute 'CoolifyClient'`.

- [ ] **Step 3: Write minimal implementation**

Append to `devops/scripts/coolify.py`:
```python
# ── transport ───────────────────────────────────────────────────────────────
def real_transport(method, url, headers, body):
    data = body.encode() if isinstance(body, str) else body
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()


HINTS = {
    401: "Token invalid or missing ability (need read/write/deploy; read:sensitive for env values).",
    403: "Token lacks the required ability for this action.",
    404: "Resource not found — check the uuid.",
    409: "Conflict (often a domain already in use) — retry with force_domain_override=true.",
    422: "Validation failed — wrong app-create variant or missing required fields.",
    429: "Rate limited / deploy queue saturated.",
}

MUTATING = {"POST", "PATCH", "PUT", "DELETE"}


class CoolifyClient:
    def __init__(self, base_url, token, apply=False, transport=None,
                 sleeper=time.sleep, max_retries=4):
        self.base = base_url.rstrip("/")
        self.token = token
        self.apply = apply
        self.transport = transport or real_transport
        self.sleeper = sleeper
        self.max_retries = max_retries

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def request(self, method, path, body=None, *, destructive=False,
                confirm=None, resource_name=None):
        method = method.upper()
        url = self.base + path
        payload = json.dumps(body) if body is not None else None
        attempt = 0
        while True:
            status, headers, raw = self.transport(method, url, self._headers(), payload)
            if status == 429 and attempt < self.max_retries:
                wait = float(headers.get("Retry-After", 2) or 2)
                attempt += 1
                self.sleeper(wait)
                continue
            if status >= 400:
                text = raw.decode(errors="replace") if raw else ""
                raise APIError(status, text, HINTS.get(status, ""))
            if not raw:
                return {}
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return {"raw": raw.decode(errors="replace")}

    def get(self, p, **kw):
        return self.request("GET", p, **kw)

    def post(self, p, body=None, **kw):
        return self.request("POST", p, body, **kw)

    def patch(self, p, body=None, **kw):
        return self.request("PATCH", p, body, **kw)

    def delete(self, p, **kw):
        return self.request("DELETE", p, **kw)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd C:/Otros/Skills/devops/scripts && python -m unittest -v test_coolify.TestReads`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
cd C:/Otros/Skills && git add devops/scripts/coolify.py devops/scripts/test_coolify.py && git commit -m "feat(devops): HTTP transport, GET reads, status->hint mapping"
```

---

### Task 4: Safety engine — dry-run default, --apply, destructive confirm

**Files:**
- Modify: `devops/scripts/coolify.py` (extend `CoolifyClient.request`)
- Test: `devops/scripts/test_coolify.py`

**Interfaces:**
- Consumes: `CoolifyClient`, `ConfirmError`, `MUTATING` from Task 3.
- Produces:
  - `class DryRun` with attrs `method, path, body`, a `__str__` → `"WOULD <METHOD> <path> …  (re-run with --apply to perform)"`, and `to_dict() -> {"dry_run": True, "method", "path", "body"}`.
  - `CoolifyClient.request` now: for `method in MUTATING`, if `not self.apply` returns a `DryRun` **without calling transport**; if `apply` and `destructive` and `confirm != resource_name`, raises `ConfirmError`.

- [ ] **Step 1: Write the failing test**

Append a class to `devops/scripts/test_coolify.py`:
```python
class TestSafety(unittest.TestCase):
    def test_write_is_dryrun_and_skips_transport(self):
        t = RecordingTransport([])  # empty: any transport call would IndexError
        c = coolify.CoolifyClient("https://ex.test/api/v1", "1|s", transport=t, apply=False)
        out = c.post("/applications/uuid1/restart")
        self.assertIsInstance(out, coolify.DryRun)
        self.assertEqual(t.calls, [])
        self.assertIn("WOULD POST", str(out))

    def test_apply_performs_write(self):
        t = RecordingTransport([(200, {}, {"ok": True})])
        c = coolify.CoolifyClient("https://ex.test/api/v1", "1|s", transport=t, apply=True)
        out = c.post("/applications/uuid1/restart")
        self.assertEqual(out, {"ok": True})
        self.assertEqual(t.calls[0][0], "POST")

    def test_destructive_requires_matching_confirm(self):
        t = RecordingTransport([])
        c = coolify.CoolifyClient("https://ex.test/api/v1", "1|s", transport=t, apply=True)
        with self.assertRaises(coolify.ConfirmError):
            c.delete("/applications/uuid1", destructive=True,
                     confirm="wrong", resource_name="web")
        self.assertEqual(t.calls, [])

    def test_destructive_with_correct_confirm_proceeds(self):
        t = RecordingTransport([(200, {}, {"deleted": True})])
        c = coolify.CoolifyClient("https://ex.test/api/v1", "1|s", transport=t, apply=True)
        out = c.delete("/applications/uuid1", destructive=True,
                       confirm="web", resource_name="web")
        self.assertEqual(out, {"deleted": True})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd C:/Otros/Skills/devops/scripts && python -m unittest -v test_coolify.TestSafety`
Expected: FAIL — `AttributeError: module 'coolify' has no attribute 'DryRun'`.

- [ ] **Step 3: Write minimal implementation**

In `devops/scripts/coolify.py`, add the `DryRun` class immediately above `class CoolifyClient`:
```python
class DryRun:
    def __init__(self, method, path, body):
        self.method, self.path, self.body = method, path, body

    def __str__(self):
        b = f" body={json.dumps(self.body)}" if self.body is not None else ""
        return f"WOULD {self.method} {self.path}{b}  (re-run with --apply to perform)"

    def to_dict(self):
        return {"dry_run": True, "method": self.method, "path": self.path, "body": self.body}
```

Then replace the opening of `CoolifyClient.request` (the lines from `method = method.upper()` down to `payload = json.dumps(...)`) with the gated version:
```python
    def request(self, method, path, body=None, *, destructive=False,
                confirm=None, resource_name=None):
        method = method.upper()
        if method in MUTATING:
            if not self.apply:
                return DryRun(method, path, body)
            if destructive and confirm != resource_name:
                raise ConfirmError(
                    f"Destructive {method} {path} needs --confirm matching the resource "
                    f"name '{resource_name}' (got {confirm!r})."
                )
        url = self.base + path
        payload = json.dumps(body) if body is not None else None
        attempt = 0
        # ... (the existing retry/raise/parse loop stays unchanged) ...
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd C:/Otros/Skills/devops/scripts && python -m unittest -v test_coolify.TestSafety`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
cd C:/Otros/Skills && git add devops/scripts/coolify.py devops/scripts/test_coolify.py && git commit -m "feat(devops): dry-run-by-default safety engine with destructive confirm"
```

---

### Task 5: 429 retry/back-off honoring Retry-After

**Files:**
- Modify: `devops/scripts/coolify.py` (already has the retry loop from Task 3 — this task adds a focused test and verifies the behavior)
- Test: `devops/scripts/test_coolify.py`

**Interfaces:**
- Consumes: `CoolifyClient` retry loop (Task 3), `sleeper` injection.
- Produces: verified behavior — a `429` with `Retry-After` header retries after sleeping that many seconds, up to `max_retries`, then succeeds; a persistent `429` past `max_retries` raises `APIError(429)`.

- [ ] **Step 1: Write the failing test**

Append to `devops/scripts/test_coolify.py`:
```python
class TestRetry(unittest.TestCase):
    def test_429_then_success_sleeps_retry_after(self):
        slept = []
        t = RecordingTransport([
            (429, {"Retry-After": "5"}, {"message": "slow down"}),
            (200, {}, {"ok": True}),
        ])
        c = coolify.CoolifyClient("https://ex.test/api/v1", "1|s",
                                  transport=t, sleeper=slept.append)
        out = c.get("/deployments/dep1")
        self.assertEqual(out, {"ok": True})
        self.assertEqual(slept, [5.0])
        self.assertEqual(len(t.calls), 2)

    def test_429_exhausts_then_raises(self):
        t = RecordingTransport([(429, {}, {"m": "x"})] * 10)
        c = coolify.CoolifyClient("https://ex.test/api/v1", "1|s",
                                  transport=t, sleeper=lambda *_: None, max_retries=3)
        with self.assertRaises(coolify.APIError) as cm:
            c.get("/deployments/dep1")
        self.assertEqual(cm.exception.status, 429)
```

- [ ] **Step 2: Run test to verify it fails (or passes immediately)**

Run: `cd C:/Otros/Skills/devops/scripts && python -m unittest -v test_coolify.TestRetry`
Expected: PASS — the loop from Task 3 already implements this. (If it FAILS, the retry loop was altered in Task 4; restore the `while True` body shown in Task 3 Step 3.)

- [ ] **Step 3: No new implementation needed**

The Task 3 retry loop satisfies both tests. Do not add code unless a test failed.

- [ ] **Step 4: Confirm green**

Run: `cd C:/Otros/Skills/devops/scripts && python -m unittest -v test_coolify.TestRetry`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
cd C:/Otros/Skills && git add devops/scripts/test_coolify.py && git commit -m "test(devops): pin 429 retry/back-off behavior"
```

---

### Task 6: Deployment status state machine

**Files:**
- Modify: `devops/scripts/coolify.py`
- Test: `devops/scripts/test_coolify.py`

**Interfaces:**
- Consumes: `CoolifyClient.get`.
- Produces:
  - `TERMINAL_SUCCESS = {"finished"}`, `TERMINAL_FAILURE = {"failed", "cancelled-by-user"}`.
  - `classify_status(s: str) -> "success" | "failure" | "running"` (unknown strings → `"running"`, i.e. keep polling).
  - `wait_for_deployment(client, dep_uuid, timeout=600, interval=3, sleeper=None) -> dict` — polls `GET /deployments/{uuid}` until status is terminal or `timeout` elapsed; on timeout sets `dep["_timed_out"]=True` and returns the last payload.

- [ ] **Step 1: Write the failing test**

Append to `devops/scripts/test_coolify.py`:
```python
class TestDeployState(unittest.TestCase):
    def test_classify(self):
        self.assertEqual(coolify.classify_status("finished"), "success")
        self.assertEqual(coolify.classify_status("failed"), "failure")
        self.assertEqual(coolify.classify_status("cancelled-by-user"), "failure")
        self.assertEqual(coolify.classify_status("in_progress"), "running")
        self.assertEqual(coolify.classify_status("queued"), "running")
        self.assertEqual(coolify.classify_status("weird-new-status"), "running")

    def test_wait_polls_until_terminal(self):
        t = RecordingTransport([
            (200, {}, {"status": "queued"}),
            (200, {}, {"status": "in_progress"}),
            (200, {}, {"status": "finished", "logs": "done"}),
        ])
        c = coolify.CoolifyClient("https://ex.test/api/v1", "1|s", transport=t)
        dep = coolify.wait_for_deployment(c, "dep1", interval=1, sleeper=lambda *_: None)
        self.assertEqual(dep["status"], "finished")
        self.assertEqual(len(t.calls), 3)

    def test_wait_times_out(self):
        t = RecordingTransport([(200, {}, {"status": "in_progress"})] * 50)
        c = coolify.CoolifyClient("https://ex.test/api/v1", "1|s", transport=t)
        dep = coolify.wait_for_deployment(c, "dep1", timeout=3, interval=1,
                                          sleeper=lambda *_: None)
        self.assertTrue(dep.get("_timed_out"))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd C:/Otros/Skills/devops/scripts && python -m unittest -v test_coolify.TestDeployState`
Expected: FAIL — `AttributeError: module 'coolify' has no attribute 'classify_status'`.

- [ ] **Step 3: Write minimal implementation**

Append to `devops/scripts/coolify.py`:
```python
# ── deployment state machine ──────────────────────────────────────────────────
TERMINAL_SUCCESS = {"finished"}
TERMINAL_FAILURE = {"failed", "cancelled-by-user"}


def classify_status(s):
    if s in TERMINAL_SUCCESS:
        return "success"
    if s in TERMINAL_FAILURE:
        return "failure"
    return "running"  # queued / in_progress / unknown → keep polling


def wait_for_deployment(client, dep_uuid, timeout=600, interval=3, sleeper=None):
    sleeper = sleeper or client.sleeper
    waited = 0
    dep = {}
    while True:
        dep = client.get(f"/deployments/{dep_uuid}")
        if classify_status(dep.get("status", "")) != "running":
            return dep
        if waited >= timeout:
            dep["_timed_out"] = True
            return dep
        sleeper(interval)
        waited += interval
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd C:/Otros/Skills/devops/scripts && python -m unittest -v test_coolify.TestDeployState`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
cd C:/Otros/Skills && git add devops/scripts/coolify.py devops/scripts/test_coolify.py && git commit -m "feat(devops): deployment status state machine + wait_for_deployment"
```

---

### Task 7: Resource routing tables + env-file parsing

**Files:**
- Modify: `devops/scripts/coolify.py`
- Test: `devops/scripts/test_coolify.py`

**Interfaces:**
- Produces:
  - `LIST_PATHS = {"apps":"/applications","db":"/databases","svc":"/services","server":"/servers","project":"/projects"}`.
  - `ITEM_PREFIX` = same mapping (used as `f"{ITEM_PREFIX[g]}/{uuid}"`).
  - `APP_CREATE = {"public":"/applications/public", "private-github-app":..., "private-deploy-key":..., "dockerfile":..., "dockerimage":...}`.
  - `DB_ENGINES = {engine: f"/databases/{engine}"}` for the 8 engines.
  - `ENV_BASE = {"app":"/applications","db":"/databases","svc":"/services"}`.
  - `parse_env_file(text: str) -> dict` — JSON object if `text` starts with `{`, else `.env`-style `KEY=VAL` lines (ignoring blanks/`#`).

- [ ] **Step 1: Write the failing test**

Append to `devops/scripts/test_coolify.py`:
```python
class TestRouting(unittest.TestCase):
    def test_tables_present(self):
        self.assertEqual(coolify.LIST_PATHS["apps"], "/applications")
        self.assertEqual(coolify.APP_CREATE["public"], "/applications/public")
        self.assertEqual(set(coolify.DB_ENGINES), {
            "postgresql", "mysql", "mariadb", "mongodb",
            "redis", "keydb", "dragonfly", "clickhouse"})
        self.assertEqual(coolify.ENV_BASE["svc"], "/services")

    def test_parse_env_file_keyval(self):
        self.assertEqual(
            coolify.parse_env_file("# c\nFOO=bar\n\nBAZ=qux=1\n"),
            {"FOO": "bar", "BAZ": "qux=1"})

    def test_parse_env_file_json(self):
        self.assertEqual(coolify.parse_env_file('{"A":"1","B":"2"}'), {"A": "1", "B": "2"})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd C:/Otros/Skills/devops/scripts && python -m unittest -v test_coolify.TestRouting`
Expected: FAIL — `AttributeError: ... 'LIST_PATHS'`.

- [ ] **Step 3: Write minimal implementation**

Append to `devops/scripts/coolify.py`:
```python
# ── resource routing tables ───────────────────────────────────────────────────
LIST_PATHS = {
    "apps": "/applications",
    "db": "/databases",
    "svc": "/services",
    "server": "/servers",
    "project": "/projects",
}
ITEM_PREFIX = dict(LIST_PATHS)

APP_CREATE = {
    "public": "/applications/public",
    "private-github-app": "/applications/private-github-app",
    "private-deploy-key": "/applications/private-deploy-key",
    "dockerfile": "/applications/dockerfile",
    "dockerimage": "/applications/dockerimage",
}
DB_ENGINES = {e: f"/databases/{e}" for e in (
    "postgresql", "mysql", "mariadb", "mongodb",
    "redis", "keydb", "dragonfly", "clickhouse")}
ENV_BASE = {"app": "/applications", "db": "/databases", "svc": "/services"}


def parse_env_file(text):
    text = text.strip()
    if text.startswith("{"):
        return json.loads(text)
    out = {}
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd C:/Otros/Skills/devops/scripts && python -m unittest -v test_coolify.TestRouting`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
cd C:/Otros/Skills && git add devops/scripts/coolify.py devops/scripts/test_coolify.py && git commit -m "feat(devops): resource routing tables + env-file parsing"
```

---

### Task 8: Argument parser + dispatch for reads

**Files:**
- Modify: `devops/scripts/coolify.py`
- Test: `devops/scripts/test_coolify.py`

**Interfaces:**
- Consumes: `CoolifyClient`, `LIST_PATHS`, `ITEM_PREFIX`.
- Produces:
  - `build_parser() -> argparse.ArgumentParser` with a top-level `--apply`, `--confirm`, `--json` and subcommands. This task wires the **read** verbs: `ping`; `<group> list` and `<group> get <uuid>` for `apps|db|svc|server|project`; `apps logs <uuid>`; `server validate <uuid>`; `server resources <uuid>`; `resources`; `deployment get <uuid>`; `deployment history <app_uuid>`.
  - `dispatch(client, args) -> object` — returns the Python object from the matching read call (dict/list). Raises `ValueError` for an unknown command.

- [ ] **Step 1: Write the failing test**

Append to `devops/scripts/test_coolify.py`:
```python
class TestDispatchReads(unittest.TestCase):
    def _run(self, argv, responses):
        t = RecordingTransport(responses)
        c = coolify.CoolifyClient("https://ex.test/api/v1", "1|s", transport=t)
        args = coolify.build_parser().parse_args(argv)
        return coolify.dispatch(c, args), t

    def test_ping(self):
        out, t = self._run(["ping"], [(200, {}, {"version": "v4.0.0"})])
        self.assertEqual(out["version"], "v4.0.0")
        self.assertTrue(t.calls[0][1].endswith("/version"))

    def test_apps_list(self):
        out, t = self._run(["apps", "list"], [(200, {}, [{"uuid": "a1"}])])
        self.assertEqual(out[0]["uuid"], "a1")
        self.assertTrue(t.calls[0][1].endswith("/applications"))

    def test_db_get(self):
        out, t = self._run(["db", "get", "u9"], [(200, {}, {"uuid": "u9"})])
        self.assertTrue(t.calls[0][1].endswith("/databases/u9"))

    def test_deployment_get(self):
        out, t = self._run(["deployment", "get", "d1"], [(200, {}, {"status": "finished"})])
        self.assertTrue(t.calls[0][1].endswith("/deployments/d1"))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd C:/Otros/Skills/devops/scripts && python -m unittest -v test_coolify.TestDispatchReads`
Expected: FAIL — `AttributeError: ... 'build_parser'`.

- [ ] **Step 3: Write minimal implementation**

Append to `devops/scripts/coolify.py`:
```python
# ── CLI ───────────────────────────────────────────────────────────────────────
import argparse  # noqa: E402  (kept near CLI for clarity)


def build_parser():
    p = argparse.ArgumentParser(prog="coolify.py", description="Drive a Coolify instance.")
    p.add_argument("--apply", action="store_true", help="perform writes (default: dry-run)")
    p.add_argument("--confirm", default=None, help="resource name, required for destructive ops")
    p.add_argument("--json", action="store_true", help="machine-readable JSON output")
    p.add_argument("--self-test", action="store_true", help="run the offline test suite and exit")
    sub = p.add_subparsers(dest="group")

    sub.add_parser("ping")
    sub.add_parser("resources")

    for g in ("apps", "db", "svc", "server", "project"):
        gp = sub.add_parser(g).add_subparsers(dest="action")
        gp.add_parser("list")
        gp.add_parser("get").add_argument("uuid")
        gp.add_parser("delete").add_argument("uuid")
        for life in ("start", "stop", "restart"):
            gp.add_parser(life).add_argument("uuid")

    # read-only extras
    apps = _find_sub(p, "apps")
    apps.add_parser("logs").add_argument("uuid")
    srv = _find_sub(p, "server")
    srv.add_parser("validate").add_argument("uuid")
    srv.add_parser("resources").add_argument("uuid")

    dep = sub.add_parser("deployment").add_subparsers(dest="action")
    dep.add_parser("get").add_argument("uuid")
    dep.add_parser("history").add_argument("app_uuid")

    return p


def _find_sub(parser, name):
    """Return the subparsers object attached to subcommand `name`."""
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            target = action.choices.get(name)
            for a in target._actions:
                if isinstance(a, argparse._SubParsersAction):
                    return a
    raise KeyError(name)


def dispatch(client, args):
    g = args.group
    if g == "ping":
        return client.get("/version")
    if g == "resources":
        return client.get("/resources")
    if g in LIST_PATHS:
        act = args.action
        if act == "list":
            return client.get(LIST_PATHS[g])
        if act == "get":
            return client.get(f"{ITEM_PREFIX[g]}/{args.uuid}")
        if g == "apps" and act == "logs":
            return client.get(f"/applications/{args.uuid}/logs")
        if g == "server" and act == "validate":
            return client.get(f"/servers/{args.uuid}/validate")
        if g == "server" and act == "resources":
            return client.get(f"/servers/{args.uuid}/resources")
    if g == "deployment":
        if args.action == "get":
            return client.get(f"/deployments/{args.uuid}")
        if args.action == "history":
            return client.get(f"/deployments/applications/{args.app_uuid}")
    raise ValueError(f"unknown or write command not yet wired: {g} {getattr(args,'action',None)}")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd C:/Otros/Skills/devops/scripts && python -m unittest -v test_coolify.TestDispatchReads`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
cd C:/Otros/Skills && git add devops/scripts/coolify.py devops/scripts/test_coolify.py && git commit -m "feat(devops): argparse + dispatch for read commands"
```

---

### Task 9: Dispatch for writes (lifecycle, delete, create, env, deploy, wait)

**Files:**
- Modify: `devops/scripts/coolify.py` (extend `build_parser` and `dispatch`)
- Test: `devops/scripts/test_coolify.py`

**Interfaces:**
- Consumes: everything from Tasks 4–8 (`DryRun`, safety gate, `APP_CREATE`, `DB_ENGINES`, `ENV_BASE`, `parse_env_file`, `wait_for_deployment`).
- Produces (extended `dispatch`):
  - Lifecycle `apps|db|svc start|stop|restart <uuid>` → `client.post("{prefix}/{uuid}/{action}")` (dry-run unless `--apply`).
  - `delete <uuid>` for `apps|db|svc|server|project` → `client.delete(..., destructive=True, confirm=args.confirm, resource_name=<looked-up name>)`. Name lookup: `client.get` the item first and read its `name` (skip the GET in dry-run to avoid surprises — pass `resource_name=args.confirm` so dry-run just previews). In `--apply`, GET the item, use its `name`.
  - `apps create <variant> --json-body <file|->` → POST `APP_CREATE[variant]` with body from a JSON file/stdin. Unknown variant → `ValueError`.
  - `db create <engine> --json-body <file|->` → POST `DB_ENGINES[engine]`.
  - `env list <uuid> [--target app|db|svc]` → GET `{ENV_BASE[t]}/{uuid}/envs`.
  - `env set <uuid> KEY=VAL [--target ...]` → POST `.../envs` body `{"key":K,"value":V}`.
  - `env set-bulk <uuid> <file> [--target ...]` → PATCH `.../envs/bulk` body `{"data":[{"key","value"}...]}` from `parse_env_file`.
  - `env delete <uuid> <env_uuid> [--target ...]` → DELETE `.../envs/{env_uuid}` (destructive).
  - `deploy <uuid> [--tag T] [--force]` → POST `/deploy?uuid=…` (or `?tag=…`, `&force=true`); returns response.
  - `deployment wait <dep_uuid> [--timeout S]` → `wait_for_deployment`.

- [ ] **Step 1: Write the failing test**

Append to `devops/scripts/test_coolify.py`:
```python
class TestDispatchWrites(unittest.TestCase):
    def _parse(self, argv):
        return coolify.build_parser().parse_args(argv)

    def test_restart_is_dryrun_by_default(self):
        t = RecordingTransport([])
        c = coolify.CoolifyClient("https://ex.test/api/v1", "1|s", transport=t)
        out = coolify.dispatch(c, self._parse(["apps", "restart", "u1"]))
        self.assertIsInstance(out, coolify.DryRun)
        self.assertEqual(t.calls, [])

    def test_restart_apply_posts(self):
        t = RecordingTransport([(200, {}, {"ok": True})])
        c = coolify.CoolifyClient("https://ex.test/api/v1", "1|s", transport=t, apply=True)
        coolify.dispatch(c, self._parse(["--apply", "apps", "restart", "u1"]))
        self.assertEqual(t.calls[0][0], "POST")
        self.assertTrue(t.calls[0][1].endswith("/applications/u1/restart"))

    def test_delete_needs_confirm(self):
        t = RecordingTransport([(200, {}, {"uuid": "u1", "name": "web"})])
        c = coolify.CoolifyClient("https://ex.test/api/v1", "1|s", transport=t, apply=True)
        args = self._parse(["--apply", "--confirm", "wrong", "apps", "delete", "u1"])
        with self.assertRaises(coolify.ConfirmError):
            coolify.dispatch(c, args)

    def test_env_set_builds_body(self):
        t = RecordingTransport([(200, {}, {"ok": True})])
        c = coolify.CoolifyClient("https://ex.test/api/v1", "1|s", transport=t, apply=True)
        coolify.dispatch(c, self._parse(["--apply", "env", "set", "u1", "FOO=bar"]))
        method, url, body = t.calls[0]
        self.assertEqual(method, "POST")
        self.assertTrue(url.endswith("/applications/u1/envs"))
        self.assertEqual(json.loads(body), {"key": "FOO", "value": "bar"})

    def test_deploy_builds_query(self):
        t = RecordingTransport([(200, {}, {"deployments": [{"deployment_uuid": "d1"}]})])
        c = coolify.CoolifyClient("https://ex.test/api/v1", "1|s", transport=t, apply=True)
        coolify.dispatch(c, self._parse(["--apply", "deploy", "u1", "--force"]))
        url = t.calls[0][1]
        self.assertIn("uuid=u1", url)
        self.assertIn("force=true", url)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd C:/Otros/Skills/devops/scripts && python -m unittest -v test_coolify.TestDispatchWrites`
Expected: FAIL — write verbs not wired (`ValueError`) / parser missing args.

- [ ] **Step 3: Write minimal implementation**

In `build_parser()`, **add** the write-specific arguments. After the per-group loop that adds `list/get/delete/start/stop/restart`, extend the `apps` and `db` create verbs and the `env`/`deploy` groups. Replace the `# read-only extras` section's end by inserting before `return p`:
```python
    # create verbs (variant/engine aware)
    appc = _find_sub(p, "apps").add_parser("create")
    appc.add_argument("variant", choices=sorted(APP_CREATE))
    appc.add_argument("--json-body", required=True, help="path to JSON body, or - for stdin")
    dbc = _find_sub(p, "db").add_parser("create")
    dbc.add_argument("engine", choices=sorted(DB_ENGINES))
    dbc.add_argument("--json-body", required=True, help="path to JSON body, or - for stdin")

    env = sub.add_parser("env").add_subparsers(dest="action")
    for name in ("list", "set", "set-bulk", "delete"):
        ep = env.add_parser(name)
        ep.add_argument("--target", choices=("app", "db", "svc"), default="app")
        ep.add_argument("uuid")
        if name == "set":
            ep.add_argument("pair", help="KEY=VALUE")
        if name == "set-bulk":
            ep.add_argument("file", help="path to .env-style or JSON file")
        if name == "delete":
            ep.add_argument("env_uuid")

    dp = sub.add_parser("deploy")
    dp.add_argument("uuid", nargs="?")
    dp.add_argument("--tag", default=None)
    dp.add_argument("--force", action="store_true")

    # extend the existing `deployment` subparser created in Task 8:
    depsub = _find_sub(p, "deployment")
    w = depsub.add_parser("wait")
    w.add_argument("uuid")
    w.add_argument("--timeout", type=int, default=600)
```

> NOTE: the `deployment` subparser is created in Task 8 via `sub.add_parser("deployment").add_subparsers(...)`. `_find_sub(p, "deployment")` returns that same subparsers object so `wait` joins `get`/`history`.

In `dispatch()`, **insert** these branches before the final `raise ValueError`:
```python
    # lifecycle (apps/db/svc) ----------------------------------------------------
    if g in ("apps", "db", "svc") and args.action in ("start", "stop", "restart"):
        return client.post(f"{ITEM_PREFIX[g]}/{args.uuid}/{args.action}")

    # delete (destructive) -------------------------------------------------------
    if g in LIST_PATHS and args.action == "delete":
        name = args.confirm
        if client.apply:
            try:
                name = client.get(f"{ITEM_PREFIX[g]}/{args.uuid}").get("name", args.confirm)
            except APIError:
                name = args.confirm
        return client.delete(f"{ITEM_PREFIX[g]}/{args.uuid}",
                             destructive=True, confirm=args.confirm, resource_name=name)

    # create ---------------------------------------------------------------------
    if g == "apps" and args.action == "create":
        return client.post(APP_CREATE[args.variant], body=_read_json_arg(args.json_body))
    if g == "db" and args.action == "create":
        return client.post(DB_ENGINES[args.engine], body=_read_json_arg(args.json_body))

    # env ------------------------------------------------------------------------
    if g == "env":
        base = f"{ENV_BASE[args.target]}/{args.uuid}/envs"
        if args.action == "list":
            return client.get(base)
        if args.action == "set":
            k, _, v = args.pair.partition("=")
            return client.post(base, body={"key": k, "value": v})
        if args.action == "set-bulk":
            data = parse_env_file(Path(args.file).read_text(encoding="utf-8"))
            body = {"data": [{"key": k, "value": v} for k, v in data.items()]}
            return client.patch(base + "/bulk", body=body)
        if args.action == "delete":
            return client.delete(f"{base}/{args.env_uuid}",
                                 destructive=True, confirm=args.confirm,
                                 resource_name=args.confirm)

    # deploy ---------------------------------------------------------------------
    if g == "deploy":
        q = []
        if args.uuid:
            q.append(f"uuid={args.uuid}")
        if args.tag:
            q.append(f"tag={args.tag}")
        if args.force:
            q.append("force=true")
        return client.post("/deploy?" + "&".join(q))
    if g == "deployment" and args.action == "wait":
        return wait_for_deployment(client, args.uuid, timeout=args.timeout)
```

And add the small helper near `parse_env_file`:
```python
def _read_json_arg(src):
    text = sys.stdin.read() if src == "-" else Path(src).read_text(encoding="utf-8")
    return json.loads(text)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd C:/Otros/Skills/devops/scripts && python -m unittest -v test_coolify.TestDispatchWrites`
Expected: PASS (5 tests).

- [ ] **Step 5: Commit**

```bash
cd C:/Otros/Skills && git add devops/scripts/coolify.py devops/scripts/test_coolify.py && git commit -m "feat(devops): wire write/create/env/deploy/wait commands into dispatch"
```

---

### Task 10: `main()`, output formatting, and `--self-test`

**Files:**
- Modify: `devops/scripts/coolify.py`
- Test: `devops/scripts/test_coolify.py`

**Interfaces:**
- Consumes: `build_parser`, `dispatch`, `load_config`, `CoolifyClient`, all error classes.
- Produces:
  - `format_output(obj, as_json: bool) -> str` — `--json` dumps JSON (DryRun via `.to_dict()`); otherwise a compact human view (DryRun via `str`, lists as a `uuid  name  status` table when those keys exist, else pretty JSON).
  - `run_self_test() -> int` — runs the `test_coolify` suite via `unittest`, returns exit code (0 pass).
  - `main(argv=None) -> int` — parses args; if `--self-test`, runs it; else `load_config`, build `CoolifyClient(base, token, apply=args.apply)`, `dispatch`, print `format_output`. Maps `ConfigError`/`ConfirmError`/`APIError` to a stderr message + nonzero exit. `if __name__ == "__main__": sys.exit(main())`.

- [ ] **Step 1: Write the failing test**

Append to `devops/scripts/test_coolify.py`:
```python
class TestMain(unittest.TestCase):
    def test_format_json_dryrun(self):
        dr = coolify.DryRun("POST", "/applications/u1/restart", None)
        s = coolify.format_output(dr, as_json=True)
        self.assertEqual(json.loads(s)["dry_run"], True)

    def test_format_table_list(self):
        s = coolify.format_output(
            [{"uuid": "u1", "name": "web", "status": "running:healthy"}], as_json=False)
        self.assertIn("u1", s)
        self.assertIn("web", s)

    def test_main_selftest_returns_int(self):
        # Run a trivially-true subset so we don't recurse the whole suite slowly:
        rc = coolify.run_self_test(pattern="test_classify")
        self.assertEqual(rc, 0)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd C:/Otros/Skills/devops/scripts && python -m unittest -v test_coolify.TestMain`
Expected: FAIL — `AttributeError: ... 'format_output'`.

- [ ] **Step 3: Write minimal implementation**

Append to `devops/scripts/coolify.py`:
```python
# ── output + entrypoint ───────────────────────────────────────────────────────
def format_output(obj, as_json=False):
    if isinstance(obj, DryRun):
        return json.dumps(obj.to_dict(), indent=2) if as_json else str(obj)
    if as_json:
        return json.dumps(obj, indent=2)
    if isinstance(obj, list) and obj and isinstance(obj[0], dict) and "uuid" in obj[0]:
        rows = [f"{i.get('uuid',''):36}  {str(i.get('name','')):24}  {i.get('status','')}"
                for i in obj]
        return "\n".join(rows)
    return json.dumps(obj, indent=2)


def run_self_test(pattern=None):
    import unittest
    here = Path(__file__).resolve().parent
    loader = unittest.TestLoader()
    if pattern:
        loader.testNamePatterns = [f"*{pattern}*"]
    suite = loader.discover(str(here), pattern="test_coolify.py")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.self_test:
        return run_self_test()
    if not args.group:
        build_parser().print_help()
        return 2
    try:
        base, token = load_config()
        client = CoolifyClient(base, token, apply=args.apply)
        out = dispatch(client, args)
        print(format_output(out, as_json=args.json))
        return 0
    except (ConfigError, ConfirmError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    except APIError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd C:/Otros/Skills/devops/scripts && python -m unittest -v test_coolify.TestMain`
Expected: PASS (3 tests).

- [ ] **Step 5: Run the FULL suite via the shipped entrypoint**

Run: `cd C:/Otros/Skills/devops/scripts && python coolify.py --self-test`
Expected: `OK` — all tests across all classes pass.

- [ ] **Step 6: Commit**

```bash
cd C:/Otros/Skills && git add devops/scripts/coolify.py devops/scripts/test_coolify.py && git commit -m "feat(devops): main(), output formatting, --self-test entrypoint"
```

---

### Task 11: `coolify` skill (resource management)

**Files:**
- Create: `devops/coolify/SKILL.md`

**Interfaces:**
- Consumes: `coolify.py` command surface (Tasks 8–10).
- Produces: a SKILL.md with YAML frontmatter (`name: coolify`, `description:` with EN+ES triggers) and the CRUD workflow.

- [ ] **Step 1: Write the skill**

Create `devops/coolify/SKILL.md`:
```markdown
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
- Env: `python $CO env set <uuid> KEY=value --target app` (preview) → add `--apply`.
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
```

- [ ] **Step 2: Verify frontmatter + key content**

Run:
```bash
cd C:/Otros/Skills && python -c "import re,io; t=open('devops/coolify/SKILL.md',encoding='utf-8').read(); assert t.startswith('---'); assert 'name: coolify' in t; assert '--apply' in t and '--confirm' in t and 'read:sensitive' in t; print('coolify SKILL ok')"
```
Expected: `coolify SKILL ok`

- [ ] **Step 3: Commit**

```bash
cd C:/Otros/Skills && git add devops/coolify/SKILL.md && git commit -m "feat(devops): coolify resource-management skill"
```

---

### Task 12: `coolify-deploy` skill (deploy + build validation)

**Files:**
- Create: `devops/coolify-deploy/SKILL.md`

**Interfaces:**
- Consumes: `coolify.py deploy`, `deployment wait`, `apps get` (Tasks 9–10).
- Produces: SKILL.md, frontmatter `name: coolify-deploy`, EN+ES triggers; the deploy→validate→report flow.

- [ ] **Step 1: Write the skill**

Create `devops/coolify-deploy/SKILL.md`:
```markdown
---
name: coolify-deploy
description: >-
  Trigger a Coolify deployment and VALIDATE it — poll the build to a terminal state,
  then check app health, and report PASS/FAIL with logs on failure. Never reports success
  on a red build. Use when the user says "/coolify-deploy", "deploy on coolify", "redeploy
  my app", "is the coolify build passing", "validate the coolify deploy", "despliega en
  coolify", "vuelve a desplegar", "valida el build de coolify", "¿pasó el build en coolify?".
  Requires scripts/coolify.py + configured creds (token needs the `deploy` ability).
---

# Coolify deploy + build validation

Reply in the user's language (EN/ES). `CO = devops/scripts/coolify.py`.

## 1. Identify the app
- `python $CO apps list` → find the target app uuid (confirm with the user if ambiguous).

## 2. Trigger the deploy (a write → needs --apply)
- Preview: `python $CO deploy <uuid> [--force]` (shows `WOULD POST /deploy?uuid=…`).
- Perform: `python $CO deploy <uuid> [--force] --apply` → capture `deployment_uuid` from the
  response (`deployments[].deployment_uuid`). `--force` = rebuild without cache.

## 3. Validate the build  ⟵ this is the point of the skill
- `python $CO deployment wait <deployment_uuid> --timeout 900`
  - Polls until status is terminal. `finished` = build success; `failed` /
    `cancelled-by-user` = failure. A timeout returns `_timed_out: true`.
- `finished` is NOT proof the app is healthy. Then:
  `python $CO apps get <uuid>` and check `status` is `running:healthy`
  (if the app has `health_check_enabled`).

## 4. Report PASS/FAIL — with evidence (pairs with quality/prove-it-validation)
- **PASS** only if the deployment is `finished` AND the app is healthy. State both.
- **FAIL** if status is `failed`/`cancelled-by-user`/timed-out, OR the app is unhealthy.
  Show the failing build logs: `python $CO deployment get <deployment_uuid>` (the `logs`
  field). Do NOT call the deploy successful.

## Rules
- ⚠ Never report "deployed ✅" on a non-`finished` status or an unhealthy app — show the proof.
- ⚠ One in-flight deploy at a time; if `/deploy` returns 429 the queue is saturated — back off and retry.
- ✅ Resource CRUD (env vars, create/delete) lives in the `coolify` skill.
```

- [ ] **Step 2: Verify frontmatter + key content**

Run:
```bash
cd C:/Otros/Skills && python -c "t=open('devops/coolify-deploy/SKILL.md',encoding='utf-8').read(); assert 'name: coolify-deploy' in t; assert 'deployment wait' in t and 'running:healthy' in t and 'PASS' in t; print('coolify-deploy SKILL ok')"
```
Expected: `coolify-deploy SKILL ok`

- [ ] **Step 3: Commit**

```bash
cd C:/Otros/Skills && git add devops/coolify-deploy/SKILL.md && git commit -m "feat(devops): coolify-deploy build-validation skill"
```

---

### Task 13: `coolify-audit` skill (read-only audit)

**Files:**
- Create: `devops/coolify-audit/SKILL.md`

**Interfaces:**
- Consumes: `coolify.py resources`, `*list`, `env list`, `server validate` (read-only).
- Produces: SKILL.md, frontmatter `name: coolify-audit`, EN+ES triggers; the read-only audit flow.

- [ ] **Step 1: Write the skill**

Create `devops/coolify-audit/SKILL.md`:
```markdown
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
```

- [ ] **Step 2: Verify frontmatter + key content**

Run:
```bash
cd C:/Otros/Skills && python -c "t=open('devops/coolify-audit/SKILL.md',encoding='utf-8').read(); assert 'name: coolify-audit' in t; assert 'read:sensitive' in t and 'ports_exposes' in t and 'never run a command with --apply' in t.lower() or 'never run a command with `--apply`' in t; print('coolify-audit SKILL ok')"
```
Expected: `coolify-audit SKILL ok`

> If the assertion is fussy about backticks, simplify it to: `assert 'Read-only' in t`.

- [ ] **Step 3: Commit**

```bash
cd C:/Otros/Skills && git add devops/coolify-audit/SKILL.md && git commit -m "feat(devops): coolify-audit read-only audit skill"
```

---

### Task 14: Wire category into root README + final green

**Files:**
- Modify: `README.md` (repo root — categories table + design note)

**Interfaces:**
- Consumes: the finished `devops/` category.
- Produces: a `devops/` row in the root README categories table; a final full-suite green.

- [ ] **Step 1: Add the categories-table row**

In `README.md`, the categories table (the block starting `| Folder | What's inside |`) — add this row after the `quality/` row:
```markdown
| [`devops/`](devops/) | **Coolify control.** Drive a self-hosted Coolify PaaS — resource management (`coolify`), build-validated deploys (`coolify-deploy`), and read-only config audits (`coolify-audit`) — via one stdlib-only API helper. Dry-run by default. |
```

- [ ] **Step 2: Verify the row landed**

Run:
```bash
cd C:/Otros/Skills && python -c "t=open('README.md',encoding='utf-8').read(); assert '[`devops/`](devops/)' in t and 'Coolify control' in t; print('readme ok')"
```
Expected: `readme ok`

- [ ] **Step 3: Run the FULL test suite (final gate)**

Run: `cd C:/Otros/Skills/devops/scripts && python coolify.py --self-test`
Expected: `OK` — every test across Tasks 2–10 passes.

- [ ] **Step 4: Confirm no secrets are staged and tree is clean**

Run:
```bash
cd C:/Otros/Skills && git status --porcelain && git ls-files devops | grep -E "(^|/)\.env$" && echo "LEAK" || echo "no .env tracked"
```
Expected: clean working tree after commit; `no .env tracked`.

- [ ] **Step 5: Commit**

```bash
cd C:/Otros/Skills && git add README.md && git commit -m "docs(devops): list Coolify category in root README"
```

---

## Self-Review

**1. Spec coverage**

| Spec section | Task(s) |
|---|---|
| Category layout (pack.json, README, .env.example, scripts/) | 1 |
| `coolify.py` command surface (reads) | 8 |
| `coolify.py` command surface (writes/create/env/deploy/wait) | 9 |
| Safety engine (dry-run default, --apply, --confirm destructive) | 4, 9 |
| Auth & config (env + .env, abilities documented) | 1 (README/.env.example), 2 |
| Deployment polling / `finished` ≠ healthy | 6, 12 |
| Error mapping (401/409/422/429) | 3 (HINTS), 5 (429 retry) |
| App-create variants / db engines | 7 (tables), 9 (routing) |
| Bulk env + `--target` | 7 (parse), 9 (dispatch) |
| Pagination (deployment history) | 8 (history endpoint) |
| Testing via `--self-test` (offline, fixtures) | 10 |
| Offline degradation | 1 (README), 10 (self-test runs without creds) |
| `coolify` / `coolify-deploy` / `coolify-audit` skills | 11 / 12 / 13 |
| Bilingual EN/ES | 11–13 (triggers), 1 (pack.json `es`) |
| Root README entry | 14 |

No gaps.

**2. Placeholder scan** — no `TBD`/`TODO`/"add error handling"/"write tests for the above"; every code step contains complete code, every test step complete test code. Pass.

**3. Type consistency** — `CoolifyClient.request(method, path, body=None, *, destructive, confirm, resource_name)` used identically in Tasks 3/4/9; `DryRun(method, path, body)` + `.to_dict()` consistent (Tasks 4/10); `classify_status`/`wait_for_deployment` signatures match (Tasks 6/9/12); routing tables `LIST_PATHS`/`ITEM_PREFIX`/`APP_CREATE`/`DB_ENGINES`/`ENV_BASE` defined in Task 7 and consumed unchanged in 8/9; `build_parser`/`dispatch`/`format_output`/`run_self_test`/`main` consistent across 8/9/10. `_find_sub` defined in Task 8 and reused in Task 9. Pass.

> Implementation note for the executor: Tasks build one growing file. When a task says "append" or "replace the opening of `request`", apply it to the in-progress `coolify.py` — do not duplicate already-present blocks. After each task, `python -m unittest -v` (that task's class) must be green before committing.
