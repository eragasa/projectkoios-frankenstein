from __future__ import annotations

import tomllib
import unittest

from tests.support.repository_root import REPOSITORY_ROOT


class RuntimeDependenciesTest(unittest.TestCase):
    def test_pypospack_dependency_is_bound_to_the_declared_revision(self) -> None:
        project = tomllib.loads(
            REPOSITORY_ROOT.joinpath("pyproject.toml").read_text(encoding="utf-8")
        )
        source = tomllib.loads(
            REPOSITORY_ROOT.joinpath("sources/pypospack.toml").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(
            project["project"]["dependencies"],
            [
                "mpi4py>=4.1,<5",
                "numpy>=2.3,<3",
                (
                    f"pypospack[all] @ git+{source['repository']}.git@"
                    f"{source['revision']}"
                ),
            ],
        )


if __name__ == "__main__":
    unittest.main()
