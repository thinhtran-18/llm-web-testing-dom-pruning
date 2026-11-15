"""Tests for DOMPruner across all 4 modes, token budget, and Minimal Evidence constraint."""

import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from webtest.browser import BrowserController
from webtest.pruning import DOMPruner, DOMTokenizer


class TestDOMPruner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.demo_url = (ROOT / "demo" / "store.html").resolve().as_uri()
        cls.controller = BrowserController(headless=True)
        cls.controller.start()
        cls.controller.navigate(cls.demo_url)
        cls.snapshot = cls.controller.capture_snapshot("obs-pruner-test")
        cls.pruner = DOMPruner()

        # Load standard case from dataset
        cls.cart_case = json.loads((ROOT / "datasets" / "cases" / "cart-quantity.json").read_text(encoding="utf-8"))
        cls.step = cls.cart_case["steps"][0]

    @classmethod
    def tearDownClass(cls):
        cls.controller.close()

    def test_mode_full(self):
        result = self.pruner.prune(self.snapshot, mode="full")
        self.assertEqual(result.mode, "full")
        self.assertEqual(len(result.nodes), len(self.snapshot.nodes))
        for p in result.nodes:
            self.assertEqual(p.reason, "full_snapshot")
        self.assertGreater(result.token_count, 0)
        self.assertFalse(result.budget_exceeded)

    def test_mode_tag_filter(self):
        result = self.pruner.prune(self.snapshot, mode="tag_filter")
        self.assertEqual(result.mode, "tag_filter")
        self.assertLess(len(result.nodes), len(self.snapshot.nodes))
        for p in result.nodes:
            self.assertIn(p.reason, ("tag_interactive", "tag_text"))

    def test_mode_task_only_retains_action_target_and_labels(self):
        """Method A: Retains action button and label in product scope."""
        result = self.pruner.prune(
            self.snapshot,
            mode="task_only",
            step=self.step,
        )
        self.assertEqual(result.mode, "task_only")

        # Action target must be btn-add-a
        target_nodes = [p for p in result.nodes if p.reason == "action_target"]
        self.assertEqual(len(target_nodes), 1)
        self.assertEqual(target_nodes[0].node.attributes.get("id"), "btn-add-a")

        # Must have action label for Product A
        label_nodes = [p for p in result.nodes if p.reason == "action_label"]
        self.assertTrue(len(label_nodes) >= 1)
        self.assertIn("Sản phẩm A", label_nodes[0].text)

    def test_mode_task_condition_retains_minimal_evidence(self):
        """Method B: Retains both action target AND condition evidence (cart quantity)."""
        conditions = [
            {
                "condition_id": "cart_add_01",
                "target_object": "cart_item_quantity_A",
                "comparison_operator": "increase",
                "expected_value": 1,
            }
        ]
        result = self.pruner.prune(
            self.snapshot,
            mode="task_condition",
            step=self.step,
            conditions=conditions,
        )
        self.assertEqual(result.mode, "task_condition")

        # Verify Action Target
        action_targets = [p for p in result.nodes if p.reason == "action_target"]
        self.assertEqual(len(action_targets), 1)
        self.assertEqual(action_targets[0].node.attributes.get("id"), "btn-add-a")

        # Verify Condition Evidence (quantity field of Product A in cart)
        evidence_nodes = [p for p in result.nodes if p.reason == "condition_evidence"]
        self.assertTrue(len(evidence_nodes) >= 1)
        self.assertEqual(evidence_nodes[0].node.attributes.get("data-testid"), "cart_item_quantity_A")

        # Verify pruned_dom_targets contains the target_object for Test Oracle
        self.assertIn("cart_item_quantity_A", result.pruned_dom_targets)

    def test_token_budget_enforcement_and_missing_evidence_contrast(self):
        """Core research comparison:
        Under same token budget (90 tokens):
        - Method A (Task-only) keeps action target and exhausts budget on product context -> DROPS cart quantity -> MissingEvidence!
        - Method B (Task+Condition) prioritizes minimal evidence cluster -> RETAINS cart quantity!
        """
        budget = 90
        conditions = [
            {
                "condition_id": "cart_add_01",
                "target_object": "cart_item_quantity_A",
                "comparison_operator": "increase",
            }
        ]

        # Method A: Task-only
        res_a = self.pruner.prune(
            self.snapshot,
            mode="task_only",
            step=self.step,
            token_budget=budget,
        )
        self.assertLessEqual(res_a.token_count, budget)
        # In Method A, cart_item_quantity_A is NOT retained
        self.assertNotIn("cart_item_quantity_A", res_a.pruned_dom_targets)

        # Method B: Task + Condition
        res_b = self.pruner.prune(
            self.snapshot,
            mode="task_condition",
            step=self.step,
            conditions=conditions,
            token_budget=budget,
        )
        self.assertLessEqual(res_b.token_count, budget)
        # In Method B, cart_item_quantity_A IS retained as Minimal Evidence
        self.assertIn("cart_item_quantity_A", res_b.pruned_dom_targets)

    def test_text_serialization_and_reasons_mapping(self):
        result = self.pruner.prune(
            self.snapshot,
            mode="task_condition",
            step=self.step,
        )
        text = result.to_text()
        self.assertIn("# Observation:", text)
        self.assertIn("btn-add-a", text)

        # Check reasons dict
        self.assertIsInstance(result.reasons, dict)
        for nid, reason in result.reasons.items():
            self.assertIn(reason, ("action_target", "action_label", "condition_evidence", "container_context", "interactive_candidate"))


if __name__ == "__main__":
    unittest.main()
