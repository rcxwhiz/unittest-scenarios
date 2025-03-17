# Josh Bedwell © 2025

import hashlib
import itertools
import os
import unittest
from collections.abc import Callable
from os import PathLike
from pathlib import Path

from unittest_scenarios.utils.archive import is_archive, temp_archive_extract


class FileCmpMixin:

    def __new__(cls, *args, **kwargs):
        if not issubclass(cls, unittest.TestCase):
            raise TypeError(f"{cls.__name__} must be a subclass of unittest.TestCase")
        return super().__new__(cls)

    def assertDirectoryContentsEqual(self, expected_dir: str | PathLike[str], actual_dir: str | PathLike[str]) -> None:
        if not isinstance(expected_dir, Path):
            expected_dir = Path(expected_dir)
        if not isinstance(actual_dir, Path):
            actual_dir = Path(actual_dir)
        self.assertTrue(expected_dir.is_dir(), f"{expected_dir} is not a directory")
        self.assertTrue(actual_dir.is_dir(), f"{actual_dir} is not a directory")

        expected_items = {item.name for item in expected_dir.iterdir()}
        actual_items = {item.name for item in actual_dir.iterdir()}
        self.assertSetEqual(expected_items, actual_items)

        for item in expected_items:
            self.assertPathContentsEqual(os.path.join(expected_dir, item), os.path.join(actual_dir, item))

    def assertArchiveContentsEqual(self, expected_arc: str | PathLike[str], actual_arc: str | PathLike[str]) -> None:
        with temp_archive_extract(expected_arc) as expected_extracted, temp_archive_extract(actual_arc) as actual_extracted:
            self.assertDirectoryContentsEqual(expected_extracted, actual_extracted)

    def assertTextFilesEqual(self, expected_file: str | PathLike[str], actual_file: str | PathLike[str]) -> None:
        with open(expected_file, "r", newline=None) as f_expected, open(actual_file, "r", newline=None) as f_actual:
            for i, (line_expected, line_actual) in enumerate(itertools.zip_longest(f_expected, f_actual, fillvalue=None)):
                self.assertIsNotNone(line_actual, f"{actual_file} ends on line {i + 1}, expected to continue")
                self.assertIsNotNone(line_expected, f"{actual_file} continues past line {i}, expected to end")
                self.assertEqual(line_expected, line_actual, f"{actual_file} does not match {expected_file} on line {i + 1}")

    def assertFileHashesEqual(self, expected_file: str | PathLike[str], actual_file: str | PathLike[str], hash_func: Callable[[bytes], str] = lambda x: hashlib.sha256(x).hexdigest()) -> None:
        with open(expected_file, "rb") as f:
            expected_hash = hash_func(f.read())
        with open(actual_file, "rb") as f:
            actual_hash = hash_func(f.read())
        self.assertEqual(expected_hash, actual_hash, f"Hash of {actual_file} does not match {expected_file}")

    def assertPathContentsEqual(self, expected_path: str | PathLike[str], actual_path: str | PathLike[str]) -> None:
        self.assertTrue(os.path.exists(expected_path), f"{expected_path} does not exist")
        self.assertTrue(os.path.exists(actual_path), f"{actual_path} does not exist")

        if os.path.isdir(expected_path):
            self.assertDirectoryContentsEqual(expected_path, actual_path)

        elif is_archive(expected_path):
            self.assertArchiveContentsEqual(expected_path, actual_path)

        elif self._is_text_file(expected_path):
            self.assertTextFilesEqual(expected_path, actual_path)

        else:
            self.assertFileHashesEqual(expected_path, actual_path)

    def _is_text_file(self, file: str | PathLike[str]) -> bool:
        try:
            with open(file, "r") as f:
                _ = f.read(1)
        except UnicodeDecodeError:
            return False
        return True
