# Unittest Scenarios

This library adds "scenario-based testing" to Pytest via `unittest.TestCase` mixins. A "scenario-based test" is a test
that is defined by an initial and final state of files. This is useful for testing things like data pipelines/workflows
where inputs/outputs are file based, or any other type of test that is suited to be represented by a file structure. 

This package includes methods for recursively comparing directories, archives, text files, and binary files in a
cross-platform friendly way. This library also has flexible tools for configuring isolated testing environments, again
useful for data pipelines like [snakemake](https://snakemake.github.io/) that might depend on files present in the
working directory.

# Installation

# Usage
