from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from test_oracle import TestOracle

def run_demo() -> None:
    with sync_playwright() as p:
        browser: Browser = p.chromium.launch(headless=False)
        context: BrowserContext = browser.new_context()
        page: Page = context.new_page()

        # 1. Khởi tạo Oracle của Mai và bật giám sát
        oracle = TestOracle(page)
        oracle.attach_event_listeners()

        print("Đang truy cập trang web...")
        page.goto("https://demo.playwright.dev/todomvc/")

        # Giả lập Agent thao tác
        page.locator(".new-todo").fill("Học AI Agent")
        page.locator(".new-todo").press("Enter")

        # 2. Chạy riêng Oracle kiểm tra Text
        print("Đang chạy Oracle Text Match...")
        result_text = oracle.oracle_text_match(".todo-list li label", "Học AI Agent", True)
        print(f"Kết quả Text Match: {result_text}")

        # 3. Chạy riêng Oracle kiểm tra Tăng/Giảm
        print("Đang chạy Oracle Increase/Decrease...")
        result_count = oracle.oracle_increase_decrease(".todo-count strong", 0, 1)
        print(f"Kết quả Tăng/Giảm: {result_count}")

        # 4. Chạy thử ca kiểm thử gồm 2 điều kiện JSON kết hợp (giống ca GH-02 của Trang)
        print("Đang chấm ca kiểm thử có 2 điều kiện kết hợp...")
        conditions_sample = [
            {
                "condition_id": "todo_add_text",
                "target_object": ".todo-list li label",
                "comparison_operator": "text_exact_match",
                "expected_value": "Học AI Agent",
                "observation_milestone": "wait_for_dom_change"
            },
            {
                "condition_id": "todo_add_count",
                "target_object": ".todo-count strong",
                "comparison_operator": "increase",
                "before_value": 0,
                "expected_value": 1,
                "observation_milestone": "wait_for_dom_change"
            }
        ]
        final_label = oracle.evaluate_conditions(conditions_sample)
        print(f"Kết luận chung của ca 2 điều kiện: {final_label}")

        print("Nhật ký sự kiện trang:", oracle.get_traces())

        browser.close()

if __name__ == "__main__":
    run_demo()