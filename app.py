from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


def get_db():
    conn = sqlite3.connect("expenses.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        date TEXT NOT NULL,
        note TEXT)""")
    conn.commit()
    conn.close()


@app.route("/")
def home():
    conn = get_db()
    expenses = conn.execute("SELECT * FROM expenses ORDER BY date DESC").fetchall()
    total = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM expenses "
        "WHERE strftime('%Y-%m', date) = strftime('%Y-%m', 'now')"
    ).fetchone()[0]
    categories = conn.execute(
        "SELECT category, SUM(amount) AS total FROM expenses "
        "WHERE strftime('%Y-%m', date) = strftime('%Y-%m', 'now') "
        "GROUP BY category"
    ).fetchall()
    conn.close()
    return render_template("index.html", expenses=expenses, total=total, categories=categories)


@app.route("/add", methods=["POST"])
def add():
    amount = request.form["amount"]
    category = request.form["category"]
    date = request.form["date"]
    note = request.form["note"]
    conn = get_db()
    conn.execute(
        "INSERT INTO expenses (amount, category, date, note) VALUES (?, ?, ?, ?)",
        (amount, category, date, note),
    )
    conn.commit()
    conn.close()
    return redirect("/")


@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    conn = get_db()
    conn.execute("DELETE FROM expenses WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db()
    if request.method == "POST":
        conn.execute(
            "UPDATE expenses SET amount=?, category=?, date=?, note=? WHERE id=?",
            (request.form["amount"], request.form["category"],
             request.form["date"], request.form["note"], id),
        )
        conn.commit()
        conn.close()
        return redirect("/")
    expense = conn.execute("SELECT * FROM expenses WHERE id = ?", (id,)).fetchone()
    conn.close()
    return render_template("edit.html", e=expense)


init_db()

if __name__ == "__main__":
    app.run(debug=True)