from __future__ import annotations

import os
import stat
from pathlib import Path, PurePosixPath

_MAXIMUM_READ_BYTES = 64 * 1024 * 1024
_MAXIMUM_FILE_COUNT = 10_000
_READ_CHUNK_BYTES = 1024 * 1024


def read_bounded_regular_file(
    root: Path,
    relative_path: str,
    *,
    maximum_bytes: int,
    label: str,
) -> bytes:
    """Read one root-relative regular file through a pinned descriptor chain."""
    _require_secure_descriptor_support()
    parts = _relative_parts(relative_path, "relative_path")
    _validate_bound(maximum_bytes, _MAXIMUM_READ_BYTES, "maximum_bytes")
    _validate_label(label)
    descriptors: list[int] = []
    try:
        root_descriptor = _open_root(root, label)
        descriptors.append(root_descriptor)
        directory_descriptor = root_descriptor
        for part in parts[:-1]:
            directory_descriptor = _open_child_directory(
                directory_descriptor,
                part,
                label,
            )
            descriptors.append(directory_descriptor)
        file_descriptor = _open_child_file(
            directory_descriptor,
            parts[-1],
            label,
        )
        descriptors.append(file_descriptor)
        before = os.fstat(file_descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise ValueError(f"{label} must be a regular file")
        if before.st_size < 0 or before.st_size > maximum_bytes:
            raise ValueError(f"{label} exceeds its byte bound")

        chunks: list[bytes] = []
        size = 0
        while chunk := os.read(file_descriptor, _READ_CHUNK_BYTES):
            size += len(chunk)
            if size > maximum_bytes:
                raise ValueError(f"{label} exceeds its byte bound")
            chunks.append(chunk)
        after = os.fstat(file_descriptor)
        if _identity(before) != _identity(after) or size != before.st_size:
            raise ValueError(f"{label} changed during read")
        return b"".join(chunks)
    except OSError as error:
        raise ValueError(f"{label} is not a safely readable regular file") from error
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def list_regular_files(
    root: Path,
    relative_directory: str,
    *,
    maximum_files: int,
    label: str,
) -> tuple[str, ...]:
    """List a root-relative tree without following symbolic links."""
    _require_secure_descriptor_support()
    parts = _relative_parts(relative_directory, "relative_directory")
    _validate_bound(maximum_files, _MAXIMUM_FILE_COUNT, "maximum_files")
    _validate_label(label)
    descriptors: list[int] = []
    try:
        root_descriptor = _open_root(root, label)
        descriptors.append(root_descriptor)
        directory_descriptor = root_descriptor
        for part in parts:
            directory_descriptor = _open_child_directory(
                directory_descriptor,
                part,
                label,
            )
            descriptors.append(directory_descriptor)
        files: list[str] = []
        _walk_regular_files(
            directory_descriptor,
            prefix=(),
            files=files,
            maximum_files=maximum_files,
            label=label,
        )
        return tuple(files)
    except OSError as error:
        raise ValueError(f"{label} is not a safely readable directory") from error
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def _walk_regular_files(
    directory_descriptor: int,
    *,
    prefix: tuple[str, ...],
    files: list[str],
    maximum_files: int,
    label: str,
) -> None:
    before = os.fstat(directory_descriptor)
    if not stat.S_ISDIR(before.st_mode):
        raise ValueError(f"{label} contains a non-directory path")
    with os.scandir(directory_descriptor) as entries:
        ordered = sorted(
            (
                (
                    entry.name,
                    entry.is_symlink(),
                    entry.is_dir(follow_symlinks=False),
                    entry.is_file(follow_symlinks=False),
                )
                for entry in entries
            ),
            key=lambda item: item[0],
        )
    for name, is_symlink, is_directory, is_file in ordered:
        relative_parts = (*prefix, name)
        relative_path = PurePosixPath(*relative_parts).as_posix()
        if is_symlink:
            raise ValueError(f"{label} contains a symbolic link: {relative_path}")
        if is_directory:
            child_descriptor = _open_child_directory(
                directory_descriptor,
                name,
                label,
            )
            try:
                _walk_regular_files(
                    child_descriptor,
                    prefix=relative_parts,
                    files=files,
                    maximum_files=maximum_files,
                    label=label,
                )
            finally:
                os.close(child_descriptor)
        elif is_file:
            files.append(relative_path)
            if len(files) > maximum_files:
                raise ValueError(f"{label} exceeds its file-count bound")
        else:
            raise ValueError(f"{label} contains a non-regular path: {relative_path}")
    after = os.fstat(directory_descriptor)
    if _identity(before) != _identity(after):
        raise ValueError(f"{label} changed during directory inspection")


def _open_root(root: Path, label: str) -> int:
    descriptor = os.open(root, _directory_flags())
    try:
        status = os.fstat(descriptor)
        if not stat.S_ISDIR(status.st_mode):
            raise ValueError(f"{label} root must be a directory")
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def _open_child_directory(parent: int, name: str, label: str) -> int:
    descriptor = os.open(name, _directory_flags(), dir_fd=parent)
    try:
        status = os.fstat(descriptor)
        if not stat.S_ISDIR(status.st_mode):
            raise ValueError(f"{label} contains a non-directory path")
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def _open_child_file(parent: int, name: str, label: str) -> int:
    return os.open(name, _file_flags(), dir_fd=parent)


def _directory_flags() -> int:
    return os.O_RDONLY | os.O_CLOEXEC | os.O_DIRECTORY | os.O_NOFOLLOW


def _file_flags() -> int:
    return os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK


def _require_secure_descriptor_support() -> None:
    required_flags = ("O_CLOEXEC", "O_DIRECTORY", "O_NOFOLLOW", "O_NONBLOCK")
    if (
        any(not hasattr(os, name) for name in required_flags)
        or os.open not in os.supports_dir_fd
        or os.scandir not in os.supports_fd
    ):
        raise RuntimeError("secure descriptor-based evidence reads are unsupported")


def _identity(status: os.stat_result) -> tuple[int, int, int, int, int, int]:
    return (
        status.st_dev,
        status.st_ino,
        status.st_mode,
        status.st_size,
        status.st_mtime_ns,
        status.st_ctime_ns,
    )


def _relative_parts(value: str, field_name: str) -> tuple[str, ...]:
    path = PurePosixPath(value)
    if (
        not value
        or value == "."
        or value != path.as_posix()
        or path.is_absolute()
        or "." in path.parts
        or ".." in path.parts
    ):
        raise ValueError(f"{field_name} must be a normalized relative path")
    return path.parts


def _validate_bound(value: int, upper_bound: int, field_name: str) -> None:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or not 0 < value <= upper_bound
    ):
        raise ValueError(f"{field_name} is outside its supported bound")


def _validate_label(label: str) -> None:
    if not label or len(label) > 256:
        raise ValueError("evidence label is invalid")


__all__ = ["list_regular_files", "read_bounded_regular_file"]
