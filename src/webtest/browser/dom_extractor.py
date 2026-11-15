"""DOM Extractor: Extracts structured observable nodes and snapshots from Playwright pages."""

import time
from typing import Any, Dict, List, Optional

from .models import DOMNode, DOMSnapshot
from .target_mapper import TargetObjectMapper


JS_EXTRACTOR_SCRIPT = """
() => {
    function isVisible(el) {
        if (!el) return false;
        const style = window.getComputedStyle(el);
        if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
            return false;
        }
        const rect = el.getBoundingClientRect();
        return rect.width > 0 || rect.height > 0 || el.getClientRects().length > 0;
    }

    function getAccessibleRole(el) {
        const roleAttr = el.getAttribute('role');
        if (roleAttr) return roleAttr.toLowerCase();

        const tag = el.tagName.toLowerCase();
        if (tag === 'button') return 'button';
        if (tag === 'a' && el.hasAttribute('href')) return 'link';
        if (tag === 'input') {
            const type = (el.getAttribute('type') || 'text').toLowerCase();
            if (['button', 'submit', 'reset'].includes(type)) return 'button';
            if (type === 'checkbox') return 'checkbox';
            if (type === 'radio') return 'radio';
            return 'textbox';
        }
        if (tag === 'select') return 'combobox';
        if (tag === 'textarea') return 'textbox';
        if (/^h[1-6]$/.test(tag)) return 'heading';
        if (tag === 'p' || tag === 'span' || tag === 'b' || tag === 'strong' || tag === 'em') return 'text';
        if (tag === 'li') return 'listitem';
        if (tag === 'ul' || tag === 'ol') return 'list';
        if (tag === 'form') return 'form';
        if (tag === 'table') return 'table';
        if (tag === 'tr') return 'row';
        if (tag === 'td' || tag === 'th') return 'cell';
        return 'generic';
    }

    function getAccessibleName(el) {
        if (el.getAttribute('aria-label')) {
            return el.getAttribute('aria-label').trim();
        }
        if (el.getAttribute('title')) {
            return el.getAttribute('title').trim();
        }
        if (el.getAttribute('placeholder')) {
            return el.getAttribute('placeholder').trim();
        }
        if (el.tagName.toLowerCase() === 'input' && ['button', 'submit'].includes((el.type || '').toLowerCase())) {
            return (el.value || '').trim();
        }
        // Direct or descendant text
        const text = (el.innerText || el.textContent || '').trim();
        if (text && text.length <= 80) {
            return text;
        }
        return '';
    }

    function getContainerScope(el) {
        let curr = el.parentElement;
        while (curr && curr !== document.body) {
            if (curr.getAttribute('data-scope')) {
                return curr.getAttribute('data-scope').trim();
            }
            if (curr.getAttribute('data-entity')) {
                return curr.getAttribute('data-entity').trim();
            }
            if (curr.getAttribute('data-testid')) {
                return curr.getAttribute('data-testid').trim();
            }
            const id = curr.id;
            if (id) {
                if (id.includes('product-card-a') || id.includes('product-a')) return 'Sản phẩm A';
                if (id.includes('product-card-b') || id.includes('product-b')) return 'Sản phẩm B';
                if (id.includes('cart-item-a')) return 'Giỏ hàng / Sản phẩm A';
                if (id.includes('cart-item-b')) return 'Giỏ hàng / Sản phẩm B';
                if (id.includes('cart')) return 'Giỏ hàng';
                if (id.includes('catalog')) return 'Danh mục';
                if (id.includes('checkout')) return 'Thanh toán';
                if (id.includes('profile')) return 'Hồ sơ';
                return id;
            }
            const cls = curr.className || '';
            if (typeof cls === 'string') {
                if (cls.includes('product-card-a')) return 'Sản phẩm A';
                if (cls.includes('product-card-b')) return 'Sản phẩm B';
                if (cls.includes('cart-section') || cls.includes('cart-container')) return 'Giỏ hàng';
            }
            curr = curr.parentElement;
        }
        return '';
    }

    function generateUniqueSelector(el) {
        if (el.id) {
            return '#' + CSS.escape(el.id);
        }
        if (el.getAttribute('data-testid')) {
            return `[data-testid="${CSS.escape(el.getAttribute('data-testid'))}"]`;
        }
        const path = [];
        let curr = el;
        while (curr && curr.nodeType === Node.ELEMENT_NODE && curr !== document.body) {
            if (curr.id) {
                path.unshift('#' + CSS.escape(curr.id));
                break;
            }
            let selector = curr.tagName.toLowerCase();
            const parent = curr.parentElement;
            if (parent) {
                const siblings = Array.from(parent.children).filter(c => c.tagName === curr.tagName);
                if (siblings.length > 1) {
                    const idx = siblings.indexOf(curr) + 1;
                    selector += `:nth-of-type(${idx})`;
                }
            }
            path.unshift(selector);
            curr = curr.parentElement;
        }
        return path.join(' > ');
    }

    const allElements = Array.from(document.querySelectorAll('body *'));
    const results = [];
    let counter = 1;

    for (const el of allElements) {
        if (!isVisible(el)) continue;

        const tag = el.tagName.toLowerCase();
        if (['script', 'style', 'noscript', 'svg', 'path', 'meta', 'link'].includes(tag)) {
            continue;
        }

        const role = getAccessibleRole(el);
        const name = getAccessibleName(el);
        const text = (el.innerText || el.textContent || '').trim();
        const scope = getContainerScope(el);
        const selector = generateUniqueSelector(el);

        const isInteractive = (
            ['button', 'select', 'textarea'].includes(tag) ||
            (tag === 'input' && el.type !== 'hidden') ||
            (tag === 'a' && el.hasAttribute('href')) ||
            el.hasAttribute('onclick') ||
            ['button', 'link', 'checkbox', 'radio', 'combobox'].includes(role) ||
            el.tabIndex >= 0
        );

        const hasDirectText = Array.from(el.childNodes).some(
            n => n.nodeType === Node.TEXT_NODE && n.textContent.trim().length > 0
        );

        if (isInteractive || hasDirectText || ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'].includes(tag) || el.id || el.getAttribute('data-testid')) {
            const attrs = {};
            for (let i = 0; i < el.attributes.length; i++) {
                const attr = el.attributes[i];
                if (['id', 'class', 'data-testid', 'data-scope', 'data-entity', 'href', 'type', 'name'].includes(attr.name)) {
                    attrs[attr.name] = attr.value;
                }
            }

            results.push({
                node_id: `n-${counter++}`,
                tag: tag,
                role: role,
                name: name,
                text: text,
                value: el.value !== undefined ? String(el.value) : null,
                scope: scope,
                selector: selector,
                attributes: attrs,
                is_interactive: isInteractive,
                is_visible: true
            });
        }
    }

    return results;
}
"""


