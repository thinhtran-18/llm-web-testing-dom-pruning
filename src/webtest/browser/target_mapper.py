"""Target Object Mapper: maps logical target object identifiers to selectors and vice versa."""

from typing import Dict, List, Optional, Tuple


# Default mapping table for e-commerce demo cases
DEFAULT_TARGET_OBJECT_MAP: Dict[str, Dict[str, str]] = {
    # Catalog elements
    "catalog_title": {
        "selector": "#catalog-title",
        "description": "Tiêu đề danh mục sản phẩm",
        "scope": "Danh mục",
    },
    "product_card_A": {
        "selector": "#product-card-a",
        "description": "Thẻ sản phẩm A",
        "scope": "Danh mục",
    },
    "product_name_A": {
        "selector": "#product-name-a",
        "description": "Tên sản phẩm A",
        "scope": "Sản phẩm A",
    },
    "product_price_A": {
        "selector": "#product-price-a",
        "description": "Giá sản phẩm A",
        "scope": "Sản phẩm A",
    },
    "btn_add_to_cart_A": {
        "selector": "#btn-add-a",
        "description": "Nút Thêm vào giỏ của Sản phẩm A",
        "scope": "Sản phẩm A",
    },
    "product_card_B": {
        "selector": "#product-card-b",
        "description": "Thẻ sản phẩm B",
        "scope": "Danh mục",
    },
    "btn_add_to_cart_B": {
        "selector": "#btn-add-b",
        "description": "Nút Thêm vào giỏ của Sản phẩm B",
        "scope": "Sản phẩm B",
    },
    # Cart elements
    "cart_badge_count": {
        "selector": "#cart-badge",
        "description": "Huy hiệu số lượng trên giỏ hàng header",
        "scope": "Header",
    },
    "cart_section": {
        "selector": "#cart-section",
        "description": "Khu vực giỏ hàng",
        "scope": "Giỏ hàng",
    },
    "cart_item_row_A": {
        "selector": "#cart-item-a",
        "description": "Dòng sản phẩm A trong giỏ",
        "scope": "Giỏ hàng",
    },
    "cart_item_quantity_A": {
        "selector": "#cart-item-quantity-a",
        "description": "Số lượng sản phẩm A trong giỏ hàng",
        "scope": "Giỏ hàng",
    },
    "cart_item_btn_inc_A": {
        "selector": "#btn-inc-a",
        "description": "Nút tăng số lượng sản phẩm A trong giỏ",
        "scope": "Giỏ hàng",
    },
    "cart_item_btn_dec_A": {
        "selector": "#btn-dec-a",
        "description": "Nút giảm số lượng sản phẩm A trong giỏ",
        "scope": "Giỏ hàng",
    },
    "cart_item_btn_remove_A": {
        "selector": "#btn-remove-a",
        "description": "Nút xóa sản phẩm A khỏi giỏ",
        "scope": "Giỏ hàng",
    },
    "cart_item_row_B": {
        "selector": "#cart-item-b",
        "description": "Dòng sản phẩm B trong giỏ",
        "scope": "Giỏ hàng",
    },
    "cart_item_quantity_B": {
        "selector": "#cart-item-quantity-b",
        "description": "Số lượng sản phẩm B trong giỏ hàng",
        "scope": "Giỏ hàng",
    },
    "cart_total_price": {
        "selector": "#cart-total-price",
        "description": "Tổng tiền đơn hàng trong giỏ",
        "scope": "Giỏ hàng",
    },
    "btn_checkout": {
        "selector": "#btn-checkout",
        "description": "Nút Thanh toán",
        "scope": "Giỏ hàng",
    },
    # Feedback / Toast / Alert
    "toast_message": {
        "selector": "#toast-message",
        "description": "Thông báo toast (ví dụ 'Đã thêm')",
        "scope": "Thông báo",
    },
    # Checkout & Profile
    "checkout_title": {
        "selector": "#checkout-title",
        "description": "Tiêu đề trang thanh toán",
        "scope": "Thanh toán",
    },
    "profile_save_btn": {
        "selector": "#btn-save-profile",
        "description": "Nút Lưu hồ sơ",
        "scope": "Hồ sơ",
    },
    "profile_saved_toast": {
        "selector": "#profile-saved-toast",
        "description": "Thông báo Đã lưu hồ sơ",
        "scope": "Hồ sơ",
    },
    "fatal_error_banner": {
        "selector": "#fatal-error-banner",
        "description": "Biểu ngữ lỗi sập nghiêm trọng",
        "scope": "Hệ thống",
    },
}

