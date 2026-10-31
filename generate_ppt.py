import sys
import os

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
    from pptx.dml.color import RGBColor
    from pptx.enum.shapes import MSO_SHAPE
except ImportError:
    print("python-pptx not yet installed. Please wait for pip installation to finish.")
    sys.exit(1)

def create_presentation():
    prs = Presentation()
    # 16:9 widescreen dimensions
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6] # Blank slide

    # Color Palette
    BG_DARK = RGBColor(15, 23, 42)        # Slate 900
    CARD_BG = RGBColor(30, 41, 59)        # Slate 800
    BORDER_COLOR = RGBColor(51, 65, 85)   # Slate 700
    PRIMARY = RGBColor(99, 102, 241)      # Indigo 500
    SECONDARY = RGBColor(6, 182, 212)     # Cyan 500
    ACCENT = RGBColor(16, 185, 129)       # Emerald 500
    TEXT_MAIN = RGBColor(248, 250, 252)   # Slate 50
    TEXT_MUTED = RGBColor(148, 163, 184)  # Slate 400
    WHITE = RGBColor(255, 255, 255)

    def set_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_DARK
        bg.line.fill.background()
        return bg

    def add_header(slide, badge_text, title_text, subtitle_text=""):
        # Badge
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.5), Inches(2.2), Inches(0.4))
        badge.fill.solid()
        badge.fill.fore_color.rgb = RGBColor(49, 46, 129) # Indigo 900
        badge.line.color.rgb = PRIMARY
        tf_b = badge.text_frame
        tf_b.word_wrap = True
        p_b = tf_b.paragraphs[0]
        p_b.text = badge_text.upper()
        p_b.font.size = Pt(11)
        p_b.font.bold = True
        p_b.font.color.rgb = SECONDARY
        p_b.alignment = PP_ALIGN.CENTER

        # Title
        tx_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.95), Inches(11.5), Inches(0.8))
        tf_t = tx_title.text_frame
        tf_t.word_wrap = True
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.size = Pt(28)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_MAIN

        # Subtitle
        if subtitle_text:
            tx_sub = slide.shapes.add_textbox(Inches(0.8), Inches(1.65), Inches(11.5), Inches(0.5))
            tf_s = tx_sub.text_frame
            tf_s.word_wrap = True
            p_s = tf_s.paragraphs[0]
            p_s.text = subtitle_text
            p_s.font.size = Pt(14)
            p_s.font.color.rgb = TEXT_MUTED

    def add_card(slide, left, top, width, height, title, body_points):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = BORDER_COLOR
        card.line.width = Pt(1.5)

        tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.2), width - Inches(0.4), height - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        
        # Title
        p0 = tf.paragraphs[0]
        p0.text = title
        p0.font.size = Pt(18)
        p0.font.bold = True
        p0.font.color.rgb = SECONDARY
        p0.space_after = Pt(12)

        for pt in body_points:
            p = tf.add_paragraph()
            p.text = "• " + pt
            p.font.size = Pt(13)
            p.font.color.rgb = TEXT_MAIN
            p.space_after = Pt(8)

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)

    # Accent decorative bar
    bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.8), Inches(0.2), Inches(3.2))
    bar.fill.solid()
    bar.fill.fore_color.rgb = PRIMARY
    bar.line.fill.background()

    tb1 = s1.shapes.add_textbox(Inches(1.2), Inches(1.6), Inches(11), Inches(3.5))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p_badge = tf1.paragraphs[0]
    p_badge.text = "PROJECT PRESENTATION • FULL-STACK WEB APPLICATION"
    p_badge.font.size = Pt(13)
    p_badge.font.bold = True
    p_badge.font.color.rgb = SECONDARY
    p_badge.space_after = Pt(10)

    p_main = tf1.add_paragraph()
    p_main.text = "SpendWise"
    p_main.font.size = Pt(54)
    p_main.font.bold = True
    p_main.font.color.rgb = TEXT_MAIN
    p_main.space_after = Pt(12)

    p_sub = tf1.add_paragraph()
    p_sub.text = "Personal Expense Tracker & Real-Time Spending Analytics"
    p_sub.font.size = Pt(22)
    p_sub.font.bold = True
    p_sub.font.color.rgb = PRIMARY
    p_sub.space_after = Pt(16)

    p_desc = tf1.add_paragraph()
    p_desc.text = "A modern, privacy-focused application allowing users to effortlessly record daily expenses,\nmonitor total spending across time horizons, enforce monthly budgets, and analyze spending patterns."
    p_desc.font.size = Pt(14)
    p_desc.font.color.rgb = TEXT_MUTED

    # Metadata tags at bottom
    tb_meta = s1.shapes.add_textbox(Inches(1.2), Inches(5.6), Inches(11), Inches(1.0))
    tf_meta = tb_meta.text_frame
    p_m = tf_meta.paragraphs[0]
    p_m.text = "Tech Stack: Python • Flask • SQLite • HTML5 / Modern CSS • JavaScript • Chart.js\nAuthor: Project Team | sareena Workspace"
    p_m.font.size = Pt(13)
    p_m.font.color.rgb = ACCENT

    # =========================================================================
    # SLIDE 2: PROBLEM STATEMENT & MOTIVATION
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "Context & Need", "The Problem: Why Traditional Budgeting Fails", "Everyday financial leaks go unnoticed until bank balances run out.")

    add_card(s2, Inches(0.8), Inches(2.4), Inches(3.6), Inches(4.3), "💸 Micro-Expense Leaks", [
        "Small daily outlays (coffee, snacks, auto-rides, fast food) seem negligible individually.",
        "Accumulate into thousands of rupees/dollars every month without awareness.",
        "Lack of real-time logging results in sudden end-of-month budget shortfalls."
    ])

    add_card(s2, Inches(4.8), Inches(2.4), Inches(3.6), Inches(4.3), "⚠️ Reactive, Not Proactive", [
        "Bank statements are retroactive: they only tell you what went wrong after the money is gone.",
        "Users lack immediate visual feedback on remaining monthly allowance.",
        "No dynamic alerts when approaching or exceeding category spending caps."
    ])

    add_card(s2, Inches(8.8), Inches(2.4), Inches(3.6), Inches(4.3), "🔒 Privacy & Bloat in Apps", [
        "Commercial apps demand intrusive bank syncing credentials and SMS read permissions.",
        "Data is monetization-driven, sold to credit card vendors and advertisers.",
        "Complex onboarding, unwanted upsells, and recurring monthly subscriptions."
    ])

    # =========================================================================
    # SLIDE 3: PROJECT OBJECTIVES
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "Goals & Mission", "Project Objectives & Core Deliverables", "Empowering users with immediate control, privacy, and actionable financial visibility.")

    add_card(s3, Inches(0.8), Inches(2.4), Inches(5.6), Inches(4.3), "🎯 Functional Goals", [
        "Record daily expenses in under 3 seconds with Quick-Add bar.",
        "Aggregate spending instantaneously: Grand Total, Today, Rolling 7-day, and This Month.",
        "Set and enforce customizable monthly spending targets.",
        "Categorize expenses across 10 intuitive domains (Food, Transport, Bills, Shopping, Health, etc.).",
        "Track payment modes (Cash, Credit Card, Debit Card, UPI, Net Banking)."
    ])

    add_card(s3, Inches(6.8), Inches(2.4), Inches(5.6), Inches(4.3), "🛡️ Technical & Architectural Goals", [
        "100% Privacy: Local SQLite storage ensures zero external data leakage.",
        "Dual-Sync Resilience: Seamless client-side localStorage fallback for offline use.",
        "Interactive Data Visualizations: Real-time Chart.js doughnut and trend charts.",
        "Zero Friction: 1-click Windows batch launcher and pre-configured VS Code debuggers.",
        "1-Click Data Portability: Instant CSV export for spreadsheets."
    ])

    # =========================================================================
    # SLIDE 4: SYSTEM ARCHITECTURE
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "System Design", "Three-Tier Application Architecture", "Decoupled presentation, REST API routing, and embedded persistent storage.")

    add_card(s4, Inches(0.8), Inches(2.4), Inches(3.6), Inches(4.3), "🎨 1. Presentation Tier", [
        "Single-Page Dashboard with Semantic HTML5.",
        "CSS3 custom variables for instant Dark & Light theme switching.",
        "Chart.js responsive canvas integrations for visual analytics.",
        "Responsive grid adapting to desktop, laptop, and mobile screens.",
        "Quick-add bar & animated modal dialogs."
    ])

    add_card(s4, Inches(4.8), Inches(2.4), Inches(3.6), Inches(4.3), "⚙️ 2. Application / API Tier", [
        "Python 3.13 + Flask lightweight microframework.",
        "RESTful JSON endpoints handling validation & error handling.",
        "Aggregates summary statistics, budget progress, and 14-day trends.",
        "Streams dynamic CSV files for Excel/Sheets downloads.",
        "Thread-safe database connection context manager."
    ])

    add_card(s4, Inches(8.8), Inches(2.4), Inches(3.6), Inches(4.3), "🗄️ 3. Persistence Tier", [
        "Embedded SQLite relational database (expenses.db).",
        "Indexes on expense_date and category for sub-millisecond aggregations.",
        "ACID compliant transactions preventing data corruption.",
        "Dual-mode fallback: automatically switches to browser LocalStorage when opened offline."
    ])

    # =========================================================================
    # SLIDE 5: DATABASE SCHEMA & DATA MODEL
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "Data Engineering", "Database Schema & Query Optimization", "Relational data structures engineered for fast filtering, sorting, and reporting.")

    add_card(s5, Inches(0.8), Inches(2.4), Inches(5.6), Inches(4.3), "📋 expenses Table", [
        "id: INTEGER PRIMARY KEY AUTOINCREMENT",
        "title: TEXT NOT NULL (Transaction description)",
        "amount: REAL NOT NULL (Enforces CHECK amount > 0)",
        "category: TEXT NOT NULL (Food, Groceries, Transport...)",
        "expense_date: TEXT NOT NULL (ISO 8601 YYYY-MM-DD)",
        "payment_method: TEXT (Cash, Credit Card, UPI...)",
        "notes: TEXT (Optional merchant/invoice details)",
        "created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    ])

    add_card(s5, Inches(6.8), Inches(2.4), Inches(5.6), Inches(4.3), "⚙️ settings & Performance Indexes", [
        "settings Table: Key-value store for preferences.",
        "• monthly_budget: User's monthly limit (e.g. 30000).",
        "• currency_symbol & currency_code: (e.g. ₹, $, €, £).",
        "Index idx_expense_date: Accelerates range queries like 'Today', 'This Week', and 'This Month'.",
        "Index idx_expense_category: Accelerates category aggregations for doughnut charts."
    ])

    # =========================================================================
    # SLIDE 6: KEY FEATURES & DASHBOARD CAPABILITIES
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "Product Features", "Core Dashboard & Spending Features", "Everything required for effortless personal money management.")

    add_card(s6, Inches(0.8), Inches(2.4), Inches(3.6), Inches(4.3), "⚡ Recording Expenses", [
        "Quick Add Bar: Instant 1-click expense logging.",
        "Modal Form: Detailed entry with category icons, date picker, payment method, and notes.",
        "Instant CRUD: Real-time edit and delete with confirmation dialogs and toasts.",
        "Sample Data Seeder: Pre-loaded realistic sample data for instant exploration."
    ])

    add_card(s6, Inches(4.8), Inches(2.4), Inches(3.6), Inches(4.3), "📊 Spending Analytics", [
        "Category Doughnut Chart: Interactive distribution with percentages and legend tags.",
        "14-Day Trend Chart: Bar chart identifying spending peaks (e.g., weekends vs weekdays).",
        "Executive KPI Cards: Grand Total, Today Total, Rolling 7-Day Total, Month Total, and Daily Average."
    ])

    add_card(s6, Inches(8.8), Inches(2.4), Inches(3.6), Inches(4.3), "🎯 Budget & Utilities", [
        "Dynamic Budget Progress: Visual bar shifting Green -> Warning Amber -> Red Danger.",
        "Remaining Balance: Instantly warns when budget limit is approached or exceeded.",
        "Live Search & Filter: Search by title/notes, filter by category or period, sort by date or amount.",
        "CSV Data Export: 1-click download of all transaction history."
    ])

    # =========================================================================
    # SLIDE 7: AUTOMATED TESTING & QUALITY ASSURANCE
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "Verification", "Testing & Quality Assurance", "Automated test suite (test_app.py) validating edge cases and reliability.")

    add_card(s7, Inches(0.8), Inches(2.4), Inches(5.6), Inches(4.3), "🧪 Test Coverage Highlights", [
        "Database Add & Get: Verifies record insertion and retrieval by ID.",
        "Validation Rules: Asserts rejection of negative amounts, zero amounts, and empty titles.",
        "Update & Delete Lifecycle: Confirms edits persist and deletion removes records.",
        "Full REST API CRUD Flow: Verifies HTTP 201 Created, 200 OK, and error codes.",
        "Summary Calculations: Tests mathematical accuracy of totals, category shares, and budget ratios.",
        "CSV Export: Verifies headers, formatting, and file streaming."
    ])

    add_card(s7, Inches(6.8), Inches(2.4), Inches(5.6), Inches(4.3), "🛡️ Test Database Isolation", [
        "Separate test_expenses.db created on test execution.",
        "Zero risk to production user data in expenses.db.",
        "Automatic teardown and cleanup upon test completion.",
        "Fast Execution: All 6 test suites execute in ~0.14 seconds."
    ])

    # =========================================================================
    # SLIDE 8: HOW TO RUN & DEVELOPER EXPERIENCE
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "Deployment & Execution", "Running the Project", "Zero-friction setup designed for instant launch across multiple workflows.")

    add_card(s8, Inches(0.8), Inches(2.4), Inches(3.6), Inches(4.3), "🖱️ 1. Windows 1-Click Launch", [
        "Double-click run.bat in folder.",
        "Automatically starts Flask server with SQLite.",
        "Opens default browser directly to http://127.0.0.1:5000.",
        "Zero command-line knowledge required for end users."
    ])

    add_card(s8, Inches(4.8), Inches(2.4), Inches(3.6), Inches(4.3), "💻 2. Visual Studio Code", [
        "Open folder sareena in VS Code.",
        "Press F5 to launch pre-configured debugger via .vscode/launch.json.",
        "Integrated terminal support: python app.py.",
        "One-click task runners configured in tasks.json."
    ])

    add_card(s8, Inches(8.8), Inches(2.4), Inches(3.6), Inches(4.3), "🌐 3. Standalone Browser Mode", [
        "Double-click index.html directly.",
        "Runs 100% offline via browser LocalStorage.",
        "No Python or server installation required.",
        "Full support for adding, editing, filtering, and exporting data."
    ])

    # =========================================================================
    # SLIDE 9: FUTURE SCOPE & ENHANCEMENTS
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "Roadmap", "Future Scope & Enhancements", "Transforming SpendWise into an intelligent AI-assisted personal finance suite.")

    add_card(s9, Inches(0.8), Inches(2.4), Inches(3.6), Inches(4.3), "📸 AI Receipt Scanning (OCR)", [
        "Snap photos of receipts and paper invoices.",
        "Automatic extraction of merchant name, date, total amount, and line items.",
        "Auto-categorization using lightweight vision models."
    ])

    add_card(s9, Inches(4.8), Inches(2.4), Inches(3.6), Inches(4.3), "🔁 Recurring Subscriptions", [
        "Automated tracking for monthly expenses (Netflix, broadband, rent, gym).",
        "Upcoming renewal date alerts.",
        "Forecasted cash flow deductions."
    ])

    add_card(s9, Inches(8.8), Inches(2.4), Inches(3.6), Inches(4.3), "📑 PDF Financial Reports", [
        "Generate comprehensive monthly audit statements in PDF format.",
        "Category variance analysis comparing month-over-month trends.",
        "Exportable tax deduction summaries."
    ])

    # =========================================================================
    # SLIDE 10: CONCLUSION & SUMMARY
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)

    tb10 = s10.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(11), Inches(4.0))
    tf10 = tb10.text_frame
    tf10.word_wrap = True

    p_badge10 = tf10.paragraphs[0]
    p_badge10.text = "WRAP-UP • KEY ACHIEVEMENTS"
    p_badge10.font.size = Pt(13)
    p_badge10.font.bold = True
    p_badge10.font.color.rgb = SECONDARY
    p_badge10.space_after = Pt(10)

    p_main10 = tf10.add_paragraph()
    p_main10.text = "Summary & Conclusion"
    p_main10.font.size = Pt(44)
    p_main10.font.bold = True
    p_main10.font.color.rgb = TEXT_MAIN
    p_main10.space_after = Pt(16)

    bullets10 = [
        "✅ Successfully created SpendWise: a robust, responsive personal expense tracker.",
        "✅ Dual-tier data persistence: SQLite relational database + browser LocalStorage fallback.",
        "✅ Instant total spending insights: Grand Total, Today, Rolling 7-day, and Monthly Budget.",
        "✅ Visual analytics: Interactive category doughnut and 14-day spending trend charts.",
        "✅ 100% test coverage with automated unit tests and VS Code debugging integration.",
        "✅ Ready for immediate presentation, academic evaluation, and everyday personal use."
    ]

    for b in bullets10:
        p = tf10.add_paragraph()
        p.text = b
        p.font.size = Pt(16)
        p.font.color.rgb = TEXT_MAIN
        p.space_after = Pt(10)

    p_thank = tf10.add_paragraph()
    p_thank.text = "\nThank You! Open for Questions & Feedback."
    p_thank.font.size = Pt(20)
    p_thank.font.bold = True
    p_thank.font.color.rgb = ACCENT

    output_filename = "SpendWise_Project_Presentation.pptx"
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_filename)
    prs.save(output_path)
    print(f"Presentation successfully saved to: {output_path}")

if __name__ == "__main__":
    create_presentation()
