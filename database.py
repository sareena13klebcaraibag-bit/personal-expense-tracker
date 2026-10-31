import sqlite3
import os
from datetime import datetime, date, timedelta

from contextlib import contextmanager

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "expenses.db")

@contextmanager
def get_db():
    """Context manager for SQLite database connection."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initializes tables and default settings."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount > 0),
                category TEXT NOT NULL,
                expense_date TEXT NOT NULL,
                payment_method TEXT DEFAULT 'Cash',
                notes TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_expense_date ON expenses(expense_date)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_expense_category ON expenses(category)
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        # Default settings if not already present
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('currency_symbol', '₹')")
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('currency_code', 'INR')")
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('monthly_budget', '30000')")
        conn.commit()

def add_expense(title, amount, category, expense_date, payment_method="Cash", notes=""):
    """Adds a new expense record."""
    try:
        amount = round(float(amount), 2)
    except (ValueError, TypeError):
        raise ValueError("Invalid amount")

    if amount <= 0:
        raise ValueError("Amount must be greater than zero")

    title = title.strip()
    if not title:
        raise ValueError("Title cannot be empty")

    category = category.strip() or "Others"
    expense_date = expense_date.strip() or date.today().isoformat()
    payment_method = payment_method.strip() or "Cash"
    notes = (notes or "").strip()

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO expenses (title, amount, category, expense_date, payment_method, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, amount, category, expense_date, payment_method, notes))
        conn.commit()
        expense_id = cursor.lastrowid
        return get_expense_by_id(expense_id)

def update_expense(expense_id, title, amount, category, expense_date, payment_method="Cash", notes=""):
    """Updates an existing expense record."""
    try:
        amount = round(float(amount), 2)
    except (ValueError, TypeError):
        raise ValueError("Invalid amount")

    if amount <= 0:
        raise ValueError("Amount must be greater than zero")

    title = title.strip()
    if not title:
        raise ValueError("Title cannot be empty")

    category = category.strip() or "Others"
    expense_date = expense_date.strip() or date.today().isoformat()
    payment_method = payment_method.strip() or "Cash"
    notes = (notes or "").strip()

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE expenses
            SET title = ?, amount = ?, category = ?, expense_date = ?, payment_method = ?, notes = ?
            WHERE id = ?
        """, (title, amount, category, expense_date, payment_method, notes, expense_id))
        conn.commit()
        if cursor.rowcount == 0:
            return None
        return get_expense_by_id(expense_id)

def delete_expense(expense_id):
    """Deletes an expense by ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()
        return cursor.rowcount > 0

def get_expense_by_id(expense_id):
    """Retrieves a single expense by ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

