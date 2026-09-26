from __future__ import annotations

import hashlib
import os
import subprocess
import tempfile
import textwrap
import tomllib
import unittest
from dataclasses import replace
from pathlib import Path

from tests.support.repository_root import REPOSITORY_ROOT
from tools.base import DataObjectActionizer
from tools.sources.revalidation import (
    RevalidationDisposition,
    RevalidationError,
    SourceReferenceRevalidationReportSerializer,
    SourceReferenceRevalidationRequest,
    SourceReferenceRevalidationResponse,
    SourceReferenceRevalidator,
)


def _git(repository: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ("git", "-C", str(repository), *arguments),
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


class SourceRevalidationToolTest(unittest.TestCase):
    def test_request_rejects_a_component_path(self) -> None:
        with self.assertRaisesRegex(RevalidationError, "file-name stem"):
            SourceReferenceRevalidationRequest(
                repository_root=REPOSITORY_ROOT,
                component="../outside",
                checkout=REPOSITORY_ROOT,
            )

    def test_actionizes_and_serializes_a_declared_identity(self) -> None:
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
            (checkout / "example").mkdir()
            (checkout / "example/entrypoint.py").write_text(
                "# historical example\n",
                encoding="utf-8",
            )
            _git(checkout, "add", "LICENSE", "selected.txt", "example")
            _git(checkout, "commit", "--quiet", "-m", "fixture")
            revision = _git(checkout, "rev-parse", "HEAD")
            tree = _git(checkout, "rev-parse", "HEAD^{tree}")
            example_tree = _git(checkout, "rev-parse", "HEAD:example")

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

                    [selection.example_trees]
                    "example" = "{example_tree}"
                    '''
                ),
                encoding="utf-8",
            )

            request = SourceReferenceRevalidationRequest(
                repository_root=repository_root,
                component="demo",
                checkout=checkout,
            )
            actionizer: DataObjectActionizer[
                SourceReferenceRevalidationRequest,
                SourceReferenceRevalidationResponse,
            ] = SourceReferenceRevalidator()
            response = actionizer.actionize(request)
            report_model = SourceReferenceRevalidationReportSerializer().serialize(
                response
            )

            self.assertIs(response.request, request)
            self.assertEqual(
                response.disposition,
                RevalidationDisposition.DECLARED_IDENTITY_MATCHES,
            )
            with self.assertRaisesRegex(RevalidationError, "cannot authorize"):
                replace(response, pin_change_authorized=True)
            self.assertTrue(report_model.matches_declaration)
            self.assertEqual(
                report_model.disposition,
                RevalidationDisposition.DECLARED_IDENTITY_MATCHES,
            )
            self.assertFalse(report_model.pin_change_authorized)
            self.assertEqual(len(report_model.example_trees), 1)
            self.assertEqual(report_model.example_trees[0].path, "example")
            self.assertEqual(report_model.example_trees[0].declared, example_tree)
            self.assertEqual(report_model.example_trees[0].observed, example_tree)
            self.assertTrue(report_model.example_trees[0].matches)

            (checkout / "selected.txt").write_text("changed source\n", encoding="utf-8")
            _git(checkout, "add", "selected.txt")
            _git(checkout, "commit", "--quiet", "-m", "candidate")
            candidate_revision = _git(checkout, "rev-parse", "HEAD")

            candidate_request = SourceReferenceRevalidationRequest(
                repository_root=repository_root,
                component="demo",
                checkout=checkout,
                requested_revision=candidate_revision,
            )
            candidate = SourceReferenceRevalidator().actionize(candidate_request)

            self.assertFalse(candidate.matches_declaration)
            self.assertEqual(
                candidate.disposition,
                RevalidationDisposition.CANDIDATE_IDENTITY_DIFFERS_NOT_ACCEPTED,
            )
            self.assertFalse(candidate.selected_files[0].matches_declared_identity)
            self.assertFalse(candidate.pin_change_authorized)

    def test_current_pypospack_declaration_revalidates(self) -> None:
        checkout_value = os.environ.get("PYPOSPACK_CHECKOUT")
        if checkout_value is None:
            fallback = REPOSITORY_ROOT / ".upstreams" / "pypospack"
            if not fallback.is_dir():
                self.skipTest("no explicit PyPosPack conformance checkout")
            checkout = fallback
        else:
            checkout = Path(checkout_value)

        request = SourceReferenceRevalidationRequest(
            repository_root=REPOSITORY_ROOT,
            component="pypospack",
            checkout=checkout,
        )
        result = SourceReferenceRevalidator().actionize(request)

        declaration = tomllib.loads(
            (REPOSITORY_ROOT / "sources/pypospack.toml").read_text(encoding="utf-8")
        )
        selection = declaration["selection"]
        expected_selected_file_count = 1 + len(selection["additional_files"])

        self.assertTrue(result.matches_declaration)
        self.assertEqual(
            len(result.selected_files),
            expected_selected_file_count,
        )
        self.assertEqual(len(result.example_trees), 31)
        self.assertTrue(all(item.matches for item in result.example_trees))

    def test_current_pyflamestk_declaration_revalidates(self) -> None:
        checkout_value = os.environ.get("PYFLAMESTK_CHECKOUT")
        if checkout_value is None:
            fallback = REPOSITORY_ROOT / ".upstreams" / "pyflamestk"
            if not fallback.is_dir():
                self.skipTest("no explicit PyFlamestk conformance checkout")
            checkout = fallback
        else:
            checkout = Path(checkout_value)

        request = SourceReferenceRevalidationRequest(
            repository_root=REPOSITORY_ROOT,
            component="pyflamestk",
            checkout=checkout,
        )
        result = SourceReferenceRevalidator().actionize(request)

        self.assertTrue(result.matches_declaration)
        self.assertEqual(len(result.selected_files), 32)
        self.assertEqual(len(result.example_trees), 17)
        self.assertTrue(all(item.matches for item in result.example_trees))


if __name__ == "__main__":
    unittest.main()
