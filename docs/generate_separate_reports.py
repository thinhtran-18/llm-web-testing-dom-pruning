"""Script to generate professional Word (.docx) reports for Nguyen Quang Huy.
Generates:
1. Master report: Bao_Cao_Giai_Doan_1_va_2_Nguyen_Quang_Huy.docx
2. Phase 1 report: Bao_Cao_Giai_Doan_1_Nguyen_Quang_Huy.docx
3. Phase 2 report: Bao_Cao_Giai_Doan_2_Nguyen_Quang_Huy.docx
"""

from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

DOCS_DIR = Path("D:/bao2026/llm-web-testing-dom-pruning/docs")


def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)


def set_table_borders(table, color="D3D3D3", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)


def format_table_header(row, col_widths, bg_hex="1F4E79", text_color=RGBColor(255, 255, 255)):
    for i, cell in enumerate(row.cells):
        set_cell_background(cell, bg_hex)
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        cell.width = col_widths[i]
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.font.name = "Times New Roman"
                run.font.size = Pt(10.5)
                run.font.bold = True
                run.font.color.rgb = text_color


def format_table_row(row, col_widths, is_even=False, alignments=None):
    bg_hex = "F8FAFC" if is_even else "FFFFFF"
    for i, cell in enumerate(row.cells):
        if is_even:
            set_cell_background(cell, bg_hex)
        set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
        cell.width = col_widths[i]
        for p in cell.paragraphs:
            if alignments and i < len(alignments):
                p.alignment = alignments[i]
            for run in p.runs:
                run.font.name = "Times New Roman"
                run.font.size = Pt(10)
                run.font.color.rgb = RGBColor(40, 40, 40)


def add_callout_box(doc, text, title=None, border_color="1F4E79", bg_color="F0F4F8"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)

    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/>'
        f'<w:top w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(tcBorders)

    p = cell.paragraphs[0]
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(2)
    if title:
        run_title = p.add_run(f"📌 {title}\n")
        run_title.font.name = "Times New Roman"
        run_title.font.bold = True
        run_title.font.size = Pt(10.5)
        run_title.font.color.rgb = RGBColor(31, 78, 121)

    run_text = p.add_run(text)
    run_text.font.name = "Times New Roman"
    run_text.font.size = Pt(10)
    run_text.font.color.rgb = RGBColor(45, 55, 72)

    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(4)
    p_after.paragraph_format.space_after = Pt(4)


def add_code_block(doc, code_text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "F8F9FA")
    set_cell_margins(cell, top=100, bottom=100, left=160, right=160)

    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>'
        f'<w:top w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>'
        f'<w:right w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>'
        f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(tcBorders)

    p = cell.paragraphs[0]
    p.paragraph_format.line_spacing = 1.05
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run(code_text)
    run.font.name = "Consolas"
    run.font.size = Pt(9.5)
    run.font.color.rgb = RGBColor(30, 41, 59)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)