# Secondary selector aliases
SELECTOR_ALIASES: Dict[str, str] = {
    "#cart-item-a .item-qty": "cart_item_quantity_A",
    "#cart-item-b .item-qty": "cart_item_quantity_B",
    "#cart-item-a .btn-inc": "cart_item_btn_inc_A",
    "#cart-item-a .btn-dec": "cart_item_btn_dec_A",
    "#cart-item-a .btn-remove": "cart_item_btn_remove_A",
    '[data-testid="cart_item_quantity_A"]': "cart_item_quantity_A",
    '[data-testid="cart_item_quantity_B"]': "cart_item_quantity_B",
    '[data-testid="btn-add-a"]': "btn_add_to_cart_A",
    '[data-testid="btn-add-b"]': "btn_add_to_cart_B",
}


class TargetObjectMapper:
    """Manages mapping between logical target object IDs, entity references, and real CSS selectors."""

    def __init__(self, mapping: Optional[Dict[str, Dict[str, str]]] = None):
        self._map = dict(DEFAULT_TARGET_OBJECT_MAP)
        if mapping:
            self._map.update(mapping)
        self._aliases = dict(SELECTOR_ALIASES)

    def register(self, target_object: str, selector: str, description: str = "", scope: str = "") -> None:
        """Register or override a target object mapping."""
        self._map[target_object] = {
            "selector": selector,
            "description": description,
            "scope": scope,
        }
        self._aliases[selector] = target_object

    def get_selector(self, target_object: str) -> Optional[str]:
        """Get CSS selector for target object."""
        entry = self._map.get(target_object)
        return entry["selector"] if entry else None

    def get_info(self, target_object: str) -> Optional[Dict[str, str]]:
        return self._map.get(target_object)

    def find_target_object_by_selector(self, selector: str) -> Optional[str]:
        """Reverse lookup: find target_object by selector."""
        if selector in self._aliases:
            return self._aliases[selector]

        sel_clean = selector.strip().lower()
        for name, meta in self._map.items():
            if meta["selector"].lower() == sel_clean:
                return name
        for alias, name in self._aliases.items():
            if alias.lower() == sel_clean:
                return name
        return None

    def find_target_object_by_ref(self, scope: str, entity: str, field: str) -> Optional[str]:
        """Lookup target object using (scope, entity, field) reference from test-case.schema.json."""
        s_scope = scope.lower()
        s_entity = entity.lower()
        s_field = field.lower()

        # Direct check for cart quantity
        if "giỏ hàng" in s_scope or "cart" in s_scope:
            if "sản phẩm a" in s_entity or "product a" in s_entity or s_entity == "a":
                if "số lượng" in s_field or "quantity" in s_field:
                    return "cart_item_quantity_A"
            elif "sản phẩm b" in s_entity or "product b" in s_entity or s_entity == "b":
                if "số lượng" in s_field or "quantity" in s_field:
                    return "cart_item_quantity_B"

        for name, meta in self._map.items():
            meta_desc = meta.get("description", "").lower()
            meta_scope = meta.get("scope", "").lower()
            if s_entity in meta_desc and s_field in meta_desc:
                if not scope or s_scope in meta_scope or s_scope in meta_desc:
                    return name
        return None

    def all_mappings(self) -> Dict[str, Dict[str, str]]:
        """Return a copy of all mappings."""
        return dict(self._map)
