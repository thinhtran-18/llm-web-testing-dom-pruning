# Kiểm thử chức năng web bằng AI Agent

Đề tài **Nâng cao hiệu quả kiểm thử chức năng web bằng AI Agent dựa trên LLM và cắt tỉa DOM theo điều kiện kiểm tra**.

Nhóm đánh giá khả năng giữ bằng chứng kiểm thử và phát hiện lỗi chức năng khi hai cách cắt tỉa DOM dùng cùng giới hạn token. Hệ thống dự kiến dùng Python, Playwright và Chromium.

## Cấu trúc

```text
docs/                  Đặc tả và bàn giao Giai đoạn 1
contracts/             JSON Schema cho lệnh Agent và ca kiểm thử
datasets/cases/        Ba ca mẫu dùng để thống nhất dữ liệu
datasets/labels/       Nhãn chuẩn dành cho thực nghiệm
src/webtest/
  agent/               Lập kế hoạch và sinh lệnh
  browser/             Playwright và thu trạng thái
  pruning/             Các cách cắt tỉa DOM
  oracle/              Đối chiếu điều kiện và kết luận
  runner/              Điều phối lượt chạy và ghi log
demo/                  Ứng dụng web thử nghiệm
tests/                 Kiểm thử hợp đồng dữ liệu và các mô-đun
```

Đọc [đặc tả và đầu ra Giai đoạn 1](docs/giai-doan-1.md) để triển khai theo cùng hợp đồng dữ liệu.

## Kiểm tra dữ liệu mẫu

Từ thư mục gốc, chạy bằng Python 3.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

## Đóng góp

Tạo nhánh từ `main` theo dạng `<ten>/<cong-viec>`, ví dụ `huy/dom-snapshot`. Push nhánh đó và mở pull request vào `main`. Trần Văn Thịnh xem xét và merge.
