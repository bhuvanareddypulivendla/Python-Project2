import sqlite3

def connect_db():
    conn = sqlite3.connect("expense.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            category TEXT,
            note TEXT,
            date TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_expense(amount, category, note, date):
    conn = sqlite3.connect("expenses.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO expenses (amount, category, note, date) VALUES (?, ?, ?, ?)",
                (amount, category, note, date))
    conn.commit()
    conn.close()

def fetch_expenses():
    conn = sqlite3.connect("expenses.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM expenses ORDER BY date DESC")
    rows = cur.fetchall()
    conn.close()
    return rows