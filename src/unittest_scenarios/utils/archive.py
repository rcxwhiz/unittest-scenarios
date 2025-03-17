# Josh Bedwell © 2025

import contextlib
import tarfile
import tempfile
import zipfile
from os import PathLike
from pathlib import Path


def is_archive(filename: str | PathLike[str]) -> bool:
    if not isinstance(filename, Path):
        filename = Path(filename)
    return filename.suffix in (".tar", ".gz", ".tgz", ".bz2", ".tbz2", ".xz", ".txz")


@contextlib.contextmanager
def temp_archive_extract(archive_path: str | PathLike[str]):
    if not isinstance(archive_path, Path):
        archive_path = Path(archive_path)
    with tempfile.TemporaryDirectory() as temp_dir:
        if archive_path.suffix == ".zip":
            with zipfile.ZipFile(archive_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)
        elif archive_path.suffix in (".tar", ".gz", ".tgz", ".bz2", "tbz2", ".xz", "txz"):
            with tarfile.open(archive_path, "r:*") as tar_ref:
                tar_ref.extractall(temp_dir)
        else:
            raise ValueError(f"Unsupported archive extension: {archive_path.suffix}")

        yield temp_dir
