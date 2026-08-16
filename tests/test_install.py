from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("profile_scope_installer", ROOT / "install.py")
installer = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(installer)


class InstallerUnitTests(unittest.TestCase):
    def test_patch_normalization_removes_carriage_returns(self):
        with tempfile.TemporaryDirectory() as temp:
            patch = Path(temp) / "sample.patch"
            patch.write_bytes(b"one\r\ntwo\rthree\n")
            self.assertEqual(installer.normalized_patch_bytes(patch), b"one\ntwo\nthree\n")

    def test_explicit_checkout_must_have_expected_hermes_files(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(installer.InstallError):
                installer.resolve_checkout(temp)

    def test_windows_default_candidate_uses_local_app_data(self):
        candidates = installer.candidate_checkouts(
            platform_name="nt",
            home=Path("C:/Users/Example"),
            environment={"LOCALAPPDATA": "C:/Users/Example/AppData/Local"},
        )
        expected = Path("C:/Users/Example/AppData/Local") / "hermes" / "hermes-agent"
        self.assertIn(expected, candidates)

    def test_unix_default_candidate_uses_home(self):
        candidates = installer.candidate_checkouts(
            platform_name="posix", home=Path("/Users/example"), environment={}
        )
        self.assertIn(Path("/Users/example/.hermes/hermes-agent"), candidates)


if __name__ == "__main__":
    unittest.main()
