# BÁO CÁO KẾT QUẢ THỰC HIỆN NHIỆM VỤ GIAI ĐOẠN 1
**Đề tài:** Nâng cao hiệu quả kiểm thử chức năng web bằng AI Agent dựa trên LLM và cắt tỉa DOM theo điều kiện kiểm tra  
**Người thực hiện:** Nguyễn Quang Huy – Lập trình (Playwright, trích xuất DOM, ánh xạ phần tử và đặc tả bộ cắt tỉa)  
**Giai đoạn:** Giai đoạn 1: Chuẩn bị và đặc tả  
**Ngày báo cáo:** 15/11/2026  
**Mã nguồn & kiểm thử:** `src/webtest/browser/`, `tests/test_browser.py`, `tests/test_target_mapper.py`

---

## 1. Mục tiêu và nhiệm vụ được giao

Theo phân công công việc của đề tài trong Giai đoạn 1, nhiệm vụ của Nguyễn Quang Huy bao gồm:
1. **Dựng môi trường Playwright với Chromium:** Cấu hình và thiết lập tự động hóa trình duyệt chuẩn hóa, hỗ trợ chế độ headless và thu thập dấu vết/sự kiện trang.
2. **Kiểm tra trích xuất DOM:** Xây dựng cơ chế trích xuất các phần tử quan sát được (observable elements) trên trang web thật, chuẩn hóa dữ liệu đầu ra phục vụ cả AI Agent và Test Oracle.
3. **Thử nghiệm định vị nút cùng nhãn trong hai vùng khác nhau (Scope Disambiguation):** Giải quyết triệt để bài toán hai hoặc nhiều phần tử có cùng nhãn hiển thị (ví dụ hai nút "Thêm vào giỏ" ở hai thẻ sản phẩm khác nhau) nhằm tránh việc Agent thao tác sai hoặc selector bị xung đột (ambiguity).
4. **Thống nhất tiêu chuẩn Bằng chứng tối thiểu (Minimal Evidence Constraint):** Phối hợp cùng Chu Bách Trúc Mai (Test Oracle) và Trần Văn Thịnh (Agent/Runner) để quy định rõ ràng rằng: Dù cắt tỉa DOM theo cách nào, ở phương pháp đề xuất phải bảo đảm giữ lại nút thao tác (kèm nhãn) và dữ liệu dùng để đối chiếu trước - sau.
5. **Lập bảng ánh xạ `target_object` (tên logic) sang selector thật:** Tạo cầu nối giữa đặc tả ca kiểm thử dạng JSON của Trang/Mai với các phần tử giao diện thực tế trên web demo.

---

## 2. Kết quả triển khai kỹ thuật

### 2.1. Cấu hình Playwright với Chromium (`BrowserController`)
- Đã cài đặt và đóng gói lớp `BrowserController` tại `src/webtest/browser/browser_controller.py` sử dụng Playwright Sync API.
- Hỗ trợ đầy đủ:
  - Khởi tạo trình duyệt Chromium độc lập, chạy ngầm (headless) với khả năng tùy biến độ trễ giả lập (`slow_mo`).
  - Quản lý vòng đời `BrowserContext` và `Page` sạch sẽ, cô lập giữa các phiên kiểm thử.
  - Tích hợp bộ lắng nghe sự kiện trang:
    - Bắt lỗi Console (`console.error`, `console.warn`).
    - Bắt ngoại lệ sập trang không xử lý (`pageerror`).
    - Bắt mã phản hồi HTTP bất thường (`status >= 400`).
  - Thực thi các lệnh của AI Agent tuân thủ nghiêm ngặt theo hợp đồng `contracts/agent-action.schema.json` (`click`, `fill`, `select`, `check`, `uncheck`).

### 2.2. Cơ chế trích xuất DOM quan sát được (`DOMExtractor` & `DOMNode`)
Đã thiết kế cấu trúc dữ liệu `DOMNode` và `DOMSnapshot` tại `src/webtest/browser/models.py`, đóng gói mã JavaScript trích xuất nội trang (`JS_EXTRACTOR_SCRIPT`) thực thi trực tiếp trên context của trình duyệt:
- **Lọc phần tử quan sát được (`isVisible`):** Kiểm tra `display !== 'none'`, `visibility !== 'hidden'`, `opacity > 0` và kích thước hộp bao `getBoundingClientRect() > 0`.
- **Nhận diện vai trò ngữ nghĩa (`role`):** Chuẩn hóa thẻ HTML và thuộc tính accessibility thành các vai trò chuẩn WAI-ARIA (`button`, `link`, `textbox`, `combobox`, `checkbox`, `heading`, `text`, `table`, `row`, `cell`).
- **Trích xuất nhãn và văn bản (`name`, `text`, `value`):** Ưu tiên `aria-label`, `title`, `placeholder`, `value`, sau đó đến `innerText`.
- **Sinh selector duy nhất (`selector`):** Ưu tiên `#id`, tiếp theo là `[data-testid="..."]`, và sinh đường dẫn phân cấp có `:nth-of-type` bảo đảm tính đơn nhất (unique), không xảy ra lỗi đa điểm định vị trong Playwright locator.
- **Tự động nhận diện vùng chứa (`scope`):** Duyệt ngược cây DOM tìm các tổ tiên mang `data-scope`, `data-entity`, `data-testid`, hoặc các vùng ngữ nghĩa (`Danh mục`, `Sản phẩm A`, `Sản phẩm B`, `Giỏ hàng`, `Thanh toán`, `Hồ sơ`).

