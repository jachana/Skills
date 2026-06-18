import io, os, sys, unittest
from pathlib import Path
from unittest import mock

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

    def test_warns_when_base_missing_api_v1(self):
        os.environ["COOLIFY_BASE_URL"] = "https://ex.test"
        os.environ["COOLIFY_API_TOKEN"] = "1|s"
        with mock.patch("sys.stderr", new_callable=io.StringIO) as err:
            base, token = coolify.load_config(start=Path(self.id()))
        self.assertEqual(base, "https://ex.test")
        self.assertIn("/api/v1", err.getvalue())


if __name__ == "__main__":
    unittest.main()
