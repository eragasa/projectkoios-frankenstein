from __future__ import annotations

import hashlib
import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

from tools.revalidate_source_reference import build_report

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _git(repository: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ("git", "-C", str(repository), *arguments),
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


class SourceRevalidationToolTest(unittest.TestCase):
    def test_build_report_matches_a_declared_identity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository_root = root / "frankenstein"
            checkout = root / "upstream"
            (repository_root / "sources").mkdir(parents=True)
            checkout.mkdir()

            _git(checkout, "init", "--quiet")
            _git(checkout, "config", "user.name", "Test User")
            _git(checkout, "config", "user.email", "test@example.invalid")
            _git(
                checkout,
                "remote",
                "add",
                "origin",
                "git@github.com:example/upstream.git",
            )
            license_payload = b"test license\n"
            source_payload = b"observed source\n"
            (checkout / "LICENSE").write_bytes(license_payload)
            (checkout / "selected.txt").write_bytes(source_payload)
            _git(checkout, "add", "LICENSE", "selected.txt")
            _git(checkout, "commit", "--quiet", "-m", "fixture")
            revision = _git(checkout, "rev-parse", "HEAD")
            tree = _git(checkout, "rev-parse", "HEAD^{tree}")

            license_sha256 = hashlib.sha256(license_payload).hexdigest()
            source_sha256 = hashlib.sha256(source_payload).hexdigest()
            (repository_root / "sources/demo.toml").write_text(
                textwrap.dedent(
                    f'''\
                    schema_version = 1
                    component = "demo"
                    repository = "https://github.com/example/upstream"
                    revision = "{revision}"
                    tree = "{tree}"
                    license_path = "LICENSE"
                    license_sha256 = "{license_sha256}"

                    [selection]
                    source_path = "selected.txt"
                    source_sha256 = "{source_sha256}"
                    source_byte_size = {len(source_payload)}
                    '''
                ),
                encoding="utf-8",
            )

            report = build_report(repository_root, "demo", checkout)

            self.assertTrue(report["matches_declaration"])
            self.assertEqual(report["disposition"], "declared_identity_matches")
            self.assertFalse(report["pin_change_authorized"])

            (checkout / "selected.txt").write_text("changed source\n", encoding="utf-8")
            _git(checkout, "add", "selected.txt")
            _git(checkout, "commit", "--quiet", "-m", "candidate")
            candidate_revision = _git(checkout, "rev-parse", "HEAD")

            candidate = build_report(
                repository_root,
                "demo",
                checkout,
                requested_revision=candidate_revision,
            )

            self.assertFalse(candidate["matches_declaration"])
            self.assertEqual(
                candidate["disposition"],
                "candidate_identity_differs_not_accepted",
            )
            self.assertFalse(
                candidate["selected_files"][0]["matches_declared_identity"]
            )
            self.assertFalse(candidate["pin_change_authorized"])

    def test_current_pyflamestk_declaration_revalidates(self) -> None:
        checkout_value = os.environ.get("PYFLAMESTK_CHECKOUT")
        if checkout_value is None:
            fallback = REPOSITORY_ROOT / ".upstreams" / "pyflamestk"
            if not fallback.is_dir():
                self.skipTest("no explicit PyFlamestk conformance checkout")
            checkout = fallback
        else:
            checkout = Path(checkout_value)

        report = build_report(REPOSITORY_ROOT, "pyflamestk", checkout)

        self.assertTrue(report["matches_declaration"])
        self.assertEqual(len(report["selected_files"]), 32)


if __name__ == "__main__":
    unittest.main()
