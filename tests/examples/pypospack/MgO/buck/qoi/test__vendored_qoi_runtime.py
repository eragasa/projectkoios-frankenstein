from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

from tests.support.repository_root import REPOSITORY_ROOT

EXAMPLE_ROOT = REPOSITORY_ROOT / "examples/pypospack/MgO/buck"


class VendoredQoiRuntimeTest(unittest.TestCase):
    def test_plans_all_historical_mgo_qois_from_the_vendored_runtime(self) -> None:
        program = """
from collections import OrderedDict
from pathlib import Path
import json
import sys

root = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(root / "vendor"))
sys.path.insert(0, str(root))

from configuration import MgOBuckinghamConfiguration
import pypospack.qoi as qoi_runtime

scientific = MgOBuckinghamConfiguration.from_legacy_file(
    root / "data/pyposmat.config.in"
)
qoi_database = OrderedDict()
for qoi in scientific.qois:
    qoi_database[qoi.name] = OrderedDict(
        qoi_type=qoi.qoi_type,
        structures=OrderedDict(qoi.structures),
        target=qoi.target,
    )
manager = qoi_runtime.QoiManager(qoi_database)
print(json.dumps({
    "runtime": Path(qoi_runtime.__file__).resolve().as_posix(),
    "qois": len(manager.qois),
    "tasks": len(manager.tasks),
    "resolved": [value["qoi_name"] for value in manager.qois.values()],
}))
"""
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            (sys.executable, "-c", program, str(EXAMPLE_ROOT)),
            check=True,
            capture_output=True,
            text=True,
            cwd=REPOSITORY_ROOT,
            env=environment,
        )

        result = json.loads(completed.stdout)
        vendor_root = (EXAMPLE_ROOT / "vendor").resolve()
        self.assertTrue(Path(result["runtime"]).is_relative_to(vendor_root))
        self.assertEqual(result["qois"], 10)
        self.assertEqual(result["tasks"], 6)
        self.assertEqual(len(result["resolved"]), 10)
        self.assertTrue(all(result["resolved"]))


if __name__ == "__main__":
    unittest.main()
