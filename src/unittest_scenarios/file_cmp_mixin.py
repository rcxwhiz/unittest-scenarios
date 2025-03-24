# Josh Bedwell © 2025

import hashlib
import itertools
import os
import unittest
from collections.abc import Callable
from os import PathLike
from pathlib import Path
from typing import Any

from unittest_scenarios.utils.archive import is_archive, temp_archive_extract


class FileCmpMixin:
    """
    Mixin class for unittest.TestCase with file content comparisons.

    The comparisons are meant to be file *contents*, excluding metadata or any platform
    specific data.
    """

    def __new__(cls, *args, **kwargs):
        if not issubclass(cls, unittest.TestCase):
            raise TypeError(f"{cls.__name__} must be a subclass of unittest.TestCase")
        return super().__new__(cls)

    def assertDirectoryContentsEqual(
        self,
        expected_dir: str | PathLike[str],
        actual_dir: str | PathLike[str],
        a_must_have_all_items: bool = True,
        b_must_have_all_items: bool = True,
    ) -> None:
        """
        Recursively checks that all items are present in both dirs and their contents are equal.

        The parameters allowing one directory to not contain all members of the other is *not* passed recursively.

        :param expected_dir: string or path to first directory
        :param actual_dir: string or path to second directory
        :param a_must_have_all_items: The first directory must have all items in the second to be equal
        :param b_must_have_all_items: The second directory must have all items in the first to be equal
        """

        expected_dir, actual_dir = Path(expected_dir), Path(actual_dir)
        if not expected_dir.is_dir():
            self.fail(f"{expected_dir} is not a directory")
        if not actual_dir.is_dir():
            self.fail(f"{actual_dir} is not a directory")

        expected_items = {item.name for item in expected_dir.iterdir()}
        actual_items = {item.name for item in actual_dir.iterdir()}

        if a_must_have_all_items and not actual_items.issubset(expected_items):
            self.fail(f"{expected_dir} is missing items from {actual_dir}")
        if b_must_have_all_items and not expected_items.issubset(actual_items):
            self.fail(f"{actual_dir} is missing items from {expected_dir}")

        for item in expected_items & actual_items:
            self.assertPathContentsEqual(expected_dir / item, actual_dir / item)

    def assertDirectoryContentsNotEqual(
        self,
        expected_dir: str | PathLike[str],
        actual_dir: str | PathLike[str],
        a_must_have_all_items: bool = True,
        b_must_have_all_items: bool = True,
    ) -> None:
        """
        Negated version of assertDirectoryContentsEqual

        The parameters allowing one directory to not contain all members of the other is *not* passed recursively.

        :param expected_dir: string or path to first directory
        :param actual_dir: string or path to second directory
        :param a_must_have_all_items: The first directory must have all items in the second to be equal
        :param b_must_have_all_items: The second directory must have all items in the first to be equal
        """

        with self.assertRaises(AssertionError, msg="Directory contents equal."):
            self.assertDirectoryContentsEqual(
                expected_dir, actual_dir, a_must_have_all_items, b_must_have_all_items
            )

    def assertArchiveContentsEqual(
        self,
        expected_arc: str | PathLike[str],
        actual_arc: str | PathLike[str],
        a_must_have_all_items: bool = True,
        b_must_have_all_items: bool = True,
    ) -> None:
        """
        Extracts archives and recursively compares their contents. Supports all major
        archive types.

        The parameters allowing one archive to not contain all members of the other is *not* passed recursively.

        :param expected_arc: string or path to first archive
        :param actual_arc: string or path to second archive
        :param a_must_have_all_items: The first directory must have all items in the second to be equal
        :param b_must_have_all_items: The second directory must have all items in the first to be equal
        """

        with (
            temp_archive_extract(expected_arc) as expected_extracted,
            temp_archive_extract(actual_arc) as actual_extracted,
        ):
            self.assertDirectoryContentsEqual(
                expected_extracted,
                actual_extracted,
                a_must_have_all_items,
                b_must_have_all_items,
            )

    def assertArchiveContentsNotEqual(
        self,
        expected_arc: str | PathLike[str],
        actual_arc: str | PathLike[str],
        a_must_have_all_items: bool = True,
        b_must_have_all_items: bool = True,
    ) -> None:
        """
        Negated version of assertArchiveContentsEqual.

        The parameters allowing one archive to not contain all members of the other is *not* passed recursively.

        :param expected_arc: string or path to first archive
        :param actual_arc: string or path to second archive
        :param a_must_have_all_items: The first directory must have all items in the second to be equal
        :param b_must_have_all_items: The second directory must have all items in the first to be equal
        """

        with self.assertRaises(AssertionError, msg="Archive contents equal."):
            self.assertArchiveContentsEqual(
                expected_arc, actual_arc, a_must_have_all_items, b_must_have_all_items
            )

    def assertTextFilesEqual(
        self, expected_file: str | PathLike[str], actual_file: str | PathLike[str]
    ) -> None:
        """
        Checks the contents of text files line by line with universal line endings.

        :param expected_file: string or path to first text file
        :param actual_file: string or path to second text file
        """

        with (
            open(expected_file, newline=None) as f_expected,
            open(actual_file, newline=None) as f_actual,
        ):
            for i, (line_expected, line_actual) in enumerate(
                itertools.zip_longest(f_expected, f_actual, fillvalue=None)
            ):
                if line_actual is None:
                    self.fail(
                        f"{actual_file} ends on line {i + 1}, expected to continue"
                    )
                if line_expected is None:
                    self.fail(f"{actual_file} continues past line {i}, expected to end")
                self.assertEqual(
                    line_expected,
                    line_actual,
                    f"{actual_file} does not match {expected_file} on line {i + 1}",
                )

    def assertTextFilesNotEqual(
        self, expected_file: str | PathLike[str], actual_file: str | PathLike[str]
    ) -> None:
        """
        Negated version of assertTextFilesEqual.

        :param expected_file: string or path to first text file
        :param actual_file: string or path to second text file
        """

        with self.assertRaises(AssertionError, msg="Text files equal."):
            self.assertTextFilesEqual(expected_file, actual_file)

    def assertFileHashesEqual(
        self,
        expected_file: str | PathLike[str],
        actual_file: str | PathLike[str],
        hash_func: Callable[[bytes], Any] = lambda x: hashlib.sha256(x).hexdigest(),
    ) -> None:
        """
        Compares the contents of two files by hash.

        :param expected_file: string or path to first file
        :param actual_file: string or path to second file
        :param hash_func: defaults to sha256
        """

        with open(expected_file, "rb") as f:
            expected_hash = hash_func(f.read())
        with open(actual_file, "rb") as f:
            actual_hash = hash_func(f.read())
        self.assertEqual(
            expected_hash,
            actual_hash,
            f"Hash of {actual_file} does not match {expected_file}",
        )

    def assertFileHashesNotEqual(
        self,
        expected_file: str | PathLike[str],
        actual_file: str | PathLike[str],
        hash_func: Callable[[bytes], Any] = lambda x: hashlib.sha256(x).hexdigest(),
    ) -> None:
        """
        Negated version of assertFileHashesEqual.

        :param expected_file: string or path to first file
        :param actual_file: string or path to second file
        :param hash_func: defaults to sha256
        """

        with self.assertRaises(AssertionError, msg="File hashes equal."):
            self.assertFileHashesEqual(expected_file, actual_file, hash_func=hash_func)

    def assertPathContentsEqual(
        self, expected_path: str | PathLike[str], actual_path: str | PathLike[str]
    ) -> None:
        """
        Recursively compares the contents of two paths, which can be directories or any
        kind of file.

        :param expected_path: first file/dir, used to determine the comparison function
        :param actual_path: second file/dir
        """

        if not os.path.exists(expected_path):
            self.fail(f"{expected_path} does not exist")
        if not os.path.exists(actual_path):
            self.fail(f"{actual_path} does not exist")

        if os.path.isdir(expected_path):
            self.assertDirectoryContentsEqual(expected_path, actual_path)

        elif is_archive(expected_path):
            self.assertArchiveContentsEqual(expected_path, actual_path)

        elif self._is_text_file(expected_path):
            self.assertTextFilesEqual(expected_path, actual_path)

        else:
            self.assertFileHashesEqual(expected_path, actual_path)

    def assertPathContentsNotEqual(
        self, expected_path: str | PathLike[str], actual_path: str | PathLike[str]
    ) -> None:
        """
        Negated version of assertPathContentsEqual.

        :param expected_path: first file/dir, used to determine the comparison function
        :param actual_path: second file/dir
        """

        with self.assertRaises(AssertionError, msg="Path contents equal."):
            self.assertPathContentsEqual(expected_path, actual_path)

    def _is_text_file(self, file: str | PathLike[str]) -> bool:
        try:
            with open(file) as f:
                _ = f.read(1)
        except UnicodeDecodeError:
            return False
        return True
