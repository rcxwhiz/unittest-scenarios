# Josh Bedwell © 2025

import os
import shutil
import tempfile
import unittest
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Literal


class IsolatedWorkingDirMixin:
    """
    Mixin class for unittest.TestCase that makes each test occur in an isolated working
    directory. Includes options for linking or copying external files.

    Attributes:
        temp_dir_opts: kwargs that will be passed to tempfile.TemporaryDirectory() call
        external_connections: list of paths to link or copy
    """

    @dataclass
    class ExternalConnection:
        """
        An external connection to an isolated test - will be connected once per test.

        Custom callable connection strategies will receive the absolute source and
        relative destination paths.

        Attributes:
            external_path: absolute or relative string path to item to connect
            internal_path: relative destination path, keeps original name when None
            strategy: default symlink, copy also available, supports custom callables
        """

        external_path: str
        internal_path: str | None = None
        strategy: Literal["symlink", "copy"] | Callable[[str, str], None] = "symlink"

    temp_dir_opts: dict[str, Any] | None = None
    external_connections: list[ExternalConnection] | None = None

    def __new__(cls, *args, **kwargs):
        if not issubclass(cls, unittest.TestCase):
            raise TypeError(f"{cls.__name__} must be a subclass of unittest.TestCase")
        return super().__new__(cls)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._test_temp_dir: tempfile.TemporaryDirectory | None = None
        self._original_working_dir: str | None = None

    def setUp(self):
        super().setUp()

        # create temp dir and switch to it
        temp_dir_opts = self.temp_dir_opts or {}
        self._test_temp_dir = tempfile.TemporaryDirectory(**temp_dir_opts)
        self._original_working_dir = os.getcwd()
        try:
            os.chdir(self.test_dir)
        except Exception as e:
            self._test_temp_dir.cleanup()
            raise RuntimeError("Failed to change to temporary directory") from e
        self.addCleanup(self._cleanup_temp_dir)

        # apply external connections
        if self.external_connections:
            for connection in self.external_connections:
                # if external path is relative, join with original working directory
                external_path = connection.external_path
                if not os.path.isabs(external_path):
                    external_path = os.path.join(
                        self.original_working_dir, external_path
                    )
                if not os.path.exists(external_path):
                    raise FileNotFoundError(
                        f"Could not connect {external_path} to test, does not exist"
                    )
                # if internal path is none, use the basename of the external path
                internal_path = connection.internal_path
                if internal_path is None:
                    internal_path = os.path.basename(external_path)
                if isinstance(connection.strategy, Callable):
                    connection.strategy(external_path, internal_path)
                elif connection.strategy == "symlink":
                    os.symlink(external_path, internal_path)
                elif connection.strategy == "copy":
                    if os.path.isdir(external_path):
                        shutil.copytree(external_path, internal_path)
                    else:
                        shutil.copy(external_path, internal_path)
                else:
                    raise TypeError(
                        f"Unrecognized connection strategy: {connection.strategy}"
                    )

    def _cleanup_temp_dir(self):
        try:
            os.chdir(self.original_working_dir)
        except Exception as e:
            raise RuntimeError("Failed to restore original working directory") from e
        finally:
            self._test_temp_dir.cleanup()
            self._test_temp_dir = None
            self._original_working_dir = None

    @property
    def test_dir(self) -> str | None:
        """Absolute path to the test directory."""

        if self._test_temp_dir is None:
            return None
        return self._test_temp_dir.name

    @property
    def original_working_dir(self) -> str | None:
        """Absolute path to the original working directory."""

        return self._original_working_dir