def get_expenses(start_date=None, end_date=None, category=None, search=None, sort_by="date_desc"):
    """Retrieves expenses with optional filters and sorting."""
    query = "SELECT * FROM expenses WHERE 1=1"
    params = []

    if start_date:
        query += " AND expense_date >= ?"
        params.append(start_date)

    if end_date:
        query += " AND expense_date <= ?"
        params.append(end_date)

    if category and category.lower() != "all":
        query += " AND category = ?"
        params.append(category)

    if search:
        query += " AND (title LIKE ? OR notes LIKE ?)"
        search_param = f"%{search.strip()}%"
        params.extend([search_param, search_param])

    # Sorting
    sort_options = {
        "date_desc": "ORDER BY expense_date DESC, id DESC",
        "date_asc": "ORDER BY expense_date ASC, id ASC",
        "amount_desc": "ORDER BY amount DESC, expense_date DESC",
        "amount_asc": "ORDER BY amount ASC, expense_date DESC",
        "title_asc": "ORDER BY title ASC",
    }
    query += " " + sort_options.get(sort_by, sort_options["date_desc"])

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_summary(target_date_str=None):
    """Calculates comprehensive spending statistics and breakdown."""
    if target_date_str:
        try:
            ref_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
        except ValueError:
            ref_date = date.today()
    else:
        ref_date = date.today()

    today_str = ref_date.isoformat()
    # First day of current month and last day
    first_day_of_month = ref_date.replace(day=1).isoformat()
    
    # Calculate 7 days ago
    seven_days_ago = (ref_date - timedelta(days=6)).isoformat()
    # Calculate 30 days ago
    thirty_days_ago = (ref_date - timedelta(days=29)).isoformat()

    settings = get_all_settings()
    monthly_budget = float(settings.get("monthly_budget", 30000))

    with get_db() as conn:
        cursor = conn.cursor()

        # Grand total
        cursor.execute("SELECT COALESCE(SUM(amount), 0) AS total, COUNT(*) AS count FROM expenses")
        row = cursor.fetchone()
        grand_total = round(row["total"], 2)
        total_count = row["count"]

        # Today's total
        cursor.execute("SELECT COALESCE(SUM(amount), 0) AS total, COUNT(*) AS count FROM expenses WHERE expense_date = ?", (today_str,))
        row = cursor.fetchone()
        today_total = round(row["total"], 2)
        today_count = row["count"]

        # Last 7 days total (this week)
        cursor.execute("SELECT COALESCE(SUM(amount), 0) AS total, COUNT(*) AS count FROM expenses WHERE expense_date >= ? AND expense_date <= ?", (seven_days_ago, today_str))
        row = cursor.fetchone()
        week_total = round(row["total"], 2)

        # Current Month total
        # Month string prefix e.g. '2026-10'
        month_prefix = ref_date.strftime("%Y-%m")
        cursor.execute("SELECT COALESCE(SUM(amount), 0) AS total, COUNT(*) AS count FROM expenses WHERE expense_date LIKE ?", (f"{month_prefix}%",))
        row = cursor.fetchone()
        month_total = round(row["total"], 2)
        month_count = row["count"]

        # Average daily spending in the current month
        day_of_month = ref_date.day
        avg_daily_month = round(month_total / day_of_month, 2) if day_of_month > 0 else 0

        # Highest expense all-time
        cursor.execute("SELECT * FROM expenses ORDER BY amount DESC LIMIT 1")
        highest_row = cursor.fetchone()
        highest_expense = dict(highest_row) if highest_row else None

        # Category breakdown for current month (or all time if month has none)
        cursor.execute("""
            SELECT category, COALESCE(SUM(amount), 0) AS total, COUNT(*) AS count
            FROM expenses
            WHERE expense_date LIKE ?
            GROUP BY category
            ORDER BY total DESC
        """, (f"{month_prefix}%",))
        category_rows = cursor.fetchall()

        # If current month has no expenses, get all-time category breakdown
        if not category_rows:
            cursor.execute("""
                SELECT category, COALESCE(SUM(amount), 0) AS total, COUNT(*) AS count
                FROM expenses
                GROUP BY category
                ORDER BY total DESC
            """)
            category_rows = cursor.fetchall()

        calc_total = month_total if month_total > 0 else grand_total
        category_breakdown = []
        for cat in category_rows:
            cat_total = round(cat["total"], 2)
            pct = round((cat_total / calc_total * 100), 1) if calc_total > 0 else 0
            category_breakdown.append({
                "category": cat["category"],
                "total": cat_total,
                "count": cat["count"],
                "percentage": pct
            })

        # Daily spending trend for the last 14 days
        fourteen_days_ago = (ref_date - timedelta(days=13)).isoformat()
        cursor.execute("""
            SELECT expense_date, COALESCE(SUM(amount), 0) AS total, COUNT(*) AS count
            FROM expenses
            WHERE expense_date >= ? AND expense_date <= ?
            GROUP BY expense_date
            ORDER BY expense_date ASC
        """, (fourteen_days_ago, today_str))
        trend_map = {row["expense_date"]: round(row["total"], 2) for row in cursor.fetchall()}

        daily_trend = []
        for i in range(14):
            day_dt = ref_date - timedelta(days=13 - i)
            d_str = day_dt.isoformat()
            daily_trend.append({
                "date": d_str,
                "display_date": day_dt.strftime("%b %d"),
                "total": trend_map.get(d_str, 0.0)
            })

        # Payment methods breakdown
        cursor.execute("""
            SELECT payment_method, COALESCE(SUM(amount), 0) AS total, COUNT(*) AS count
            FROM expenses
            GROUP BY payment_method
            ORDER BY total DESC
        """)
        payment_methods = [
            {"method": row["payment_method"], "total": round(row["total"], 2), "count": row["count"]}
            for row in cursor.fetchall()
        ]

        # Budget calculation
        budget_pct = round((month_total / monthly_budget) * 100, 1) if monthly_budget > 0 else 0
        remaining_budget = round(monthly_budget - month_total, 2)

        return {
            "grand_total": grand_total,
            "total_transactions": total_count,
            "today_total": today_total,
            "today_count": today_count,
            "week_total": week_total,
            "month_total": month_total,
            "month_count": month_count,
            "avg_daily_month": avg_daily_month,
            "monthly_budget": monthly_budget,
            "budget_spent_percentage": budget_pct,
            "remaining_budget": remaining_budget,
            "is_budget_exceeded": month_total > monthly_budget,
            "highest_expense": highest_expense,
            "category_breakdown": category_breakdown,
            "daily_trend": daily_trend,
            "payment_methods": payment_methods,
            "current_date": today_str,
            "current_month_name": ref_date.strftime("%B %Y")
        }

