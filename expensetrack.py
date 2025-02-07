import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

dark_mode = False
logged_in = False

def toggle_theme():
    global dark_mode
    dark_mode = not dark_mode
    bg_color = "#1e1e1e" if dark_mode else "#ffffff"
    fg_color = "#ffffff" if dark_mode else "#000000"
    root.configure(bg=bg_color)
    for widget in root.winfo_children():
        try:
            if isinstance(widget, (tk.Label, tk.Button)):
                widget.configure(bg=bg_color, fg=fg_color)
        except tk.TclError:
            pass

def create_tables():
    conn = sqlite3.connect("expenses.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            category TEXT,
            description TEXT,
            amount REAL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_expense():
    if not logged_in:
        messagebox.showerror("Error", "Please log in first!")
        return
    conn = sqlite3.connect("expenses.db")
    c = conn.cursor()
    c.execute("INSERT INTO expenses (date, category, description, amount) VALUES (?, ?, ?, ?)",
              (date_entry.get(), category_entry.get(), desc_entry.get(), amount_entry.get()))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Expense added successfully!")
    
    # Clear input fields after adding an expense
    date_entry.set_date(date_entry.get_date())  # Reset to the current date
    category_entry.set('')
    desc_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)

def show_expenses():
    if not logged_in:
        messagebox.showerror("Error", "Please log in first!")
        return
    expense_window = tk.Toplevel(root)
    expense_window.title("Expenses")
    expense_window.geometry("700x400")
    
    tree = ttk.Treeview(expense_window, columns=("Date", "Category", "Description", "Amount"), show="headings")
    tree.heading("Date", text="Date")
    tree.heading("Category", text="Category")
    tree.heading("Description", text="Description")
    tree.heading("Amount", text="Amount")
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    conn = sqlite3.connect("expenses.db")
    c = conn.cursor()
    c.execute("SELECT date, category, description, amount FROM expenses")
    rows = c.fetchall()
    for row in rows:
        tree.insert("", tk.END, values=row)
    conn.close()

def plot_expenses():
    if not logged_in:
        messagebox.showerror("Error", "Please log in first!")
        return
    plot_window = tk.Toplevel(root)
    plot_window.title("Expense Analysis")
    plot_window.geometry("600x400")
    
    conn = sqlite3.connect("expenses.db")
    c = conn.cursor()
    c.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    data = c.fetchall()
    conn.close()
    
    categories = [row[0] for row in data]
    amounts = [row[1] for row in data]
    
    fig, ax = plt.subplots()
    ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
    ax.set_title("Expense Distribution")
    
    canvas = FigureCanvasTkAgg(fig, master=plot_window)
    canvas.draw()
    canvas.get_tk_widget().pack()

def register():
    username = username_entry.get()
    password = password_entry.get()
    conn = sqlite3.connect("expenses.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        messagebox.showinfo("Success", "User registered successfully!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Username already exists!")
    conn.close()

def login():
    global logged_in
    username = username_entry.get()
    password = password_entry.get()
    conn = sqlite3.connect("expenses.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    conn.close()
    if user:
        logged_in = True
        messagebox.showinfo("Success", "Login successful!")
        login_window.destroy()
        open_main_window()
    else:
        messagebox.showerror("Error", "Invalid username or password!")

def open_login_window():
    global login_window, username_entry, password_entry
    login_window = tk.Tk()
    login_window.title("Login")
    login_window.geometry("300x200")
    login_window.configure(bg="#3c3f41")
    
    tk.Label(login_window, text="Username", bg="#3c3f41", fg="white").pack(pady=5)
    username_entry = tk.Entry(login_window)
    username_entry.pack()
    
    tk.Label(login_window, text="Password", bg="#3c3f41", fg="white").pack(pady=5)
    password_entry = tk.Entry(login_window, show="*")
    password_entry.pack()
    
    tk.Button(login_window, text="Register", command=register, bg="#4CAF50", fg="white").pack(pady=5)
    tk.Button(login_window, text="Login", command=login, bg="#008CBA", fg="white").pack(pady=5)
    
    login_window.mainloop()

def open_main_window():
    global root, date_entry, category_entry, desc_entry, amount_entry
    root = tk.Tk()
    root.title("Expense Tracker")
    root.geometry("900x600")
    root.configure(bg="#282c34")
    
    tk.Label(root, text="Date:", fg="white", bg="#282c34").pack()
    date_entry = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2)
    date_entry.pack()
    
    tk.Label(root, text="Category:", fg="white", bg="#282c34").pack()
    category_entry = ttk.Combobox(root, values=["Food", "Transport", "Shopping", "Medicine", "Other"])
    category_entry.pack()
    
    tk.Label(root, text="Description:", fg="white", bg="#282c34").pack()
    desc_entry = tk.Entry(root)
    desc_entry.pack()
    
    tk.Label(root, text="Amount:", fg="white", bg="#282c34").pack()
    amount_entry = tk.Entry(root)
    amount_entry.pack()

    
    tk.Button(root, text="Add Expense", command=add_expense).pack(pady=5)
    tk.Button(root, text="Show Expenses", command=show_expenses).pack(pady=5)
    tk.Button(root, text="Plot Expenses", command=plot_expenses).pack(pady=5)
    tk.Button(root, text="Toggle Theme", command=toggle_theme).pack(pady=5)
    
    root.mainloop()

create_tables()
open_login_window()

