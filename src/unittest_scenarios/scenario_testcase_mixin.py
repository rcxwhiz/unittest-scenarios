# Josh Bedwell © 2025

import enum
import os
import shutil
from collections.abc import Callable
from pathlib import Path
from os import PathLike

from unittest_scenarios.file_cmp_mixin import FileCmpMixin
from unittest_scenarios.isolated_working_dir_mixin import IsolatedWorkingDirMixin
from unittest_scenarios.utils.archive import is_archive, temp_archive_extract


class ScenarioTestCaseMixin(IsolatedWorkingDirMixin, FileCmpMixin):
    """
    Discovers and runs scenario based tests.

    Multiple formats of test are supported. A directory "a" in the scenarios dir will
    create "test_a". Inside of "a" there might be an "initial_state" and "final_state"
    directory. The items in the "initial_state" directory will be copied into the
    isolated working directory of "test_a". After that the "run_scenario" function will
    be called. After that final state checking depends on the selected strategy. If
    NONE is selected, comparison with the final state won't happen. If it is
    FILE_NAMES, it will be checked that all matching files exist. If FILE_CONTENTS is
    selected, the working directory of the test will be recursively compared to the
    final state.

    An initial state or final state may be a directory or an archive. Missing states
    can be set to raise an error or not. In the case of an accepted missing final state
    no checking will be performed. The directory containing the initial and final state
    may also be an archive.

    Attributes:
        scenarios_dir: location to find tests
        check_strategy: how to check final state for success
        initial_state_missing_ok: should an error be raised for a missing initial state
        final_state_missing_ok: should an error be raised for a missing final state
    """

    class OutputChecking(enum.Enum):
        NONE = 0
        FILE_NAMES = 1
        FILE_CONTENTS = 2

    scenarios_dir: str | PathLike[str]
    check_strategy: OutputChecking = OutputChecking.FILE_CONTENTS
    initial_state_missing_ok = True
    final_state_missing_ok = False

    def run_scenario(self, scenario_name: str) -> None:
        raise NotImplementedError("Please provide a function for running a scenario")

    def __new__(cls, *args, **kwargs):
        # check for scenarios dir
        if not hasattr(cls, "scenarios_dir"):
            raise AttributeError("Please provide scenarios_dir")
        if not os.path.exists(cls.scenarios_dir):
            raise FileNotFoundError(f"Could not find scenarios_dir {cls.scenarios_dir}")

        # create a test for each scenario
        used_test_names = set()
        for scenario in os.listdir(cls.scenarios_dir):
            scenario_path = os.path.join(cls.scenarios_dir, scenario)
            test_name = f"test_{Path(scenario).stem}"
            i = 1
            while test_name in used_test_names:
                test_name = f"test_{Path(scenario).stem}_{i}"
                i += 1
            used_test_names.add(test_name)
            setattr(cls, test_name, cls.generate_test(scenario, scenario_path))

        return super().__new__(cls)

    @classmethod
    def generate_test(cls, scenario_name: str, scenario_path: str) -> Callable:
        def test_func(self) -> None:
            if is_archive(scenario_path):
                with temp_archive_extract(scenario_path) as extracted:
                    self._copy_initial_state(extracted)
                    self.run_scenario(scenario_name)
                    self._check_final_state(extracted)
            else:
                self._copy_initial_state(scenario_path)
                self.run_scenario(scenario_name)
                self._check_final_state(scenario_path)

        return test_func

    def _copy_initial_state(self, scenario_path: str) -> None:
        scenario_path = Path(scenario_path)
        initial_states = [
            os.path.join(scenario_path, file)
            for file in os.listdir(scenario_path)
            if Path(file).stem == "initial_state"
        ]
        if len(initial_states) == 0:
            if self.initial_state_missing_ok:
                return
            else:
                raise FileNotFoundError(
                    f"Did not find initial state in {scenario_path.name}"
                )
        if len(initial_states) > 1:
            raise FileExistsError(
                f"Found multiple initial states in {scenario_path.name}"
            )

        initial_state_path = initial_states[0]
        if is_archive(initial_state_path):
            with temp_archive_extract(initial_state_path) as extracted:
                shutil.copytree(extracted, self.test_dir, dirs_exist_ok=True)
        else:
            shutil.copytree(initial_state_path, self.test_dir, dirs_exist_ok=True)

    def _check_final_state(self, scenario_path: str) -> None:
        if self.check_strategy == ScenarioTestCaseMixin.OutputChecking.NONE:
            return

        scenario_path = Path(scenario_path)
        final_states = [
            os.path.join(scenario_path, file)
            for file in os.listdir(scenario_path)
            if Path(file).stem == "final_state"
        ]
        if len(final_states) == 0:
            if self.final_state_missing_ok:
                return
            else:
                raise FileNotFoundError(
                    f"Did not find final state in {scenario_path.name}"
                )
        if len(final_states) > 1:
            raise FileExistsError(
                f"Found multiple final states in {scenario_path.name}"
            )

        def cmp(expected, actual):
            if self.check_strategy == ScenarioTestCaseMixin.OutputChecking.FILE_NAMES:
                expected_files = set()
                for root, _, files in os.walk(expected):
                    for file in files:
                        expected_files.add(
                            os.path.relpath(os.path.join(root, file), expected)
                        )
                actual_files = set()
                for root, _, files in os.walk(actual):
                    for file in files:
                        actual_files.add(
                            os.path.relpath(os.path.join(root, file), actual)
                        )
                self.assertSetEqual(expected_files, actual_files)
            else:
                self.assertDirectoryContentsEqual(expected, actual)

        final_state_path = final_states[0]
        if is_archive(final_state_path):
            with temp_archive_extract(final_state_path) as extracted:
                cmp(extracted, os.getcwd())
        else:
            cmp(final_state_path, os.getcwd())
