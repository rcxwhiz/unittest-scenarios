from unittest_scenarios import IsolatedWorkingDirMixin

# Unittest Scenarios

[![Tests](https://github.com/rcxwhiz/unittest-scenarios/actions/workflows/test.yml/badge.svg)](https://github.com/rcxwhiz/unittest-scenarios/actions/workflows/)
[![Coverage](https://codecov.io/gh/rcxwhiz/unittest-scenarios/branch/main/graph/badge.svg)](https://codecov.io/gh/rcxwhiz/unittest-scenarios/)
[![PyPi](https://img.shields.io/pypi/v/unittest-scenarios.svg)](https://pypi.python.org/pypi/unittest-scenarios/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/unittest-scenarios)


This library adds "scenario-based testing" to Pytest via `unittest.TestCase` mixins. A "scenario-based test" is a test
that is defined by an initial and final state of files. This is useful for testing things like data pipelines/workflows
where inputs/outputs are file based, or any other type of test that is suited to be represented by a file structure. 

This package includes methods for recursively comparing directories, archives, text files, and binary files in a
cross-platform friendly way. This library also has flexible tools for configuring isolated testing environments, again
useful for data pipelines like [snakemake](https://snakemake.github.io/) that might depend on files present in the
working directory.

# Installation

```shell
pip install unittest-scenarios
```

# Usage

## FileCmpMixin

This class provides several methods for checking the *contents* of files or directories to see if they are equal. The
idea is to be able to recursively compare files and paths in a platform-agnostic way. Provides the following methods:

| Method                            | Usage                                                                                     |
|-----------------------------------|-------------------------------------------------------------------------------------------|
| `assertDirectoryContentsEqual`    | Recursively compares contents of directories, detecting appropriate methods               |
| `assertDirectoryContentsNotEqual` | Negative of above                                                                         |
| `assertArchiveContentsEqual`      | Temporarily extracts both archives and compares them using `assertDirectoryContentsEqual` |
| `assertArchiveContentsNotEqual`   | Negative of above                                                                         |
| `assertTextFilesEqual`            | Opens files with universal line endings and compares line by line                         |
| `assertTextFilesNotEqual`         | Negative of above                                                                         |
| `assertFileHashesEqual`           | Compares hash of file contents with customizable hash function                            |
| `assertFileHashesNotEqual`        | Negative of above                                                                         |
| `assertPathContentsEqual`         | Automatically detects file types and recursively compares with appropriate method         |
| `assertPathContentsNotEqual`      | Negative of above                                                                         |

```python
class MyTestCase(FileCmpMixin, unittest.TestCase):
    def test_a(self):
        self.assertTextFilesEqual("file_a.txt", "file_b.txt")
```

This mixin can be useful for any situation where you are comparing files during tests. 

## IsolatedWorkingDirMixin

This class causes each test to execute in an isolated temporary directory. It also provides options to connect external
files via `ExternalConnection`. Default connection method is `"symlink"`, with `"copy"` also available in addition to
providing a callable that takes the absolute source path and the destination path relative to the test directory. 

```python
class MyIsolatedTestCase(IsolatedWorkingDirMixin, unittest.TestCase):
    external_connections = [IsolatedWorkingDirMixin.ExternalConnection(external_path="utils/")]

    def test_a(self):
        data = pd.read_csv("utils/data.csv")
```

This mixin can be useful when you are testing something that modifies its working directory. 

## ScenarioTestCaseMixin

In the following example each file will be opened and converted to uppercase. For each scenario the `final_state` will
presumably contain all the files from `initial_state` in upper case.

```python
class MyScenarioTestCase(ScenarioTestCaseMixin, unittest.TestCase):
    scenarios_dir = Path(__file__).parent / "scenarios"

    def run_scenario(self, scenario_name: str) -> None:
        for filename in os.listdir():
            with open(filename, "r") as f:
                content = f.read()
            with open(filename, "w") as f:
                f.write(content.upper())
```

In a more realistic or topical example:

```python
class MyScenariosTestCase(ScenarioTestCaseMixin, unittest.TestCase):
    scenarios_dir = Path(__file__).parent / "successful_scenarios"
    check_strategy = OutputChecking.FILE_CONTENTS
    external_connections = [
        ExternalConnection(external_path=Path(__file__).parent.parent / "utils", strategy="symlink"),
        ExternalConnection(external_path=Path(__file__).parent.parent / "config", strategy=copy_config),
        ExternalConnection(external_path=Path(__file__).parent.parent / "workflow", strategy="symlink"),
    ]

    def run_scenario(self, scenario_name: str) -> None:
        with open("expected_outputs.txt", "r") as f:
            expected_outputs = f.read()
        result = subprocess.run(["snakemake", "--use-conda", expected_outputs])
        self.assertEqual(0, result.returncode, f"Snakemake had non-zero return code: {result.returncode}")
```

Which would allow you to easily set up a ton of tests for your pipeline without having to update code. This mixin is
useful for quickly and simply generating these file based tests. 
