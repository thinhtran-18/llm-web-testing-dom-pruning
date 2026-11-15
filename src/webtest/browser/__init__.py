"""Browser and DOM extraction package."""

from .browser_controller import BrowserController
from .dom_extractor import DOMExtractor
from .models import DOMNode, DOMSnapshot
from .target_mapper import DEFAULT_TARGET_OBJECT_MAP, TargetObjectMapper

__all__ = [
    "BrowserController",
    "DOMExtractor",
    "DOMNode",
    "DOMSnapshot",
    "TargetObjectMapper",
    "DEFAULT_TARGET_OBJECT_MAP",
]

