"""Browser Controller: Manages Playwright Chromium lifecycle, page interactions, and snapshots."""

import time
from typing import Any, Dict, List, Optional

from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

from .dom_extractor import DOMExtractor
from .models import DOMNode, DOMSnapshot
from .target_mapper import TargetObjectMapper


class BrowserController:
    """Controls Playwright Chromium, executes agent actions, and extracts DOM snapshots."""

    def __init__(
        self,
        headless: bool = True,
        target_mapper: Optional[TargetObjectMapper] = None,
        slow_mo: int = 0,
    ):
        self.headless = headless
        self.slow_mo = slow_mo
        self.target_mapper = target_mapper or TargetObjectMapper()
        self.extractor = DOMExtractor(self.target_mapper)

        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self.current_snapshot: Optional[DOMSnapshot] = None

        # Trace and telemetry events
        self.console_logs: List[Dict[str, Any]] = []
        self.page_errors: List[str] = []
        self.network_errors: List[Dict[str, Any]] = []

    def start(self) -> Page:
        """Launch Chromium browser and open a fresh page."""
        if not self._playwright:
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(
                headless=self.headless,
                slow_mo=self.slow_mo,
            )
            self._context = self._browser.new_context()
            self._page = self._context.new_page()
            self._setup_listeners(self._page)
        return self._page

    def _setup_listeners(self, page: Page) -> None:
        """Register event listeners for crashes, console errors, and HTTP failures."""
        page.on(
            "console",
            lambda msg: self.console_logs.append({
                "type": msg.type,
                "text": msg.text,
                "time": time.time(),
            }) if msg.type in ("error", "warning") else None
        )
        page.on(
            "pageerror",
            lambda exc: self.page_errors.append(str(exc))
        )
        page.on(
            "response",
            lambda res: self.network_errors.append({
                "url": res.url,
                "status": res.status,
                "time": time.time(),
            }) if res.status >= 400 else None
        )

    @property
    def page(self) -> Page:
        if not self._page:
            self.start()
        return self._page

    def navigate(self, url: str, wait_until: str = "load") -> None:
        """Navigate to a URL and wait for specified state."""
        self.page.goto(url, wait_until=wait_until)

    def capture_snapshot(self, observation_id: Optional[str] = None) -> DOMSnapshot:
        """Capture and cache observable DOM snapshot."""
        snapshot = self.extractor.extract_from_page(self.page, observation_id)
        self.current_snapshot = snapshot
        return snapshot

    def locate_node_by_target(
        self,
        role: str,
        name: str,
        scope: Optional[str] = None,
        entity: Optional[str] = None,
    ) -> Optional[DOMNode]:
        """Disambiguate and locate a node within snapshot based on role, name, and scope/entity.
        Solves the critical requirement: định vị nút cùng nhãn trong hai vùng khác nhau.
        """
        if not self.current_snapshot:
            self.capture_snapshot()

        candidates = self.current_snapshot.find_nodes(
            role=role,
            name=name,
            scope=scope,
            entity=entity,
        )
        if len(candidates) == 1:
            return candidates[0]
        elif len(candidates) > 1:
            # If multiple match, prioritize exact scope match
            if scope:
                for cand in candidates:
                    if cand.scope and scope.lower() == cand.scope.lower():
                        return cand
            return candidates[0]
        return None

    def execute_action(self, action_cmd: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent action adhering to contracts/agent-action.schema.json."""
        target_id = action_cmd.get("target_id")
        action = action_cmd.get("action")
        value = action_cmd.get("value", "")
        obs_id = action_cmd.get("observation_id")

        if not self.current_snapshot:
            raise RuntimeError("No active snapshot available to execute action")

        node = self.current_snapshot.get_node_by_id(target_id)
        if not node:
            raise ValueError(f"Target node {target_id} not found in current snapshot {self.current_snapshot.observation_id}")

        selector = node.selector
        locator = self.page.locator(selector)

        if action == "click":
            locator.click()
        elif action == "fill":
            locator.fill(value)
        elif action == "select":
            locator.select_option(value)
        elif action == "check":
            locator.check()
        elif action == "uncheck":
            locator.uncheck()
        else:
            raise ValueError(f"Unsupported action: {action}")

        return {
            "status": "success",
            "action": action,
            "target_id": target_id,
            "selector": selector,
            "scope": node.scope,
        }

    def wait_for_settle(self, settle_ms: int = 200, timeout_ms: int = 3000) -> None:
        """Wait for page stabilization."""
        self.page.wait_for_timeout(settle_ms)

    def close(self) -> None:
        """Tear down browser context."""
        if self._context:
            self._context.close()
            self._context = None
        if self._browser:
            self._browser.close()
            self._browser = None
        if self._playwright:
            self._playwright.stop()
            self._playwright = None
        self._page = None
        self.current_snapshot = None

