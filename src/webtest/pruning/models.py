"""Data models for DOM pruning results and pruned nodes."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..browser.models import DOMNode


@dataclass
class PrunedNode:
    """A DOM node retained during pruning, tagged with retention reason and token cost."""
    node: DOMNode
    reason: str  # e.g., 'action_target', 'action_label', 'condition_evidence', 'container_context', 'tag_interactive', 'full_snapshot'
    token_cost: int = 0

    @property
    def node_id(self) -> str:
        return self.node.node_id

    @property
    def role(self) -> str:
        return self.node.role

    @property
    def name(self) -> str:
        return self.node.name

    @property
    def text(self) -> str:
        return self.node.text

    @property
    def selector(self) -> str:
        return self.node.selector

    @property
    def scope(self) -> Optional[str]:
        return self.node.scope

    @property
    def target_object(self) -> Optional[str]:
        return self.node.target_object

    def format_line(self) -> str:
        base = self.node.format_line()
        return f"{base} [reason={self.reason}]"


@dataclass
class PrunedDOMResult:
    """Encapsulates the pruned DOM representation, tokens, reasons, and target sets for Oracle."""
    observation_id: str
    mode: str
    nodes: List[PrunedNode] = field(default_factory=list)
    token_count: int = 0
    token_budget: Optional[int] = None
    budget_exceeded: bool = False
    serialized_text: str = ""

    @property
    def kept_node_ids(self) -> List[str]:
        """List of node IDs retained in pruned DOM."""
        return [p.node.node_id for p in self.nodes]

    @property
    def kept_selectors(self) -> List[str]:
        """List of selectors retained in pruned DOM."""
        return [p.node.selector for p in self.nodes]

    @property
    def reasons(self) -> Dict[str, str]:
        """Mapping from node_id to retention reason."""
        return {p.node.node_id: p.reason for p in self.nodes}

    @property
    def pruned_dom_targets(self) -> List[str]:
        """List of target identifiers retained in pruned DOM for Test Oracle evaluate_conditions.
        Contains:
        1. target_object names (e.g., 'cart_item_quantity_A')
        2. selectors (e.g., '#cart-item-a .item-qty')
        3. node_ids (e.g., 'n-21')
        4. scope/entity descriptions (e.g., 'Giỏ hàng:Sản phẩm A:Số lượng')
        This ensures 100% compatibility with Mai's TestOracle.evaluate_conditions().
        """
        targets = set()
        for p in self.nodes:
            targets.add(p.node.node_id)
            targets.add(p.node.selector)
            if p.node.target_object:
                targets.add(p.node.target_object)
            if p.node.scope:
                targets.add(p.node.scope)
                if p.node.name:
                    targets.add(f"{p.node.scope}:{p.node.name}")
            if p.node.attributes.get("data-testid"):
                targets.add(p.node.attributes["data-testid"])
        return sorted(list(targets))

    def to_text(self) -> str:
        """Compact serialized text representation for LLM prompt."""
        if self.serialized_text:
            return self.serialized_text
        lines = [f"# Observation: {self.observation_id} (Mode: {self.mode}, Tokens: {self.token_count})"]
        for p in self.nodes:
            lines.append(p.node.format_line())
        self.serialized_text = "\n".join(lines)
        return self.serialized_text

    def to_dict(self) -> Dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "mode": self.mode,
            "token_count": self.token_count,
            "token_budget": self.token_budget,
            "budget_exceeded": self.budget_exceeded,
            "kept_node_ids": self.kept_node_ids,
            "reasons": self.reasons,
            "nodes": [
                {
                    "node_id": p.node.node_id,
                    "reason": p.reason,
                    "token_cost": p.token_cost,
                    "line": p.node.format_line(),
                    "selector": p.node.selector,
                    "target_object": p.node.target_object,
                }
                for p in self.nodes
            ],
            "serialized_text": self.to_text(),
        }

