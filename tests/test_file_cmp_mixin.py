# Josh Bedwell © 2025

import os
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path

from src.unittest_scenarios import FileCmpMixin

from .win_tempfile import NamedTempFile

text_a = """
    Sed euismod varius semper. Integer pretium maximus dolor

    et mattis. Suspendisse luctus eros id sem mattis semper.
    Sed dui dui, scelerisque sit amet diam a.
    """

text_b = """
    Fusce suscipit turpis in nisi ornare cursus. Suspendisse ex massa, aliquam congue accumsan vitae, tempor nec nunc.
    Nullam accumsan interdum orci, in eleifend leo porta.
    """

text_c = """
    Etiam lorem elit, finibus quis purus id, tempor mattis libero.

    Pellentesque finibus urna non orci luctus, sed condimentum lacus vestibulum. Etiam sit amet sapien eget.
    """


def _create_tar(tar_path, files):
    with tarfile.open(tar_path, "w") as tar:
        for filename, content in files.items():
            file_path = os.path.join(os.path.dirname(tar_path), filename)
            if isinstance(content, str):
                with open(file_path, "w") as f:
                    f.write(content)
            else:
                with open(file_path, "wb") as f:
                    f.write(content)
            tar.add(file_path, arcname=filename)
            os.remove(file_path)


def _create_zip(zip_path, files):
    with zipfile.ZipFile(zip_path, "w") as zip:
        for filename, content in files.items():
            file_path = os.path.join(os.path.dirname(zip_path), filename)
            if isinstance(content, str):
                with open(file_path, "w") as f:
                    f.write(content)
            else:
                with open(file_path, "wb") as f:
                    f.write(content)
            zip.write(file_path, arcname=filename)
            os.remove(file_path)


