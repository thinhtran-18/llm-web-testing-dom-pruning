import re
from typing import List, TypedDict, Optional, Any
from playwright.sync_api import Page, Locator, ConsoleMessage, Response, TimeoutError

# Định nghĩa kiểu dữ liệu cho nhật ký lỗi
class TraceLog(TypedDict, total=False):
    type: str
    message: Optional[str]
    text: Optional[str]
    status: Optional[int]
    url: Optional[str]
    expected: Optional[Any]
    actual: Optional[Any]
    expectedPath: Optional[str]
    actualUrl: Optional[str]


class TestOracle:
    def __init__(self, page: Page):
        self.page: Page = page
        # Cửa sổ chờ (đơn vị: milliseconds)
        self.ACTION_WAIT: int = 5000
        self.ORACLE_WAIT: int = 10000
        self.NAVIGATION_WAIT: int = 30000
        
        self.trace_logs: List[TraceLog] = []

    # ==========================================
    # PHẦN 1: GHI SỰ KIỆN CỦA TRANG (EVENT LISTENERS)
    # ==========================================
    
    def attach_event_listeners(self) -> None:
        # Bắt lỗi sập trang (Crash)
        def handle_page_error(exception: Exception) -> None:
            self.trace_logs.append({
                "type": "Crash",
                "message": f"Page crashed: {str(exception)}"
            })

        # Bắt lỗi Console
        def handle_console(msg: ConsoleMessage) -> None:
            if msg.type == "error":
                self.trace_logs.append({
                    "type": "ConsoleError",
                    "text": msg.text
                })

        # Bắt lỗi Mạng (HTTP 4xx, 5xx)
        def handle_response(response: Response) -> None:
            if response.status >= 400:
                self.trace_logs.append({
                    "type": "NetworkError",
                    "status": response.status,
                    "url": response.url
                })

        self.page.on("pageerror", handle_page_error)
        self.page.on("console", handle_console)
        self.page.on("response", handle_response)

    def get_traces(self) -> List[TraceLog]:
        return self.trace_logs

    # ==========================================
    # PHẦN 2: CÁC HÀM ORACLE ĐỐI CHIẾU TRẠNG THÁI
    # ==========================================

    def oracle_presence(self, selector: str, expect_visible: bool = True) -> str:
        """
        1. Oracle Có mặt (Presence)
        """
        try:
            locator: Locator = self.page.locator(selector)
            state = "visible" if expect_visible else "hidden"
            
            # Chờ mốc quan sát
            locator.wait_for(state=state, timeout=self.ORACLE_WAIT)
            return "PASS"
        except TimeoutError:
            # Hết hạn chờ mà trạng thái không đổi
            return "ONR"

    def oracle_text_match(self, selector: str, expected_text: str, exact_match: bool = False) -> str:
        """
        2. Oracle Khớp văn bản (Text Match)
        """
        try:
            locator: Locator = self.page.locator(selector)
            locator.wait_for(state="visible", timeout=self.ORACLE_WAIT)
            
            actual_text = locator.inner_text().strip()
            is_match = (actual_text == expected_text) if exact_match else (expected_text in actual_text)
            
            if is_match:
                return "PASS"
            else:
                self.trace_logs.append({
                    "type": "OracleMismatch",
                    "expected": expected_text,
                    "actual": actual_text
                })
                return "ONR"
        except TimeoutError:
            # Không tìm thấy phần tử để lấy text
            return "NLE"

    def oracle_increase_decrease(self, selector: str, before_value: int, expected_diff: int) -> str:
        """
        3. Oracle Tăng/Giảm (Increase/Decrease)
        """
        try:
            locator: Locator = self.page.locator(selector)
            locator.wait_for(state="visible", timeout=self.ORACLE_WAIT)
            
            actual_text = locator.inner_text().strip()
            # Lọc lấy số từ chuỗi (VD: "Tổng: 2" -> lấy 2)
            numbers = re.findall(r"\d+", actual_text)
            
            if not numbers:
                return "ONR"
            
            after_value = int(numbers[0])
            expected_after = before_value + expected_diff
            
            if after_value == expected_after:
                return "PASS"
            else:
                self.trace_logs.append({
                    "type": "OracleMismatch",
                    "expected": expected_after,
                    "actual": after_value
                })
                return "ONR"
        except TimeoutError:
            return "NLE"

    def oracle_url(self, expected_path: str) -> str:
        """
        4. Oracle URL (Điều hướng)
        """
        try:
            # Bắt buộc chờ mạng rảnh rỗi để qua các chuyển hướng trung gian
            self.page.wait_for_load_state("networkidle", timeout=self.NAVIGATION_WAIT)
            current_url = self.page.url
            
            if expected_path in current_url:
                return "PASS"
            else:
                self.trace_logs.append({
                    "type": "OracleMismatch",
                    "expectedPath": expected_path,
                    "actualUrl": current_url
                })
                return "NLE"
        except TimeoutError:
            # Vượt quá 30s trang không tải xong
            return "Crash"