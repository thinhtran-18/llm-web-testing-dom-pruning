"""Unit tests for TargetObjectMapper."""

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from webtest.browser.target_mapper import TargetObjectMapper


class TestTargetObjectMapper(unittest.TestCase):
    def setUp(self):
        self.mapper = TargetObjectMapper()

    def test_default_mappings_exist(self):
        sel = self.mapper.get_selector("cart_item_quantity_A")
        self.assertEqual(sel, "#cart-item-quantity-a")

        # Reverse lookup for both primary and alias selector
        self.assertEqual(self.mapper.find_target_object_by_selector("#cart-item-quantity-a"), "cart_item_quantity_A")
        self.assertEqual(self.mapper.find_target_object_by_selector("#cart-item-a .item-qty"), "cart_item_quantity_A")

        btn_a = self.mapper.get_selector("btn_add_to_cart_A")
        self.assertEqual(btn_a, "#btn-add-a")

    def test_reverse_lookup(self):
        target = self.mapper.find_target_object_by_selector("#btn-add-a")
        self.assertEqual(target, "btn_add_to_cart_A")

    def test_ref_lookup(self):
        target = self.mapper.find_target_object_by_ref(
            scope="Giỏ hàng",
            entity="Sản phẩm A",
            field="Số lượng",
        )
        self.assertEqual(target, "cart_item_quantity_A")

    def test_custom_registration(self):
        self.mapper.register("custom_btn", "#custom-btn", "Nút tùy biến", "Header")
        self.assertEqual(self.mapper.get_selector("custom_btn"), "#custom-btn")
        self.assertEqual(self.mapper.find_target_object_by_selector("#custom-btn"), "custom_btn")


if __name__ == "__main__":
    unittest.main()