class FileCmpTestCase(unittest.TestCase):

    def test_subclass_requirement(self):
        """Test that cannot be instantiated without subclassing unittest.TestCase"""

        class BadClass(FileCmpMixin):
            pass

        with self.assertRaises(TypeError):
            _ = BadClass()

    def test_txt_equal(self):
        """Compare contents of text files that should be equal"""

        class TestClass(FileCmpMixin, unittest.TestCase):
            def test_method(self):
                with NamedTempFile() as tf1, NamedTempFile() as tf2:
                    with open(tf1.name, "w") as f1:
                        f1.write(text_a)
                    with open(tf2.name, "w") as f2:
                        f2.write(text_a)

                    self.assertTextFilesEqual(tf1.name, tf2.name)

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_method"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())

    def test_txt_cross_platform(self):
        """Compare contents of text files with different line endings that should be equal"""

        class TestClass(FileCmpMixin, unittest.TestCase):
            def test_method(self):
                with NamedTempFile() as tf1, NamedTempFile() as tf2:
                    with open(tf1.name, "w", newline="\n") as f1:
                        f1.write(text_a)
                    with open(tf2.name, "w", newline="\r\n") as f2:
                        f2.write(text_a)

                    self.assertTextFilesEqual(tf1.name, tf2.name)

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_method"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())

    def test_txt_not_equal(self):
        """Compare contents of text files that should not be equal"""

        class TestClass(FileCmpMixin, unittest.TestCase):
            def test_method(self):
                with NamedTempFile() as tf1, NamedTempFile() as tf2:
                    with open(tf1.name, "w") as f1:
                        f1.write(text_a)
                    with open(tf2.name, "w") as f2:
                        f2.write(text_b)

                    self.assertTextFilesNotEqual(tf1.name, tf2.name)

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_method"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())

    def test_hash_equal(self):
        """Compare hashes of contents of files that should be equal"""

        class TestClass(FileCmpMixin, unittest.TestCase):
            def test_method(self):
                with NamedTempFile() as tf1, NamedTempFile() as tf2:
                    with open(tf1.name, "w") as f1:
                        f1.write(text_a)
                    with open(tf2.name, "w") as f2:
                        f2.write(text_a)

                    self.assertFileHashesEqual(tf1.name, tf2.name)

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_method"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())

    def test_hash_not_equal(self):
        """Compare hashes of contents of files that should not be equal (different line endings)"""

        class TestClass(FileCmpMixin, unittest.TestCase):
            def test_method(self):
                with NamedTempFile() as tf1, NamedTempFile() as tf2:
                    with open(tf1.name, "w", newline="\n") as f1:
                        f1.write(text_a)
                    with open(tf2.name, "w", newline="\r\n") as f2:
                        f2.write(text_a)

                    self.assertFileHashesNotEqual(tf1.name, tf2.name)

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_method"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())

    def test_archives_equal(self):
        """Test that equivalently constructed zip and tar files are equal"""

        class TestClass(FileCmpMixin, unittest.TestCase):
            def test_method_1(self):
                with (
                    NamedTempFile(suffix=".zip") as z1,
                    NamedTempFile(suffix=".zip") as z2,
                ):
                    files = {"a.txt": text_a, "b.txt": text_b}
                    _create_zip(z1.name, files)
                    _create_zip(z2.name, files)

                    self.assertArchiveContentsEqual(z1.name, z2.name)

            def test_method_2(self):
                with (
                    NamedTempFile(suffix=".tar") as t1,
                    NamedTempFile(suffix=".tar") as t2,
                ):
                    files = {"a.txt": text_a, "b.txt": text_b}
                    _create_tar(t1.name, files)
                    _create_tar(t2.name, files)

                    self.assertArchiveContentsEqual(t1.name, t2.name)

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_method_1"))
        suite.addTest(TestClass("test_method_2"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())

    def test_archives_contents_not_equal(self):
        """Test that archives with files with same names but different contents are not equal"""

        class TestClass(FileCmpMixin, unittest.TestCase):
            def test_method(self):
                with (
                    NamedTempFile(suffix=".tar") as t1,
                    NamedTempFile(suffix=".tar") as t2,
                ):
                    _create_tar(t1.name, {"a.txt": text_a, "b.txt": text_b})
                    _create_tar(t2.name, {"a.txt": text_a, "b.txt": text_c})

                    self.assertArchiveContentsNotEqual(t1.name, t2.name)

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_method"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())

    def test_archives_missing_files(self):
        """Compare that a left or right archive missing a file will be considered not equal"""

        class TestClass(FileCmpMixin, unittest.TestCase):
            def test_method_1(self):
                with (
                    NamedTempFile(suffix=".zip") as z1,
                    NamedTempFile(suffix=".zip") as z2,
                ):
                    _create_zip(z1.name, {"a.txt": text_a, "b.txt": text_b})
                    _create_zip(z2.name, {"a.txt": text_a})

                    self.assertArchiveContentsNotEqual(z1.name, z2.name)

            def test_method_2(self):
                with (
                    NamedTempFile(suffix=".zip") as z1,
                    NamedTempFile(suffix=".zip") as z2,
                ):
                    _create_zip(z1.name, {"a.txt": text_a})
                    _create_zip(z2.name, {"a.txt": text_a, "b.txt": text_b})

                    self.assertArchiveContentsNotEqual(z1.name, z2.name)

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_method_1"))
        suite.addTest(TestClass("test_method_2"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())

    def test_archives_missing_files_okay(self):
        """Use a or b must have all items filters"""

        class TestClass(FileCmpMixin, unittest.TestCase):
            def test_method_1(self):
                with (
                    NamedTempFile(suffix=".zip") as z1,
                    NamedTempFile(suffix=".zip") as z2,
                ):
                    _create_zip(z1.name, {"a.txt": text_a, "b.txt": text_b})
                    _create_zip(z2.name, {"a.txt": text_a})

                    self.assertArchiveContentsEqual(
                        z1.name, z2.name, b_must_have_all_items=False
                    )
                    self.assertArchiveContentsNotEqual(
                        z1.name, z2.name, a_must_have_all_items=False
                    )

            def test_method_2(self):
                with (
                    NamedTempFile(suffix=".zip") as z1,
                    NamedTempFile(suffix=".zip") as z2,
                ):
                    _create_zip(z1.name, {"a.txt": text_a})
                    _create_zip(z2.name, {"a.txt": text_a, "b.txt": text_b})

                    self.assertArchiveContentsEqual(
                        z1.name, z2.name, a_must_have_all_items=False
                    )
                    self.assertArchiveContentsNotEqual(
                        z1.name, z2.name, b_must_have_all_items=False
                    )

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_method_1"))
        suite.addTest(TestClass("test_method_2"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())

    def test_only_common_archive_files(self):
        """Tests behavior when only common files are compared"""

        class TestClass(FileCmpMixin, unittest.TestCase):
            def test_method_1(self):
                with (
                    NamedTempFile(suffix=".zip") as z1,
                    NamedTempFile(suffix=".zip") as z2,
                ):
                    _create_zip(z1.name, {"a.txt": text_a})
                    _create_zip(z2.name, {"b.txt": text_b})

                    self.assertArchiveContentsEqual(
                        z1.name,
                        z2.name,
                        a_must_have_all_items=False,
                        b_must_have_all_items=False,
                    )

            def test_method_2(self):
                with (
                    NamedTempFile(suffix=".zip") as z1,
                    NamedTempFile(suffix=".zip") as z2,
                ):
                    _create_zip(z1.name, {"a.txt": text_a, "c.txt": text_c})
                    _create_zip(z2.name, {"b.txt": text_b, "c.txt": text_c})

                    self.assertArchiveContentsEqual(
                        z1.name,
                        z2.name,
                        a_must_have_all_items=False,
                        b_must_have_all_items=False,
                    )

            def test_method_3(self):
                with (
                    NamedTempFile(suffix=".zip") as z1,
                    NamedTempFile(suffix=".zip") as z2,
                ):
                    _create_zip(z1.name, {"a.txt": text_a, "c.txt": text_c})
                    _create_zip(z2.name, {"b.txt": text_b, "c.txt": text_a})

                    self.assertArchiveContentsNotEqual(
                        z1.name,
                        z2.name,
                        a_must_have_all_items=False,
                        b_must_have_all_items=False,
                    )

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_method_1"))
        suite.addTest(TestClass("test_method_2"))
        suite.addTest(TestClass("test_method_3"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())

    def test_nested_archives_equal(self):
        """Compare nested archives that should be equal"""

        class TestClass(FileCmpMixin, unittest.TestCase):
            def test_method(self):
                with (
                    NamedTempFile(suffix=".tar") as t1,
                    NamedTempFile(suffix=".tar") as t2,
                ):
                    files = {"a.txt": text_a, "b.txt": text_b}
                    _create_tar(t1.name, files)
                    _create_tar(t2.name, files)
                    t1.flush()
                    t2.flush()
                    t1.close()
                    t2.close()

                    with (
                        NamedTempFile(suffix=".tar") as t11,
                        NamedTempFile(suffix=".tar") as t22,
                    ):
                        with open(t1.name, "rb") as t1:
                            _create_tar(
                                t11.name, {"c.txt": text_c, "arc.tar": t1.read()}
                            )
                        with open(t2.name, "rb") as t2:
                            _create_tar(
                                t22.name, {"c.txt": text_c, "arc.tar": t2.read()}
                            )

                        self.assertArchiveContentsEqual(t11.name, t22.name)

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_method"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())

    def test_nested_archives_not_equal(self):
        """Compare archives that have a difference in the nested archive"""

        class TestClass(FileCmpMixin, unittest.TestCase):
            def test_method(self):
                with (
                    NamedTempFile(suffix=".tar") as t1,
                    NamedTempFile(suffix=".tar") as t2,
                ):
                    _create_tar(t1.name, {"a.txt": text_a, "b.txt": text_b})
                    _create_tar(t2.name, {"a.txt": text_a, "b.txt": text_c})
                    t1.flush()
                    t2.flush()
                    t1.close()
                    t2.close()

                    with (
                        NamedTempFile(suffix=".tar") as t11,
                        NamedTempFile(suffix=".tar") as t22,
                    ):
                        with open(t1.name, "rb") as t1:
                            _create_tar(
                                t11.name, {"c.txt": text_c, "arc.tar": t1.read()}
                            )
                        with open(t2.name, "rb") as t2:
                            _create_tar(
                                t22.name, {"c.txt": text_c, "arc.tar": t2.read()}
                            )

                        self.assertArchiveContentsNotEqual(t11.name, t22.name)

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_method"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())

    def test_archive_types(self):
        """Try comparing every type of supported archive"""

        class TestClass(FileCmpMixin, unittest.TestCase):
            def test_method_1(self):
                with NamedTempFile(suffix=".zip") as z:
                    with zipfile.ZipFile(z.name, "w") as zip:
                        file_path = os.path.join(os.path.dirname(z.name), "a.txt")
                        with open(file_path, "w") as f:
                            f.write(text_a)
                        zip.write(file_path, arcname="a.txt")
                        os.remove(file_path)
                    self.assertArchiveContentsEqual(z.name, z.name)

            def test_method_2(self):
                with NamedTempFile(suffix=".tar") as t:
                    with tarfile.open(t.name, "w") as tar:
                        file_path = os.path.join(os.path.dirname(t.name), "a.txt")
                        with open(file_path, "w") as f:
                            f.write(text_a)
                        tar.add(file_path, arcname="a.txt")
                        os.remove(file_path)
                    self.assertArchiveContentsEqual(t.name, t.name)

            def test_method_3(self):
                with NamedTempFile(suffix=".tar.gz") as t:
                    with tarfile.open(t.name, "w:gz") as tar:
                        file_path = os.path.join(os.path.dirname(t.name), "a.txt")
                        with open(file_path, "w") as f:
                            f.write(text_a)
                        tar.add(file_path, arcname="a.txt")
                        os.remove(file_path)
                    self.assertArchiveContentsEqual(t.name, t.name)

            def test_method_4(self):
                with NamedTempFile(suffix=".tgz") as t:
                    with tarfile.open(t.name, "w:gz") as tar:
                        file_path = os.path.join(os.path.dirname(t.name), "a.txt")
                        with open(file_path, "w") as f:
                            f.write(text_a)
                        tar.add(file_path, arcname="a.txt")
                        os.remove(file_path)
                    self.assertArchiveContentsEqual(t.name, t.name)

            def test_method_5(self):
                with NamedTempFile(suffix=".tar.bz2") as t:
                    with tarfile.open(t.name, "w:bz2") as tar:
                        file_path = os.path.join(os.path.dirname(t.name), "a.txt")
                        with open(file_path, "w") as f:
                            f.write(text_a)
                        tar.add(file_path, arcname="a.txt")
                        os.remove(file_path)
                    self.assertArchiveContentsEqual(t.name, t.name)

            def test_method_6(self):
                with NamedTempFile(suffix=".tbz2") as t:
                    with tarfile.open(t.name, "w:bz2") as tar:
                        file_path = os.path.join(os.path.dirname(t.name), "a.txt")
                        with open(file_path, "w") as f:
                            f.write(text_a)
                        tar.add(file_path, arcname="a.txt")
                        os.remove(file_path)
                    self.assertArchiveContentsEqual(t.name, t.name)

            def test_method_7(self):
                with NamedTempFile(suffix=".tar.xz") as t:
                    with tarfile.open(t.name, "w:xz") as tar:
                        file_path = os.path.join(os.path.dirname(t.name), "a.txt")
                        with open(file_path, "w") as f:
                            f.write(text_a)
                        tar.add(file_path, arcname="a.txt")
                        os.remove(file_path)
                    self.assertArchiveContentsEqual(t.name, t.name)

            def test_method_8(self):
                with NamedTempFile(suffix=".txz") as t:
                    with tarfile.open(t.name, "w:xz") as tar:
                        file_path = os.path.join(os.path.dirname(t.name), "a.txt")
                        with open(file_path, "w") as f:
                            f.write(text_a)
                        tar.add(file_path, arcname="a.txt")
                        os.remove(file_path)
                    self.assertArchiveContentsEqual(t.name, t.name)

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_method_1"))
        suite.addTest(TestClass("test_method_2"))
        suite.addTest(TestClass("test_method_3"))
        suite.addTest(TestClass("test_method_4"))
        suite.addTest(TestClass("test_method_5"))
        suite.addTest(TestClass("test_method_6"))
        suite.addTest(TestClass("test_method_7"))
        suite.addTest(TestClass("test_method_8"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())

    def test_dirs_equal(self):
        """Compare two directories with equal contents"""

        class TestClass(FileCmpMixin, unittest.TestCase):
            def test_method(self):
                with (
                    tempfile.TemporaryDirectory() as d1,
                    tempfile.TemporaryDirectory() as d2,
                ):
                    with open(os.path.join(d1, "a.txt"), "w") as f:
                        f.write(text_a)
                    with open(os.path.join(d1, "b.txt"), "w") as f:
                        f.write(text_b)

                    with open(os.path.join(d2, "a.txt"), "w") as f:
                        f.write(text_a)
                    with open(os.path.join(d2, "b.txt"), "w") as f:
                        f.write(text_b)

                    self.assertDirectoryContentsEqual(d1, d2)

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_method"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())

    def test_nested_dirs_equal(self):
        """Compare nested directories with equal contents"""

        class TestClass(FileCmpMixin, unittest.TestCase):
            def test_method(self):
                with (
                    tempfile.TemporaryDirectory() as d1,
                    tempfile.TemporaryDirectory() as d2,
                ):
                    with open(os.path.join(d1, "a.txt"), "w") as f:
                        f.write(text_a)
                    with open(os.path.join(d1, "b.txt"), "w") as f:
                        f.write(text_b)
                    os.mkdir(os.path.join(d1, "d"))
                    with open(os.path.join(d1, "d", "c.txt"), "w") as f:
                        f.write(text_c)

                    with open(os.path.join(d2, "a.txt"), "w") as f:
                        f.write(text_a)
                    with open(os.path.join(d2, "b.txt"), "w") as f:
                        f.write(text_b)
                    os.mkdir(os.path.join(d2, "d"))
                    with open(os.path.join(d2, "d", "c.txt"), "w") as f:
                        f.write(text_c)

                    self.assertDirectoryContentsEqual(d1, d2)

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_method"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())

    def test_dirs_not_equal(self):
        """Compare directories with different contents"""

        class TestClass(FileCmpMixin, unittest.TestCase):
            def test_method(self):
                with (
                    tempfile.TemporaryDirectory() as d1,
                    tempfile.TemporaryDirectory() as d2,
                ):
                    with open(os.path.join(d1, "a.txt"), "w") as f:
                        f.write(text_a)
                    with open(os.path.join(d1, "b.txt"), "w") as f:
                        f.write(text_b)

                    with open(os.path.join(d2, "a.txt"), "w") as f:
                        f.write(text_a)
                    with open(os.path.join(d2, "b.txt"), "w") as f:
                        f.write(text_c)

                    self.assertDirectoryContentsNotEqual(d1, d2)

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_method"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())

    def test_dirs_missing_members(self):
        """Test left and right directories missing a member"""

        class TestClass(FileCmpMixin, unittest.TestCase):
            def test_method_1(self):
                with (
                    tempfile.TemporaryDirectory() as d1,
                    tempfile.TemporaryDirectory() as d2,
                ):
                    with open(os.path.join(d1, "a.txt"), "w") as f:
                        f.write(text_a)
                    with open(os.path.join(d1, "b.txt"), "w") as f:
                        f.write(text_b)

                    with open(os.path.join(d2, "a.txt"), "w") as f:
                        f.write(text_a)

                    self.assertDirectoryContentsNotEqual(d1, d2)

            def test_method_2(self):
                with (
                    tempfile.TemporaryDirectory() as d1,
                    tempfile.TemporaryDirectory() as d2,
                ):
                    with open(os.path.join(d1, "a.txt"), "w") as f:
                        f.write(text_a)

                    with open(os.path.join(d2, "a.txt"), "w") as f:
                        f.write(text_a)
                    with open(os.path.join(d2, "b.txt"), "w") as f:
                        f.write(text_b)

                    self.assertDirectoryContentsNotEqual(d1, d2)

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_method_1"))
        suite.addTest(TestClass("test_method_2"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())

    def test_dirs_missing_members_okay(self):
        """Tests modifiers for both directories not needing all items"""

        class TestClass(FileCmpMixin, unittest.TestCase):
            def test_method_1(self):
                with (
                    tempfile.TemporaryDirectory() as d1,
                    tempfile.TemporaryDirectory() as d2,
                ):
                    with open(os.path.join(d1, "a.txt"), "w") as f:
                        f.write(text_a)
                    with open(os.path.join(d1, "b.txt"), "w") as f:
                        f.write(text_b)

                    with open(os.path.join(d2, "a.txt"), "w") as f:
                        f.write(text_a)

                    self.assertDirectoryContentsEqual(
                        d1, d2, b_must_have_all_items=False
                    )
                    self.assertDirectoryContentsNotEqual(
                        d1, d2, a_must_have_all_items=False
                    )

            def test_method_2(self):
                with (
                    tempfile.TemporaryDirectory() as d1,
                    tempfile.TemporaryDirectory() as d2,
                ):
                    with open(os.path.join(d1, "a.txt"), "w") as f:
                        f.write(text_a)

                    with open(os.path.join(d2, "a.txt"), "w") as f:
                        f.write(text_a)
                    with open(os.path.join(d2, "b.txt"), "w") as f:
                        f.write(text_b)

                    self.assertDirectoryContentsEqual(
                        d1, d2, a_must_have_all_items=False
                    )
                    self.assertDirectoryContentsNotEqual(
                        d1, d2, b_must_have_all_items=False
                    )

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_method_1"))
        suite.addTest(TestClass("test_method_2"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())

    def test_dirs_only_cmp_common_items(self):
        """Tests when directories are only comparing common items"""

        class TestClass(FileCmpMixin, unittest.TestCase):
            def test_method_1(self):
                with (
                    tempfile.TemporaryDirectory() as d1,
                    tempfile.TemporaryDirectory() as d2,
                ):
                    with open(os.path.join(d1, "b.txt"), "w") as f:
                        f.write(text_b)

                    with open(os.path.join(d2, "a.txt"), "w") as f:
                        f.write(text_a)

                    self.assertDirectoryContentsEqual(
                        d1, d2, a_must_have_all_items=False, b_must_have_all_items=False
                    )

            def test_method_2(self):
                with (
                    tempfile.TemporaryDirectory() as d1,
                    tempfile.TemporaryDirectory() as d2,
                ):
                    with open(os.path.join(d1, "b.txt"), "w") as f:
                        f.write(text_b)
                    with open(os.path.join(d1, "c.txt"), "w") as f:
                        f.write(text_c)

                    with open(os.path.join(d2, "a.txt"), "w") as f:
                        f.write(text_a)
                    with open(os.path.join(d2, "c.txt"), "w") as f:
                        f.write(text_c)

                    self.assertDirectoryContentsEqual(
                        d1, d2, a_must_have_all_items=False, b_must_have_all_items=False
                    )

            def test_method_3(self):
                with (
                    tempfile.TemporaryDirectory() as d1,
                    tempfile.TemporaryDirectory() as d2,
                ):
                    with open(os.path.join(d1, "b.txt"), "w") as f:
                        f.write(text_b)
                    with open(os.path.join(d1, "c.txt"), "w") as f:
                        f.write(text_c)

                    with open(os.path.join(d2, "a.txt"), "w") as f:
                        f.write(text_a)
                    with open(os.path.join(d2, "c.txt"), "w") as f:
                        f.write(text_b)

                    self.assertDirectoryContentsNotEqual(
                        d1, d2, a_must_have_all_items=False, b_must_have_all_items=False
                    )

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_method_1"))
        suite.addTest(TestClass("test_method_2"))
        suite.addTest(TestClass("test_method_3"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())

    def test_hash_files_equal(self):
        """Compare equal images"""

        class TestClass(FileCmpMixin, unittest.TestCase):
            def test_method(self):
                test_files = Path(__file__).parent / "test_files"
                self.assertPathContentsEqual(test_files / "a.png", test_files / "a.png")

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_method"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())

    def test_hash_files_not_equal(self):
        """Compare not equal images"""

        class TestClass(FileCmpMixin, unittest.TestCase):
            def test_method(self):
                test_files = Path(__file__).parent / "test_files"
                self.assertPathContentsNotEqual(
                    test_files / "a.png", test_files / "b.png"
                )

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_method"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())
