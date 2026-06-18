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
