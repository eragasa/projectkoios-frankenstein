from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from projectkoios.frankensteins.evidence import read_bounded_regular_file

PYPOSPACK_COMPONENT = "pypospack"
# TODO: Update the PyPosPack pin only after revalidating its selected contracts.
PYPOSPACK_REPOSITORY_URL = "https://github.com/eragasa/pypospack"
PYPOSPACK_REVISION = "21cdecaf3b05c87acc532d992be2c04d85bfbc22"
PYPOSPACK_TREE = "a5a4cee972e487512275c34f308251e6cc38c2fa"
PYPOSPACK_LAMMPS_PATH = "pypospack/io/lammps.py"
PYPOSPACK_LAMMPS_SHA256 = (
    "28f54c2ce369feb5e8ba228d13edde6595c77fc9ab3bbbb31e452087a5dd8607"
)
PYPOSPACK_LAMMPS_BYTE_SIZE = 3_030
PYPOSPACK_LICENSE_PATH = "LICENSE"
PYPOSPACK_LICENSE_SHA256 = (
    "05f25c4caf59b20bbcadbb1e3e1c33b154d273ef7daa7e7740bca8a0ed0f4c83"
)
PYPOSPACK_LAMMPS_LIMITATIONS = (
    "The referenced write_lammps_structure_file function is syntactically "
    "invalid and has no implemented serialization body.",
    "The referenced LammpsStructure.write method assigns a dummy charge of "
    "1.0 instead of accepting per-atom charges.",
    "The referenced position transformation ignores off-diagonal lattice "
    "terms even though tilt factors are emitted.",
)
_MAX_SOURCE_BYTES = 1_000_000


@dataclass(frozen=True)
class PypospackLammpsProvenance:
    component: str
    repository_url: str
    revision: str
    tree: str
    source_path: str
    source_sha256: str
    source_byte_size: int
    license_path: str
    license_sha256: str
    source_limitations: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.component != PYPOSPACK_COMPONENT:
            raise ValueError("LAMMPS provenance component is invalid")
        if self.repository_url != PYPOSPACK_REPOSITORY_URL:
            raise ValueError("LAMMPS provenance repository is invalid")
        if self.revision != PYPOSPACK_REVISION or self.tree != PYPOSPACK_TREE:
            raise ValueError("LAMMPS provenance Git identity is invalid")
        if self.source_path != PYPOSPACK_LAMMPS_PATH:
            raise ValueError("LAMMPS provenance source path is invalid")
        if self.source_sha256 != PYPOSPACK_LAMMPS_SHA256:
            raise ValueError("LAMMPS provenance source hash is invalid")
        if self.source_byte_size != PYPOSPACK_LAMMPS_BYTE_SIZE:
            raise ValueError("LAMMPS provenance source size is invalid")
        if self.license_path != PYPOSPACK_LICENSE_PATH:
            raise ValueError("LAMMPS provenance license path is invalid")
        if self.license_sha256 != PYPOSPACK_LICENSE_SHA256:
            raise ValueError("LAMMPS provenance license hash is invalid")
        if self.source_limitations != PYPOSPACK_LAMMPS_LIMITATIONS:
            raise ValueError("LAMMPS provenance limitations are invalid")

    def to_dict(self) -> dict[str, object]:
        return {
            "component": self.component,
            "repository_url": self.repository_url,
            "revision": self.revision,
            "tree": self.tree,
            "source_path": self.source_path,
            "source_sha256": self.source_sha256,
            "source_byte_size": self.source_byte_size,
            "license_path": self.license_path,
            "license_sha256": self.license_sha256,
            "source_limitations": list(self.source_limitations),
        }


def verify_pypospack_lammps_checkout(
    checkout_root: Path,
) -> PypospackLammpsProvenance:
    """Verify selected files in an explicit checkout without fetching it."""
    source_payload = read_bounded_regular_file(
        checkout_root,
        PYPOSPACK_LAMMPS_PATH,
        maximum_bytes=_MAX_SOURCE_BYTES,
        label="PyPosPack LAMMPS source",
    )
    license_payload = read_bounded_regular_file(
        checkout_root,
        PYPOSPACK_LICENSE_PATH,
        maximum_bytes=_MAX_SOURCE_BYTES,
        label="PyPosPack license",
    )
    source_sha256 = hashlib.sha256(source_payload).hexdigest()
    if (
        source_sha256 != PYPOSPACK_LAMMPS_SHA256
        or len(source_payload) != PYPOSPACK_LAMMPS_BYTE_SIZE
    ):
        raise ValueError("pypospack/io/lammps.py does not match the bound source")
    license_sha256 = hashlib.sha256(license_payload).hexdigest()
    if license_sha256 != PYPOSPACK_LICENSE_SHA256:
        raise ValueError("PyPosPack license does not match the bound source")

    return PypospackLammpsProvenance(
        component=PYPOSPACK_COMPONENT,
        repository_url=PYPOSPACK_REPOSITORY_URL,
        revision=PYPOSPACK_REVISION,
        tree=PYPOSPACK_TREE,
        source_path=PYPOSPACK_LAMMPS_PATH,
        source_sha256=source_sha256,
        source_byte_size=len(source_payload),
        license_path=PYPOSPACK_LICENSE_PATH,
        license_sha256=license_sha256,
        source_limitations=PYPOSPACK_LAMMPS_LIMITATIONS,
    )
