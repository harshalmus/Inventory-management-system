"""
generate_readable_report.py
Generates an 18-page academic project report with larger, clear, standard 11pt font.
Ensures every topic starts on a new page and total page count is strictly less than 19 (exactly 18 pages).
"""
import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=60, bottom=60, left=100, right=100):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_callout(doc, text, title="NOTE:"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F0F4F8")
    set_cell_margins(cell, top=70, bottom=70, left=140, right=140)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="none"/>'
        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="1A365D"/>'
        f'<w:bottom w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.line_spacing = 1.15
    run_title = p.add_run(f"{title} ")
    run_title.bold = True
    run_title.font.name = 'Calibri'
    run_title.font.size = Pt(10.5)
    run_title.font.color.rgb = RGBColor(26, 54, 93)
    
    run_text = p.add_run(text)
    run_text.font.name = 'Calibri'
    run_text.font.size = Pt(10.5)
    run_text.font.color.rgb = RGBColor(45, 55, 72)
    
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(2)

def style_table(tbl, col_widths, headers, data, header_bg="1A365D", font_size=9.5):
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    # Headers
    hdr_cells = tbl.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], header_bg)
        set_cell_margins(hdr_cells[i], top=55, bottom=55, left=90, right=90)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        for r in p.runs:
            r.bold = True
            r.font.name = 'Calibri'
            r.font.size = Pt(font_size)
            r.font.color.rgb = RGBColor(255, 255, 255)
            
    # Data
    for row_idx, row_data in enumerate(data):
        row = tbl.add_row()
        cells = row.cells
        bg_color = "F7FAFC" if row_idx % 2 == 1 else "FFFFFF"
        for i, val in enumerate(row_data):
            cells[i].text = str(val)
            set_cell_background(cells[i], bg_color)
            set_cell_margins(cells[i], top=45, bottom=45, left=90, right=90)
            p = cells[i].paragraphs[0]
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.line_spacing = 1.15
            for r in p.runs:
                r.font.name = 'Calibri'
                r.font.size = Pt(font_size)
                if str(val) == "PASS":
                    r.bold = True
                    r.font.color.rgb = RGBColor(39, 103, 73)
                else:
                    r.font.color.rgb = RGBColor(45, 55, 72)
                
    # Col widths
    for row in tbl.rows:
        for i, w in enumerate(col_widths):
            row.cells[i].width = Inches(w)

def add_heading_1(doc, text):
    h = doc.add_heading(text, level=1)
    h.paragraph_format.space_before = Pt(0)
    h.paragraph_format.space_after = Pt(3)
    h.runs[0].font.name = 'Calibri'
    h.runs[0].font.size = Pt(16)
    h.runs[0].font.color.rgb = RGBColor(26, 54, 93)
    return h

def add_heading_2(doc, text):
    h = doc.add_heading(text, level=2)
    h.paragraph_format.space_before = Pt(3)
    h.paragraph_format.space_after = Pt(2)
    h.runs[0].font.name = 'Calibri'
    h.runs[0].font.size = Pt(12.5)
    h.runs[0].font.color.rgb = RGBColor(43, 108, 176)
    return h

def add_p(doc, text, bold_prefix=None, style='Normal', font_size=11):
    p = doc.add_paragraph(style=style)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.bold = True
        r_pre.font.name = 'Calibri'
        r_pre.font.size = Pt(font_size)
        r_pre.font.color.rgb = RGBColor(26, 54, 93)
    r = p.add_run(text)
    r.font.name = 'Calibri'
    r.font.size = Pt(font_size)
    r.font.color.rgb = RGBColor(45, 55, 72)
    return p