class DOMExtractor:
    """Extracts structured DOM nodes and snapshots from Playwright pages or HTML."""

    def __init__(self, target_mapper: Optional[TargetObjectMapper] = None):
        self.target_mapper = target_mapper or TargetObjectMapper()

    def extract_from_page(self, page, observation_id: Optional[str] = None) -> DOMSnapshot:
        """Extract observable snapshot from a live Playwright page."""
        obs_id = observation_id or f"obs-{int(time.time() * 1000) % 100000}"
        url = page.url
        title = page.title()

        raw_nodes = page.evaluate(JS_EXTRACTOR_SCRIPT)
        nodes: List[DOMNode] = []

        for item in raw_nodes:
            attrs = item.get("attributes", {})
            testid = attrs.get("data-testid")
            el_id = attrs.get("id")
            selector = item.get("selector", "")

            # 1. Match by data-testid
            target_obj = None
            if testid:
                if testid in self.target_mapper._map:
                    target_obj = testid
                else:
                    target_obj = self.target_mapper.find_target_object_by_selector(f'[data-testid="{testid}"]')

            # 2. Match by selector
            if not target_obj:
                target_obj = self.target_mapper.find_target_object_by_selector(selector)

            # 3. Match by ID
            if not target_obj and el_id:
                target_obj = self.target_mapper.find_target_object_by_selector(f"#{el_id}")

            node = DOMNode(
                node_id=item["node_id"],
                tag=item["tag"],
                role=item["role"],
                name=item["name"],
                text=item["text"],
                value=item.get("value"),
                scope=item.get("scope") or None,
                selector=selector,
                attributes=attrs,
                is_interactive=item.get("is_interactive", False),
                is_visible=item.get("is_visible", True),
                target_object=target_obj,
            )
            nodes.append(node)

        return DOMSnapshot(
            observation_id=obs_id,
            url=url,
            title=title,
            timestamp=time.time(),
            nodes=nodes,
        )
