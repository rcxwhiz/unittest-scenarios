# Josh Bedwell © 2025

import unittest
from pathlib import Path

from src.unittest_scenarios import ScenarioTestCaseMixin


class TestScenarioMixin(unittest.TestCase):

    def test_subclass_requirement(self):
        """Test unittest.TestCase subclass requirement"""

        class BadClass(ScenarioTestCaseMixin):
            scenarios_dir = Path(__file__).parent / "test_files" / "equal_dirs"

        with self.assertRaises(TypeError):
            _ = BadClass()

    def test_missing_run_func(self):
        """Test error when no run scenario function provided"""

        class TestClass(ScenarioTestCaseMixin, unittest.TestCase):
            scenarios_dir = Path(__file__).parent / "test_files" / "equal_dirs"

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_a"))
        result = unittest.TextTestRunner().run(suite)
        self.assertFalse(result.wasSuccessful())

    def test_run_func_runs(self):
        """Demonstrate the run scenario function is called by modifying an external value"""

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
        """Test an error is raised when no scenario directory provided"""

        class TestClass(ScenarioTestCaseMixin, unittest.TestCase):

            def run_scenario(self, scenario_name: str) -> None:
                pass

        with self.assertRaises(AttributeError):
            _ = TestClass()

    def test_bad_scenario_dir(self):
        """Tests an error is raised when the scenarios dir does not exist"""

        class TestClass(ScenarioTestCaseMixin, unittest.TestCase):
            scenarios_dir = "qwertyuiop"

            def run_scenario(self, scenario_name: str) -> None:
                pass

        with self.assertRaises(FileNotFoundError):
            _ = TestClass()

    def test_missing_initial_state(self):
        """Tests that a scenario can run without an initial state"""

        expected_text = """    def run_scenario(self, scenario_name: str) -> None:
        raise NotImplementedError("Please provide a function for running a scenario")
"""

        class TestClass(ScenarioTestCaseMixin, unittest.TestCase):
            scenarios_dir = (
                Path(__file__).parent / "test_files" / "missing_initial_state"
            )

            def run_scenario(self, scenario_name: str) -> None:
                with open("a.txt", "w") as f:
                    f.write(expected_text)

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_a"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())

    def test_missing_final_state(self):
        """Tests that a scenario can run and will pass without a final state"""

        class TestClass(ScenarioTestCaseMixin, unittest.TestCase):
            scenarios_dir = Path(__file__).parent / "test_files" / "missing_final_state"

            def run_scenario(self, scenario_name: str) -> None:
                pass

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_a"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())

    def test_equal_dirs(self):
        """Show correct checking behavior for dirs that are the same"""

        class TestClass(ScenarioTestCaseMixin, unittest.TestCase):
            scenarios_dir = Path(__file__).parent / "test_files" / "equal_dirs"

            def run_scenario(self, scenario_name: str) -> None:
                pass

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_a"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())

    def test_not_equal_dirs(self):
        """Shows correct checking behavior for dirs that are not the same"""

        class TestClass(ScenarioTestCaseMixin, unittest.TestCase):
            scenarios_dir = Path(__file__).parent / "test_files" / "not_equal_dirs"

            def run_scenario(self, scenario_name: str) -> None:
                pass

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_a"))
        result = unittest.TextTestRunner().run(suite)
        self.assertFalse(result.wasSuccessful())

    def test_equal_tars(self):
        """Shows correct checking behavior for tars that are the same"""

        class TestClass(ScenarioTestCaseMixin, unittest.TestCase):
            scenarios_dir = Path(__file__).parent / "test_files" / "equal_tars"

            def run_scenario(self, scenario_name: str) -> None:
                pass

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_a"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())

    def test_not_equal_tars(self):
        """Shows correct checking behavior for tars that are not the same"""

        class TestClass(ScenarioTestCaseMixin, unittest.TestCase):
            scenarios_dir = Path(__file__).parent / "test_files" / "not_equal_tars"

            def run_scenario(self, scenario_name: str) -> None:
                pass

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_a"))
        result = unittest.TextTestRunner().run(suite)
        self.assertFalse(result.wasSuccessful())

    def test_equal_zips(self):
        """Shows correct checking behavior for zips that are the same"""

        class TestClass(ScenarioTestCaseMixin, unittest.TestCase):
            scenarios_dir = Path(__file__).parent / "test_files" / "equal_zips"

            def run_scenario(self, scenario_name: str) -> None:
                pass

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_a"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())

    def test_not_equal_zips(self):
        """Shows correct checking behavior for zips that are not the same"""

        class TestClass(ScenarioTestCaseMixin, unittest.TestCase):
            scenarios_dir = Path(__file__).parent / "test_files" / "not_equal_zips"

            def run_scenario(self, scenario_name: str) -> None:
                pass

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_a"))
        result = unittest.TextTestRunner().run(suite)
        self.assertFalse(result.wasSuccessful())

    def test_names_equal(self):
        """Shows correct checking behavior when only names need to be the same"""

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
        """Shows correct name checking behavior with different names"""

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
        """Tests that no check will pass even with nothing in common"""

        class TestClass(ScenarioTestCaseMixin, unittest.TestCase):
            scenarios_dir = Path(__file__).parent / "test_files" / "diff_names"
            check_strategy = ScenarioTestCaseMixin.OutputChecking.NONE

            def run_scenario(self, scenario_name: str) -> None:
                pass

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_a"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())

    def test_fully_archived_scenario(self):
        """Tests that an entire scenario can be given as an archive"""

        class TestClass(ScenarioTestCaseMixin, unittest.TestCase):
            scenarios_dir = Path(__file__).parent / "test_files" / "zipped_scenario"

            def run_scenario(self, scenario_name: str) -> None:
                pass

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_a"))
        result = unittest.TextTestRunner().run(suite)
        self.assertTrue(result.wasSuccessful())

    def test_multiple_initial_states(self):
        class TestClass(ScenarioTestCaseMixin, unittest.TestCase):
            scenarios_dir = Path(__file__).parent / "test_files" / "multiple_initials"

            def run_scenario(self, scenario_name: str) -> None:
                pass

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_a"))
        result = unittest.TextTestRunner().run(suite)
        self.assertFalse(result.wasSuccessful())

    def test_multiple_final_states(self):
        class TestClass(ScenarioTestCaseMixin, unittest.TestCase):
            scenarios_dir = Path(__file__).parent / "test_files" / "multiple_finals"

            def run_scenario(self, scenario_name: str) -> None:
                pass

        suite = unittest.TestSuite()
        suite.addTest(TestClass("test_a"))
        result = unittest.TextTestRunner().run(suite)
        self.assertFalse(result.wasSuccessful())
