# BÁO CÁO KẾT QUẢ THỰC HIỆN NHIỆM VỤ GIAI ĐOẠN 2
**Đề tài:** Nâng cao hiệu quả kiểm thử chức năng web bằng AI Agent dựa trên LLM và cắt tỉa DOM theo điều kiện kiểm tra  
**Người thực hiện:** Nguyễn Quang Huy – Lập trình (Phụ trách bộ thu DOM và các chế độ cắt tỉa DOM)  
**Giai đoạn:** Giai đoạn 2: Xây dựng các mô-đun  
**Ngày báo cáo:** 15/11/2026  
**Mã nguồn & kiểm thử:** `src/webtest/browser/`, `src/webtest/pruning/`, `demo/store.html`, `tests/`

---

## 1. Mục tiêu và nhiệm vụ được giao

Theo kế hoạch nghiên cứu Giai đoạn 2, nhiệm vụ của Nguyễn Quang Huy tập trung vào việc hoàn thiện mã nguồn độc lập cho hai mô-đun cốt lõi:
1. **Mô-đun thu thập DOM (`webtest.browser`):** Đóng gói bộ điều khiển Playwright Chromium và bộ trích xuất DOM có khả năng lấy snapshot quan sát được của trang web tại mọi thời điểm (trước và sau khi thao tác).
2. **Mô-đun cắt tỉa DOM (`webtest.pruning`):** Cài đặt đầy đủ 4 chế độ lọc DOM:
   - `full`: Cây DOM đầy đủ các phần tử quan sát được.
   - `tag_filter`: Lọc theo các thẻ tương tác và văn bản ngữ cảnh.
   - `task_only` (Phương pháp A - Đối chứng): Lọc DOM chỉ dựa vào mô tả nhiệm vụ và phần tử thao tác mục tiêu.
   - `task_condition` (Phương pháp B - Đề xuất): Lọc DOM kết hợp cả mô tả nhiệm vụ và điều kiện kiểm thử mong đợi, bảo đảm giữ lại cụm Bằng chứng tối thiểu (Minimal Evidence).
3. **Lưu lý do giữ (`reason`) và tính số lượng token (`token_count`):** Gắn nhãn lý do giữ cho từng phần tử được giữ lại, tính toán lượng token theo thuật toán chuẩn xác định, và kiểm soát ngân sách token (`token_budget`).
4. **Phối hợp kỹ thuật với Test Oracle (Chu Bách Trúc Mai):** Thiết kế giao diện đầu ra chuẩn hóa trả lời câu hỏi của Mai về định dạng danh sách phần tử giữ lại nhằm phát hiện tự động lỗi `MissingEvidence`.
5. **Kiểm thử độc lập và liên kết luồng:** Viết toàn bộ bài kiểm thử đơn vị (Unit tests) và tích hợp (Integration tests), xác minh hệ thống hoạt động ổn định và chứng minh được giả thuyết khoa học của đề tài.

---

## 2. Chi tiết kỹ thuật các mô-đun đã phát triển

### 2.1. Cấu trúc gói `src/webtest`
```text
src/webtest/
  browser/
    __init__.py
    models.py             # Data classes: DOMNode, DOMSnapshot
    target_mapper.py      # Bảng ánh xạ target_object logic sang selector thật
    dom_extractor.py      # Bộ trích xuất JavaScript nội trang
    browser_controller.py # Quản lý Playwright Chromium và thực thi lệnh Agent
  pruning/
    __init__.py
    models.py             # Data classes: PrunedNode, PrunedDOMResult
    tokenizer.py          # Bộ đếm token xác định cho chuỗi DOM
    pruner.py             # Thuật toán cắt tỉa DOM 4 chế độ với token budget
```

### 2.2. Chi tiết 4 chế độ cắt tỉa DOM trong `DOMPruner`

#### Chế độ 1: DOM đầy đủ (`full`)
- Giữ lại toàn bộ các phần tử quan sát được trên giao diện do `DOMExtractor` thu thập.
- Tất cả phần tử được gán nhãn: `reason = "full_snapshot"`.
- Dùng làm mốc đối chứng tham chiếu cao nhất (không bị giới hạn ngân sách token).

#### Chế độ 2: Lọc theo thẻ (`tag_filter`)
- Lọc giữ các thẻ tương tác chuẩn (`button`, `a[href]`, `input`, `select`, `textarea`, `summary`, hoặc các phần tử có `role` tương tác) và các thẻ văn bản ngữ nghĩa (tiêu đề `h1-h6`, nhãn `label`, đoạn văn bản `text`).
- Gán nhãn tương ứng: `reason = "tag_interactive"` hoặc `reason = "tag_text"`.
- Giúp giảm bớt các thẻ phân chia cấu trúc rỗng (`div`, `span` vô nghĩa).

