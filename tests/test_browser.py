"""Tests for BrowserController and DOMExtractor with Playwright and Chromium."""

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from webtest.browser import BrowserController


class TestBrowserController(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.demo_url = (ROOT / "demo" / "store.html").resolve().as_uri()
        cls.controller = BrowserController(headless=True)
        cls.controller.start()

    @classmethod
    def tearDownClass(cls):
        cls.controller.close()

    def setUp(self):
        self.controller.navigate(self.demo_url)

    def test_dom_snapshot_extraction(self):
        snapshot = self.controller.capture_snapshot("obs-test-01")
        self.assertEqual(snapshot.observation_id, "obs-test-01")
        self.assertGreater(len(snapshot.nodes), 5)

        # Check catalog title node
        title_nodes = [n for n in snapshot.nodes if "Cửa hàng Trực tuyến" in n.text]
        self.assertTrue(len(title_nodes) >= 1)
        self.assertEqual(title_nodes[0].role, "heading")

    def test_scope_disambiguation_buttons_with_same_label(self):
        """Core Giai đoạn 1 experiment:
        Disambiguate two buttons that have identical label 'Thêm vào giỏ'
        located in two distinct scopes (Product A vs Product B).
        """
        snapshot = self.controller.capture_snapshot("obs-disambiguation")

        # Find all buttons with label 'Thêm vào giỏ'
        buttons = [n for n in snapshot.nodes if n.role == "button" and "Thêm vào giỏ" in n.name]
        self.assertEqual(len(buttons), 2, "Must find exactly two buttons with label 'Thêm vào giỏ'")

        # Button 1 belongs to Product A
        btn_a = self.controller.locate_node_by_target(
            role="button",
            name="Thêm vào giỏ",
            scope="Sản phẩm A",
        )
        self.assertIsNotNone(btn_a)
        self.assertEqual(btn_a.attributes.get("id"), "btn-add-a")
        self.assertEqual(btn_a.scope, "Sản phẩm A")

        # Button 2 belongs to Product B
        btn_b = self.controller.locate_node_by_target(
            role="button",
            name="Thêm vào giỏ",
            scope="Sản phẩm B",
        )
        self.assertIsNotNone(btn_b)
        self.assertEqual(btn_b.attributes.get("id"), "btn-add-b")
        self.assertEqual(btn_b.scope, "Sản phẩm B")

        # Ensure their selectors are distinct and scoped
        self.assertNotEqual(btn_a.selector, btn_b.selector)

    def test_execute_agent_action_click_and_observe_state_change(self):
        """Execute click on Product A button and verify quantity increments from 1 to 2."""
        snapshot_before = self.controller.capture_snapshot("obs-before-add")
        btn_a = self.controller.locate_node_by_target(
            role="button",
            name="Thêm vào giỏ",
            scope="Sản phẩm A",
        )
        self.assertIsNotNone(btn_a)

        # Execute Agent Action adhering to agent-action.schema.json
        action_cmd = {
            "schema_version": "0.1",
            "observation_id": snapshot_before.observation_id,
            "action": "click",
            "target_id": btn_a.node_id,
        }
        res = self.controller.execute_action(action_cmd)
        self.assertEqual(res["status"], "success")

        # Settle
        self.controller.wait_for_settle(settle_ms=100)

        # Capture snapshot after action
        snapshot_after = self.controller.capture_snapshot("obs-after-add")
        qty_node = [n for n in snapshot_after.nodes if n.attributes.get("data-testid") == "cart_item_quantity_A"][0]
        self.assertEqual(qty_node.text, "2")


if __name__ == "__main__":
    unittest.main()

