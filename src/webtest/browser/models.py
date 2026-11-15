"""Data models for DOM nodes and snapshots."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class DOMNode:
    """Represents an observable element in the DOM tree."""
    node_id: str
    tag: str
    role: str
    name: str = ""
    text: str = ""
    value: Optional[str] = None
    scope: Optional[str] = None
    container_selector: Optional[str] = None
    selector: str = ""
    attributes: Dict[str, Any] = field(default_factory=dict)
    is_interactive: bool = False
    is_visible: bool = True
    target_object: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "tag": self.tag,
            "role": self.role,
            "name": self.name,
            "text": self.text,
            "value": self.value,
            "scope": self.scope,
            "container_selector": self.container_selector,
            "selector": self.selector,
            "attributes": self.attributes,
            "is_interactive": self.is_interactive,
            "is_visible": self.is_visible,
            "target_object": self.target_object,
        }

    def format_line(self) -> str:
        """Format node for compact serialized representation."""
        role_tag = self.role or self.tag
        el_id = self.attributes.get("id")
        testid = self.attributes.get("data-testid")
        if el_id:
            role_tag += f"#{el_id}"
        elif testid:
            role_tag += f"[{testid}]"

        parts = [f"[{self.node_id}]", role_tag]
        if self.name:
            parts.append(f'"{self.name}"')
        elif self.text and len(self.text) <= 50:
            parts.append(f'"{self.text}"')
        if self.value:
            parts.append(f'val="{self.value}"')
        if self.scope:
            parts.append(f'in [{self.scope}]')
        return " ".join(parts)


@dataclass
class DOMSnapshot:
    """Snapshot of observable DOM state at a specific observation milestone."""
    observation_id: str
    url: str
    title: str = ""
    timestamp: float = 0.0
    nodes: List[DOMNode] = field(default_factory=list)

    def get_node_by_id(self, node_id: str) -> Optional[DOMNode]:
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        return None

    def get_node_by_selector(self, selector: str) -> Optional[DOMNode]:
        for node in self.nodes:
            if node.selector == selector:
                return node
        return None

    def find_nodes(
        self,
        role: Optional[str] = None,
        name: Optional[str] = None,
        scope: Optional[str] = None,
        entity: Optional[str] = None,
        is_interactive: Optional[bool] = None,
    ) -> List[DOMNode]:
        """Find matching nodes with optional filters."""
        results = []
        for node in self.nodes:
            if role and node.role != role:
                continue
            if name and name.lower() not in (node.name or "").lower() and name.lower() not in (node.text or "").lower():
                continue
            if scope and (not node.scope or scope.lower() not in node.scope.lower()):
                continue
            if entity:
                matches_entity = (
                    (node.scope and entity.lower() in node.scope.lower())
                    or (node.attributes.get("data-entity", "").lower() == entity.lower())
                    or (entity.lower() in (node.text or "").lower())
                )
                if not matches_entity:
                    continue
            if is_interactive is not None and node.is_interactive != is_interactive:
                continue
            results.append(node)
        return results

    def to_dict(self) -> Dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "url": self.url,
            "title": self.title,
            "timestamp": self.timestamp,
            "nodes": [node.to_dict() for node in self.nodes],
        }