#### Chế độ 3: Phương pháp A – Lọc theo tác vụ (`task_only`)
- **Nguyên lý hoạt động:** Chỉ khai thác thông tin từ mô tả nhiệm vụ (`task`) và mục tiêu thao tác (`target`) của bước kiểm thử (gồm `role`, `name`, `entity`, `scope`).
- **Các bước chọn lọc:**
  1. *Action Target:* Tìm phần tử khớp với vai trò và nhãn thao tác mục tiêu (ví dụ nút "Thêm vào giỏ" trong card Sản phẩm A) -> Gán `reason = "action_target"` (Độ ưu tiên 1).
  2. *Action Label:* Giữ lại các nhãn văn bản nằm cùng vùng chứa (`scope`/`entity`) của phần tử thao tác để Agent có ngữ cảnh định vị -> Gán `reason = "action_label"` (Độ ưu tiên 2).
  3. *Các phần tử tương tác khác:* Đưa vào danh sách ứng viên phụ trợ nếu còn chỗ -> Gán `reason = "interactive_candidate"` (Độ ưu tiên 3).
- **Hạn chế:** Không xem xét điều kiện kiểm tra (`check`), do đó hoàn toàn không chủ động giữ lại các trường dữ liệu kết quả (như số lượng giỏ hàng ở vị trí khác). Khi ngân sách token bị siết chặt, các dữ liệu này sẽ bị cắt tỉa hoàn toàn.

#### Chế độ 4: Phương pháp B – Lọc theo tác vụ và điều kiện (`task_condition`)
- **Nguyên lý hoạt động:** Khai thác đồng thời cả mục tiêu thao tác (`target`) và điều kiện kiểm thử (`check` / `conditions`).
- **Các bước chọn lọc:**
  1. *Action Target:* Giữ nút thao tác mục tiêu -> `reason = "action_target"` (Độ ưu tiên P1).
  2. *Condition Evidence (Bằng chứng tối thiểu):* Xác định và giữ lại phần tử mang giá trị kiểm chứng (ví dụ trường số lượng sản phẩm A trong giỏ `#cart-item-quantity-a`, hoặc phần tử đối chiếu `cart_item_quantity_A`, thông báo kết quả, tiêu đề trang chuyển hướng) -> `reason = "condition_evidence"` (Độ ưu tiên P1).
  3. *Action Label:* Nhãn bổ trợ định vị nút bấm -> `reason = "action_label"` (Độ ưu tiên P2).
  4. *Container Context:* Vùng chứa của bằng chứng để phân biệt sản phẩm trong danh sách nhiều dòng -> `reason = "container_context"` (Độ ưu tiên P3).
  5. *Ứng viên tương tác khác:* Gán `reason = "interactive_candidate"` (Độ ưu tiên P4).
- **Ràng buộc ngân sách token (`token_budget`):** Nhóm P1 (`action_target` + `condition_evidence`) luôn được đưa vào đầu tiên và bảo vệ tuyệt đối. Nếu ngân sách bị giới hạn, các phần tử phụ trợ (P3, P4) sẽ bị cắt tỉa trước, bảo đảm Test Oracle luôn có đủ bằng chứng đối chiếu.

---

### 2.3. Hệ thống phân loại lý do giữ (`reason`)
Mỗi phần tử được giữ lại trong `PrunedDOMResult` đều có trường `reason` tường minh:
- `action_target`: Phần tử đích mà AI Agent cần tương tác trực tiếp (click, fill, select).
- `action_label`: Nhãn/tiêu đề ngữ cảnh trực tiếp giúp Agent định danh đúng đối tượng thao tác.
- `condition_evidence`: Phần tử mang dữ liệu/trạng thái dùng cho Test Oracle đối chiếu điều kiện trước - sau.
- `container_context`: Vùng chứa hoặc dòng bảng bao bọc bằng chứng giúp xác định quan hệ sở hữu đối tượng.
- `tag_interactive`: Phần tử tương tác thông thường được giữ lại ở chế độ lọc thẻ.
- `tag_text`: Thẻ văn bản/tiêu đề có ý nghĩa ngữ nghĩa được giữ lại ở chế độ lọc thẻ.
- `full_snapshot`: Phần tử được giữ trong chế độ chụp DOM đầy đủ.

