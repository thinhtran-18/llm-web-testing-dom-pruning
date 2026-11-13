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

        # 2. Chạy Oracle kiểm tra Text
        print("Đang chạy Oracle Text Match...")
        result_text = oracle.oracle_text_match(".todo-list li label", "Học AI Agent", True)
        print(f"Kết quả Text Match: {result_text}")

        # 3. Chạy Oracle kiểm tra Tăng/Giảm
        print("Đang chạy Oracle Increase/Decrease...")
        result_count = oracle.oracle_increase_decrease(".todo-count strong", 0, 1)
        print(f"Kết quả Tăng/Giảm: {result_count}")

        print("Nhật ký sự kiện trang:", oracle.get_traces())

        browser.close()

if __name__ == "__main__":
    run_demo()