def get_all_settings():
    """Gets all settings as a key-value dictionary."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM settings")
        return {row["key"]: row["value"] for row in cursor.fetchall()}

def update_setting(key, value):
    """Updates or sets a setting value."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO settings (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """, (key, str(value)))
        conn.commit()

def clear_all_expenses():
    """Deletes all expense records."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses")
        conn.commit()

def seed_sample_data():
    """Seeds realistic sample data for demonstration."""
    clear_all_expenses()
    today = date.today()

    sample_items = [
        # Today
        ("Morning Coffee & Croissant", 180, "Food & Dining", today.isoformat(), "UPI", "Local Cafe"),
        ("Grocery Essentials & Milk", 650, "Groceries", today.isoformat(), "Debit Card", "Supermarket run"),
        ("Metro Card Recharge", 300, "Transportation", today.isoformat(), "UPI", "Commute recharge"),
        
        # Yesterday
        ("Work Lunch at Bistro", 420, "Food & Dining", (today - timedelta(days=1)).isoformat(), "Credit Card", "Team lunch"),
        ("Pharmacy Medicines", 280, "Health & Medical", (today - timedelta(days=1)).isoformat(), "Cash", "Vitamins & band-aids"),
        ("Cab Ride to Client Meeting", 350, "Transportation", (today - timedelta(days=1)).isoformat(), "UPI", "Uber ride"),
        
        # 2 days ago
        ("Electricity & Power Bill", 1850, "Utilities & Bills", (today - timedelta(days=2)).isoformat(), "Net Banking", "Monthly power bill"),
        ("Movie Tickets & Popcorn", 750, "Entertainment", (today - timedelta(days=2)).isoformat(), "Credit Card", "Weekend cinema"),
        
        # 3 days ago
        ("Casual T-Shirts Shopping", 1499, "Shopping", (today - timedelta(days=3)).isoformat(), "Credit Card", "Autumn apparel"),
        ("Dinner with Friends", 1120, "Food & Dining", (today - timedelta(days=3)).isoformat(), "UPI", "Italian diner"),

        # 4 days ago
        ("Fuel / Petrol Refill", 1500, "Transportation", (today - timedelta(days=4)).isoformat(), "Credit Card", "Full tank refill"),
        ("Fruit Basket & Veggies", 340, "Groceries", (today - timedelta(days=4)).isoformat(), "Cash", "Organic market"),

        # 5 days ago
        ("High-Speed Fiber Internet", 999, "Utilities & Bills", (today - timedelta(days=5)).isoformat(), "Net Banking", "Monthly broadband"),
        ("Haircut & Grooming", 450, "Personal Care", (today - timedelta(days=5)).isoformat(), "UPI", "Salon haircut"),

        # 6 days ago
        ("Online Programming Course", 1299, "Education", (today - timedelta(days=6)).isoformat(), "Credit Card", "Udemy web dev course"),
        ("Takeout Pizza & Wings", 580, "Food & Dining", (today - timedelta(days=6)).isoformat(), "UPI", "Friday night treat"),

        # Earlier this month
        ("Gym Membership Monthly", 2000, "Health & Medical", (today - timedelta(days=8)).isoformat(), "Credit Card", "Fitness club"),
        ("Household Cleaning Supplies", 620, "Groceries", (today - timedelta(days=10)).isoformat(), "Debit Card", "Detergents and towels"),
        ("Mobile Phone Plan Recharge", 499, "Utilities & Bills", (today - timedelta(days=12)).isoformat(), "UPI", "Quarterly prepaid"),
        ("Books & Stationery", 780, "Education", (today - timedelta(days=14)).isoformat(), "Cash", "Novel and notebook"),
        ("Streaming Service Subscription", 499, "Entertainment", (today - timedelta(days=16)).isoformat(), "Credit Card", "Netflix renewal")
    ]

    with get_db() as conn:
        cursor = conn.cursor()
        for title, amount, category, exp_date, pay_method, notes in sample_items:
            cursor.execute("""
                INSERT INTO expenses (title, amount, category, expense_date, payment_method, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (title, amount, category, exp_date, pay_method, notes))
        conn.commit()