def build_cover_header(doc, sub_title):
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(0.8)

    p_header = doc.add_paragraph()
    p_header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_header.paragraph_format.space_after = Pt(2)
    r_uni = p_header.add_run("BÁO CÁO KỸ THUẬT NGHIÊN CỨU & PHÁT TRIỂN\n")
    r_uni.font.name = "Times New Roman"
    r_uni.font.size = Pt(13)
    r_uni.font.bold = True
    r_uni.font.color.rgb = RGBColor(100, 116, 139)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_after = Pt(8)
    r_main_title = p_title.add_run(
        "NÂNG CAO HIỆU QUẢ KIỂM THỬ CHỨC NĂNG WEB BẰNG AI AGENT\n"
        "DỰA TRÊN LLM VÀ CẮT TỈA DOM THEO ĐIỀU KIỆN KIỂM TRA\n"
    )
    r_main_title.font.name = "Times New Roman"
    r_main_title.font.size = Pt(15)
    r_main_title.font.bold = True
    r_main_title.font.color.rgb = RGBColor(31, 78, 121)

    r_sub = p_title.add_run(sub_title)
    r_sub.font.name = "Times New Roman"
    r_sub.font.size = Pt(13)
    r_sub.font.bold = True
    r_sub.font.color.rgb = RGBColor(192, 57, 43)

    tbl_info = doc.add_table(rows=5, cols=2)
    tbl_info.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_info, color="CBD5E1", sz="4")
    col_w = [Inches(2.2), Inches(4.3)]

    info_data = [
        ("Người thực hiện:", "Nguyễn Quang Huy"),
        ("Phân công vai trò:", "Lập trình – Playwright, trích xuất DOM, ánh xạ phần tử và các chế độ cắt tỉa DOM"),
        ("Giai đoạn báo cáo:", sub_title),
        ("Mã nguồn phụ trách:", "src/webtest/browser/, src/webtest/pruning/, demo/store.html, tests/"),
        ("Thời gian thực hiện:", "Tháng 11/2026"),
    ]

    for idx, (lbl, val) in enumerate(info_data):
        row = tbl_info.rows[idx]
        set_cell_background(row.cells[0], "F1F5F9")
        set_cell_margins(row.cells[0], top=60, bottom=60, left=100, right=100)
        set_cell_margins(row.cells[1], top=60, bottom=60, left=100, right=100)
        row.cells[0].width = col_w[0]
        row.cells[1].width = col_w[1]

        p0 = row.cells[0].paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r0 = p0.add_run(lbl)
        r0.font.name = "Times New Roman"
        r0.font.size = Pt(10)
        r0.font.bold = True
        r0.font.color.rgb = RGBColor(51, 65, 85)

        p1 = row.cells[1].paragraphs[0]
        r1 = p1.add_run(val)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(10)
        r1.font.color.rgb = RGBColor(15, 23, 42)
        if idx == 0:
            r1.font.bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(10)


def add_signature(doc):
    tbl_sig = doc.add_table(rows=1, cols=2)
    tbl_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_sig.autofit = False
    set_table_borders(tbl_sig, color="FFFFFF")
    tbl_sig.rows[0].cells[0].width = Inches(3.2)
    tbl_sig.rows[0].cells[1].width = Inches(3.3)

    p_sig_left = tbl_sig.rows[0].cells[0].paragraphs[0]
    p_sig_left.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sl1 = p_sig_left.add_run("XÁC NHẬN CỦA NHÓM TRƯỞNG\n\n\n\n")
    r_sl1.font.bold = True
    r_sl2 = p_sig_left.add_run("Trần Văn Thịnh")
    r_sl2.font.bold = True

    p_sig_right = tbl_sig.rows[0].cells[1].paragraphs[0]
    p_sig_right.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sr1 = p_sig_right.add_run("NGƯỜI LẬP BÁO CÁO\n\n\n\n")
    r_sr1.font.bold = True
    r_sr2 = p_sig_right.add_run("Nguyễn Quang Huy")
    r_sr2.font.bold = True

    for p in (p_sig_left, p_sig_right):
        for run in p.runs:
            run.font.name = "Times New Roman"
            run.font.size = Pt(11)


