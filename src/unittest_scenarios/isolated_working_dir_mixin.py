import os
import tempfile
import unittest


class IsolatedWorkingDirMixin:

    def __new__(cls, *args, **kwargs):
        if not issubclass(cls, unittest.TestCase):
            raise TypeError(f"{cls.__name__} must be a subclass of unittest.TestCase")
        return super().__new__(cls)

    def setUp(self):
        super().setUp()
        self.test_temp_dir = tempfile.TemporaryDirectory()
        self.test_path = self.test_temp_dir.name
        self.original_working_dir = os.getcwd()
        try:
            os.chdir(self.test_path)
        except Exception as e:
            self.test_temp_dir.cleanup()
            raise RuntimeError(f"Failed to change to temporary directory: {e}")
        self.addCleanup(self.cleanup_temp_dir)

    def cleanup_temp_dir(self):
        try:
            os.chdir(self.original_working_dir)
        except Exception as e:
            raise RuntimeError(f"Failed to restore original working directory: {e}")
        finally:
            self.test_temp_dir.cleanup()
