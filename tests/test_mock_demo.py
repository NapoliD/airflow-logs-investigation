"""The mock demo has to run end to end on a clean checkout.

It is the first thing anyone does with this repository, it depends on nothing
but the standard library, and it reads every mock fixture on the way through —
so running it is also the cheapest check that the fixtures are still coherent.
"""

import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import mock_demo  # noqa: E402  (path has to be set up first)


class MockDataFixtures(unittest.TestCase):
    """Every fixture the demo reads must exist and parse."""

    def test_mock_data_directory_resolves(self):
        self.assertTrue(mock_demo.MOCK_DATA_DIR.is_dir(),
                        f"missing mock data directory: {mock_demo.MOCK_DATA_DIR}")

    def test_every_json_fixture_parses(self):
        files = sorted(mock_demo.MOCK_DATA_DIR.rglob("*.json"))
        self.assertTrue(files, "no JSON fixtures found")
        for path in files:
            with self.subTest(fixture=path.relative_to(REPO_ROOT)):
                with open(path, encoding="utf-8") as handle:
                    json.load(handle)

    def test_environment_fixture_has_the_fields_the_demo_reads(self):
        env = mock_demo.load_json(
            mock_demo.MOCK_DATA_DIR / "config" / "mwaa_environment.json")["Environment"]
        for field in ("Name", "Status", "AirflowVersion", "EnvironmentClass", "WebserverUrl"):
            self.assertIn(field, env)

    def test_task_log_fixtures_are_present(self):
        logs = sorted((mock_demo.MOCK_DATA_DIR / "s3").rglob("*.log"))
        self.assertTrue(logs, "no task log fixtures under mock_data/s3")


class DemoRun(unittest.TestCase):
    """The seven investigation steps, start to finish."""

    def test_demo_runs_clean(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            mock_demo.main()
        output = buffer.getvalue()
        self.assertIn("Demo completed successfully!", output)

    def test_analysis_step_identifies_a_root_cause(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            analysis = mock_demo.step6_analyze_failure()
        self.assertIsInstance(analysis, dict)
        self.assertTrue(analysis, "step 6 returned an empty analysis")


if __name__ == "__main__":
    unittest.main()
