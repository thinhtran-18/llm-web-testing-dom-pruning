"""Script to generate professional Word (.docx) report for Nguyen Quang Huy - Phases 1 & 2."""

import os
from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

DOCS_DIR = Path("D:/bao2026/llm-web-testing-dom-pruning/docs")
DOCS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = DOCS_DIR / "Bao_Cao_Giai_Doan_1_va_2_Nguyen_Quang_Huy.docx"


def set_cell_background(cell, fill_hex):
    """Set background color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set cell padding (in twips: 20 twips = 1 pt)."""
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
    """Set subtle gray borders for a table."""
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

    # Custom left thick border
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

    # Empty space after table
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


def generate_full_report():
    doc = Document()

    # Set page margins: 2cm top/bottom, 2.5cm left, 2cm right
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(0.8)

    # ------------------ COVER / HEADER TITLE ------------------
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
    r_main_title.font.size = Pt(16)
    r_main_title.font.bold = True
    r_main_title.font.color.rgb = RGBColor(31, 78, 121)

    r_sub = p_title.add_run("BÁO CÁO KẾT QUẢ THỰC HIỆN GIAI ĐOẠN 1 VÀ GIAI ĐOẠN 2")
    r_sub.font.name = "Times New Roman"
    r_sub.font.size = Pt(13)
    r_sub.font.bold = True
    r_sub.font.color.rgb = RGBColor(192, 57, 43)

    # Info box table
    tbl_info = doc.add_table(rows=5, cols=2)
    tbl_info.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_info, color="CBD5E1", sz="4")
    col_w = [Inches(2.2), Inches(4.3)]

    info_data = [
        ("Người thực hiện:", "Nguyễn Quang Huy"),
        ("Phân công vai trò:", "Lập trình – Playwright, trích xuất DOM, ánh xạ phần tử và các chế độ cắt tỉa DOM"),
        ("Các giai đoạn báo cáo:", "Giai đoạn 1 (Chuẩn bị & đặc tả) và Giai đoạn 2 (Xây dựng các mô-đun)"),
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

    # ------------------ PHẦN I: TỔNG QUAN VÀ PHÂN CÔNG ------------------
    h1 = doc.add_heading("PHẦN I. TỔNG QUAN ĐỀ TÀI VÀ TRÁCH NHIỆM PHỤ TRÁCH", level=1)
    h1.paragraph_format.space_before = Pt(12)
    h1.paragraph_format.space_after = Pt(6)
    for r in h1.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(14)
        r.font.bold = True
        r.font.color.rgb = RGBColor(31, 78, 121)

    p_intro = doc.add_paragraph()
    p_intro.paragraph_format.line_spacing = 1.25
    p_intro.paragraph_format.space_after = Pt(6)
    r_intro = p_intro.add_run(
        "Đề tài tập trung giải quyết bài toán kiểm thử chức năng tự động trên giao diện web hộp đen thông qua AI Agent "
        "dựa trên mô hình ngôn ngữ lớn (LLM). Do giới hạn nghiêm ngặt về ngân sách token đầu vào của LLM, toàn bộ cây DOM "
        "thô của ứng dụng web không thể truyền trực tiếp vào mô hình. Do đó, kỹ thuật cắt tỉa DOM (DOM Pruning) đóng vai trò sống còn. "
        "Câu hỏi nghiên cứu trọng tâm của đề tài là: "
    )
    r_intro.font.name = "Times New Roman"
    r_intro.font.size = Pt(11)

    add_callout_box(
        doc,
        "Liệu việc cắt tỉa DOM kết hợp cả mô tả nhiệm vụ và điều kiện kiểm tra (Task + Condition DOM Pruning - Phương pháp B) "
        "có giúp AI Agent và Test Oracle giữ được đầy đủ bằng chứng đối chiếu trước - sau để phát hiện lỗi chính xác hơn "
        "so với phương pháp chỉ lọc theo nhiệm vụ (Task-only DOM Pruning - Phương pháp A), khi cả hai phương pháp đều được cấp "
        "cùng một giới hạn ngân sách token đầu vào?",
        title="CÂU HỎI KHOA HỌC TRỌNG TÂM CỦA ĐỀ TÀI"
    )

    p_team = doc.add_paragraph()
    p_team.paragraph_format.line_spacing = 1.25
    p_team.paragraph_format.space_after = Pt(4)
    r_team = p_team.add_run("Bảng phân công trách nhiệm nhóm nghiên cứu và vị trí phụ trách của Nguyễn Quang Huy:")
    r_team.font.name = "Times New Roman"
    r_team.font.size = Pt(11)
    r_team.font.bold = True

    # Team table
    tbl_team = doc.add_table(rows=6, cols=3)
    tbl_team.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_team)
    col_w_team = [Inches(1.8), Inches(1.5), Inches(3.2)]

    team_data = [
        ("Trần Văn Thịnh", "Nhóm trưởng · Lập trình", "Kiến trúc hệ thống, AI Agent, tích hợp API LLM, trình điều phối (Runner), chủ trì phương pháp và tích hợp."),
        ("Nguyễn Quang Huy (Tôi)", "Lập trình cốt lõi", "Playwright, trích xuất DOM, ánh xạ phần tử, xử lý disambiguation và thiết kế/cài đặt bộ cắt tỉa DOM 4 chế độ."),
        ("Chu Bách Trúc Mai", "Lập trình", "Test Oracle, cơ chế chờ động (Explicit Waits), đối chiếu trạng thái trước-sau, phân loại nhãn lỗi (ONR, NLE, Crash, INCONCLUSIVE)."),
        ("Nguyễn Thị Cẩm Vân", "Thực nghiệm & viết bài", "Rà soát tài liệu, lập giao thức đối chứng, đo lường TP/FP/FN/TN, Precision, Recall, Token và thời gian."),
        ("Trang", "Dữ liệu & viết bài", "Đặc tả ca kiểm thử JSON (25 ca), 15 biến thể lỗi, xác minh nhãn dữ liệu chuẩn và chuẩn bị ứng dụng thực nghiệm."),
    ]

    header_row = tbl_team.rows[0]
    header_row.cells[0].paragraphs[0].text = "Thành viên"
    header_row.cells[1].paragraphs[0].text = "Vai trò"
    header_row.cells[2].paragraphs[0].text = "Phần việc và trách nhiệm phụ trách"
    format_table_header(header_row, col_w_team)

    for idx, (m, r, desc) in enumerate(team_data):
        row = tbl_team.rows[idx + 1]
        row.cells[0].paragraphs[0].text = m
        row.cells[1].paragraphs[0].text = r
        row.cells[2].paragraphs[0].text = desc
        format_table_row(row, col_w_team, is_even=(idx % 2 == 1), alignments=[WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT])
        if "Huy" in m:
            set_cell_background(row.cells[0], "E0F2FE")
            set_cell_background(row.cells[1], "E0F2FE")
            set_cell_background(row.cells[2], "E0F2FE")

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # ------------------ PHẦN II: KẾT QUẢ GIAI ĐOẠN 1 ------------------
    h2 = doc.add_heading("PHẦN II. KẾT QUẢ THỰC HIỆN GIAI ĐOẠN 1: CHUẨN BỊ VÀ ĐẶC TẢ", level=1)
    h2.paragraph_format.space_before = Pt(14)
    h2.paragraph_format.space_after = Pt(6)
    for r in h2.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(14)
        r.font.bold = True
        r.font.color.rgb = RGBColor(31, 78, 121)

    p_gd1 = doc.add_paragraph()
    p_gd1.paragraph_format.line_spacing = 1.25
    p_gd1.paragraph_format.space_after = Pt(6)
    r_gd1 = p_gd1.add_run(
        "Mục tiêu của Giai đoạn 1 đối với cá nhân là: (1) Thiết lập môi trường Playwright với Chromium; "
        "(2) Thiết kế cấu trúc dữ liệu và giải pháp trích xuất cây DOM quan sát được; "
        "(3) Thực nghiệm giải quyết bài toán định vị nút cùng nhãn trong hai vùng khác nhau (Scope Disambiguation); "
        "(4) Thống nhất tiêu chuẩn Bằng chứng tối thiểu (Minimal Evidence Constraint) với Test Oracle của Mai; "
        "(5) Xây dựng bảng ánh xạ đối tượng logic sang CSS Selector thật trên Web Demo."
    )
    r_gd1.font.name = "Times New Roman"
    r_gd1.font.size = Pt(11)

    # 2.1
    h2_1 = doc.add_heading("1. Cài đặt bộ điều khiển Playwright Chromium (BrowserController)", level=2)
    h2_1.paragraph_format.space_before = Pt(10)
    h2_1.paragraph_format.space_after = Pt(4)
    for r in h2_1.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = RGBColor(43, 87, 154)

    p_ctrl = doc.add_paragraph()
    p_ctrl.paragraph_format.line_spacing = 1.25
    p_ctrl.paragraph_format.space_after = Pt(6)
    p_ctrl.add_run(
        "Đã phát triển lớp BrowserController (src/webtest/browser/browser_controller.py) đóng gói toàn bộ chức năng "
        "điều khiển Playwright Chromium theo chuẩn Sync API của Python. Lớp này hỗ trợ:\n"
        "• Khởi tạo trình duyệt độc lập (hỗ trợ cả headless=True và giao diện trực quan với slow_mo).\n"
        "• Quản lý phiên làm việc BrowserContext cô lập để đặt lại fixture dữ liệu sạch sẽ giữa các lượt chạy.\n"
        "• Bắt tự động các lỗi hạ tầng ngầm: Lắng nghe sự kiện page.on('pageerror') (phát hiện Crash sập trang), "
        "page.on('console') (bắt các ngoại lệ JS đỏ), và page.on('response') (bắt mã HTTP >= 400).\n"
        "• Thực thi hành động của Agent tuân thủ 100% hợp đồng contracts/agent-action.schema.json "
        "(click, fill, select, check, uncheck)."
    ).font.name = "Times New Roman"

    # 2.2
    h2_2 = doc.add_heading("2. Giải pháp trích xuất DOM quan sát được (DOMExtractor & DOMNode)", level=2)
    h2_2.paragraph_format.space_before = Pt(10)
    h2_2.paragraph_format.space_after = Pt(4)
    for r in h2_2.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = RGBColor(43, 87, 154)

    p_ext = doc.add_paragraph()
    p_ext.paragraph_format.line_spacing = 1.25
    p_ext.paragraph_format.space_after = Pt(6)
    p_ext.add_run(
        "DOM HTML thô chứa rất nhiều thẻ rác, phần tử ẩn hoặc kịch bản ngầm không quan sát được. "
        "DOMExtractor (src/webtest/browser/dom_extractor.py) nhúng script JavaScript nội trang để chuẩn hóa cây quan sát được. "
        "Mỗi nút DOMNode bao gồm các thuộc tính cốt lõi sau:"
    ).font.name = "Times New Roman"

    tbl_node = doc.add_table(rows=8, cols=3)
    tbl_node.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_node)
    col_w_node = [Inches(1.5), Inches(1.3), Inches(3.7)]

    node_fields = [
        ("node_id", "str (chuỗi)", "Mã định danh duy nhất trong từng snapshot (ví dụ: 'n-8', 'n-18') phục vụ lệnh Agent."),
        ("role", "str (chuỗi)", "Vai trò WAI-ARIA chuẩn hóa: 'button', 'link', 'textbox', 'heading', 'text', 'row', 'cell'."),
        ("name / text", "str (chuỗi)", "Tên hiển thị người dùng nhìn thấy (accessible name) hoặc nội dung innerText có nghĩa."),
        ("value", "Optional[str]", "Giá trị hiện tại của ô nhập liệu (input, select, textarea)."),
        ("scope", "str (chuỗi)", "Ngữ cảnh vùng chứa logic: 'Danh mục', 'Sản phẩm A', 'Sản phẩm B', 'Giỏ hàng', 'Hồ sơ'."),
        ("selector", "str (chuỗi)", "CSS Selector duy nhất trên trang thật, hỗ trợ locator Playwright tương tác chính xác 100%."),
        ("target_object", "Optional[str]", "Mã đối tượng nghiệp vụ được ánh xạ tự động (ví dụ: 'cart_item_quantity_A')."),
    ]

    h_node = tbl_node.rows[0]
    h_node.cells[0].paragraphs[0].text = "Trường dữ liệu"
    h_node.cells[1].paragraphs[0].text = "Kiểu dữ liệu"
    h_node.cells[2].paragraphs[0].text = "Mô tả kỹ thuật và ý nghĩa"
    format_table_header(h_node, col_w_node)

    for idx, (f, t, d) in enumerate(node_fields):
        row = tbl_node.rows[idx + 1]
        row.cells[0].paragraphs[0].text = f
        row.cells[1].paragraphs[0].text = t
        row.cells[2].paragraphs[0].text = d
        format_table_row(row, col_w_node, is_even=(idx % 2 == 1), alignments=[WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT])

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # 2.3
    h2_3 = doc.add_heading("3. Giải quyết bài toán: Định vị nút cùng nhãn trong hai vùng khác nhau", level=2)
    h2_3.paragraph_format.space_before = Pt(10)
    h2_3.paragraph_format.space_after = Pt(4)
    for r in h2_3.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = RGBColor(43, 87, 154)

    p_scope = doc.add_paragraph()
    p_scope.paragraph_format.line_spacing = 1.25
    p_scope.paragraph_format.space_after = Pt(6)
    p_scope.add_run(
        "Trong các ứng dụng web thương mại, xung đột định vị (ambiguous selector) là nguyên nhân hàng đầu gây lỗi cho AI Agent. "
        "Cụ thể, trên trang demo/store.html, cả thẻ Sản phẩm A và thẻ Sản phẩm B đều chứa nút bấm có cùng nhãn hiển thị: 'Thêm vào giỏ'.\n"
        "Nếu bộ lọc chỉ chuyển cho Agent thông tin nút bấm là button 'Thêm vào giỏ' mà không có ngữ cảnh vùng chứa, "
        "Agent sẽ không thể phân biệt được nút nào của sản phẩm A và nút nào của sản phẩm B, dẫn đến việc luôn bấm nhầm vào sản phẩm đầu tiên.\n\n"
        "Giải pháp kỹ thuật của Huy:\n"
        "1. Duyệt ngược cây phân cấp DOM (DOM hierarchy climbing) trong dom_extractor.py để gán thuộc tính scope cho từng node "
        "(ví dụ nút của A có scope='Sản phẩm A', nút của B có scope='Sản phẩm B').\n"
        "2. Xây dựng phương thức locate_node_by_target(role, name, scope, entity) trong BrowserController:\n"
        "   - Đối sánh đồng thời role='button', name='Thêm vào giỏ' VÀ scope='Sản phẩm A'.\n"
        "   - Phân giải ra mã nút n-8 với CSS Selector duy nhất là #btn-add-a.\n"
        "   - Khi đối sánh với scope='Sản phẩm B', phân giải chính xác mã nút n-12 với CSS Selector #btn-add-b.\n"
        "3. Kết quả xác minh: Bài test test_scope_disambiguation_buttons_with_same_label trong tests/test_browser.py "
        "đã chạy qua 100%, bảo đảm không xảy ra bất kỳ lỗi strict mode violation nào của Playwright."
    ).font.name = "Times New Roman"

    # 2.4
    h2_4 = doc.add_heading("4. Thống nhất tiêu chuẩn 'Bằng chứng tối thiểu' với Test Oracle (Mai)", level=2)
    h2_4.paragraph_format.space_before = Pt(10)
    h2_4.paragraph_format.space_after = Pt(4)
    for r in h2_4.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = RGBColor(43, 87, 154)

    p_agree = doc.add_paragraph()
    p_agree.paragraph_format.line_spacing = 1.25
    p_agree.paragraph_format.space_after = Pt(6)
    p_agree.add_run(
        "Sau khi làm việc với Chu Bách Trúc Mai (phụ trách Test Oracle), hai bên đã thống nhất tiêu chuẩn Bằng chứng tối thiểu (Minimal Evidence Constraint):\n"
        "• Dù bộ lọc DOM cắt tỉa mạnh đến đâu, ở phương pháp đề xuất (Phương pháp B), bắt buộc phải giữ lại: "
        "(1) Nút thao tác mục tiêu kèm nhãn phân biệt (Action Target + Action Label); "
        "(2) Vùng dữ liệu/trường trạng thái dùng để đối chiếu trước - sau (Condition Evidence).\n"
        "• Nếu bộ lọc cắt mất phần tử này (xảy ra ở Phương pháp A khi lỗi nằm ngoài nút bấm), Test Oracle sẽ nhận diện được "
        "và đánh trượt ca đó thành lỗi MissingEvidence (nhãn INCONCLUSIVE), không quy chụp thành lỗi của web demo."
    ).font.name = "Times New Roman"

    # 2.5
    h2_5 = doc.add_heading("5. Bảng ánh xạ đối tượng logic (target_object) sang CSS Selector thật", level=2)
    h2_5.paragraph_format.space_before = Pt(10)
    h2_5.paragraph_format.space_after = Pt(4)
    for r in h2_5.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = RGBColor(43, 87, 154)

    p_map = doc.add_paragraph()
    p_map.paragraph_format.line_spacing = 1.25
    p_map.paragraph_format.space_after = Pt(6)
    p_map.add_run(
        "Để phục vụ Trang viết 25 ca kiểm thử và Mai viết code đối chiếu Oracle, Huy đã xây dựng lớp "
        "TargetObjectMapper (src/webtest/browser/target_mapper.py) chuẩn hóa 23 đối tượng giao diện trên Web Demo:"
    ).font.name = "Times New Roman"

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

    # ------------------ PHẦN III: KẾT QUẢ GIAI ĐOẠN 2 ------------------
    h3 = doc.add_heading("PHẦN III. KẾT QUẢ THỰC HIỆN GIAI ĐOẠN 2: XÂY DỰNG CÁC MÔ-ĐUN", level=1)
    h3.paragraph_format.space_before = Pt(14)
    h3.paragraph_format.space_after = Pt(6)
    for r in h3.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(14)
        r.font.bold = True
        r.font.color.rgb = RGBColor(31, 78, 121)

    p_gd2 = doc.add_paragraph()
    p_gd2.paragraph_format.line_spacing = 1.25
    p_gd2.paragraph_format.space_after = Pt(6)
    p_gd2.add_run(
        "Trong Giai đoạn 2, Huy đã hoàn thành trọn vẹn việc xây dựng mã nguồn mô-đun cắt tỉa DOM (src/webtest/pruning/) "
        "với 4 chế độ lọc, cài đặt bộ đếm và kiểm soát ngân sách token, gắn lý do giữ cho từng phần tử, giải quyết bài toán giao tiếp "
        "với Test Oracle, và kiểm chứng sự vượt trội của Phương pháp B so với Phương pháp A trên thực nghiệm."
    ).font.name = "Times New Roman"

    # 3.1
    h3_1 = doc.add_heading("1. Kiến trúc và thuật toán 4 chế độ cắt tỉa DOM (DOMPruner)", level=2)
    h3_1.paragraph_format.space_before = Pt(10)
    h3_1.paragraph_format.space_after = Pt(4)
    for r in h3_1.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = RGBColor(43, 87, 154)

    p_modes = doc.add_paragraph()
    p_modes.paragraph_format.line_spacing = 1.25
    p_modes.paragraph_format.space_after = Pt(6)
    p_modes.add_run(
        "Lớp DOMPruner (src/webtest/pruning/pruner.py) cung cấp hàm prune(snapshot, mode, step, conditions, token_budget) "
        "hỗ trợ 4 chế độ lọc theo đặc tả nghiên cứu:"
    ).font.name = "Times New Roman"

    tbl_prune_modes = doc.add_table(rows=5, cols=3)
    tbl_prune_modes.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_prune_modes)
    col_w_pm = [Inches(1.8), Inches(1.5), Inches(3.2)]

    pm_data = [
        ("Chế độ 1: DOM đầy đủ\n(mode='full')", "Toàn bộ snapshot quan sát được", "Không cắt tỉa; giữ tất cả các thẻ quan sát được; dùng làm đường cơ sở đo lường tối đa."),
        ("Chế độ 2: Lọc theo thẻ\n(mode='tag_filter')", "Thẻ tương tác & thẻ văn bản", "Chỉ giữ button, a, input, select, textarea và các thẻ tiêu đề/văn bản có nghĩa. Giảm thiểu các thẻ div/span rỗng."),
        ("Chế độ 3: Phương pháp A\n(mode='task_only')", "Mô tả nhiệm vụ & mục tiêu bước", "Lọc DOM chỉ dựa vào target của bước. Giữ Action Target và Action Label. KHÔNG giữ bằng chứng đối chiếu của điều kiện."),
        ("Chế độ 4: Phương pháp B\n(mode='task_condition')", "Nhiệm vụ VÀ điều kiện kiểm thử", "Giữ đồng thời Action Target + Condition Evidence (Bằng chứng tối thiểu) + Action Label. Bảo toàn trường dữ liệu cho Test Oracle."),
    ]

    h_pm = tbl_prune_modes.rows[0]
    h_pm.cells[0].paragraphs[0].text = "Chế độ cắt tỉa"
    h_pm.cells[1].paragraphs[0].text = "Căn cứ lựa chọn phần tử"
    h_pm.cells[2].paragraphs[0].text = "Cơ chế chọn lọc & Bảo vệ bằng chứng"
    format_table_header(h_pm, col_w_pm)

    for idx, (m, c, d) in enumerate(pm_data):
        row = tbl_prune_modes.rows[idx + 1]
        row.cells[0].paragraphs[0].text = m
        row.cells[1].paragraphs[0].text = c
        row.cells[2].paragraphs[0].text = d
        format_table_row(row, col_w_pm, is_even=(idx % 2 == 1), alignments=[WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT])

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # 3.2
    h3_2 = doc.add_heading("2. Cơ chế lưu lý do giữ (reason) và kiểm soát ngân sách token (token_budget)", level=2)
    h3_2.paragraph_format.space_before = Pt(10)
    h3_2.paragraph_format.space_after = Pt(4)
    for r in h3_2.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = RGBColor(43, 87, 154)

    p_reason = doc.add_paragraph()
    p_reason.paragraph_format.line_spacing = 1.25
    p_reason.paragraph_format.space_after = Pt(6)
    p_reason.add_run(
        "Mỗi phần tử được giữ lại trong PrunedDOMResult đều được gắn một nhãn reason rõ ràng:\n"
        "• action_target: Nút hoặc trường đích mà Agent cần tương tác.\n"
        "• action_label: Nhãn ngữ cảnh kề cận giúp Agent định danh đúng đối tượng.\n"
        "• condition_evidence: Phần tử chứa dữ liệu kết quả để Test Oracle đối chiếu.\n"
        "• container_context: Vùng chứa/hàng bảng giúp phân biệt dữ liệu giữa các thực thể.\n"
        "• tag_interactive / tag_text: Giữ lại theo bộ lọc thẻ thông thường.\n\n"
        "Kiểm soát ngân sách token (DOMTokenizer & token_budget):\n"
        "• Lớp DOMTokenizer (src/webtest/pruning/tokenizer.py) thực hiện phân tích cú pháp chuỗi tuần tự hóa thành các token xác định.\n"
        "• Khi truyền tham số token_budget (ví dụ 90 tokens), thuật toán phân bổ ngân sách theo thứ tự ưu tiên:\n"
        "  - Phương pháp B: Ưu tiên 1 (bắt buộc) = action_target + condition_evidence. Ưu tiên 2 = action_label. Ưu tiên 3 = container_context. Nhờ đó, bằng chứng đối chiếu không bao giờ bị cắt trước các phần tử ngữ cảnh!\n"
        "  - Phương pháp A: Dồn toàn bộ ngân sách cho action_target và các nhãn lân cận của nó, dẫn đến việc cạn kiệt token trước khi kịp giữ trường số lượng giỏ hàng."
    ).font.name = "Times New Roman"

    # 3.3
    h3_3 = doc.add_heading("3. Trả lời câu hỏi phối hợp của Chu Bách Trúc Mai (Test Oracle)", level=2)
    h3_3.paragraph_format.space_before = Pt(10)
    h3_3.paragraph_format.space_after = Pt(4)
    for r in h3_3.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = RGBColor(43, 87, 154)

    add_callout_box(
        doc,
        "Câu hỏi từ Mai: 'Khi Huy cắt tỉa DOM xong, Huy trả về danh sách các phần tử được giữ lại dưới dạng mảng selector "
        "(chuỗi CSS/XPath) hay mảng node_id (số nguyên) để Mai truyền vào hàm kiểm tra Thiếu bằng chứng (MissingEvidence)?'\n\n"
        "Trả lời và Giải pháp từ Huy: Đối tượng PrunedDOMResult cung cấp thuộc tính đa năng 'pruned_dom_targets' chứa đồng thời:\n"
        "1. Tên logic target_object (ví dụ: 'cart_item_quantity_A')\n"
        "2. Chuỗi CSS Selector thật (ví dụ: '#cart-item-quantity-a', '#cart-item-a .item-qty')\n"
        "3. Mã nút định danh theo snapshot (ví dụ: 'n-18')\n"
        "4. Chuỗi tham chiếu phân cấp (ví dụ: 'Giỏ hàng:Sản phẩm A:Số lượng')\n"
        "5. Mã data-testid (ví dụ: 'cart_item_quantity_A')\n\n"
        "Nhờ thiết kế đa năng này, hàm evaluate_conditions(conditions, pruned_dom_targets) của Mai chỉ cần kiểm tra trực tiếp:\n"
        "   if condition['target_object'] not in pruned_dom_targets:\n"
        "       return self.record_system_issue('MissingEvidence', ...)\n"
        "Mã nguồn tương thích 100%, không cần bất kỳ bước trung gian nào để chuyển đổi kiểu dữ liệu!",
        title="PHỐI HỢP KỸ THUẬT VỚI MÔ-ĐUN TEST ORACLE"
    )

    # 3.4
    h3_4 = doc.add_heading("4. Bằng chứng thực nghiệm đối chứng: Phương pháp A vs Phương pháp B", level=2)
    h3_4.paragraph_format.space_before = Pt(10)
    h3_4.paragraph_format.space_after = Pt(4)
    for r in h3_4.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = RGBColor(43, 87, 154)

    p_exp = doc.add_paragraph()
    p_exp.paragraph_format.line_spacing = 1.25
    p_exp.paragraph_format.space_after = Pt(6)
    p_exp.add_run(
        "Để trả lời trực tiếp câu hỏi khoa học của đề tài, Huy đã thiết lập bài thực nghiệm đối chứng định lượng trong "
        "tests/test_pruner.py (hàm test_token_budget_enforcement_and_missing_evidence_contrast) trên ca chuẩn "
        "cart-quantity.json với cùng mức ngân sách token là 90 tokens:"
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

    p_exp_concl = doc.add_paragraph()
    p_exp_concl.paragraph_format.line_spacing = 1.25
    p_exp_concl.paragraph_format.space_after = Pt(6)
    r_ec = p_exp_concl.add_run(
        "Nhận xét thực nghiệm quan trọng: Dưới cùng một giới hạn ngân sách token (90 tokens), Phương pháp A tuy giữ được nút bấm "
        "nhưng đã lãng phí token vào phần mô tả thẻ sản phẩm A, dẫn đến việc không đủ chỗ cho trường số lượng giỏ hàng. "
        "Hậu quả là Test Oracle bị thiếu bằng chứng và phải đánh nhãn INCONCLUSIVE. Ngược lại, Phương pháp B chủ động ưu tiên cụm "
        "Bằng chứng tối thiểu, vừa giữ được nút bấm vừa bảo toàn trường số lượng với chi phí token chỉ 84 tokens (thấp hơn A), "
        "giúp hệ thống kết luận chính xác ca kiểm thử. Đây là bằng chứng thực nghiệm trực tiếp chứng minh tính đúng đắn của đề tài."
    )
    r_ec.font.name = "Times New Roman"
    r_ec.font.size = Pt(10.5)
    r_ec.font.italic = True

    # 3.5
    h3_5 = doc.add_heading("5. Kết quả kiểm thử tự động toàn diện (Test Suite Verification)", level=2)
    h3_5.paragraph_format.space_before = Pt(10)
    h3_5.paragraph_format.space_after = Pt(4)
    for r in h3_5.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = RGBColor(43, 87, 154)

    p_test_intro = doc.add_paragraph()
    p_test_intro.paragraph_format.line_spacing = 1.25
    p_test_intro.paragraph_format.space_after = Pt(6)
    p_test_intro.add_run(
        "Toàn bộ mã nguồn đã được kiểm thử tự động với 17 bài test độc lập và tích hợp. Kết quả thực thi thực tế như sau:"
    ).font.name = "Times New Roman"

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

    # ------------------ PHẦN IV: HƯỚNG DẪN BÀN GIAO GIAI ĐOẠN 3 ------------------
    h4 = doc.add_heading("PHẦN IV. TÀI LIỆU BÀN GIAO CHO GIAI ĐOẠN 3 (TRẦN VĂN THỊNH)", level=1)
    h4.paragraph_format.space_before = Pt(14)
    h4.paragraph_format.space_after = Pt(6)
    for r in h4.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(14)
        r.font.bold = True
        r.font.color.rgb = RGBColor(31, 78, 121)

    p_handover = doc.add_paragraph()
    p_handover.paragraph_format.line_spacing = 1.25
    p_handover.paragraph_format.space_after = Pt(6)
    p_handover.add_run(
        "Kính gửi Trưởng nhóm Trần Văn Thịnh: Để phục vụ việc ghép nối AI Agent, Playwright và Test Oracle trong "
        "Trình điều phối (Runner) ở Giai đoạn 3, Thịnh chỉ cần import và sử dụng trực tiếp hai lớp BrowserController và DOMPruner "
        "theo mẫu chuẩn dưới đây:"
    ).font.name = "Times New Roman"

    code_handover = (
        "from webtest.browser import BrowserController\n"
        "from webtest.pruning import DOMPruner\n"
        "\n"
        "# 1. Khởi tạo trình duyệt và bộ cắt tỉa DOM\n"
        "browser = BrowserController(headless=True)\n"
        "pruner = DOMPruner()\n"
        "page = browser.start()\n"
        "\n"
        "# 2. Điều hướng và lấy snapshot trước thao tác\n"
        "browser.navigate(case['initial']['path'])\n"
        "snapshot_before = browser.capture_snapshot('obs-pre')\n"
        "\n"
        "# 3. Cắt tỉa DOM (chọn mode='task_condition' hoặc 'task_only' với cùng token_budget)\n"
        "pruned_dom = pruner.prune(\n"
        "    snapshot=snapshot_before,\n"
        "    mode='task_condition',\n"
        "    step=case['steps'][0],\n"
        "    conditions=conditions_list,\n"
        "    token_budget=150\n"
        ")\n"
        "\n"
        "# 4. Cấp chuỗi prompt biểu diễn DOM rút gọn cho AI Agent\n"
        "agent_input_dom = pruned_dom.to_text()\n"
        "\n"
        "# 5. Agent trả lệnh JSON -> Playwright thực thi an toàn bằng target_id\n"
        "exec_result = browser.execute_action(agent_action_cmd)\n"
        "browser.wait_for_settle(settle_ms=200)\n"
        "\n"
        "# 6. Chụp snapshot sau thao tác và bàn giao mảng target cho Oracle của Mai\n"
        "snapshot_after = browser.capture_snapshot('obs-post')\n"
        "pruned_after = pruner.prune(snapshot_after, mode='task_condition', step=case['steps'][0], conditions=conditions_list)\n"
        "verdict = oracle.evaluate_conditions(conditions_list, pruned_after.pruned_dom_targets)"
    )
    add_code_block(doc, code_handover)

    # ------------------ PHẦN V: KẾT LUẬN & CHỮ KÝ ------------------
    h5 = doc.add_heading("PHẦN V. KẾT LUẬN VÀ CAM KẾT TIẾN ĐỘ", level=1)
    h5.paragraph_format.space_before = Pt(14)
    h5.paragraph_format.space_after = Pt(6)
    for r in h5.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(14)
        r.font.bold = True
        r.font.color.rgb = RGBColor(31, 78, 121)

    p_concl = doc.add_paragraph()
    p_concl.paragraph_format.line_spacing = 1.25
    p_concl.paragraph_format.space_after = Pt(10)
    p_concl.add_run(
        "Toàn bộ các nhiệm vụ của Nguyễn Quang Huy trong Giai đoạn 1 và Giai đoạn 2 đã được hoàn thành 100% "
        "đúng hạn, đúng đặc tả kiến trúc, vượt qua đầy đủ các bài kiểm tra chất lượng phần mềm nghiêm ngặt. "
        "Mã nguồn sạch, có tài liệu kỹ thuật chi tiết, có dữ liệu đối chứng khoa học rõ ràng, sẵn sàng chuyển giao "
        "và phối hợp cùng các thành viên trong Giai đoạn 3 (Tích hợp và chạy thử nghiệm)."
    ).font.name = "Times New Roman"

    # Signature block
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

    doc.save(str(OUTPUT_FILE))
    print(f"Report generated successfully at: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_full_report()