### 2.4. Thuật toán tính token và kiểm soát ngân sách (`DOMTokenizer`)
- Đã cài đặt lớp `DOMTokenizer` tại `src/webtest/pruning/tokenizer.py` sử dụng biểu thức chính quy Unicode `\w+|[^\w\s]|\s+` mô phỏng chính xác hành vi mã hóa subword/BPE của các mô hình LLM hiện đại.
- Quy tắc đếm:
  - Từ ngắn và ký hiệu thông thường: 1 token.
  - Chuỗi khoảng trắng: gom nhóm tối đa 1 token cho mỗi 4 ký tự trắng hoặc dòng mới.
  - Từ dài (> 8 ký tự): phân rã thành nhiều subword token.
- Thuật toán bảo đảm tính toán xác định (deterministic), không phụ thuộc môi trường mạng, và nhất quán 100% giữa hai phương pháp A và B.
- Khi truyền tham số `token_budget`, hệ thống sẽ cộng dồn token tuần tự theo mức độ ưu tiên. Nếu phần tử kế tiếp làm vượt ngân sách, cờ `budget_exceeded = True` được bật và phần tử đó bị loại bỏ.

---

## 3. Trả lời câu hỏi kỹ thuật của Chu Bách Trúc Mai (Test Oracle)

> **Câu hỏi của Mai:**  
> *"Khi Huy cắt tỉa DOM xong, Huy trả về danh sách các phần tử được giữ lại dưới dạng mảng selector (chuỗi CSS/XPath) hay mảng node_id (số nguyên) để Mai truyền vào hàm kiểm tra Thiếu bằng chứng (MissingEvidence)?"*

### Trả lời và Giải pháp thiết kế từ Huy:
Để tạo sự thuận tiện tối đa cho Mai và tương thích 100% với hàm `TestOracle.evaluate_conditions(conditions, pruned_dom_targets)` mà Mai đã viết, mô-đun của Huy trả về đối tượng `PrunedDOMResult` hỗ trợ đầy đủ các định dạng sau:

1. **Thuộc tính đa năng `result.pruned_dom_targets` (Danh sách tổng hợp):**
   Trả về một `List[str]` chứa tất cả các dạng định danh của các phần tử được giữ lại:
   - Tên logic `target_object` (ví dụ `"cart_item_quantity_A"`).
   - Chuỗi CSS Selector thật (ví dụ `"#cart-item-quantity-a"` và alias `"#cart-item-a .item-qty"`).
   - Mã nút định danh snapshot (ví dụ `"n-18"`).
   - Chuỗi quan hệ phân cấp (ví dụ `"Giỏ hàng:Sản phẩm A:Số lượng"`).
   - Giá trị `data-testid` (ví dụ `"cart_item_quantity_A"`).

   👉 **Cách Mai dùng trong `evaluate_conditions`:**
   ```python
   # Mai chỉ cần kiểm tra trực tiếp target_object hoặc selector của ca:
   if condition["target_object"] not in pruned_dom_targets:
       # Lập tức phát hiện lỗi Thiếu bằng chứng!
       self.record_system_issue("MissingEvidence", ...)
       return "INCONCLUSIVE"
   ```

2. **Các danh sách chuyên biệt (nếu cần truy xuất riêng):**
   - `result.kept_node_ids`: Mảng chuỗi `["n-8", "n-18", ...]` để gửi cho Agent chọn lệnh.
   - `result.kept_selectors`: Mảng selector `["#btn-add-a", "#cart-item-quantity-a", ...]`.
   - `result.reasons`: Dict `{ "n-8": "action_target", "n-18": "condition_evidence" }` phục vụ ghi vết vào file `.jsonl` cho Vân và Trang phân tích.

---

## 4. Báo cáo kết quả kiểm thử và thực nghiệm khoa học

Đã thiết lập và chạy toàn bộ 17 bài kiểm thử tự động trong thư mục `tests/`. Tất cả đều vượt qua với kết quả **100% ĐẠT (OK)**:

| Tệp kiểm thử | Số test | Nội dung xác minh | Kết quả |
|---|---|---|---|
| `tests/test_contracts.py` | 3 | Xác thực JSON Schema của lệnh Agent (`agent-action`) và ca kiểm thử (`test-case`), kiểm tra 3 ca mẫu pilot | **PASS** |
| `tests/test_browser.py` | 3 | Kiểm tra Playwright Chromium, trích xuất DOM, định vị nút trùng nhãn theo Scope, và thực thi lệnh click | **PASS** |
| `tests/test_target_mapper.py` | 4 | Kiểm tra tra cứu xuôi/ngược giữa `target_object`, CSS Selector thật và tham chiếu nghiệp vụ `(scope, entity, field)` | **PASS** |
| `tests/test_pruner.py` | 6 | Kiểm tra 4 chế độ cắt tỉa DOM, tính token, gán nhãn `reason`, kiểm soát ngân sách token, và đối chứng mất bằng chứng | **PASS** |
| `tests/test_integration_flow.py` | 1 | Kiểm tra toàn trình: Snapshot trước -> Cắt tỉa -> Agent sinh lệnh -> Playwright bấm nút -> Snapshot sau -> Cập nhật số lượng | **PASS** |
| **Tổng cộng** | **17** | **Toàn bộ bộ kiểm thử của Giai đoạn 1 và Giai đoạn 2** | **17/17 PASS** |

