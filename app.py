import csv
import io
import os
from flask import Flask, jsonify, request, render_template, send_from_directory, Response
import database as db

app = Flask(__name__, static_folder="static", template_folder="templates")

# Initialize DB on launch
db.init_db()

# If expenses table is completely empty, seed sample data so the app looks great immediately
with db.get_db() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM expenses")
    count = cursor.fetchone()["count"]
    if count == 0:
        db.seed_sample_data()

@app.route("/")
def index():
    """Serves the main application dashboard."""
    return render_template("index.html")

@app.route("/api/expenses", methods=["GET"])
def get_expenses_route():
    """Get expenses with optional filtering and sorting."""
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    category = request.args.get("category")
    search = request.args.get("search")
    sort_by = request.args.get("sort_by", "date_desc")

    expenses = db.get_expenses(start_date, end_date, category, search, sort_by)
    return jsonify({"status": "success", "data": expenses, "count": len(expenses)})

@app.route("/api/expenses/<int:expense_id>", methods=["GET"])
def get_single_expense_route(expense_id):
    """Retrieve an expense by ID."""
    expense = db.get_expense_by_id(expense_id)
    if not expense:
        return jsonify({"status": "error", "message": "Expense not found"}), 404
    return jsonify({"status": "success", "data": expense})

@app.route("/api/expenses", methods=["POST"])
def add_expense_route():
    """Create a new expense entry."""
    data = request.get_json(silent=True) or request.form.to_dict()
    if not data:
        return jsonify({"status": "error", "message": "Invalid or missing payload"}), 400

    title = data.get("title", "")
    amount = data.get("amount")
    category = data.get("category", "Others")
    expense_date = data.get("expense_date", "")
    payment_method = data.get("payment_method", "Cash")
    notes = data.get("notes", "")

    if not title:
        return jsonify({"status": "error", "message": "Title is required"}), 400

    if amount is None or str(amount).strip() == "":
        return jsonify({"status": "error", "message": "Amount is required"}), 400

    try:
        new_expense = db.add_expense(title, amount, category, expense_date, payment_method, notes)
        return jsonify({"status": "success", "message": "Expense recorded successfully", "data": new_expense}), 201
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500

@app.route("/api/expenses/<int:expense_id>", methods=["PUT"])
def update_expense_route(expense_id):
    """Update an existing expense entry."""
    data = request.get_json(silent=True) or request.form.to_dict()
    if not data:
        return jsonify({"status": "error", "message": "Invalid or missing payload"}), 400

    title = data.get("title", "")
    amount = data.get("amount")
    category = data.get("category", "Others")
    expense_date = data.get("expense_date", "")
    payment_method = data.get("payment_method", "Cash")
    notes = data.get("notes", "")

    try:
        updated = db.update_expense(expense_id, title, amount, category, expense_date, payment_method, notes)
        if not updated:
            return jsonify({"status": "error", "message": "Expense not found"}), 404
        return jsonify({"status": "success", "message": "Expense updated successfully", "data": updated})
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500

@app.route("/api/expenses/<int:expense_id>", methods=["DELETE"])
def delete_expense_route(expense_id):
    """Delete an expense entry."""
    success = db.delete_expense(expense_id)
    if not success:
        return jsonify({"status": "error", "message": "Expense not found"}), 404
    return jsonify({"status": "success", "message": "Expense deleted successfully"})

@app.route("/api/summary", methods=["GET"])
def get_summary_route():
    """Get high-level spending summaries and metrics."""
    target_date = request.args.get("date")
    summary = db.get_summary(target_date)
    settings = db.get_all_settings()
    summary["currency_symbol"] = settings.get("currency_symbol", "₹")
    summary["currency_code"] = settings.get("currency_code", "INR")
    return jsonify({"status": "success", "data": summary})

@app.route("/api/settings", methods=["GET"])
def get_settings_route():
    """Get all settings."""
    settings = db.get_all_settings()
    return jsonify({"status": "success", "data": settings})

@app.route("/api/settings", methods=["POST"])
def update_settings_route():
    """Update user settings (budget, currency, etc.)."""
    data = request.get_json(silent=True) or request.form.to_dict()
    if not data:
        return jsonify({"status": "error", "message": "Invalid payload"}), 400

    for key, val in data.items():
        if key in ["monthly_budget", "currency_symbol", "currency_code"]:
            db.update_setting(key, val)

    return jsonify({"status": "success", "message": "Settings updated", "data": db.get_all_settings()})

@app.route("/api/export/csv", methods=["GET"])
def export_csv_route():
    """Export all expenses as a downloadable CSV."""
    expenses = db.get_expenses(sort_by="date_desc")
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Date", "Title", "Amount", "Category", "Payment Method", "Notes", "Created At"])

    for exp in expenses:
        writer.writerow([
            exp["id"],
            exp["expense_date"],
            exp["title"],
            exp["amount"],
            exp["category"],
            exp["payment_method"],
            exp["notes"],
            exp.get("created_at", "")
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=expenses_export.csv"}
    )

@app.route("/api/import", methods=["POST"])
def import_expenses_route():
    """Import expenses from a JSON array."""
    data = request.get_json(silent=True)
    if not data or not isinstance(data, list):
        return jsonify({"status": "error", "message": "Expected a JSON list of expenses"}), 400

    imported_count = 0
    for item in data:
        try:
            db.add_expense(
                title=item.get("title", "Imported Expense"),
                amount=item.get("amount", 0),
                category=item.get("category", "Others"),
                expense_date=item.get("expense_date", ""),
                payment_method=item.get("payment_method", "Cash"),
                notes=item.get("notes", "")
            )
            imported_count += 1
        except Exception:
            continue

    return jsonify({"status": "success", "message": f"Successfully imported {imported_count} expenses"})

@app.route("/api/seed", methods=["POST"])
def seed_route():
    """Seed sample data."""
    db.seed_sample_data()
    return jsonify({"status": "success", "message": "Sample data seeded successfully"})

@app.route("/api/clear", methods=["POST"])
def clear_route():
    """Clear all expenses."""
    db.clear_all_expenses()
    return jsonify({"status": "success", "message": "All expenses cleared"})

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  🚀 Personal Expense Tracker Server Running!")
    print("  🌐 Open in browser: http://127.0.0.1:5000")
    print("="*60 + "\n")
    app.run(host="127.0.0.1", port=5000, debug=True)
