import os
import tempfile
import unittest


class IsolatedWorkingDirMixin:
    temp_dir_suffix = None
    temp_dir_prefix = None
    temp_dir_location = None

    def __new__(cls, *args, **kwargs):
        if not issubclass(cls, unittest.TestCase):
            raise TypeError(f"{cls.__name__} must be a subclass of unittest.TestCase")
        return super().__new__(cls)

    def __init__(self):
        self._test_temp_dir: tempfile.TemporaryDirectory | None = None
        self._original_working_dir: str | None = None

    def setUp(self):
        super().setUp()
        self._test_temp_dir = tempfile.TemporaryDirectory(suffix=self.temp_dir_suffix, prefix=self.temp_dir_prefix, dir=self.temp_dir_location)
        self._original_working_dir = os.getcwd()
        try:
            os.chdir(self._test_temp_dir.name)
        except Exception as e:
            self._test_temp_dir.cleanup()
            raise RuntimeError(f"Failed to change to temporary directory: {e}")
        self.addCleanup(self.cleanup_temp_dir)

    def cleanup_temp_dir(self):
        try:
            os.chdir(self._original_working_dir)
        except Exception as e:
            raise RuntimeError(f"Failed to restore original working directory: {e}")
        finally:
            self._test_temp_dir.cleanup()
            self._test_temp_dir = None
            self._original_working_dir = None

    @property
    def test_dir(self) -> str | None:
        if self._test_temp_dir is None:
            return None
        return self._test_temp_dir.name

    @property
    def original_working_dir(self) -> str | None:
        return self._original_working_dir