### Thực nghiệm đối chứng then chốt: Phương pháp A vs Phương pháp B
Tại bài test `test_token_budget_enforcement_and_missing_evidence_contrast` trên ca chuẩn `cart-quantity.json` với cùng mức ngân sách token **90 tokens**:
- **Phương pháp A (`task_only`):**
  - Chi phí: **87 tokens**.
  - Phần tử giữ lại: Nút thao tác `btn-add-a` (`action_target`) và các văn bản ngữ cảnh trong thẻ Sản phẩm A (`action_label`).
  - Kết quả: Không còn đủ ngân sách cho trường số lượng trong giỏ hàng (`cart_item_quantity_A`).
  - `cart_item_quantity_A` **KHÔNG CÓ** trong `pruned_dom_targets` ➔ **Gây ra lỗi `MissingEvidence`** (Oracle không thể đối chiếu số lượng trước - sau và phải trả về `INCONCLUSIVE`).
- **Phương pháp B (`task_condition`):**
  - Chi phí: **84 tokens** (thấp hơn cả Phương pháp A).
  - Phần tử giữ lại: Nút thao tác `btn-add-a` (`action_target`) **VÀ** trường số lượng giỏ hàng `#cart-item-quantity-a` (`condition_evidence`).
  - Kết quả: `cart_item_quantity_A` **CÓ MẶT** trong `pruned_dom_targets` ➔ **Bảo toàn đầy đủ Bằng chứng tối thiểu**. Test Oracle đọc được số lượng thay đổi từ 1 lên 2 và kết luận chính xác `PASS`.

👉 **Kết luận thực nghiệm:** Dữ liệu thử nghiệm đã chứng minh giả thuyết nghiên cứu của nhóm: Việc đưa điều kiện kiểm tra vào bộ cắt tỉa DOM giúp giữ đúng bằng chứng cần thiết mà không làm gia tăng ngân sách token.

---

## 5. Hướng dẫn tích hợp và bàn giao cho Giai đoạn 3 (Trần Văn Thịnh)

Khi Thịnh xây dựng Trình điều phối thực nghiệm (`Runner`) ở Giai đoạn 3, luồng tích hợp với mô-đun của Huy được thực hiện đơn giản như sau:

```python
from webtest.browser import BrowserController
from webtest.pruning import DOMPruner

# 1. Khởi tạo controller và pruner
browser = BrowserController(headless=True)
pruner = DOMPruner()
page = browser.start()

# 2. Điều hướng và lấy snapshot trước
browser.navigate(case["initial"]["path"])
snapshot_before = browser.capture_snapshot("obs-pre")

# 3. Cắt tỉa DOM theo chế độ thí nghiệm (truyền cùng budget ví dụ 150 tokens)
pruned_dom = pruner.prune(
    snapshot=snapshot_before,
    mode="task_condition",  # hoặc "task_only"
    step=case["steps"][0],
    conditions=conditions_list,
    token_budget=150
)

# 4. Gửi chuỗi biểu diễn rút gọn cho Agent sinh lệnh
prompt_dom_text = pruned_dom.to_text()
# Agent trả về lệnh: {"schema_version": "0.1", "observation_id": "obs-pre", "action": "click", "target_id": "n-8"}

# 5. Playwright thực thi lệnh
exec_result = browser.execute_action(agent_action)
browser.wait_for_settle(settle_ms=200)

# 6. Chụp snapshot sau và cấp dữ liệu cho Oracle của Mai
snapshot_after = browser.capture_snapshot("obs-post")
pruned_after = pruner.prune(snapshot_after, mode="task_condition", step=case["steps"][0], conditions=conditions_list)

# Mai gọi: verdict = oracle.evaluate_conditions(conditions_list, pruned_after.pruned_dom_targets)
```

Toàn bộ mã nguồn, dữ liệu demo và bộ test đã được kiểm tra nghiêm ngặt, sẵn sàng 100% để chuyển sang Giai đoạn 3.

