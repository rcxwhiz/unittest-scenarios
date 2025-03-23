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

# Usage
