import os
import tarfile
import tempfile
import unittest
import zipfile

from win_tempfile import NamedTempFile

from src.unittest_scenarios import FileCmpMixin


class FileCmpTestCase(FileCmpMixin, unittest.TestCase):
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

    def create_tar(self, tar_path, files):
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

    def create_zip(self, zip_path, files):
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

    def test_subclass_requirement(self):
        class BadClass(FileCmpMixin):
            pass

        with self.assertRaises(TypeError):
            _ = BadClass()

    def test_txt_equal(self):
        with NamedTempFile() as tf1, NamedTempFile() as tf2:
            with open(tf1.name, "w") as f1:
                f1.write(self.text_a)
            with open(tf2.name, "w") as f2:
                f2.write(self.text_a)

            self.assertTextFilesEqual(tf1.name, tf2.name)

    def test_txt_cross_platform(self):
        with NamedTempFile() as tf1, NamedTempFile() as tf2:
            with open(tf1.name, "w", newline="\n") as f1:
                f1.write(self.text_a)
            with open(tf2.name, "w", newline="\r\n") as f2:
                f2.write(self.text_a)

            self.assertTextFilesEqual(tf1.name, tf2.name)

    def test_txt_not_equal(self):
        with NamedTempFile() as tf1, NamedTempFile() as tf2:
            with open(tf1.name, "w") as f1:
                f1.write(self.text_a)
            with open(tf2.name, "w") as f2:
                f2.write(self.text_b)

            self.assertTextFilesNotEqual(tf1.name, tf2.name)

    def test_hash_equal(self):
        with NamedTempFile() as tf1, NamedTempFile() as tf2:
            with open(tf1.name, "w") as f1:
                f1.write(self.text_a)
            with open(tf2.name, "w") as f2:
                f2.write(self.text_a)

            self.assertFileHashesEqual(tf1.name, tf2.name)

    def test_hash_not_equal(self):
        with NamedTempFile() as tf1, NamedTempFile() as tf2:
            with open(tf1.name, "w", newline="\n") as f1:
                f1.write(self.text_a)
            with open(tf2.name, "w", newline="\r\n") as f2:
                f2.write(self.text_a)

            self.assertFileHashesNotEqual(tf1.name, tf2.name)

    def test_archives_equal(self):
        with NamedTempFile(suffix=".zip") as z1, NamedTempFile(suffix=".zip") as z2:
            files = {"a.txt": self.text_a, "b.txt": self.text_b}
            self.create_zip(z1.name, files)
            self.create_zip(z2.name, files)

            self.assertArchiveContentsEqual(z1.name, z2.name)

        with NamedTempFile(suffix=".tar") as t1, NamedTempFile(suffix=".tar") as t2:
            files = {"a.txt": self.text_a, "b.txt": self.text_b}
            self.create_tar(t1.name, files)
            self.create_tar(t2.name, files)

            self.assertArchiveContentsEqual(t1.name, t2.name)

    def test_archives_contents_not_equal(self):
        with NamedTempFile(suffix=".tar") as t1, NamedTempFile(suffix=".tar") as t2:
            self.create_tar(t1.name, {"a.txt": self.text_a, "b.txt": self.text_b})
            self.create_tar(t2.name, {"a.txt": self.text_a, "b.txt": self.text_c})

            self.assertArchiveContentsNotEqual(t1.name, t2.name)

    def test_archives_missing_files(self):
        with NamedTempFile(suffix=".zip") as z1, NamedTempFile(suffix=".zip") as z2:
            self.create_zip(z1.name, {"a.txt": self.text_a, "b.txt": self.text_b})
            self.create_zip(z2.name, {"a.txt": self.text_a})

            self.assertArchiveContentsNotEqual(z1.name, z2.name)

        with NamedTempFile(suffix=".zip") as z1, NamedTempFile(suffix=".zip") as z2:
            self.create_zip(z1.name, {"a.txt": self.text_a})
            self.create_zip(z2.name, {"a.txt": self.text_a, "b.txt": self.text_b})

            self.assertArchiveContentsNotEqual(z1.name, z2.name)

    def test_nested_archives_equal(self):
        with NamedTempFile(suffix=".tar") as t1, NamedTempFile(suffix=".tar") as t2:
            files = {"a.txt": self.text_a, "b.txt": self.text_b}
            self.create_tar(t1.name, files)
            self.create_tar(t2.name, files)
            t1.flush()
            t2.flush()
            t1.close()
            t2.close()

            with (
                NamedTempFile(suffix=".tar") as t11,
                NamedTempFile(suffix=".tar") as t22,
            ):
                with open(t1.name, "rb") as t1:
                    self.create_tar(
                        t11.name, {"c.txt": self.text_c, "arc.tar": t1.read()}
                    )
                with open(t2.name, "rb") as t2:
                    self.create_tar(
                        t22.name, {"c.txt": self.text_c, "arc.tar": t2.read()}
                    )

                self.assertArchiveContentsEqual(t11.name, t22.name)

    def test_nested_archives_not_equal(self):
        with NamedTempFile(suffix=".tar") as t1, NamedTempFile(suffix=".tar") as t2:
            self.create_tar(t1.name, {"a.txt": self.text_a, "b.txt": self.text_b})
            self.create_tar(t2.name, {"a.txt": self.text_a, "b.txt": self.text_c})
            t1.flush()
            t2.flush()
            t1.close()
            t2.close()

            with (
                NamedTempFile(suffix=".tar") as t11,
                NamedTempFile(suffix=".tar") as t22,
            ):
                with open(t1.name, "rb") as t1:
                    self.create_tar(
                        t11.name, {"c.txt": self.text_c, "arc.tar": t1.read()}
                    )
                with open(t2.name, "rb") as t2:
                    self.create_tar(
                        t22.name, {"c.txt": self.text_c, "arc.tar": t2.read()}
                    )

                self.assertArchiveContentsNotEqual(t11.name, t22.name)

    def test_archive_types(self):
        with NamedTempFile(suffix=".zip") as z:
            with zipfile.ZipFile(z.name, "w") as zip:
                file_path = os.path.join(os.path.dirname(z.name), "a.txt")
                with open(file_path, "w") as f:
                    f.write(self.text_a)
                zip.write(file_path, arcname="a.txt")
                os.remove(file_path)
            self.assertArchiveContentsEqual(z.name, z.name)

        with NamedTempFile(suffix=".tar") as t:
            with tarfile.open(t.name, "w") as tar:
                file_path = os.path.join(os.path.dirname(t.name), "a.txt")
                with open(file_path, "w") as f:
                    f.write(self.text_a)
                tar.add(file_path, arcname="a.txt")
                os.remove(file_path)
            self.assertArchiveContentsEqual(t.name, t.name)

        with NamedTempFile(suffix=".tar.gz") as t:
            with tarfile.open(t.name, "w:gz") as tar:
                file_path = os.path.join(os.path.dirname(t.name), "a.txt")
                with open(file_path, "w") as f:
                    f.write(self.text_a)
                tar.add(file_path, arcname="a.txt")
                os.remove(file_path)
            self.assertArchiveContentsEqual(t.name, t.name)

        with NamedTempFile(suffix=".tgz") as t:
            with tarfile.open(t.name, "w:gz") as tar:
                file_path = os.path.join(os.path.dirname(t.name), "a.txt")
                with open(file_path, "w") as f:
                    f.write(self.text_a)
                tar.add(file_path, arcname="a.txt")
                os.remove(file_path)
            self.assertArchiveContentsEqual(t.name, t.name)

        with NamedTempFile(suffix=".tar.bz2") as t:
            with tarfile.open(t.name, "w:bz2") as tar:
                file_path = os.path.join(os.path.dirname(t.name), "a.txt")
                with open(file_path, "w") as f:
                    f.write(self.text_a)
                tar.add(file_path, arcname="a.txt")
                os.remove(file_path)
            self.assertArchiveContentsEqual(t.name, t.name)

        with NamedTempFile(suffix=".tbz2") as t:
            with tarfile.open(t.name, "w:bz2") as tar:
                file_path = os.path.join(os.path.dirname(t.name), "a.txt")
                with open(file_path, "w") as f:
                    f.write(self.text_a)
                tar.add(file_path, arcname="a.txt")
                os.remove(file_path)
            self.assertArchiveContentsEqual(t.name, t.name)

        with NamedTempFile(suffix=".tar.xz") as t:
            with tarfile.open(t.name, "w:xz") as tar:
                file_path = os.path.join(os.path.dirname(t.name), "a.txt")
                with open(file_path, "w") as f:
                    f.write(self.text_a)
                tar.add(file_path, arcname="a.txt")
                os.remove(file_path)
            self.assertArchiveContentsEqual(t.name, t.name)

        with NamedTempFile(suffix=".txz") as t:
            with tarfile.open(t.name, "w:xz") as tar:
                file_path = os.path.join(os.path.dirname(t.name), "a.txt")
                with open(file_path, "w") as f:
                    f.write(self.text_a)
                tar.add(file_path, arcname="a.txt")
                os.remove(file_path)
            self.assertArchiveContentsEqual(t.name, t.name)

    def test_dirs_equal(self):
        with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
            with open(os.path.join(d1, "a.txt"), "w") as f:
                f.write(self.text_a)
            with open(os.path.join(d1, "b.txt"), "w") as f:
                f.write(self.text_b)

            with open(os.path.join(d2, "a.txt"), "w") as f:
                f.write(self.text_a)
            with open(os.path.join(d2, "b.txt"), "w") as f:
                f.write(self.text_b)

            self.assertDirectoryContentsEqual(d1, d2)

    def test_nested_dirs_equal(self):
        with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
            with open(os.path.join(d1, "a.txt"), "w") as f:
                f.write(self.text_a)
            with open(os.path.join(d1, "b.txt"), "w") as f:
                f.write(self.text_b)
            os.mkdir(os.path.join(d1, "d"))
            with open(os.path.join(d1, "d", "c.txt"), "w") as f:
                f.write(self.text_c)

            with open(os.path.join(d2, "a.txt"), "w") as f:
                f.write(self.text_a)
            with open(os.path.join(d2, "b.txt"), "w") as f:
                f.write(self.text_b)
            os.mkdir(os.path.join(d2, "d"))
            with open(os.path.join(d2, "d", "c.txt"), "w") as f:
                f.write(self.text_c)

            self.assertDirectoryContentsEqual(d1, d2)

    def test_dirs_not_equal(self):
        with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
            with open(os.path.join(d1, "a.txt"), "w") as f:
                f.write(self.text_a)
            with open(os.path.join(d1, "b.txt"), "w") as f:
                f.write(self.text_b)

            with open(os.path.join(d2, "a.txt"), "w") as f:
                f.write(self.text_a)
            with open(os.path.join(d2, "b.txt"), "w") as f:
                f.write(self.text_c)

            self.assertDirectoryContentsNotEqual(d1, d2)

    def test_dirs_missing_members(self):
        with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
            with open(os.path.join(d1, "a.txt"), "w") as f:
                f.write(self.text_a)
            with open(os.path.join(d1, "b.txt"), "w") as f:
                f.write(self.text_b)

            with open(os.path.join(d2, "a.txt"), "w") as f:
                f.write(self.text_a)

            self.assertDirectoryContentsNotEqual(d1, d2)

        with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
            with open(os.path.join(d1, "a.txt"), "w") as f:
                f.write(self.text_a)

            with open(os.path.join(d2, "a.txt"), "w") as f:
                f.write(self.text_a)
            with open(os.path.join(d2, "b.txt"), "w") as f:
                f.write(self.text_b)

            self.assertDirectoryContentsNotEqual(d1, d2)
