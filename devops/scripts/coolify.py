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


def load_config(start: Path | None = None):
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


class DryRun:
    def __init__(self, method, path, body):
        self.method, self.path, self.body = method, path, body

    def __str__(self):
        b = f" body={json.dumps(self.body)}" if self.body is not None else ""
        return f"WOULD {self.method} {self.path}{b}  (re-run with --apply to perform)"

    def to_dict(self):
        return {"dry_run": True, "method": self.method, "path": self.path, "body": self.body}


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
