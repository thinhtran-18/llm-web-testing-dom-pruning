import re
from typing import List, TypedDict, Optional, Any, Dict
from playwright.sync_api import Page, Locator, ConsoleMessage, Response, TimeoutError

# Định nghĩa kiểu dữ liệu cho nhật ký lỗi
class TraceLog(TypedDict, total=False):
    type: str
    condition_id: Optional[str]
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
            locator: Locator = self.page.locator(selector).first
            state = "visible" if expect_visible else "hidden"
            
            locator.wait_for(state=state, timeout=self.ORACLE_WAIT)
            return "PASS"
        except TimeoutError:
            return "ONR"

    def oracle_text_match(self, selector: str, expected_text: str, exact_match: bool = False) -> str:
        """
        2. Oracle Khớp văn bản (Text Match - 1 phần tử)
        """
        try:
            locator: Locator = self.page.locator(selector).first
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
            return "NLE"

    def oracle_text_match_all(self, selector: str, expected_text: str, exact_match: bool = False) -> str:
        """
        2b. Oracle Khớp văn bản cho NHIỀU kết quả cùng lúc (Hỗ trợ ca Tìm kiếm / Lọc TK-01, TK-03)
        """
        try:
            locator: Locator = self.page.locator(selector)
            locator.first.wait_for(state="visible", timeout=self.ORACLE_WAIT)
            
            all_texts = [t.strip() for t in locator.all_inner_texts()]
            if not all_texts:
                return "ONR"

            for idx, actual_text in enumerate(all_texts):
                is_match = (actual_text == expected_text) if exact_match else (expected_text in actual_text)
                if not is_match:
                    self.trace_logs.append({
                        "type": "OracleMismatch",
                        "message": f"Phần tử thứ {idx + 1} không khớp",
                        "expected": expected_text,
                        "actual": actual_text
                    })
                    return "ONR"
            return "PASS"
        except TimeoutError:
            return "NLE"

    def oracle_increase_decrease(self, selector: str, before_value: int, expected_diff: int) -> str:
        """
        3. Oracle Tăng/Giảm (Increase/Decrease)
        """
        try:
            locator: Locator = self.page.locator(selector).first
            locator.wait_for(state="visible", timeout=self.ORACLE_WAIT)
            
            actual_text = locator.inner_text().strip()
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
            has_crash = any(
                log.get("type") == "Crash" or (log.get("type") == "NetworkError" and log.get("status", 0) >= 500)
                for log in self.trace_logs
            )
            if has_crash:
                return "Crash"
                
            self.trace_logs.append({
                "type": "NavigationTimeout",
                "message": "Hết hạn Navigation Wait (30s) nhưng trang chưa đạt trạng thái ổn định",
                "actualUrl": self.page.url
            })
            return "INCONCLUSIVE"

    # ==========================================
    # PHẦN 3: CHẤM CA NHIỀU ĐIỀU KIỆN & GHI LỖI HỆ THỐNG (ĐỐI SOÁT GĐ 3 & 4)
    # ==========================================

    def record_system_issue(self, issue_type: str, expected: Any = None, actual: Any = None, message: str = "") -> str:
        """
        Ghi nhận các lượt Agent bấm sai phần tử ('AgentWrongAction') 
        hoặc bộ lọc DOM cắt mất bằng chứng ('MissingEvidence').
        """
        self.trace_logs.append({
            "type": issue_type,
            "message": message,
            "expected": expected,
            "actual": actual
        })
        return "INCONCLUSIVE"

    def evaluate_conditions(
        self,
        conditions: List[Dict[str, Any]],
        pruned_dom_targets: Optional[List[str]] = None
    ) -> str:
        """
        Chấm một ca kiểm thử có 1 hoặc nhiều điều kiện JSON:
        - Ca chỉ PASS khi MỌI điều kiện đều PASS.
        - Điều kiện nào trượt trước sẽ dừng ngay và lấy nhãn của điều kiện đó.
        - Nếu truyền danh sách phần tử giữ lại sau cắt tỉa (pruned_dom_targets) mà thiếu target_object,
          hệ thống tự động ghi nhận MissingEvidence và trả về INCONCLUSIVE.
        """
        # Nếu trước đó trang đã sập (Crash) thì chốt Crash ngay
        if any(log.get("type") == "Crash" for log in self.trace_logs):
            return "Crash"

        for cond in conditions:
            cond_id = cond.get("condition_id", "")
            target = cond.get("target_object", "")
            operator = cond.get("comparison_operator", "")
            expected = cond.get("expected_value")
            before_val = cond.get("before_value", 0)

            # Kiểm tra bằng chứng tối thiểu trong DOM đã cắt tỉa (nếu có truyền vào)
            if pruned_dom_targets is not None and target != "page_url":
                if target not in pruned_dom_targets:
                    return self.record_system_issue(
                        issue_type="MissingEvidence",
                        expected=target,
                        actual="Bị cắt khỏi DOM",
                        message=f"Bộ cắt tỉa DOM làm mất phần tử đích của điều kiện {cond_id}"
                    )

            # Gọi hàm Oracle tương ứng với phép so sánh (comparison_operator)
            result = "INCONCLUSIVE"
            if operator == "url_contains":
                result = self.oracle_url(str(expected))
            elif operator == "is_visible":
                result = self.oracle_presence(target, True)
            elif operator == "is_hidden":
                result = self.oracle_presence(target, False)
            elif operator == "text_exact_match":
                result = self.oracle_text_match(target, str(expected), exact_match=True)
            elif operator == "text_contains":
                result = self.oracle_text_match(target, str(expected), exact_match=False)
            elif operator == "text_match_all":
                result = self.oracle_text_match_all(target, str(expected), exact_match=False)
            elif operator == "increase":
                result = self.oracle_increase_decrease(target, int(before_val), int(expected))
            elif operator == "decrease":
                result = self.oracle_increase_decrease(target, int(before_val), -abs(int(expected)))

            # Nếu điều kiện hiện tại trượt -> dừng ngay và lấy nhãn của điều kiện đó
            if result != "PASS":
                self.trace_logs.append({
                    "type": "FailedCondition",
                    "condition_id": cond_id,
                    "message": f"Trượt tại điều kiện {cond_id} với nhãn {result}"
                })
                return result

        return "PASS"