import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime
import matplotlib.pyplot as plt  # New import for charts

# === Category-wise monthly budget limits ===
category_limits = {
    "Food": 15000,
    "Travel": 10000,
    "Bills": 5000,
    "Shopping": 8000,
    "Health": 7000,
    "Other": 5000
}

# === Database Setup ===
def connect_db():
    conn = sqlite3.connect("expenses.db")
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

def delete_expense_by_id(expense_id):
    conn = sqlite3.connect("expenses.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
    conn.commit()
    conn.close()

# === Functions for GUI ===
def add_expense():
    amount = amount_entry.get()
    category = category_var.get()
    note = note_entry.get()
    date = date_entry.get()

    if not amount or not category:
        messagebox.showerror("Error", "Amount and Category are required!")
        return

    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Amount must be a positive number!")
        return

    insert_expense(amount, category, note, date)

    amount_entry.delete(0, tk.END)
    note_entry.delete(0, tk.END)
    refresh_table()

def delete_selected_expense():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "No item selected to delete.")
        return

    item = tree.item(selected)
    expense_id = item['values'][0]
    delete_expense_by_id(expense_id)
    refresh_table()

def refresh_table():
    for row in tree.get_children():
        tree.delete(row)

    rows = fetch_expenses()
    for row in rows:
        tree.insert("", tk.END, values=row)

    update_category_totals()

def update_category_totals():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    today_month = datetime.date.today().strftime('%Y-%m')
    warnings = []

    for category, limit in category_limits.items():
        cursor.execute("SELECT SUM(amount) FROM expenses WHERE category=? AND date LIKE ?", (category, f"{today_month}%",))
        total = cursor.fetchone()[0]
        if total is None:
            total = 0.0

        if total > limit:
            warnings.append(f"{category}: ₹{total:.2f} (Limit: ₹{limit})")

    conn.close()

    if warnings:
        messagebox.showwarning("Budget Limit Exceeded", "\n".join(warnings))

def show_expense_chart():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    today_month = datetime.date.today().strftime('%Y-%m')

    categories = []
    amounts = []

    for category in category_limits:
        cursor.execute("SELECT SUM(amount) FROM expenses WHERE category=? AND date LIKE ?", (category, f"{today_month}%",))
        total = cursor.fetchone()[0]
        if total and total > 0:
            categories.append(category)
            amounts.append(total)

    conn.close()

    if not categories:
        messagebox.showinfo("No Data", "No expenses found for this month.")
        return

    # Pie chart
    plt.figure(figsize=(6, 6))
    plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=140)
    plt.title(f'Category-wise Expenses for {today_month}')
    plt.axis('equal')  # Equal aspect ratio ensures the pie is circular.
    plt.show()

# === GUI Setup ===
connect_db()
root = tk.Tk()
root.title("💰 Smart Expense Manager with Category Limits")
root.geometry("750x450")

tk.Label(root, text="Amount:").grid(row=0, column=0, padx=5, pady=5)
amount_entry = tk.Entry(root)
amount_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="Category:").grid(row=0, column=2, padx=5, pady=5)
category_var = tk.StringVar()
category_menu = ttk.Combobox(root, textvariable=category_var)
category_menu['values'] = tuple(category_limits.keys())
category_menu.grid(row=0, column=3, padx=5, pady=5)

tk.Label(root, text="Note:").grid(row=1, column=0, padx=5, pady=5)
note_entry = tk.Entry(root)
note_entry.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5, pady=5)

tk.Label(root, text="Date:").grid(row=1, column=2, padx=5, pady=5)
date_entry = tk.Entry(root)
date_entry.grid(row=1, column=3, padx=5, pady=5)
date_entry.insert(0, datetime.date.today().strftime('%Y-%m-%d'))

add_btn = tk.Button(root, text="➕ Add Expense", command=add_expense)
add_btn.grid(row=2, column=1, columnspan=2, pady=10)

columns = ("ID", "Amount", "Category", "Note", "Date")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100)
tree.grid(row=3, column=0, columnspan=4, padx=10, pady=10)

delete_btn = tk.Button(root, text="🗑️ Delete Selected", command=delete_selected_expense)
delete_btn.grid(row=4, column=1, columnspan=2, pady=5)

chart_btn = tk.Button(root, text="📊 Show Charts", command=show_expense_chart)
chart_btn.grid(row=5, column=1, columnspan=2, pady=10)

refresh_table()
root.mainloop()
