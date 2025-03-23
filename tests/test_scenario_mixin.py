# Josh Bedwell © 2025

import unittest
from pathlib import Path

from src.unittest_scenarios import ScenarioTestCaseMixin


class TestScenarioMixin(unittest.TestCase):

    def test_subclass_requirement(self):
        class BadClass(ScenarioTestCaseMixin):
            scenarios_dir = Path(__file__).parent / "test_files" / "equal_dirs"

        with self.assertRaises(TypeError):
            _ = BadClass()

    def test_missing_run_func(self):
        class TestClass(ScenarioTestCaseMixin, unittest.TestCase):
            scenarios_dir = Path(__file__).parent / "test_files" / "equal_dirs"

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_a"))
        result = unittest.TextTestRunner().run(suite)
        self.assertFalse(result.wasSuccessful())

    def test_run_func_runs(self):
        check_var = [False]

        class TestClass(ScenarioTestCaseMixin, unittest.TestCase):
            scenarios_dir = Path(__file__).parent / "test_files" / "equal_dirs"

            def run_scenario(self, scenario_name: str) -> None:
                check_var[0] = True

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_a"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())
        self.assertTrue(check_var[0])

    def test_missing_scenario_dir(self):
        class TestClass(ScenarioTestCaseMixin, unittest.TestCase):
            scenarios_dir = "qwertyuiop"

            def run_scenario(self, scenario_name: str) -> None:
                pass

        with self.assertRaises(FileNotFoundError):
            _ = TestClass()

    def test_missing_initial_state(self):
        class TestClass(ScenarioTestCaseMixin, unittest.TestCase):
            scenarios_dir = (
                Path(__file__).parent / "test_files" / "missing_initial_state"
            )

            def run_scenario(self, scenario_name: str) -> None:
                pass

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_a"))
        result = unittest.TextTestRunner().run(suite)
        self.assertFalse(result.wasSuccessful())

    def test_missing_final_state(self):
        class TestClass(ScenarioTestCaseMixin, unittest.TestCase):
            scenarios_dir = Path(__file__).parent / "test_files" / "missing_final_state"

            def run_scenario(self, scenario_name: str) -> None:
                pass

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_a"))
        result = unittest.TextTestRunner().run(suite)
        self.assertFalse(result.wasSuccessful())

    def test_equal_dirs(self):
        class TestClass(ScenarioTestCaseMixin, unittest.TestCase):
            scenarios_dir = Path(__file__).parent / "test_files" / "equal_dirs"

            def run_scenario(self, scenario_name: str) -> None:
                pass

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_a"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())

    def test_not_equal_dirs(self):
        class TestClass(ScenarioTestCaseMixin, unittest.TestCase):
            scenarios_dir = Path(__file__).parent / "test_files" / "not_equal_dirs"

            def run_scenario(self, scenario_name: str) -> None:
                pass

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_a"))
        result = unittest.TextTestRunner().run(suite)
        self.assertFalse(result.wasSuccessful())

    def test_equal_tars(self):
        class TestClass(ScenarioTestCaseMixin, unittest.TestCase):
            scenarios_dir = Path(__file__).parent / "test_files" / "equal_tars"

            def run_scenario(self, scenario_name: str) -> None:
                pass

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_a"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())

    def test_not_equal_tars(self):
        class TestClass(ScenarioTestCaseMixin, unittest.TestCase):
            scenarios_dir = Path(__file__).parent / "test_files" / "not_equal_tars"

            def run_scenario(self, scenario_name: str) -> None:
                pass

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_a"))
        result = unittest.TextTestRunner().run(suite)
        self.assertFalse(result.wasSuccessful())

    def test_equal_zips(self):
        class TestClass(ScenarioTestCaseMixin, unittest.TestCase):
            scenarios_dir = Path(__file__).parent / "test_files" / "equal_zips"

            def run_scenario(self, scenario_name: str) -> None:
                pass

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_a"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())

    def test_not_equal_zips(self):
        class TestClass(ScenarioTestCaseMixin, unittest.TestCase):
            scenarios_dir = Path(__file__).parent / "test_files" / "not_equal_zips"

            def run_scenario(self, scenario_name: str) -> None:
                pass

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_a"))
        result = unittest.TextTestRunner().run(suite)
        self.assertFalse(result.wasSuccessful())

    def test_names_equal(self):
        class TestClass(ScenarioTestCaseMixin, unittest.TestCase):
            scenarios_dir = Path(__file__).parent / "test_files" / "not_equal_dirs"
            check_strategy = ScenarioTestCaseMixin.OutputChecking.FILE_NAMES

            def run_scenario(self, scenario_name: str) -> None:
                pass

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_a"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())

    def test_names_not_equal(self):
        class TestClass(ScenarioTestCaseMixin, unittest.TestCase):
            scenarios_dir = Path(__file__).parent / "test_files" / "diff_names"
            check_strategy = ScenarioTestCaseMixin.OutputChecking.FILE_NAMES

            def run_scenario(self, scenario_name: str) -> None:
                pass

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_a"))
        result = unittest.TextTestRunner().run(suite)
        self.assertFalse(result.wasSuccessful())

    def test_no_check(self):
        class TestClass(ScenarioTestCaseMixin, unittest.TestCase):
            scenarios_dir = Path(__file__).parent / "test_files" / "diff_names"
            check_strategy = ScenarioTestCaseMixin.OutputChecking.NONE

            def run_scenario(self, scenario_name: str) -> None:
                pass

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_a"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())
