"""End-to-End integration test combining BrowserController and DOMPruner."""

import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from webtest.browser import BrowserController
from webtest.pruning import DOMPruner


class TestIntegrationFlow(unittest.TestCase):
    """Verifies full flow: snapshot -> prune -> action execution -> post-action snapshot -> condition verification."""

    @classmethod
    def setUpClass(cls):
        cls.demo_url = (ROOT / "demo" / "store.html").resolve().as_uri()
        cls.controller = BrowserController(headless=True)
        cls.controller.start()
        cls.pruner = DOMPruner()

        cls.cart_case = json.loads((ROOT / "datasets" / "cases" / "cart-quantity.json").read_text(encoding="utf-8"))
        cls.step = cls.cart_case["steps"][0]

    @classmethod
    def tearDownClass(cls):
        cls.controller.close()

    def setUp(self):
        self.controller.navigate(self.demo_url)

    def test_full_cycle_add_to_cart_with_pruning(self):
        # 1. Capture snapshot before action
        snap_before = self.controller.capture_snapshot("obs-pre")

        # 2. Prune DOM using task_condition
        conditions = [
            {
                "condition_id": "cart_add_01",
                "target_object": "cart_item_quantity_A",
                "comparison_operator": "increase",
                "expected_value": 1,
            }
        ]
        pruned_before = self.pruner.prune(
            snap_before,
            mode="task_condition",
            step=self.step,
            conditions=conditions,
            token_budget=120,
        )

        # Confirm minimal evidence is present in pruned representation
        self.assertIn("cart_item_quantity_A", pruned_before.pruned_dom_targets)

        # 3. Resolve action target from pruned nodes
        action_target_pnode = [p for p in pruned_before.nodes if p.reason == "action_target"][0]
        self.assertEqual(action_target_pnode.node.attributes.get("id"), "btn-add-a")

        # 4. Agent issues action JSON
        action_cmd = {
            "schema_version": "0.1",
            "observation_id": snap_before.observation_id,
            "action": "click",
            "target_id": action_target_pnode.node_id,
        }
        exec_res = self.controller.execute_action(action_cmd)
        self.assertEqual(exec_res["status"], "success")

        # Settle
        self.controller.wait_for_settle(settle_ms=100)

        # 5. Capture snapshot after action
        snap_after = self.controller.capture_snapshot("obs-post")
        pruned_after = self.pruner.prune(
            snap_after,
            mode="task_condition",
            step=self.step,
            conditions=conditions,
            token_budget=120,
        )

        # Verify evidence node in post snapshot has updated value '2'
        evidence_nodes = [p for p in pruned_after.nodes if p.reason == "condition_evidence"]
        self.assertTrue(len(evidence_nodes) >= 1)
        self.assertEqual(evidence_nodes[0].text, "2")


if __name__ == "__main__":
    unittest.main()