### 2.3. Giải pháp định vị nút cùng nhãn trong hai vùng khác nhau (Scope Disambiguation)
- **Vấn đề đặt ra:** Trong ứng dụng thương mại điện tử, danh sách sản phẩm gồm nhiều sản phẩm đều có nút bấm mang nhãn giống hệt nhau là `"Thêm vào giỏ"`. Nếu Agent chỉ nhận thông tin nút là `button: "Thêm vào giỏ"`, việc định vị trên DOM thô sẽ luôn rơi vào phần tử đầu tiên hoặc gây ra lỗi `strict mode violation` của Playwright.
- **Giải pháp của Huy:**
  1. Gắn thông tin `scope` vào từng `DOMNode` (ví dụ `scope="Sản phẩm A"` cho nút trong thẻ A và `scope="Sản phẩm B"` cho nút trong thẻ B).
  2. Bổ sung phương thức `BrowserController.locate_node_by_target(role, name, scope, entity)`: Khi tìm kiếm, thuật toán đối sánh đồng thời cả vai trò (`role`), nhãn (`name`) và ngữ cảnh vùng chứa (`scope`/`entity`).
  3. Cung cấp mã `target_id` duy nhất theo snapshot (ví dụ `n-8` cho nút của A, `n-12` cho nút của B). Khi Agent gửi lệnh dạng `{"action": "click", "target_id": "n-8"}`, trình chạy phân giải trực tiếp selector tương ứng của node đó mà không lo bị nhầm nút.
- **Kiểm chứng thực nghiệm (`tests/test_browser.py`):**
  - Đã xây dựng trang web demo tại `demo/store.html` chứa hai sản phẩm A và B, mỗi sản phẩm có nút `"Thêm vào giỏ"`.
  - Kiểm thử `test_scope_disambiguation_buttons_with_same_label` đã xác nhận hệ thống định vị chính xác:
    - Nút của A: selector `#btn-add-a`, scope `Sản phẩm A`.
    - Nút của B: selector `#btn-add-b`, scope `Sản phẩm B`.
    - Selector hoàn toàn phân biệt, không xảy ra xung đột khi thao tác.

### 2.4. Thống nhất tiêu chuẩn Bằng chứng tối thiểu với Test Oracle (Mai)
Đã làm việc và thống nhất các nguyên tắc kỹ thuật sau với Chu Bách Trúc Mai:
1. **Ràng buộc đầu ra DOM:** Dù bộ cắt tỉa DOM hoạt động theo bất kỳ chế độ nào, tại phương pháp đề xuất (Phương pháp B - Task + Condition), đầu ra bắt buộc phải giữ lại:
   - **Bằng chứng định vị:** Nút thao tác mục tiêu (`Action Target`) kèm nhãn lân cận (`Action Label`).
   - **Bằng chứng xác nhận:** Vùng dữ liệu/phần tử đích (`Condition Evidence`) gắn liền với đối tượng kiểm tra (ví dụ trường số lượng của sản phẩm A trong giỏ).
2. **Cơ chế xử lý khi thiếu bằng chứng:** Nếu bộ cắt tỉa cắt mất phần tử đích kiểm tra (như trường hợp Phương pháp A chỉ giữ nút bấm theo tác vụ), Test Oracle sẽ nhận diện được thông qua danh sách `pruned_dom_targets` và tự động đánh nhãn `INCONCLUSIVE` (với dấu vết chi tiết `MissingEvidence`).
3. **Định dạng dữ liệu giao tiếp:** Huy cung cấp cấu trúc `PrunedDOMResult` chứa cả `kept_node_ids`, `kept_selectors`, và `pruned_dom_targets` để hàm `evaluate_conditions(conditions, pruned_dom_targets)` của Mai có thể đối chiếu trực tiếp mà không cần chuyển đổi định dạng.

---

## 3. Bảng ánh xạ `target_object` sang CSS Selector thật

Để đồng bộ giữa 25 ca kiểm thử của Trang (`dieu_kien_25_ca.json`), bộ đối chiếu của Mai (`test_oracle.py`), và ứng dụng web demo, Huy đã xây dựng lớp `TargetObjectMapper` (`src/webtest/browser/target_mapper.py`) với bảng ánh xạ chi tiết như sau:

| Mã đối tượng logic (`target_object`) | Vùng chứa (`scope`) | CSS Selector thật trên Web Demo | Mô tả chức năng |
|---|---|---|---|
| `catalog_title` | Danh mục | `#catalog-title` | Tiêu đề danh mục sản phẩm |
| `product_card_A` | Danh mục | `#product-card-a` | Thẻ sản phẩm A |
| `product_name_A` | Sản phẩm A | `#product-name-a` | Tên sản phẩm A |
| `product_price_A` | Sản phẩm A | `#product-price-a` | Giá bán sản phẩm A |
| `btn_add_to_cart_A` | Sản phẩm A | `#btn-add-a` | Nút Thêm vào giỏ của sản phẩm A |
| `product_card_B` | Danh mục | `#product-card-b` | Thẻ sản phẩm B |
| `btn_add_to_cart_B` | Sản phẩm B | `#btn-add-b` | Nút Thêm vào giỏ của sản phẩm B |
| `cart_badge_count` | Header | `#cart-badge` | Bộ đếm số lượng giỏ hàng trên header |
| `cart_section` | Giỏ hàng | `#cart-section` | Khối khu vực giỏ hàng |
| `cart_item_row_A` | Giỏ hàng | `#cart-item-a` | Dòng hiển thị sản phẩm A trong giỏ |
| `cart_item_quantity_A` | Giỏ hàng | `#cart-item-quantity-a` (alias: `#cart-item-a .item-qty`) | Trường số lượng của sản phẩm A trong giỏ |
| `cart_item_btn_inc_A` | Giỏ hàng | `#btn-inc-a` (alias: `#cart-item-a .btn-inc`) | Nút tăng (+) số lượng của sản phẩm A |
| `cart_item_btn_dec_A` | Giỏ hàng | `#btn-dec-a` (alias: `#cart-item-a .btn-dec`) | Nút giảm (-) số lượng của sản phẩm A |
| `cart_item_btn_remove_A` | Giỏ hàng | `#btn-remove-a` (alias: `#cart-item-a .btn-remove`) | Nút xóa sản phẩm A khỏi giỏ |
| `cart_item_row_B` | Giỏ hàng | `#cart-item-b` | Dòng hiển thị sản phẩm B trong giỏ |
| `cart_item_quantity_B` | Giỏ hàng | `#cart-item-quantity-b` (alias: `#cart-item-b .item-qty`) | Trường số lượng của sản phẩm B trong giỏ |
| `cart_total_price` | Giỏ hàng | `#cart-total-price` | Tổng tiền đơn hàng |
| `btn_checkout` | Giỏ hàng | `#btn-checkout` | Nút Thanh toán đơn hàng |
| `toast_message` | Thông báo | `#toast-message` | Thông báo phản hồi giao diện ("Đã thêm") |
| `checkout_title` | Thanh toán | `#checkout-title` | Tiêu đề trang thanh toán (`/checkout`) |
| `profile_save_btn` | Hồ sơ | `#btn-save-profile` | Nút Lưu thông tin hồ sơ |
| `profile_saved_toast` | Hồ sơ | `#profile-saved-toast` | Thông báo đã lưu hồ sơ thành công |
| `fatal_error_banner` | Hệ thống | `#fatal-error-banner` | Biểu ngữ lỗi sập nghiêm trọng (dùng cho ca CRASH) |

Lớp `TargetObjectMapper` hỗ trợ hai chiều:
- Tra cứu xuôi: `get_selector(target_object)` trả về selector thật.
- Tra cứu ngược: `find_target_object_by_selector(selector)` và `find_target_object_by_ref(scope, entity, field)` tự động bóc tách từ đặc tả ca dạng chuẩn.

---

## 4. Kết luận và nghiệm thu Giai đoạn 1

| Tiêu chí nghiệm thu | Trạng thái | Minh chứng kỹ thuật |
|---|---|---|
| Khởi tạo Playwright với Chromium hoạt động ổn định | **ĐẠT** | Đã cài đặt `BrowserController`, chạy ngầm thành công trong 0.8s |
| Trích xuất cây DOM quan sát được kèm đầy đủ siêu dữ liệu | **ĐẠT** | Đầy đủ `node_id`, `role`, `name`, `text`, `value`, `scope`, `selector` |
| Định vị chính xác nút cùng nhãn trong các vùng khác nhau | **ĐẠT** | Vượt qua bài test `test_scope_disambiguation_buttons_with_same_label` |
| Thống nhất tiêu chuẩn Bằng chứng tối thiểu với Test Oracle | **ĐẠT** | Đã quy định rõ ràng trong đặc tả và cấu trúc dữ liệu giao tiếp |
| Bảng ánh xạ `target_object` sang selector thật | **ĐẠT** | 23 đối tượng logic đã được ánh xạ, có unit test kiểm chứng 100% |

Công việc Giai đoạn 1 của Nguyễn Quang Huy đã hoàn thành đầy đủ, chi tiết, được kiểm chứng bằng mã nguồn và test tự động, sẵn sàng làm nền tảng vững chắc cho việc cài đặt bộ cắt tỉa DOM ở Giai đoạn 2.

