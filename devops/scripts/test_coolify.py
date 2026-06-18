import io, json, os, sys, unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import coolify  # noqa: E402


class RecordingTransport:
    """Fake transport: returns queued (status, headers, payload) responses and
    records each (method, url, body) call. No network. `payload` is a dict/list
    (JSON-encoded), bytes, or None."""
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def __call__(self, method, url, headers, body):
        self.calls.append((method, url, body))
        status, hdrs, payload = self.responses.pop(0)
        if isinstance(payload, (bytes, type(None))):
            raw = payload or b""
        else:
            raw = json.dumps(payload).encode()
        return status, hdrs, raw


class TestReads(unittest.TestCase):
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

    def test_warns_when_base_missing_api_v1(self):
        os.environ["COOLIFY_BASE_URL"] = "https://ex.test"
        os.environ["COOLIFY_API_TOKEN"] = "1|s"
        with mock.patch("sys.stderr", new_callable=io.StringIO) as err:
            base, token = coolify.load_config(start=Path(self.id()))
        self.assertEqual(base, "https://ex.test")
        self.assertIn("/api/v1", err.getvalue())


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


if __name__ == "__main__":
    unittest.main()
