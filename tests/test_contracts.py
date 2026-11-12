import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.action = self.validator_for("agent-action")
        self.case = self.validator_for("test-case")

    def validator_for(self, name):
        schema = read_json(ROOT / "contracts" / f"{name}.schema.json")
        Draft202012Validator.check_schema(schema)
        return Draft202012Validator(schema)

    def test_examples_match_case_schema_and_labels(self):
        labels = read_json(ROOT / "datasets" / "labels" / "pilot.json")
        cases = [read_json(path) for path in (ROOT / "datasets" / "cases").glob("*.json")]
        self.assertEqual(len(cases), 3)
        for case in cases:
            with self.subTest(case_id=case["case_id"]):
                self.case.validate(case)
                step_ids = [step["step_id"] for step in case["steps"]]
                self.assertEqual(len(step_ids), len(set(step_ids)))
                for step in case["steps"]:
                    self.assertLessEqual(step["wait"]["settle_ms"], step["wait"]["timeout_ms"])
        self.assertCountEqual([case["case_id"] for case in cases], [label["case_id"] for label in labels])
        self.assertCountEqual([label["fault"]["expected_verdict"] for label in labels], ["ONR", "NLE", "CRASH"])

    def test_click_uses_current_snapshot_reference(self):
        self.action.validate({
            "schema_version": "0.1",
            "observation_id": "obs-1",
            "action": "click",
            "target_id": "n-21",
        })

    def test_fill_requires_value(self):
        command = {
            "schema_version": "0.1",
            "observation_id": "obs-1",
            "action": "fill",
            "target_id": "n-22",
        }
        self.assertFalse(self.action.is_valid(command))
        self.action.validate({**command, "value": ""})