def generate_phase_1_report():
    doc = Document()
    build_cover_header(doc, "BÁO CÁO KẾT QUẢ THỰC HIỆN GIAI ĐOẠN 1: CHUẨN BỊ VÀ ĐẶC TẢ")

    h1 = doc.add_heading("I. MỤC TIÊU VÀ NHIỆM VỤ ĐƯỢC GIAO", level=1)
    for r in h1.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(13)
        r.font.bold = True
        r.font.color.rgb = RGBColor(31, 78, 121)

    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.25
    p.add_run(
        "Theo phân công đề cương Giai đoạn 1, Nguyễn Quang Huy phụ trách:\n"
        "1. Dựng Playwright với Chromium, kiểm tra trích xuất DOM.\n"
        "2. Thử nghiệm định vị nút cùng nhãn trong hai vùng khác nhau (Scope Disambiguation).\n"
        "3. Thống nhất tiêu chuẩn 'Bằng chứng tối thiểu' (Minimal Evidence Constraint) với Test Oracle (Mai).\n"
        "4. Lập bảng ánh xạ target_object (tên logic) sang CSS Selector thật trên Web Demo."
    ).font.name = "Times New Roman"

    add_callout_box(
        doc,
        "Yêu cầu nhiệm vụ với Huy: Cần thống nhất rõ ràng với Huy rằng dù bộ lọc DOM cắt tỉa theo cách nào, "
        "đầu ra DOM chuyển cho Test Oracle bắt buộc phải giữ lại đủ nút thao tác (kèm nhãn) và phần văn bản (text)/trường "
        "dữ liệu dùng để đối chiếu. Nếu bộ lọc cắt mất các phần tử này, Oracle sẽ tự động đánh trượt ca kiểm thử đó thành "
        "lỗi 'Thiếu bằng chứng' (Missing Evidence). Lý do: Đảm bảo Test Oracle có đủ 'Bằng chứng tối thiểu' để đối chiếu "
        "trạng thái Trước - Sau.",
        title="THỎA THUẬN QUAN TRỌNG VỚI TEST ORACLE"
    )

    h2 = doc.add_heading("II. KẾT QUẢ TRIỂN KHAI KỸ THUẬT", level=1)
    for r in h2.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(13)
        r.font.bold = True
        r.font.color.rgb = RGBColor(31, 78, 121)

    p2 = doc.add_paragraph()
    p2.paragraph_format.line_spacing = 1.25
    p2.add_run(
        "1. Bộ điều khiển Playwright Chromium (BrowserController):\n"
        "   - Đã cài đặt src/webtest/browser/browser_controller.py quản lý Chromium headless, cách ly context.\n"
        "   - Bắt tự động các sự kiện: pageerror (Crash), console.error, HTTP >= 400.\n"
        "   - Thực thi các lệnh Agent tuân thủ contracts/agent-action.schema.json (click, fill, select, check, uncheck).\n\n"
        "2. Thuật toán trích xuất DOM quan sát được (DOMExtractor & DOMNode):\n"
        "   - Đã cài đặt src/webtest/browser/dom_extractor.py và models.py.\n"
        "   - Lọc bỏ các thẻ ẩn và rác, trích xuất: node_id, tag, role, name, text, value, scope, selector.\n\n"
        "3. Thực nghiệm giải quyết bài toán Định vị nút cùng nhãn trong hai vùng khác nhau (Scope Disambiguation):\n"
        "   - Thử nghiệm trên demo/store.html: Thẻ Sản phẩm A và Thẻ Sản phẩm B đều có nút 'Thêm vào giỏ'.\n"
        "   - Duyệt ngược cây DOM để gán scope='Sản phẩm A' và scope='Sản phẩm B'.\n"
        "   - Phương thức locate_node_by_target(role='button', name='Thêm vào giỏ', scope='Sản phẩm A') phân giải "
        "chính xác ra #btn-add-a (mã n-8), hoàn toàn không bị xung đột với #btn-add-b (mã n-12) của Sản phẩm B.\n"
        "   - Kiểm chứng thành công tại tests/test_browser.py."
    ).font.name = "Times New Roman"

    h3 = doc.add_heading("III. BẢNG ÁNH XẠ TARGET_OBJECT SANG CSS SELECTOR THẬT", level=1)
    for r in h3.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(13)
        r.font.bold = True
        r.font.color.rgb = RGBColor(31, 78, 121)

    tbl_map = doc.add_table(rows=16, cols=3)
    tbl_map.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_map)
    col_w_map = [Inches(2.0), Inches(1.8), Inches(2.7)]

    map_sample = [
        ("catalog_title", "#catalog-title", "Tiêu đề danh mục sản phẩm (scope: Danh mục)"),
        ("product_card_A", "#product-card-a", "Thẻ sản phẩm A (scope: Danh mục)"),
        ("product_name_A", "#product-name-a", "Tên hiển thị sản phẩm A"),
        ("product_price_A", "#product-price-a", "Giá bán sản phẩm A (100.000đ)"),
        ("btn_add_to_cart_A", "#btn-add-a", "Nút Thêm vào giỏ của Sản phẩm A"),
        ("product_card_B", "#product-card-b", "Thẻ sản phẩm B (scope: Danh mục)"),
        ("btn_add_to_cart_B", "#btn-add-b", "Nút Thêm vào giỏ của Sản phẩm B"),
        ("cart_badge_count", "#cart-badge", "Huy hiệu số lượng giỏ hàng trên Header"),
        ("cart_item_row_A", "#cart-item-a", "Dòng sản phẩm A trong giỏ hàng"),
        ("cart_item_quantity_A", "#cart-item-quantity-a", "Trường số lượng Sản phẩm A trong giỏ (alias: #cart-item-a .item-qty)"),
        ("cart_item_btn_inc_A", "#btn-inc-a", "Nút tăng (+) số lượng Sản phẩm A trong giỏ"),
        ("cart_item_btn_dec_A", "#btn-dec-a", "Nút giảm (-) số lượng Sản phẩm A trong giỏ"),
        ("cart_total_price", "#cart-total-price", "Tổng tiền đơn hàng trong giỏ"),
        ("btn_checkout", "#btn-checkout", "Nút Thanh toán đơn hàng"),
        ("toast_message", "#toast-message", "Thông báo phản hồi giao diện ('Đã thêm vào giỏ')"),
    ]

    h_map = tbl_map.rows[0]
    h_map.cells[0].paragraphs[0].text = "Tên logic (target_object)"
    h_map.cells[1].paragraphs[0].text = "CSS Selector thật"
    h_map.cells[2].paragraphs[0].text = "Mô tả chức năng & Ngữ cảnh"
    format_table_header(h_map, col_w_map)

    for idx, (to, sel, desc) in enumerate(map_sample):
        row = tbl_map.rows[idx + 1]
        row.cells[0].paragraphs[0].text = to
        row.cells[1].paragraphs[0].text = sel
        row.cells[2].paragraphs[0].text = desc
        format_table_row(row, col_w_map, is_even=(idx % 2 == 1), alignments=[WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT])

    doc.add_paragraph().paragraph_format.space_after = Pt(10)
    add_signature(doc)

    out_p1 = DOCS_DIR / "Bao_Cao_Giai_Doan_1_Nguyen_Quang_Huy.docx"
    doc.save(str(out_p1))
    print(f"Phase 1 report saved at: {out_p1}")


