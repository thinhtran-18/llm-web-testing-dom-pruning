"""DOM Pruning module implementing Full, Tag Filter, Task-Only, and Task+Condition modes."""

from typing import Any, Dict, List, Optional, Set, Tuple

from ..browser.models import DOMNode, DOMSnapshot
from ..browser.target_mapper import TargetObjectMapper
from .models import PrunedDOMResult, PrunedNode
from .tokenizer import DOMTokenizer


class DOMPruner:
    """Prunes DOM snapshots according to 4 modes with reason tracking and token budget control."""

    VALID_MODES = {"full", "tag_filter", "task_only", "task_condition"}

    def __init__(self, target_mapper: Optional[TargetObjectMapper] = None):
        self.target_mapper = target_mapper or TargetObjectMapper()

    def prune(
        self,
        snapshot: DOMSnapshot,
        mode: str = "task_condition",
        step: Optional[Dict[str, Any]] = None,
        conditions: Optional[List[Dict[str, Any]]] = None,
        token_budget: Optional[int] = None,
    ) -> PrunedDOMResult:
        """Prune DOM snapshot according to chosen mode and optional token budget."""
        if mode not in self.VALID_MODES:
            raise ValueError(f"Invalid mode '{mode}'. Expected one of {self.VALID_MODES}")

        if mode == "full":
            return self._prune_full(snapshot, token_budget)
        elif mode == "tag_filter":
            return self._prune_tag_filter(snapshot, token_budget)
        elif mode == "task_only":
            return self._prune_task_only(snapshot, step, token_budget)
        elif mode == "task_condition":
            return self._prune_task_condition(snapshot, step, conditions, token_budget)

    def _calculate_node_token(self, node: DOMNode) -> int:
        line = node.format_line()
        return DOMTokenizer.count_tokens(line)

    def _prune_full(self, snapshot: DOMSnapshot, budget: Optional[int]) -> PrunedDOMResult:
        """Full mode: keep all observable nodes."""
        pruned_nodes: List[PrunedNode] = []
        for node in snapshot.nodes:
            cost = self._calculate_node_token(node)
            pruned_nodes.append(PrunedNode(node=node, reason="full_snapshot", token_cost=cost))

        return self._apply_budget_and_build(
            observation_id=snapshot.observation_id,
            mode="full",
            pruned_nodes=pruned_nodes,
            budget=budget,
        )

    def _prune_tag_filter(self, snapshot: DOMSnapshot, budget: Optional[int]) -> PrunedDOMResult:
        """Tag filter mode: keep interactive elements and semantic text/headings."""
        pruned_nodes: List[PrunedNode] = []
        for node in snapshot.nodes:
            if node.is_interactive:
                cost = self._calculate_node_token(node)
                pruned_nodes.append(PrunedNode(node=node, reason="tag_interactive", token_cost=cost))
            elif node.role in ("heading", "label") or (node.tag.startswith("h") and len(node.tag) == 2):
                cost = self._calculate_node_token(node)
                pruned_nodes.append(PrunedNode(node=node, reason="tag_text", token_cost=cost))
            elif node.text and len(node.text) <= 100 and node.role == "text":
                cost = self._calculate_node_token(node)
                pruned_nodes.append(PrunedNode(node=node, reason="tag_text", token_cost=cost))

        return self._apply_budget_and_build(
            observation_id=snapshot.observation_id,
            mode="tag_filter",
            pruned_nodes=pruned_nodes,
            budget=budget,
        )

    def _prune_task_only(
        self,
        snapshot: DOMSnapshot,
        step: Optional[Dict[str, Any]],
        budget: Optional[int],
    ) -> PrunedDOMResult:
        """Method A - Task-only DOM Pruning: Keeps only action target and immediate action context."""
        step = step or {}
        target_spec = step.get("target", {})
        entity = target_spec.get("entity", "").lower()
        role = target_spec.get("role", "").lower()
        name = target_spec.get("name", "").lower()
        scope = target_spec.get("scope", "").lower()

        action_target_nodes: List[DOMNode] = []
        action_label_nodes: List[DOMNode] = []
        other_candidates: List[DOMNode] = []

        for node in snapshot.nodes:
            node_role = (node.role or "").lower()
            node_name = (node.name or "").lower()
            node_scope = (node.scope or "").lower()
            node_text = (node.text or "").lower()

            is_target_role = not role or (node_role == role)
            is_target_name = not name or (name in node_name or name in node_text)
            matches_scope_or_entity = (
                (scope and scope in node_scope)
                or (entity and (entity in node_scope or entity in node_text or entity in node.attributes.get("data-entity", "").lower()))
            )

            if is_target_role and is_target_name and (matches_scope_or_entity or not (scope or entity)):
                action_target_nodes.append(node)
                continue

            if matches_scope_or_entity and (node.role in ("heading", "label", "text") or entity in node_text):
                action_label_nodes.append(node)
                continue

            if node.is_interactive:
                other_candidates.append(node)

        pruned_nodes: List[PrunedNode] = []
        seen_ids = set()

        for n in action_target_nodes:
            if n.node_id not in seen_ids:
                pruned_nodes.append(PrunedNode(node=n, reason="action_target", token_cost=self._calculate_node_token(n)))
                seen_ids.add(n.node_id)

        for n in action_label_nodes:
            if n.node_id not in seen_ids:
                pruned_nodes.append(PrunedNode(node=n, reason="action_label", token_cost=self._calculate_node_token(n)))
                seen_ids.add(n.node_id)

        for n in other_candidates:
            if n.node_id not in seen_ids:
                pruned_nodes.append(PrunedNode(node=n, reason="interactive_candidate", token_cost=self._calculate_node_token(n)))
                seen_ids.add(n.node_id)

        return self._apply_budget_and_build(
            observation_id=snapshot.observation_id,
            mode="task_only",
            pruned_nodes=pruned_nodes,
            budget=budget,
        )

    def _prune_task_condition(
        self,
        snapshot: DOMSnapshot,
        step: Optional[Dict[str, Any]],
        conditions: Optional[List[Dict[str, Any]]],
        budget: Optional[int],
    ) -> PrunedDOMResult:
        """Method B - Task + Condition DOM Pruning: Guarantees Minimal Evidence constraint for Test Oracle."""
        step = step or {}
        target_spec = step.get("target", {})
        entity = target_spec.get("entity", "").lower()
        role = target_spec.get("role", "").lower()
        name = target_spec.get("name", "").lower()
        scope = target_spec.get("scope", "").lower()

        check_spec = step.get("check", {})
        check_ref = check_spec.get("ref", {})
        check_scope = check_ref.get("scope", "").lower()
        check_entity = check_ref.get("entity", "").lower()
        check_field = check_ref.get("field", "").lower()
        check_landmark = (check_spec.get("landmark") or "").lower()

        # Extract target_objects from conditions
        condition_target_objects = set()
        if conditions:
            for cond in conditions:
                if "target_object" in cond:
                    condition_target_objects.add(cond["target_object"].lower())

        # If check_ref is provided, map to target_object if possible
        if check_scope and check_entity and check_field:
            ref_target = self.target_mapper.find_target_object_by_ref(check_scope, check_entity, check_field)
            if ref_target:
                condition_target_objects.add(ref_target.lower())

        action_target_nodes: List[DOMNode] = []
        action_label_nodes: List[DOMNode] = []
        condition_evidence_nodes: List[DOMNode] = []
        container_context_nodes: List[DOMNode] = []
        other_candidates: List[DOMNode] = []

        for node in snapshot.nodes:
            node_role = (node.role or "").lower()
            node_name = (node.name or "").lower()
            node_scope = (node.scope or "").lower()
            node_text = (node.text or "").lower()
            node_target_obj = (node.target_object or "").lower()
            node_selector = (node.selector or "").lower()
            node_testid = (node.attributes.get("data-testid") or "").lower()

            # Check 1: Action Target
            is_target_role = not role or (node_role == role)
            is_target_name = not name or (name in node_name or name in node_text)
            matches_scope_or_entity = (
                (scope and scope in node_scope)
                or (entity and (entity in node_scope or entity in node_text or entity in node.attributes.get("data-entity", "").lower()))
            )

            if is_target_role and is_target_name and (matches_scope_or_entity or not (scope or entity)):
                action_target_nodes.append(node)
                continue

            # Check 2: Condition Evidence (Minimal Evidence for Test Oracle)
            is_evidence = False

            # 2a. Direct match with target_object
            if node_target_obj and node_target_obj in condition_target_objects:
                is_evidence = True
            elif node_testid and node_testid in condition_target_objects:
                is_evidence = True

            # 2b. Selector match in target mapper
            if not is_evidence and condition_target_objects:
                for target_obj in condition_target_objects:
                    mapped_sel = self.target_mapper.get_selector(target_obj)
                    if mapped_sel and (mapped_sel.lower() == node_selector or mapped_sel.lower() in node_selector):
                        is_evidence = True
                        break

            # 2c. Match with check_ref (scope, entity, field)
            if not is_evidence and (check_scope or check_entity or check_field):
                in_check_scope = not check_scope or (check_scope in node_scope or check_scope in node_text)
                in_check_entity = not check_entity or (check_entity in node_scope or check_entity in node_text)
                if in_check_scope and in_check_entity:
                    # Look for field (e.g. quantity element, or number element)
                    if check_field in ("số lượng", "quantity"):
                        if "item-qty" in node.attributes.get("class", "") or "qty" in node.attributes.get("id", "") or (node.role == "text" and node_text.isdigit()):
                            is_evidence = True
                    elif check_field in node_text or check_field in node_name:
                        is_evidence = True

            # 2d. Landmark match
            if not is_evidence and check_landmark and (check_landmark in node_text or check_landmark in node_name):
                is_evidence = True

            if is_evidence:
                condition_evidence_nodes.append(node)
                continue

            # Check 3: Action Label
            if matches_scope_or_entity and (node.role in ("heading", "label", "text") or entity in node_text):
                action_label_nodes.append(node)
                continue

            # Check 4: Container Context
            if check_scope and check_scope in node_scope and (node.role in ("heading", "text", "row")):
                container_context_nodes.append(node)
                continue

            # Check 5: Other interactive
            if node.is_interactive:
                other_candidates.append(node)

        # Build prioritized list:
        # P1 (Minimal Evidence Cluster): Action Target + Condition Evidence
        # P2: Action Label
        # P3: Container Context
        # P4: Other candidates
        pruned_nodes: List[PrunedNode] = []
        seen_ids = set()

        for n in action_target_nodes:
            if n.node_id not in seen_ids:
                pruned_nodes.append(PrunedNode(node=n, reason="action_target", token_cost=self._calculate_node_token(n)))
                seen_ids.add(n.node_id)

        for n in condition_evidence_nodes:
            if n.node_id not in seen_ids:
                pruned_nodes.append(PrunedNode(node=n, reason="condition_evidence", token_cost=self._calculate_node_token(n)))
                seen_ids.add(n.node_id)

        for n in action_label_nodes:
            if n.node_id not in seen_ids:
                pruned_nodes.append(PrunedNode(node=n, reason="action_label", token_cost=self._calculate_node_token(n)))
                seen_ids.add(n.node_id)

        for n in container_context_nodes:
            if n.node_id not in seen_ids:
                pruned_nodes.append(PrunedNode(node=n, reason="container_context", token_cost=self._calculate_node_token(n)))
                seen_ids.add(n.node_id)

        for n in other_candidates:
            if n.node_id not in seen_ids:
                pruned_nodes.append(PrunedNode(node=n, reason="interactive_candidate", token_cost=self._calculate_node_token(n)))
                seen_ids.add(n.node_id)

        return self._apply_budget_and_build(
            observation_id=snapshot.observation_id,
            mode="task_condition",
            pruned_nodes=pruned_nodes,
            budget=budget,
        )

    def _apply_budget_and_build(
        self,
        observation_id: str,
        mode: str,
        pruned_nodes: List[PrunedNode],
        budget: Optional[int],
    ) -> PrunedDOMResult:
        """Enforces token budget and constructs final PrunedDOMResult."""
        header = f"# Observation: {observation_id} (Mode: {mode})"
        header_tokens = DOMTokenizer.count_tokens(header)

        retained: List[PrunedNode] = []
        running_tokens = header_tokens
        budget_exceeded = False

        for pnode in pruned_nodes:
            cost = pnode.token_cost
            if budget is not None:
                if running_tokens + cost > budget:
                    budget_exceeded = True
                    break
            retained.append(pnode)
            running_tokens += cost

        result = PrunedDOMResult(
            observation_id=observation_id,
            mode=mode,
            nodes=retained,
            token_count=running_tokens,
            token_budget=budget,
            budget_exceeded=budget_exceeded,
        )
        result.to_text()
        return result
