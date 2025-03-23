# Josh Bedwell © 2025

import os
import shutil
import unittest

from src.unittest_scenarios import IsolatedWorkingDirMixin

from .win_tempfile import NamedTempFile


class TestIsolatedWorkingDirMixin(unittest.TestCase):

    def test_subclass_requirement(self):
        """Test unittest.TestCase subclass requirement"""

        class BadClass(IsolatedWorkingDirMixin):
            pass

        with self.assertRaises(TypeError):
            _ = BadClass()

    def test_working_directory(self):
        """Test that the tests working directory is different and the original is restored post-test"""

        original_working_directory = [os.getcwd()]
        test_working_directory = []

        class TestClass(IsolatedWorkingDirMixin, unittest.TestCase):
            def test_method(self):
                test_working_directory.append(os.getcwd())
                self.assertNotEqual(test_working_directory, original_working_directory)

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_method"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())
        self.assertEqual([os.getcwd()], original_working_directory)

    def test_global_isolation(self):
        """Test that the test working directory is empty"""

        class TestClass(IsolatedWorkingDirMixin, unittest.TestCase):
            def test_method(self):
                self.assertEqual(len(os.listdir()), 0)

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_method"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())

    def test_inner_isolation(self):
        """Test that modifications to the working directory are not preserved between tests"""

        class TestClass(IsolatedWorkingDirMixin, unittest.TestCase):
            def test_method_a(self):
                with open("a.txt", "w") as f:
                    f.write("")
                self.assertTrue(os.path.exists("a.txt"))
                self.assertFalse(os.path.exists("b.txt"))

            def test_method_b(self):
                with open("b.txt", "w") as f:
                    f.write("")
                self.assertTrue(os.path.exists("b.txt"))
                self.assertFalse(os.path.exists("a.txt"))

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_method_a"))
        suite.addTest(TestClass("test_method_b"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())

    def test_cleanup(self):
        """Test that the temporary dir is deleted after the test is complete"""

        test_dir = []

        class TestClass(IsolatedWorkingDirMixin, unittest.TestCase):
            def test_method(self):
                self.assertTrue(os.path.exists(self.test_dir))
                test_dir.append(self.test_dir)

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_method"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())

        self.assertFalse(os.path.exists(test_dir[0]))

    def test_link(self):
        """Test linking external item to the testing dir, showing that files and directories are available as links that can modify the outside"""

        try:
            os.mkdir("a")
            with open(os.path.join("a", "b.txt"), "w") as f:
                f.write("")
            with open("c.txt", "w") as f:
                f.write("")

            class TestClass(IsolatedWorkingDirMixin, unittest.TestCase):
                external_connections = [
                    IsolatedWorkingDirMixin.ExternalConnection(
                        external_path="a", strategy="symlink"
                    ),
                    IsolatedWorkingDirMixin.ExternalConnection(
                        external_path="c.txt", strategy="symlink"
                    ),
                ]

                def test_method(self):
                    self.assertTrue(os.path.exists("a"))
                    self.assertTrue(os.path.exists(os.path.join("a", "b.txt")))
                    self.assertTrue(os.path.exists("c.txt"))

                    self.assertTrue(os.path.islink("a"))
                    self.assertTrue(os.path.islink("c.txt"))

                    with open(os.path.join("a", "d.txt"), "w") as f:
                        f.write("")

            suite = unittest.TestSuite()
            suite.addTest(TestClass("test_method"))
            result = unittest.TextTestRunner().run(suite)
            self.assertTrue(result.wasSuccessful())

            self.assertTrue(os.path.exists(os.path.join("a", "d.txt")))

        finally:
            shutil.rmtree("a")
            os.remove("c.txt")

    def test_copy(self):
        """Test copying external item to the testing dir, showing external versions are not modified"""

        try:
            os.mkdir("a")
            with open(os.path.join("a", "b.txt"), "w") as f:
                f.write("")
            with open("c.txt", "w") as f:
                f.write("")

            class TestClass(IsolatedWorkingDirMixin, unittest.TestCase):
                external_connections = [
                    IsolatedWorkingDirMixin.ExternalConnection(
                        external_path="a", strategy="copy"
                    ),
                    IsolatedWorkingDirMixin.ExternalConnection(
                        external_path="c.txt", strategy="copy"
                    ),
                ]

                def test_method(self):
                    self.assertTrue(os.path.exists("a"))
                    self.assertTrue(os.path.exists(os.path.join("a", "b.txt")))
                    self.assertTrue(os.path.exists("c.txt"))

                    self.assertFalse(os.path.islink("a"))
                    self.assertFalse(os.path.islink("c.txt"))

                    with open(os.path.join("a", "d.txt"), "w") as f:
                        f.write("")

            suite = unittest.TestSuite()
            suite.addTest(TestClass("test_method"))
            result = unittest.TextTestRunner().run(suite)
            self.assertTrue(result.wasSuccessful())

            self.assertFalse(os.path.exists(os.path.join("a", "d.txt")))
        finally:
            shutil.rmtree("a")
            os.remove("c.txt")

    def test_custom_connection(self):
        """Demonstrate a custom outside connection function that changes file contents to uppercase"""

        def connect_upper(src: str, dest: str) -> None:
            with open(src) as f:
                content = f.read()
            with NamedTempFile() as t:
                with open(t.name, "w") as tf:
                    tf.write(content.upper())
                shutil.copy(t.name, dest)

        try:
            with open("a.txt", "w") as f:
                f.write("lowercase message")

            class TestClass(IsolatedWorkingDirMixin, unittest.TestCase):
                external_connections = [
                    IsolatedWorkingDirMixin.ExternalConnection(
                        external_path="a.txt", strategy=connect_upper
                    )
                ]

                def test_method(self):
                    self.assertTrue(os.path.exists("a.txt"))
                    self.assertFalse(os.path.islink("a.txt"))
                    with open("a.txt") as f:
                        content = f.read()
                    self.assertTrue(content.isupper())

            suite = unittest.TestSuite()
            suite.addTest(TestClass("test_method"))
            result = unittest.TextTestRunner().run(suite)
            self.assertTrue(result.wasSuccessful())

            with open("a.txt") as f:
                content = f.read()
            self.assertTrue(content.islower())
        finally:
            os.remove("a.txt")