def generate_phase_2_report():
    doc = Document()
    build_cover_header(doc, "BÁO CÁO KẾT QUẢ THỰC HIỆN GIAI ĐOẠN 2: XÂY DỰNG CÁC MÔ-ĐUN")

    h1 = doc.add_heading("I. MỤC TIÊU VÀ NHIỆM VỤ ĐƯỢC GIAO", level=1)
    for r in h1.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(13)
        r.font.bold = True
        r.font.color.rgb = RGBColor(31, 78, 121)

    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.25
    p.add_run(
        "Theo kế hoạch Giai đoạn 2, Nguyễn Quang Huy phụ trách:\n"
        "1. Viết bộ thu DOM và 4 chế độ cắt tỉa: full, tag_filter, task_only, task_condition.\n"
        "2. Gắn nhãn lý do giữ (reason) cho từng nút và tính toán lượng token (token_count), kiểm soát ngân sách (token_budget).\n"
        "3. Trả lời câu hỏi phối hợp của Chu Bách Trúc Mai về định dạng mảng trả về cho Test Oracle.\n"
        "4. Thực hiện thực nghiệm đối chứng định lượng giữa Phương pháp A và Phương pháp B.\n"
        "5. Viết bộ test tự động và hoàn thiện tài liệu bàn giao Giai đoạn 3."
    ).font.name = "Times New Roman"

    h2 = doc.add_heading("II. KIẾN TRÚC MÔ-ĐUN CẮT TỈA DOM 4 CHẾ ĐỘ (DOMPruner)", level=1)
    for r in h2.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(13)
        r.font.bold = True
        r.font.color.rgb = RGBColor(31, 78, 121)

    tbl_pm = doc.add_table(rows=5, cols=3)
    tbl_pm.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_pm)
    col_w_pm = [Inches(1.8), Inches(1.5), Inches(3.2)]

    pm_data = [
        ("Chế độ 1: DOM đầy đủ\n(mode='full')", "Toàn bộ snapshot quan sát được", "Không cắt tỉa; giữ tất cả các thẻ quan sát được; dùng làm đường cơ sở đo lường tối đa."),
        ("Chế độ 2: Lọc theo thẻ\n(mode='tag_filter')", "Thẻ tương tác & thẻ văn bản", "Chỉ giữ button, a, input, select, textarea và các thẻ tiêu đề/văn bản có nghĩa. Giảm thiểu các thẻ div/span rỗng."),
        ("Chế độ 3: Phương pháp A\n(mode='task_only')", "Mô tả nhiệm vụ & mục tiêu bước", "Lọc DOM chỉ dựa vào target của bước. Giữ Action Target và Action Label. KHÔNG giữ bằng chứng đối chiếu của điều kiện."),
        ("Chế độ 4: Phương pháp B\n(mode='task_condition')", "Nhiệm vụ VÀ điều kiện kiểm thử", "Giữ đồng thời Action Target + Condition Evidence (Bằng chứng tối thiểu) + Action Label. Bảo toàn trường dữ liệu cho Test Oracle."),
    ]

    h_pm = tbl_pm.rows[0]
    h_pm.cells[0].paragraphs[0].text = "Chế độ cắt tỉa"
    h_pm.cells[1].paragraphs[0].text = "Căn cứ lựa chọn phần tử"
    h_pm.cells[2].paragraphs[0].text = "Cơ chế chọn lọc & Bảo vệ bằng chứng"
    format_table_header(h_pm, col_w_pm)

    for idx, (m, c, d) in enumerate(pm_data):
        row = tbl_pm.rows[idx + 1]
        row.cells[0].paragraphs[0].text = m
        row.cells[1].paragraphs[0].text = c
        row.cells[2].paragraphs[0].text = d
        format_table_row(row, col_w_pm, is_even=(idx % 2 == 1), alignments=[WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT])

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    h3 = doc.add_heading("III. PHỐI HỢP VỚI TEST ORACLE & THỰC NGHIỆM ĐỐI CHỨNG", level=1)
    for r in h3.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(13)
        r.font.bold = True
        r.font.color.rgb = RGBColor(31, 78, 121)

    add_callout_box(
        doc,
        "Trả lời câu hỏi của Chu Bách Trúc Mai: Đối tượng PrunedDOMResult cung cấp thuộc tính đa năng 'pruned_dom_targets' "
        "chứa đồng thời: target_object ('cart_item_quantity_A'), selector ('#cart-item-quantity-a'), node_id ('n-18') "
        "và chuỗi phân cấp ('Giỏ hàng:Sản phẩm A:Số lượng'). Nhờ đó hàm evaluate_conditions(conditions, pruned_dom_targets) "
        "của Mai kiểm tra trực tiếp mà không cần chuyển đổi kiểu dữ liệu!",
        title="TRẢ LỜI CÂU HỎI KỸ THUẬT CỦA MAI"
    )

    p_exp = doc.add_paragraph()
    p_exp.paragraph_format.line_spacing = 1.25
    p_exp.add_run(
        "Số liệu thực nghiệm đối chứng trên ca cart-quantity.json dưới cùng giới hạn 90 tokens:"
    ).font.name = "Times New Roman"

    tbl_exp = doc.add_table(rows=6, cols=3)
    tbl_exp.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_exp)
    col_w_exp = [Inches(2.2), Inches(2.1), Inches(2.2)]

    exp_data = [
        ("Ngân sách token cấp phát", "90 tokens", "90 tokens (Bằng nhau tuyệt đối)"),
        ("Token thực dùng", "87 tokens", "84 tokens (Tiết kiệm hơn 3 tokens)"),
        ("Giữ nút bấm thao tác (Action Target)", "CÓ (#btn-add-a, reason=action_target)", "CÓ (#btn-add-a, reason=action_target)"),
        ("Giữ số lượng giỏ hàng (Condition Evidence)", "KHÔNG (Bị cắt tỉa do hết token)", "CÓ (#cart-item-quantity-a, reason=condition_evidence)"),
        ("Kết quả Test Oracle", "INCONCLUSIVE (MissingEvidence)", "PASS (Bắt trúng thay đổi từ 1 lên 2)"),
    ]

    h_exp = tbl_exp.rows[0]
    h_exp.cells[0].paragraphs[0].text = "Chỉ số so sánh"
    h_exp.cells[1].paragraphs[0].text = "Phương pháp A (Task-only)"
    h_exp.cells[2].paragraphs[0].text = "Phương pháp B (Task + Condition)"
    format_table_header(h_exp, col_w_exp)

    for idx, (m, a, b) in enumerate(exp_data):
        row = tbl_exp.rows[idx + 1]
        row.cells[0].paragraphs[0].text = m
        row.cells[1].paragraphs[0].text = a
        row.cells[2].paragraphs[0].text = b
        format_table_row(row, col_w_exp, is_even=(idx % 2 == 1), alignments=[WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER])

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    h4 = doc.add_heading("IV. KẾT QUẢ KIỂM THỬ TỰ ĐỘNG (17/17 TESTS PASS)", level=1)
    for r in h4.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(13)
        r.font.bold = True
        r.font.color.rgb = RGBColor(31, 78, 121)

    tbl_tests = doc.add_table(rows=6, cols=4)
    tbl_tests.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_tests)
    col_w_t = [Inches(2.2), Inches(1.0), Inches(2.5), Inches(0.8)]

    tests_summary = [
        ("tests/test_contracts.py", "3 tests", "Kiểm tra schema JSON hợp đồng (agent-action, test-case) và nhãn pilot", "PASS"),
        ("tests/test_browser.py", "3 tests", "Kiểm tra Chromium, trích xuất DOM, Scope Disambiguation và lệnh click", "PASS"),
        ("tests/test_target_mapper.py", "4 tests", "Kiểm tra ánh xạ logic target_object sang CSS Selector và tra cứu ref", "PASS"),
        ("tests/test_pruner.py", "6 tests", "Kiểm tra 4 chế độ lọc, token budget, gán reason và đối chứng mất bằng chứng", "PASS"),
        ("tests/test_integration_flow.py", "1 test", "Kiểm tra toàn trình Pre-snapshot -> Pruning -> Action -> Post-snapshot -> Oracle", "PASS"),
    ]

    h_t = tbl_tests.rows[0]
    h_t.cells[0].paragraphs[0].text = "Tệp kiểm thử"
    h_t.cells[1].paragraphs[0].text = "Số bài test"
    h_t.cells[2].paragraphs[0].text = "Phạm vi xác minh kỹ thuật"
    h_t.cells[3].paragraphs[0].text = "Kết quả"
    format_table_header(h_t, col_w_t)

    for idx, (f, c, sc, st) in enumerate(tests_summary):
        row = tbl_tests.rows[idx + 1]
        row.cells[0].paragraphs[0].text = f
        row.cells[1].paragraphs[0].text = c
        row.cells[2].paragraphs[0].text = sc
        row.cells[3].paragraphs[0].text = st
        format_table_row(row, col_w_t, is_even=(idx % 2 == 1), alignments=[WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER])
        row.cells[3].paragraphs[0].runs[0].font.bold = True
        row.cells[3].paragraphs[0].runs[0].font.color.rgb = RGBColor(34, 139, 34)

    doc.add_paragraph().paragraph_format.space_after = Pt(10)
    add_signature(doc)

    out_p2 = DOCS_DIR / "Bao_Cao_Giai_Doan_2_Nguyen_Quang_Huy.docx"
    doc.save(str(out_p2))
    print(f"Phase 2 report saved at: {out_p2}")


if __name__ == "__main__":
    generate_phase_1_report()
    generate_phase_2_report()