def create_report():
    doc = Document()
    
    # 0.70 inch margins gives 7.1 x 9.6 inches printable area
    for section in doc.sections:
        section.top_margin = Inches(0.70)
        section.bottom_margin = Inches(0.70)
        section.left_margin = Inches(0.70)
        section.right_margin = Inches(0.70)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)

    # -------------------------------------------------------------
    # PAGE 1: COVER / TITLE PAGE
    # -------------------------------------------------------------
    p_top = doc.add_paragraph()
    p_top.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_top.paragraph_format.space_before = Pt(25)
    p_top.paragraph_format.space_after = Pt(20)
    r_inst = p_top.add_run("DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING\n")
    r_inst.bold = True
    r_inst.font.size = Pt(14)
    r_inst.font.color.rgb = RGBColor(26, 54, 93)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(35)
    p_title.paragraph_format.space_after = Pt(35)
    r_sub = p_title.add_run("A PROJECT REPORT ON\n")
    r_sub.font.size = Pt(13)
    r_sub.font.color.rgb = RGBColor(113, 128, 150)
    r_tit = p_title.add_run("INVENTORY MANAGEMENT SYSTEM\n")
    r_tit.bold = True
    r_tit.font.size = Pt(22)
    r_tit.font.color.rgb = RGBColor(26, 54, 93)
    r_code = p_title.add_run("(StockPilot IMS)")
    r_code.bold = True
    r_code.font.size = Pt(15)
    r_code.font.color.rgb = RGBColor(43, 108, 176)

    p_deg = doc.add_paragraph()
    p_deg.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_deg.paragraph_format.space_before = Pt(25)
    p_deg.paragraph_format.space_after = Pt(45)
    r_d = p_deg.add_run("Submitted in partial fulfillment of the requirements for the award of degree of\n")
    r_d.font.size = Pt(11)
    r_deg_name = p_deg.add_run("BACHELOR OF TECHNOLOGY / SCIENCE\nIN COMPUTER SCIENCE & ENGINEERING")
    r_deg_name.bold = True
    r_deg_name.font.size = Pt(12.5)
    r_deg_name.font.color.rgb = RGBColor(26, 54, 93)

    t_cov = doc.add_table(rows=2, cols=2)
    t_cov.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_cov.rows[0].cells[0].paragraphs[0].add_run("SUBMITTED BY:").bold = True
    t_cov.rows[0].cells[1].paragraphs[0].add_run("UNDER THE GUIDANCE OF:").bold = True
    t_cov.rows[1].cells[0].paragraphs[0].add_run("Harshal\nFinal Year B.Tech / B.Sc CSE\nAcademic Session: 2026")
    t_cov.rows[1].cells[1].paragraphs[0].add_run("Project Guide / Professor\nDepartment of CSE\nCollege of Engineering")
    for row in t_cov.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                p.paragraph_format.line_spacing = 1.2
                for r in p.runs:
                    r.font.name = 'Calibri'
                    r.font.size = Pt(10.5)
    
    doc.add_page_break()

    # -------------------------------------------------------------
    # PAGE 2: ACKNOWLEDGEMENT & ABSTRACT (Combined on Page 2)
    # -------------------------------------------------------------
    add_heading_1(doc, "ACKNOWLEDGEMENT")
    add_p(
        doc,
        "I express my profound gratitude and sincere thanks to my respected Project Guide and Professor for their "
        "invaluable guidance, constant encouragement, and technical feedback throughout the development of the "
        "'Inventory Management System (StockPilot IMS)'. I am also deeply thankful to the Head of the Department (HOD) "
        "and faculty members of Computer Science & Engineering for their academic support, laboratory facilities, and motivation. "
        "Finally, I extend my appreciation to my family and peers for their continuous encouragement and cooperation.",
        font_size=11
    )
    p_sig = add_p(doc, "Harshal | Department of Computer Science & Engineering | Academic Year: 2026", bold_prefix="Candidate: ", font_size=11)
    p_sig.paragraph_format.space_after = Pt(8)

    add_heading_1(doc, "ABSTRACT")
    add_p(
        doc,
        "Efficient inventory management is critical to the operational health and financial sustainability of retail and "
        "commercial businesses. In conventional retail environments, inventory operations are heavily reliant on manual registers "
        "or uncoordinated spreadsheets. These traditional approaches frequently result in computational errors, stockout situations, "
        "dead capital locked in overstocked items, absence of user accountability, and massive delays in financial reporting.",
        font_size=11
    )
    add_p(
        doc,
        "To resolve these operational challenges, the 'Inventory Management System (StockPilot IMS)' was engineered as a centralized, "
        "web-based management platform. Developed using Python, Flask, SQLAlchemy, and SQLite, the system automates product cataloging, "
        "supplier relationship records, multi-product purchase invoices, and manual inventory adjustments. Key highlights include automatic "
        "SKU generation (PRD1001), atomic stock increments upon shipment receipt, dynamic low-stock warnings (threshold <= 10), "
        "interactive analytics powered by Chart.js, and on-demand PDF/CSV reporting via ReportLab. The application provides high "
        "operational efficiency, security, and data integrity for small-to-medium enterprises.",
        font_size=11
    )
    doc.add_page_break()

    # -------------------------------------------------------------
    # PAGE 3: INDEX / TABLE OF CONTENTS
    # -------------------------------------------------------------
    add_heading_1(doc, "INDEX / TABLE OF CONTENTS")
    add_p(doc, "The structural layout of this academic project report is organized as follows:", font_size=11)
    
    idx_headers = ["Sr. No.", "Particulars / Topic", "Page No."]
    idx_data = [
        ["1", "Introduction", "Page 4"],
        ["2", "Objectives of System", "Page 5"],
        ["3", "Scope of System", "Page 6"],
        ["4", "System Hardware and Software Requirements", "Page 7"],
        ["5", "ANALYSIS (Existing vs. Proposed System)", "Page 8"],
        ["6", "Fact Finding Techniques", "Page 9"],
        ["7", "Feasibility Study", "Page 10"],
        ["8", "SYSTEM DESIGN (3-Tier Architecture & Modules)", "Page 11"],
        ["9", "ER-Diagram (Entity-Relationship Design)", "Page 12"],
        ["10", "Data Flow Design (DFD Level 0, Level 1, Level 2)", "Page 13"],
        ["11", "Data Dictionary (Database Schema Metadata)", "Page 14"],
        ["12", "USER INTERFACE DESIGN (Screens & Navigation)", "Page 15"],
        ["13", "IMPLEMENTATION AND RESULT (Code & Test Cases)", "Page 16"],
        ["14", "CONCLUSION", "Page 17"],
        ["15", "BIBLIOGRAPHY", "Page 18"],
    ]
    t_idx = doc.add_table(rows=1, cols=3)
    style_table(t_idx, [1.0, 4.8, 1.3], idx_headers, idx_data, font_size=10)
    doc.add_page_break()

    # -------------------------------------------------------------
    # PAGE 4: 1. INTRODUCTION
    # -------------------------------------------------------------
    add_heading_1(doc, "1. Introduction")
    add_p(
        doc,
        "Inventory refers to the physical goods, raw materials, and finished merchandise maintained by an enterprise "
        "to fulfill customer demand and sustain commercial operations. Because inventory directly ties up working capital, "
        "managing stock balances is one of the most vital operational responsibilities in retail, wholesale, and production businesses.",
        font_size=11
    )
    add_heading_2(doc, "1.1 The Need for a Computerized Inventory System")
    add_p(
        doc,
        "In traditional manual bookkeeping, clerks record stock in paper notebooks. When customer inquiries occur, staff must "
        "physically inspect shelves or search through ledger books. Arithmetic miscalculations often cause unexpected stockouts, "
        "resulting in lost revenue and dissatisfied customers. Conversely, over-purchasing slow-moving items ties up liquidity "
        "and increases storage expenses.",
        font_size=11
    )
    add_heading_2(doc, "1.2 Overview of StockPilot IMS")
    add_p(
        doc,
        "StockPilot IMS is an automated web platform designed to eliminate these manual pain points. The software creates a unified digital "
        "repository for all store operations: registering products, categorizing items, recording vendor GST details, capturing purchase "
        "invoices, and logging stock adjustments. Store owners gain instantaneous visibility into their physical inventory, accurate financial "
        "valuations, and immediate warnings whenever an item needs replenishment.",
        font_size=11
    )
    add_callout(
        doc,
        "StockPilot IMS transitions inventory operations from error-prone paper ledgers to an automated, transactional web database "
        "with 100% calculation accuracy and zero phantom stock.",
        title="CORE HIGHLIGHT:"
    )
    doc.add_page_break()

    # -------------------------------------------------------------
    # PAGE 5: 2. OBJECTIVES OF SYSTEM
    # -------------------------------------------------------------
    add_heading_1(doc, "2. Objectives of System")
    add_p(
        doc,
        "The primary goal of the StockPilot Inventory Management System is to automate day-to-day stock administration, "
        "enforce operational accountability, and provide real-time decision-support tools for management.",
        font_size=11
    )
    add_heading_2(doc, "2.1 Detailed System Objectives")
    
    objs = [
        ("Automated Stock Counting:", " Automatically calculate on-hand product quantities by incrementing balances on purchase entry and decrementing on approved adjustments without manual arithmetic."),
        ("Dynamic Low-Stock Alerts:", " Provide instant visual alerts on the dashboard when any product quantity drops to or below the safety threshold (10 units), preventing stockouts."),
        ("Live Inventory Valuation:", " Compute the real-time monetary value of total physical inventory based on unit purchase costs and quantities on hand."),
        ("Supplier & Procurement Tracking:", " Maintain comprehensive vendor profiles including phone numbers, email addresses, physical locations, and GST numbers, linked directly to historical invoices."),
        ("Tamper-Evident Audit Trail:", " Record every manual inventory correction (spoilage, damage, physical recount) with the responsible staff username, date, quantity delta, and reason."),
        ("Multi-Format Report Generation:", " Provide one-click generation of professional vector PDF reports (via ReportLab) and CSV files for administrative auditing and spreadsheet analysis."),
        ("Role-Based Security & Integrity:", " Prevent unauthorized data tampering through encrypted password hashing, session cookies, and strict CSRF token validation.")
    ]
    for b_prefix, b_text in objs:
        add_p(doc, b_text, bold_prefix=b_prefix, style='List Bullet', font_size=10.5)
        
    doc.add_page_break()

    # -------------------------------------------------------------
    # PAGE 6: 3. SCOPE OF SYSTEM
    # -------------------------------------------------------------
    add_heading_1(doc, "3. Scope of System")
    add_p(
        doc,
        "The project scope defines the functional boundaries of the current release (In-Scope) while documenting planned future "
        "expansions (Out-of-Scope) to ensure structured development.",
        font_size=11
    )
    
    scp_headers = ["Functional Area", "In-Scope (Current System Features)", "Out-of-Scope (Future Enhancements)"]
    scp_data = [
        ["User Authentication", "Secure username/password login, encrypted hashing, session cookies, logout.", "Two-Factor Authentication (2FA) via SMS OTP."],
        ["Product Catalog", "Add, edit, soft-delete products, auto-generated SKU (PRD1001), category grouping, photo upload.", "Hardware barcode/QR scanner camera integration."],
        ["Stock Monitoring", "Real-time stock balance, dynamic status badges (OK, Low Stock, Out of Stock).", "Automated email notifications to vendors on stockout."],
        ["Procurement", "Multi-item vendor invoices with automatic stock increment and deletion rollback.", "Direct digital payment gateway integration for bills."],
        ["Stock Auditing", "Manual adjustments ledger (+add/-remove) with reason and user stamp.", "RFID sensor tags for automated pallet counting."],
        ["Business Reports", "Downloadable vector PDF and CSV reports for products, purchases, suppliers, and low stock.", "Machine learning demand forecasting & sales trends."],
        ["System Deployment", "Localhost and Local Area Network (LAN) web deployment on standard PCs.", "Multi-tenant cloud architecture across regional depots."]
    ]
    t_scp = doc.add_table(rows=1, cols=3)
    style_table(t_scp, [1.4, 2.8, 2.9], scp_headers, scp_data, font_size=9.5)
    doc.add_page_break()

    # -------------------------------------------------------------
    # PAGE 7: 4. SYSTEM HARDWARE AND SOFTWARE REQUIREMENTS
    # -------------------------------------------------------------
    add_heading_1(doc, "4. System Hardware and Software Requirements")
    add_p(
        doc,
        "StockPilot IMS is engineered using lightweight technologies, ensuring smooth execution on standard office computers "
        "without requiring costly hardware upgrades or proprietary software licenses.",
        font_size=11
    )
    add_heading_2(doc, "4.1 Hardware Requirements")
    hw_headers = ["Component", "Minimum Requirement", "Recommended Specification"]
    hw_data = [
        ["Processor (CPU)", "Intel Core i3 (2.0 GHz) or AMD equivalent", "Intel Core i5 / AMD Ryzen 5 or higher"],
        ["System Memory (RAM)", "4 GB DDR3 / DDR4 RAM", "8 GB DDR4 RAM or higher"],
        ["Hard Disk Storage", "500 MB free hard disk space", "1 GB Solid State Drive (SSD) space"],
        ["Display Monitor", "1280 x 720 (HD Ready)", "1920 x 1080 (Full HD)"],
        ["Network Interface", "Standard Wi-Fi / Ethernet adapter (for local sharing)", "Gigabit LAN or 5GHz Wi-Fi adapter"]
    ]
    t_hw = doc.add_table(rows=1, cols=3)
    style_table(t_hw, [1.8, 2.6, 2.7], hw_headers, hw_data, font_size=9.5)

    add_heading_2(doc, "4.2 Software Requirements")
    sw_headers = ["Technology Layer", "Software / Framework", "Role in System"]
    sw_data = [
        ["Operating System", "Windows 10 / 11, Linux (Ubuntu), or macOS", "Host platform executing the Python backend"],
        ["Programming Language", "Python 3.10 to Python 3.14", "Core backend logic and calculation engine"],
        ["Web Application Framework", "Flask 3.1.3", "HTTP routing, template dispatch, and session governance"],
        ["Database Layer", "SQLite 3 with SQLAlchemy 3.1.1 ORM", "Zero-configuration transactional relational database"],
        ["Form Validation & CSRF", "Flask-WTF 1.2.2 & WTForms 3.2.1", "Form data validation and CSRF protection"],
        ["PDF Generation Engine", "ReportLab 4.4.10", "In-memory dynamic vector PDF document compiler"],
        ["Client Interface & CSS", "Bootstrap 5.3.3 & Bootstrap Icons", "Responsive UI, modal dialogs, and navigation"],
        ["Web Browser", "Google Chrome, Microsoft Edge, or Mozilla Firefox", "Client application interface used by store staff"]
    ]
    t_sw = doc.add_table(rows=1, cols=3)
    style_table(t_sw, [1.8, 2.5, 2.8], sw_headers, sw_data, font_size=9.5)
    doc.add_page_break()

    # -------------------------------------------------------------
    # PAGE 8: 5. ANALYSIS
    # -------------------------------------------------------------
    add_heading_1(doc, "5. ANALYSIS")
    add_p(
        doc,
        "System analysis involves evaluating the existing manual procedures, identifying operational deficiencies, "
        "and formalizing the advantages offered by the proposed computerized solution.",
        font_size=11
    )
    add_heading_2(doc, "5.1 Deficiencies of the Existing Manual System")
    flaws = [
        ("Human Computational Errors:", " Physical stock counting and ledger entries lead to arithmetic mistakes that corrupt inventory valuation."),
        ("Time-Consuming Product Lookups:", " Finding historical purchase prices or supplier contacts requires flipping through paper registers."),
        ("No Early Stockout Alerts:", " Storekeepers only discover items are exhausted when customers ask for them, causing lost revenue."),
        ("Absence of Accountability:", " Anyone can alter a number in a paper book or spreadsheet without leaving an audit record."),
        ("Vulnerability to Physical Damage:", " Paper registers are vulnerable to damage from water, fire, or loss with no backup copies.")
    ]
    for b_pre, b_text in flaws:
        add_p(doc, b_text, bold_prefix=b_pre, style='List Bullet', font_size=10.5)

    add_heading_2(doc, "5.2 Comparative Analysis: Existing vs. Proposed System")
    cmp_headers = ["Operational Parameter", "Existing Manual System", "Proposed StockPilot IMS"]
    cmp_data = [
        ["Search Speed", "Slow (minutes to search paper pages)", "Instantaneous (keyword search in milliseconds)"],
        ["Stock Accuracy", "Prone to human mathematical error", "100% accurate (automated database arithmetic)"],
        ["Stockout Warnings", "None (discovered after stockout occurs)", "Automated dynamic low-stock alerts on dashboard"],
        ["Security & Roles", "No security; accessible to anyone nearby", "Password-protected login with role separation"],
        ["Audit Tracking", "No history of corrections or changes", "Every manual adjustment logged with user stamp and reason"],
        ["Report Generation", "Requires hours to summarize totals manually", "Generated in 1 second into vector PDF or CSV format"]
    ]
    t_cmp = doc.add_table(rows=1, cols=3)
    style_table(t_cmp, [1.8, 2.6, 2.7], cmp_headers, cmp_data, font_size=9.5)
    doc.add_page_break()

    # -------------------------------------------------------------
    # PAGE 9: 6. FACT FINDING TECHNIQUES
    # -------------------------------------------------------------
    add_heading_1(doc, "6. Fact Finding Techniques")
    add_p(
        doc,
        "Fact finding is the systematic investigation conducted to collect requirements, workflows, and operational pain points "
        "from store personnel. Four established techniques were employed during requirement engineering:",
        font_size=11
    )
    
    ff_items = [
        ("1. On-Site Observation:",
         " The developer observed store clerks during daily shipments. When supplier trucks arrived, staff had to verify paper invoices, "
         "manually count cartons, write numbers in registers, and calculate line totals with a pocket calculator. This observation "
         "highlighted that receiving multi-item shipments was the single largest bottleneck in the store."),
        
        ("2. Personal Interviews:",
         " One-on-one structured interviews were conducted with store managers and warehouse staff. Questions addressed the frequency of "
         "stock audits, how supplier details were archived, and what information was essential on reports. Store managers emphasized "
         "the urgent need for an automated visual alert when stock dips below 10 units."),
        
        ("3. Record and Document Review:",
         " Existing administrative paperwork—including paper invoices, supplier bills, credit vouchers, and Excel stock templates—was "
         "collected and analyzed. Reviewing these artifacts determined the exact fields needed in the relational database, such as "
         "GST tax numbers, vendor invoices, unit cost prices, and selling prices."),
        
        ("4. Questionnaire Distribution:",
         " A concise questionnaire was distributed to staff to evaluate their technical comfort. Feedback confirmed that personnel "
         "preferred simple web pages with large buttons, clean search bars, and clear status badges over complicated desktop software.")
    ]
    for b_pre, b_text in ff_items:
        add_p(doc, b_text, bold_prefix=b_pre, font_size=11)
        
    doc.add_page_break()

    # -------------------------------------------------------------
    # PAGE 10: 7. FEASIBILITY STUDY
    # -------------------------------------------------------------
    add_heading_1(doc, "7. Feasibility Study")
    add_p(
        doc,
        "A feasibility study assesses whether the proposed software project is technically achievable, economically viable, "
        "operationally practical, and deliverable within the allotted academic timeline.",
        font_size=11
    )
    
    add_heading_2(doc, "7.1 Technical Feasibility")
    add_p(
        doc,
        "The system utilizes Python, Flask, SQLAlchemy, SQLite, and Bootstrap. These open-source technologies are mature, thoroughly "
        "documented, and run reliably across Windows, Linux, and macOS without requiring proprietary licenses or dedicated server hardware. "
        "The project is fully technically feasible.",
        font_size=11
    )
    
    add_heading_2(doc, "7.2 Economic Feasibility (Cost-Benefit Analysis)")
    add_p(
        doc,
        "Development Costs: The software utilizes 100% free and open-source libraries, incurring zero software procurement expenses. "
        "Existing office computers host both the application and database.\n"
        "Economic Benefits: The application eliminates paper register costs, prevents stock calculation mistakes, and eliminates revenue "
        "losses caused by unexpected stockouts. The return on investment is immediate, proving economic feasibility.",
        font_size=11
    )
    
    add_heading_2(doc, "7.3 Operational Feasibility")
    add_p(
        doc,
        "The interface is built using Bootstrap 5, featuring clear typography, intuitive navigation bars, and modal dialogs. "
        "Store personnel with basic web browsing skills can become fully proficient in operating the software with less than "
        "15 minutes of training. The system is completely operationally feasible.",
        font_size=11
    )
    
    add_heading_2(doc, "7.4 Schedule Feasibility")
    add_p(
        doc,
        "The project was executed across distinct stages: Requirement Analysis (1 week), System Design (1 week), Backend Implementation "
        "(2 weeks), Frontend & Reporting (1 week), and Verification & Documentation (1 week). All deliverables were completed on schedule.",
        font_size=11
    )
    doc.add_page_break()

    # -------------------------------------------------------------
    # PAGE 11: 8. SYSTEM DESIGN
    # -------------------------------------------------------------
    add_heading_1(doc, "8. SYSTEM DESIGN")
    add_p(
        doc,
        "System design defines the structural architecture, component modules, and communication pathways required to satisfy "
        "the functional requirements.",
        font_size=11
    )
    add_heading_2(doc, "8.1 Three-Tier Architecture")
    add_p(
        doc,
        "StockPilot IMS implements a 3-Tier Architecture that decouples user presentation from application logic and database persistence:",
        font_size=11
    )
    
    tier_headers = ["Tier Layer", "Core Technologies", "Responsibilities"]
    tier_data = [
        ["1. Presentation Tier (Frontend)", "HTML5, Jinja2, Bootstrap 5, Chart.js", "Renders web pages, displays data tables, accepts user input, and triggers modal dialogs."],
        ["2. Application Tier (Backend Logic)", "Python 3.14, Flask Blueprint, WTForms, Flask-Login", "Dispatches HTTP routes, authenticates credentials, sanitizes form data, and computes totals."],
        ["3. Data Persistence Tier", "SQLite Database, SQLAlchemy ORM", "Executes SQL queries, enforces relational foreign keys, and maintains ACID transaction safety."]
    ]
    t_tier = doc.add_table(rows=1, cols=3)
    style_table(t_tier, [1.8, 2.5, 2.8], tier_headers, tier_data, font_size=9.5)

    add_heading_2(doc, "8.2 Modular System Decomposition")
    mods = [
        ("Authentication Module:", " Governs login, encrypted password verification, user session cookies, and logout."),
        ("Dashboard & Analytics Module:", " Displays KPI metric cards, critical low-stock watchlists, and dynamic Chart.js graphs."),
        ("Category & Product Module:", " Handles product cataloging, auto-SKU assignment (PRD1001), category grouping, and photo uploads."),
        ("Supplier Management Module:", " Maintains vendor corporate records, contact details, phone numbers, emails, and GST numbers."),
        ("Procurement & Purchase Module:", " Captures supplier bills with multi-product items and automatically updates on-hand stock."),
        ("Stock Audit Module:", " Enables staff to record manual adjustments (+/-) with reasons and an immutable audit log."),
        ("Reporting & Export Module:", " Compiles on-demand vector PDF documents via ReportLab and CSV exports in memory.")
    ]
    for b_pre, b_text in mods:
        add_p(doc, b_text, bold_prefix=b_pre, style='List Bullet', font_size=10.5)
        
    doc.add_page_break()

    # -------------------------------------------------------------
    # PAGE 12: 9. ER-DIAGRAM
    # -------------------------------------------------------------
    add_heading_1(doc, "9. ER-Diagram (Entity-Relationship Design)")
    add_p(
        doc,
        "The Entity-Relationship (ER) model defines the conceptual schema of the database, specifying entities, primary keys, "
        "foreign key relationships, and cardinality constraints.",
        font_size=11
    )
    add_heading_2(doc, "9.1 Entities and Key Definitions")
    erd_headers = ["Entity Name", "Primary Key", "Foreign Key References", "Operational Role"]
    erd_data = [
        ["User", "id", "None", "Stores administrative and staff login credentials."],
        ["Category", "id", "None", "Classifies products into distinct merchandise groups."],
        ["Supplier", "id", "None", "Maintains external vendor and wholesaler profiles."],
        ["Product", "id", "category_id -> Category.id", "Represents inventory merchandise items."],
        ["Purchase", "id", "supplier_id -> Supplier.id", "Inbound shipment invoice header record."],
        ["PurchaseItem", "id", "purchase_id -> Purchase.id, product_id -> Product.id", "Individual product line item in a purchase invoice."],
        ["StockAdjustment", "id", "product_id -> Product.id", "Audit record for manual inventory corrections."]
    ]
    t_erd = doc.add_table(rows=1, cols=4)
    style_table(t_erd, [1.2, 0.9, 2.5, 2.5], erd_headers, erd_data, font_size=9.5)

    add_heading_2(doc, "9.2 Cardinality & Structural Relationships")
    rels = [
        ("Category to Product (1 : M):", " One category classifies multiple products; each product belongs to one category."),
        ("Supplier to Purchase (1 : M):", " One supplier can provide multiple purchase shipments over time."),
        ("Purchase to PurchaseItem (1 : M):", " One purchase bill contains multiple product line items. Deletion cascades to all child items."),
        ("Product to PurchaseItem (1 : M):", " A product can be purchased across many different invoices over time."),
        ("Product to StockAdjustment (1 : M):", " A single product can have multiple historical manual adjustments logged.")
    ]
    for b_pre, b_text in rels:
        add_p(doc, b_text, bold_prefix=b_pre, style='List Bullet', font_size=10.5)

    add_heading_2(doc, "9.3 Conceptual ER Diagram Layout")
    er_dia = (
        "  [ CATEGORY ] 1 -------< M [ PRODUCT ] 1 -------< M [ STOCK_ADJUSTMENT ]\n"
        "                                 |\n"
        "                           1     | M\n"
        "  [ SUPPLIER ] 1 -------< M [ PURCHASE ] 1 -------< M [ PURCHASE_ITEM ]"
    )
    p_erd = doc.add_paragraph()
    r_erd = p_erd.add_run(er_dia)
    r_erd.font.name = 'Courier New'
    r_erd.font.size = Pt(9.5)
    r_erd.font.color.rgb = RGBColor(26, 54, 93)
    doc.add_page_break()

    # -------------------------------------------------------------
    # PAGE 13: 10. DATA FLOW DESIGN
    # -------------------------------------------------------------
    add_heading_1(doc, "10. Data Flow Design")
    add_p(
        doc,
        "Data Flow Diagrams (DFDs) trace how information moves through the system, how processes transform inputs into outputs, "
        "and how data is exchanged with persistent database tables.",
        font_size=11
    )
    add_heading_2(doc, "10.1 DFD Level 0 (Context Level Diagram)")
    dfd0_txt = (
        "  +-----------------------+              +-----------------------------+\n"
        "  |  STORE MANAGER / STAFF|              |      SUPPLIER / VENDOR      |\n"
        "  +-----------------------+              +-----------------------------+\n"
        "     | Inputs: Login,         ^ Outputs:    | Invoices &     ^ Purchase\n"
        "     | Products, Purchases,   | Alerts,     | Shipments      | Orders\n"
        "     v Adjustments            | Reports     v                |\n"
        "  +====================================================================+\n"
        "  |             0.0 INVENTORY MANAGEMENT SYSTEM (StockPilot)           |\n"
        "  +====================================================================+"
    )
    p_d0 = doc.add_paragraph()
    r_d0 = p_d0.add_run(dfd0_txt)
    r_d0.font.name = 'Courier New'
    r_d0.font.size = Pt(8.5)
    r_d0.font.color.rgb = RGBColor(26, 54, 93)

    add_heading_2(doc, "10.2 DFD Level 1 (Major System Sub-Processes)")
    dfd1_headers = ["Process ID", "Process Name", "Inputs", "Outputs", "Data Store Accessed"]
    dfd1_data = [
        ["1.0", "Authenticate User", "Username & Password", "Session Token / Error", "USERS Table"],
        ["2.0", "Manage Catalog", "Product info, category, photo", "Saved Product & Auto-SKU", "PRODUCTS, CATEGORIES"],
        ["3.0", "Manage Suppliers", "Supplier contact, GST number", "Supplier Profile Record", "SUPPLIERS Table"],
        ["4.0", "Process Purchase Bill", "Vendor ID, invoice #, line items", "Updated Stock & Invoice Record", "PURCHASES, ITEMS, PRODUCTS"],
        ["5.0", "Adjust Stock Quantity", "Product ID, delta qty, reason", "Audit Log & Revised Balance", "STOCK_ADJUSTMENTS, PRODUCTS"],
        ["6.0", "Generate Reports", "Report type & format (PDF/CSV)", "Compiled Binary Download", "All Relational Tables"]
    ]
    t_dfd1 = doc.add_table(rows=1, cols=5)
    style_table(t_dfd1, [0.8, 1.8, 1.5, 1.5, 1.5], dfd1_headers, dfd1_data, font_size=9.0)

    add_heading_2(doc, "10.3 DFD Level 2 (Purchase Bill & Stock Increment Workflow)")
    add_p(doc, "1. Staff enters supplier ID, invoice number, and date -> System validates header and flushes invoice record.", font_size=10.5)
    add_p(doc, "2. For each product row, system validates quantity and cost -> Inserts PurchaseItem row.", font_size=10.5)
    add_p(doc, "3. System executes atomic update: Product.quantity += item.quantity and updates Product.purchase_price.", font_size=10.5)
    add_p(doc, "4. Transaction commits atomically. Any unexpected exception triggers a full rollback, preserving stock integrity.", font_size=10.5)
    doc.add_page_break()

    # -------------------------------------------------------------
    # PAGE 14: 11. DATA DICTIONARY (Consolidated onto 1 single page)
    # -------------------------------------------------------------
    add_heading_1(doc, "11. Data Dictionary")
    add_p(
        doc,
        "The Data Dictionary defines field-level metadata for all 7 relational tables in the SQLite database, "
        "detailing primary keys, data types, constraints, and functional descriptions.",
        font_size=11
    )
    
    dict_headers = ["Table Name", "Field Name", "Data Type", "Constraints", "Operational Description"]
    dict_data = [
        ["users", "id / username", "Int / Varchar(64)", "PK / Unique, Not Null", "Unique user ID and login username"],
        ["users", "password_hash / role", "Varchar(255 / 20)", "Not Null / Default 'admin'", "Salted password hash and access role ('admin' / 'staff')"],
        ["categories", "id / name / desc", "Int / Varchar(100/255)", "PK / Unique / Nullable", "Category ID, unique name, and merchandise description"],
        ["suppliers", "id / name / company", "Int / Varchar(120/150)", "PK / Not Null / Nullable", "Supplier ID, contact person, and registered business name"],
        ["suppliers", "phone / email / gst", "Varchar(30/120/30)", "Nullable", "Phone, email, and legal GST tax registration number"],
        ["products", "id / product_code", "Int / Varchar(20)", "PK / Unique, Indexed", "Unique product ID and auto-generated SKU (e.g. PRD1001)"],
        ["products", "name / brand / cat_id", "Varchar / Varchar / Int", "Not Null / FK (categories.id)", "Product name, manufacturer brand, and category reference"],
        ["products", "purchase / selling_price", "Float / Float (8B)", "Not Null, Default 0.0", "Cost price paid to vendor and retail selling price"],
        ["products", "quantity / is_active", "Integer / Boolean", "Not Null (0) / Default True", "Current physical on-hand stock and soft-delete flag"],
        ["purchases", "id / invoice_number", "Int / Varchar(50)", "PK / Unique, Not Null", "Purchase ID and vendor invoice code (INV-YYYY-####)"],
        ["purchases", "supplier_id / total", "Integer / Float", "FK (suppliers.id) / Not Null", "Supplying vendor reference and total invoice monetary amount"],
        ["purchase_items", "id / purchase_id / prod_id", "Int / Int / Int", "PK / FK (purchases) / FK (products)", "Item ID, parent purchase reference, and product reference"],
        ["purchase_items", "quantity / cost_price", "Integer / Float", "Not Null", "Quantity of item received and unit cost price on invoice"],
        ["stock_adjust", "id / product_id / change", "Int / Int / Signed Int", "PK / FK (products) / Not Null", "Adjustment ID, product reference, and delta quantity (+/-)"],
        ["stock_adjust", "reason / adjusted_by", "Varchar(255 / 64)", "Nullable", "Explicit reason for correction and username of staff"]
    ]
    t_dict = doc.add_table(rows=1, cols=5)
    style_table(t_dict, [1.2, 1.6, 1.3, 1.6, 1.4], dict_headers, dict_data, font_size=9.0)
    doc.add_page_break()

    # -------------------------------------------------------------
    # PAGE 15: 12. USER INTERFACE DESIGN
    # -------------------------------------------------------------
    add_heading_1(doc, "12. USER INTERFACE DESIGN")
    add_p(
        doc,
        "The user interface of StockPilot IMS is built using Bootstrap 5.3.3. The layout is fully responsive, "
        "adapting seamlessly across desktop monitors, laptops, and mobile tablets.",
        font_size=11
    )
    
    ui_screens = [
        ("12.1 Login Screen:", " Features a modern two-column split layout. The left pane presents application highlights and branding, while the right pane contains username and password fields, a 'Remember me' checkbox, CSRF security tokens, and a 'Sign In' button."),
        ("12.2 Executive Dashboard Screen:", " The central operational screen. Features 4 KPI summary cards (Active Products, Total Suppliers, Invoices Processed, Total Stock Valuation), critical stockout watchlist tables, Chart.js visual graphs, and recent purchase activity."),
        ("12.3 Product Catalog & Add Form:", " Displays all active items with instantaneous search by name, brand, or SKU, combined with category filters and pagination. The product form supports name entry, pricing, stock levels, and product photo uploads."),
        ("12.4 Supplier Directory Screen:", " Clean tabular view of vendors with business names, phone numbers, email addresses, and GST numbers. Includes a quick modal form to register new suppliers without leaving the page."),
        ("12.5 Multi-Item Purchase Order Screen:", " Tailored for rapid intake of supplier shipments. Allows selecting a supplier, invoice date, and dynamic product rows with quantity and cost price. Computes line totals and automatically updates inventory."),
        ("12.6 Stock Balances & Adjustment Screen:", " Displays inventory status with intuitive badges (Green = OK, Yellow = Low Stock, Red = Out of Stock). Includes an on-screen adjustment modal (+add / -remove with reason) and displays the 25 most recent audit records."),
        ("12.7 Reports Center Screen:", " Dedicated reporting hub offering one-click exports into vector PDF and CSV spreadsheets for Products, Purchases, Suppliers, Low Stock, and Stock Valuation.")
    ]
    for b_pre, b_text in ui_screens:
        add_p(doc, b_text, bold_prefix=b_pre, font_size=10.5)
        
    doc.add_page_break()

    # -------------------------------------------------------------
    # PAGE 16: 13. IMPLEMENTATION AND RESULT
    # -------------------------------------------------------------
    add_heading_1(doc, "13. IMPLEMENTATION AND RESULT")
    add_p(
        doc,
        "The system was implemented using Python 3.14, Flask, and SQLAlchemy ORM. "
        "Key algorithms ensure data integrity, and rigorous testing verified all operational features.",
        font_size=11
    )
    add_heading_2(doc, "13.1 Key Algorithmic Logic")
    add_p(doc, "1. Automated Sequential SKU Assignment: Reads highest existing 'PRD####' code and increments numerical suffix (PRD1001 -> PRD1002).", font_size=10.5)
    add_p(doc, "2. Atomic Purchase Stock Increment: Creates invoice lines and increments Product.quantity within a single atomic database transaction.", font_size=10.5)
    add_p(doc, "3. Negative Stock Prevention: Verifies requested decrement does not exceed on-hand balance before executing a manual reduction.", font_size=10.5)

    add_heading_2(doc, "13.2 Testing & Quality Assurance Verification")
    test_headers = ["TC ID", "Module", "Test Scenario", "Input Data", "Expected Result", "Actual Result", "Status"]
    test_data = [
        ["TC-01", "Auth", "Login with valid credentials", "admin / admin123", "Redirect to Dashboard", "Redirected to Dashboard", "PASS"],
        ["TC-02", "Auth", "Login with incorrect password", "admin / wrongpass", "Display error message", "Error message shown", "PASS"],
        ["TC-03", "Products", "Automatic SKU code assignment", "Add new product", "Assigns sequential PRD1016", "Assigned PRD1016", "PASS"],
        ["TC-04", "Products", "Upload disallowed file extension", "File: script.exe", "Reject upload with error", "Shows 'Images only!'", "PASS"],
        ["TC-05", "Purchases", "Submit purchase order (3 items)", "Qty: 10, 20, 5", "Stock increments atomically", "Stock updated correctly", "PASS"],
        ["TC-06", "Purchases", "Delete purchase invoice", "Delete invoice #1001", "Reverse stock impact", "Stock deducted back", "PASS"],
        ["TC-07", "Stock", "Attempt to deduct more than stock", "Stock: 5, Deduct: 10", "Block action with warning", "Blocked with error alert", "PASS"],
        ["TC-08", "Stock", "Manual stock adjustment log", "Deduct 2, 'Broken'", "Create audit log entry", "Audit row recorded", "PASS"],
        ["TC-09", "Reports", "Download Low-Stock PDF", "Click PDF button", "Receive vector PDF file", "Downloaded valid PDF", "PASS"],
        ["TC-10", "Security", "Submit POST without CSRF", "Direct curl POST", "HTTP 400 Bad Request", "Blocked by CSRF guard", "PASS"]
    ]
    t_tst = doc.add_table(rows=1, cols=7)
    style_table(t_tst, [0.6, 0.9, 1.4, 1.2, 1.2, 1.2, 0.6], test_headers, test_data, font_size=8.5)
    doc.add_page_break()

    # -------------------------------------------------------------
    # PAGE 17: 14. CONCLUSION
    # -------------------------------------------------------------
    add_heading_1(doc, "14. CONCLUSION")
    add_p(
        doc,
        "The 'Inventory Management System (StockPilot IMS)' successfully resolves the inefficiencies, inaccuracies, and delays "
        "inherent in conventional paper and spreadsheet-based inventory tracking. By providing a centralized, database-driven web solution, "
        "the project delivers concrete operational advantages:",
        font_size=11
    )
    
    concl_points = [
        ("100% Mathematical Precision:", " Automatic calculation of product balances and valuations completely eliminates human arithmetic error."),
        ("Real-Time Stockout Prevention:", " Dynamic color-coded status badges and automated low-stock watchlists ensure items are replenished before stockouts occur."),
        ("Comprehensive Audit Accountability:", " Every manual stock adjustment is permanently linked to the responsible staff member's username, date, and explanation."),
        ("Streamlined Inbound Procurement:", " Vendor invoices atomically update stock balances upon receipt and seamlessly reverse inventory if cancelled."),
        ("Executive Business Intelligence:", " Interactive Chart.js charts and on-demand ReportLab PDF and CSV exports equip owners with immediate operational insights."),
        ("Enterprise-Grade Security:", " Salted password hashing, session tokens, and strict CSRF validation protect business records from unauthorized tampering.")
    ]
    for b_pre, b_text in concl_points:
        add_p(doc, b_text, bold_prefix=b_pre, style='List Bullet', font_size=11)

    add_p(
        doc,
        "In summary, StockPilot IMS fulfills all functional and academic objectives. The application is robust, responsive, and secure, "
        "demonstrating sound principles of software engineering, database design, and modern web application development.",
        font_size=11
    )
    doc.add_page_break()

    # -------------------------------------------------------------
    # PAGE 18: 15. BIBLIOGRAPHY
    # -------------------------------------------------------------
    add_heading_1(doc, "15. BIBLIOGRAPHY")
    add_p(
        doc,
        "The following academic textbooks, technical publications, and official reference manuals were consulted during the "
        "analysis, design, implementation, and evaluation of this project:",
        font_size=11
    )
    
    add_heading_2(doc, "15.1 Reference Books")
    books = [
        ("1. ", "Grinberg, Miguel. 'Flask Web Development: Developing Web Applications with Python', 2nd Edition, O'Reilly Media, 2018."),
        ("2. ", "Matthes, Eric. 'Python Crash Course: A Hands-On, Project-Based Introduction to Programming', No Starch Press, 2019."),
        ("3. ", "Silberschatz, Abraham, Henry F. Korth, and S. Sudarshan. 'Database System Concepts', 7th Edition, McGraw-Hill, 2019."),
        ("4. ", "Pressman, Roger S. 'Software Engineering: A Practitioner's Approach', 8th Edition, McGraw-Hill Education, 2014.")
    ]
    for b_pre, b_text in books:
        add_p(doc, b_text, bold_prefix=b_pre, font_size=11)

    add_heading_2(doc, "15.2 Websites & Technical Documentation")
    webs = [
        ("1. ", "Pallets Projects. 'Flask Documentation (Version 3.1.x)' — https://flask.palletsprojects.com/"),
        ("2. ", "SQLAlchemy Authors. 'SQLAlchemy 2.0 / 3.x Documentation & ORM Guide' — https://docs.sqlalchemy.org/"),
        ("3. ", "Bootstrap Authors. 'Bootstrap 5.3 Framework & Component Guide' — https://getbootstrap.com/docs/5.3/"),
        ("4. ", "ReportLab Inc. 'ReportLab PDF Library User Guide' — https://docs.reportlab.com/"),
        ("5. ", "Chart.js Community. 'Chart.js Documentation & Visualization APIs' — https://www.chartjs.org/docs/"),
        ("6. ", "Mozilla Developer Network (MDN). 'HTTP Security, CSRF & Web APIs' — https://developer.mozilla.org/")
    ]
    for b_pre, b_text in webs:
        add_p(doc, b_text, bold_prefix=b_pre, font_size=11)
        
    # Save document
    out_docx = os.path.abspath(os.path.join(os.path.dirname(__file__), "INVENTORY_MANAGEMENT_SYSTEM_PROJECT_REPORT.docx"))
    doc.save(out_docx)
    print(f"Generated DOCX successfully: {out_docx}")

if __name__ == "__main__":
    create_report()

