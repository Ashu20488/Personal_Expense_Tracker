
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
from datetime import date, datetime
from collections import defaultdict
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# DATABASE
conn = sqlite3.connect("expenses.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trans_date TEXT NOT NULL,
    trans_type TEXT NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL,
    note TEXT
)
""")
conn.commit()

# COLORS
BG = "#F0F4F8"
NAVY = "#172957"
BLUE = "#2864E8"
GREEN = "#138044"
RED = "#E53935"
WHITE = "#FFFFFF"
TEXT = "#23324D"

# MAIN WINDOW
root = tk.Tk()
root.title("Personal Expense Tracker Pro")
root.geometry("1250x850")
root.minsize(1050, 700)
root.configure(bg=BG)

style = ttk.Style()
style.theme_use("clam")
style.configure(
    "Treeview",
    rowheight=26,
    font=("Arial", 10),
    background=WHITE,
    fieldbackground=WHITE
)
style.configure(
    "Treeview.Heading",
    font=("Arial", 10, "bold"),
    background="#DFE6F0",
    foreground=TEXT
)

# HEADER
header = tk.Frame(root, bg=NAVY, height=76)
header.pack(fill="x")
header.pack_propagate(False)

tk.Label(
    header,
    text="PERSONAL EXPENSE TRACKER",
    font=("Arial", 22, "bold"),
    bg=NAVY, fg=WHITE
).pack(pady=(9, 1))

tk.Label(
    header,
    text="Track your money smartly",
    font=("Arial", 10),
    bg=NAVY, fg="#D8E4FF"
).pack()

# SUMMARY CARDS
summary = tk.Frame(root, bg=BG)
summary.pack(fill="x", padx=12, pady=8)

def create_card(parent, title, color):
    card = tk.Frame(
        parent, bg=WHITE,
        highlightbackground="#D1DCE8",
        highlightthickness=1
    )
    tk.Label(
        card, text=title, font=("Arial", 10),
        fg="#63738A", bg=WHITE
    ).pack(pady=(8, 2))

    value = tk.Label(
        card, text="₹0.00",
        font=("Arial", 19, "bold"),
        fg=color, bg=WHITE
    )
    value.pack(pady=(0, 8))
    return card, value

card1, income_label = create_card(summary, "TOTAL INCOME", GREEN)
card2, expense_label = create_card(summary, "TOTAL EXPENSES", RED)
card3, balance_label = create_card(summary, "BALANCE", BLUE)

for card in (card1, card2, card3):
    card.pack(side="left", fill="x", expand=True, padx=4)

# SEARCH AND MONTH FILTER
filter_frame = tk.Frame(root, bg=BG)
filter_frame.pack(fill="x", padx=17, pady=(0, 7))

tk.Label(
    filter_frame, text="Search:",
    font=("Arial", 10, "bold"), bg=BG, fg=TEXT
).pack(side="left")

search_var = tk.StringVar()
ttk.Entry(
    filter_frame, textvariable=search_var, width=22
).pack(side="left", padx=(6, 18))

tk.Label(
    filter_frame, text="Month:",
    font=("Arial", 10, "bold"), bg=BG, fg=TEXT
).pack(side="left")

month_var = tk.StringVar(value="All")
month_box = ttk.Combobox(
    filter_frame,
    textvariable=month_var,
    values=[
        "All", "01", "02", "03", "04", "05", "06",
        "07", "08", "09", "10", "11", "12"
    ],
    width=9,
    state="readonly"
)
month_box.pack(side="left", padx=6)

# MAIN CONTENT
content = tk.Frame(root, bg=BG)
content.pack(fill="both", expand=True, padx=12, pady=(0, 8))

# LEFT FORM
form = tk.Frame(
    content, bg=WHITE,
    highlightbackground="#D1DCE8",
    highlightthickness=1,
    width=220
)
form.pack(side="left", fill="y", padx=(0, 8))
form.pack_propagate(False)

tk.Label(
    form, text="Add Transaction",
    font=("Arial", 16, "bold"),
    bg=WHITE, fg=NAVY
).pack(pady=(10, 8))

def field_label(text):
    tk.Label(
        form, text=text,
        font=("Arial", 10, "bold"),
        bg=WHITE, fg=TEXT
    ).pack(anchor="w", padx=12, pady=(5, 2))

field_label("Type")
type_var = tk.StringVar(value="Expense")
type_box = ttk.Combobox(
    form, textvariable=type_var,
    values=["Expense", "Income"],
    state="readonly"
)
type_box.pack(fill="x", padx=12)

field_label("Category")
category_var = tk.StringVar(value="Food")
category_box = ttk.Combobox(
    form, textvariable=category_var,
    values=[
        "Food", "Travel", "Shopping", "Bills",
        "Education", "Health", "Entertainment",
        "Salary", "Business", "Gift", "Other"
    ]
)
category_box.pack(fill="x", padx=12)

field_label("Amount (₹)")
amount_entry = ttk.Entry(form)
amount_entry.pack(fill="x", padx=12)

field_label("Note")
note_entry = ttk.Entry(form)
note_entry.pack(fill="x", padx=12)

field_label("Date (YYYY-MM-DD)")
date_entry = ttk.Entry(form)
date_entry.insert(0, date.today().isoformat())
date_entry.pack(fill="x", padx=12)

# BUTTON HELPER
def make_button(parent, text, color, command, fg=WHITE):
    return tk.Button(
        parent, text=text, command=command,
        bg=color, fg=fg,
        activebackground=color, activeforeground=fg,
        relief="flat", cursor="hand2",
        font=("Arial", 10, "bold"),
        pady=7
    )

# RIGHT TRANSACTION HISTORY
right = tk.Frame(content, bg=WHITE)
right.pack(side="left", fill="both", expand=True)

tk.Label(
    right, text="Transaction History",
    font=("Arial", 16, "bold"),
    bg=WHITE, fg=NAVY
).pack(anchor="w", padx=10, pady=(10, 7))

table_frame = tk.Frame(right, bg=WHITE)
table_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

columns = ("ID", "Date", "Type", "Category", "Amount", "Note")
table = ttk.Treeview(
    table_frame, columns=columns,
    show="headings", selectmode="extended"
)

for col in columns:
    table.heading(col, text=col)
    table.column(col, anchor="center", width=100)

table.column("ID", width=45)
table.column("Note", width=135)

yscroll = ttk.Scrollbar(
    table_frame, orient="vertical", command=table.yview
)
xscroll = ttk.Scrollbar(
    table_frame, orient="horizontal", command=table.xview
)
table.configure(
    yscrollcommand=yscroll.set,
    xscrollcommand=xscroll.set
)
table.grid(row=0, column=0, sticky="nsew")
yscroll.grid(row=0, column=1, sticky="ns")
xscroll.grid(row=1, column=0, sticky="ew")
table_frame.rowconfigure(0, weight=1)
table_frame.columnconfigure(0, weight=1)

# CHART - FIXED SIZE AND BIGGER PERCENTAGES
chart_frame = tk.Frame(
    root, bg=WHITE,
    highlightbackground="#D1DCE8",
    highlightthickness=1,
    height=230
)
chart_frame.pack(fill="x", padx=12, pady=(0, 10))
chart_frame.pack_propagate(False)

fig = Figure(figsize=(9, 2.3), dpi=100, facecolor=WHITE)
ax = fig.add_subplot(111)

canvas = FigureCanvasTkAgg(fig, master=chart_frame)
canvas.get_tk_widget().pack(fill="both", expand=True)

# REFRESH
def refresh():
    for item in table.get_children():
        table.delete(item)

    rows = cur.execute("""
        SELECT id, trans_date, trans_type, category, amount, note
        FROM transactions
        ORDER BY trans_date DESC, id DESC
    """).fetchall()

    income = 0.0
    expenses = 0.0
    categories = defaultdict(float)

    search_text = search_var.get().strip().lower()
    selected_month = month_var.get()

    for row in rows:
        tid, trans_date, trans_type, category, amount, note = row

        if trans_type == "Income":
            income += amount
        else:
            expenses += amount
            categories[category] += amount

        if selected_month != "All":
            if trans_date[5:7] != selected_month:
                continue

        searchable = " ".join([
            str(tid), trans_date, trans_type,
            category, str(amount), note or ""
        ]).lower()

        if search_text and search_text not in searchable:
            continue

        table.insert(
            "", "end",
            values=(
                tid, trans_date, trans_type,
                category, f"₹{amount:,.2f}", note or ""
            )
        )

    income_label.config(text=f"₹{income:,.2f}")
    expense_label.config(text=f"₹{expenses:,.2f}")
    balance_label.config(text=f"₹{income - expenses:,.2f}")

    # DRAW CHART
    ax.clear()

    if categories:
        labels = list(categories.keys())
        values = list(categories.values())

        wedges, _, autotexts = ax.pie(
            values,
            labels=None,
            autopct=lambda p: f"{p:.1f}%" if p >= 3 else "",
            startangle=90,
            pctdistance=0.58,
            radius=0.82,
            textprops={"fontsize": 11, "fontweight": "bold"},
            wedgeprops={"linewidth": 1.2, "edgecolor": "white"}
        )

        for txt in autotexts:
            txt.set_fontsize(11)
            txt.set_color("white")
            txt.set_fontweight("bold")

        ax.legend(
            wedges,
            [
                f"{label} - ₹{value:,.0f}"
                for label, value in zip(labels, values)
            ],
            title="Expense Categories",
            loc="center left",
            bbox_to_anchor=(1.00, 0.5),
            fontsize=9,
            title_fontsize=10,
            frameon=False
        )

        ax.set_title(
            "Expenses by Category",
            fontsize=12,
            fontweight="bold",
            pad=5
        )
        ax.axis("equal")
        fig.subplots_adjust(
            left=0.03, right=0.70,
            top=0.78, bottom=0.04
        )
    else:
        ax.text(
            0.5, 0.5, "No expense data available",
            ha="center", va="center",
            fontsize=11, color="#63738A",
            transform=ax.transAxes
        )
        ax.set_xticks([])
        ax.set_yticks([])
        fig.subplots_adjust(
            left=0.05, right=0.95,
            top=0.78, bottom=0.08
        )

    canvas.draw_idle()

# ADD TRANSACTION
def add_transaction():
    trans_type = type_var.get()
    category = category_var.get().strip()
    amount_text = amount_entry.get().strip()
    note = note_entry.get().strip()
    trans_date = date_entry.get().strip()

    if not category:
        messagebox.showerror("Error", "Enter a category.")
        return

    try:
        amount = float(amount_text)
        if amount <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror(
            "Invalid Amount",
            "Enter an amount greater than zero."
        )
        return

    try:
        datetime.strptime(trans_date, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror(
            "Invalid Date",
            "Use date format YYYY-MM-DD."
        )
        return

    cur.execute("""
        INSERT INTO transactions
        (trans_date, trans_type, category, amount, note)
        VALUES (?, ?, ?, ?, ?)
    """, (trans_date, trans_type, category, amount, note))
    conn.commit()

    amount_entry.delete(0, tk.END)
    note_entry.delete(0, tk.END)
    refresh()

# DELETE SELECTED
def delete_selected():
    selected = table.selection()

    if not selected:
        messagebox.showwarning(
            "Select Transaction",
            "Select a transaction from the table first."
        )
        return

    if not messagebox.askyesno(
        "Confirm Delete",
        "Delete the selected transaction(s)?"
    ):
        return

    for item in selected:
        transaction_id = table.item(item, "values")[0]
        cur.execute(
            "DELETE FROM transactions WHERE id = ?",
            (transaction_id,)
        )

    conn.commit()
    refresh()

# EXPORT CSV
def export_csv():
    rows = cur.execute("""
        SELECT id, trans_date, trans_type, category, amount, note
        FROM transactions
        ORDER BY trans_date DESC, id DESC
    """).fetchall()

    if not rows:
        messagebox.showinfo("Export CSV", "No transactions to export.")
        return

    filepath = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV Files", "*.csv")],
        title="Save Expense Report"
    )

    if not filepath:
        return

    try:
        with open(filepath, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow([
                "ID", "Date", "Type", "Category", "Amount", "Note"
            ])
            writer.writerows(rows)

        messagebox.showinfo(
            "Success", "CSV exported successfully."
        )
    except OSError as exc:
        messagebox.showerror("Export Error", str(exc))

# BUTTONS - KEEP VISIBLE
make_button(
    form, "Add Transaction", BLUE, add_transaction
).pack(fill="x", padx=12, pady=(14, 4))

make_button(
    form, "Delete Selected", "#FDE2E2",
    delete_selected, fg=RED
).pack(fill="x", padx=12, pady=4)

make_button(
    form, "Export CSV", "#DDFBE8",
    export_csv, fg=GREEN
).pack(fill="x", padx=12, pady=4)

# LIVE SEARCH AND FILTER
search_var.trace_add("write", lambda *_: refresh())
month_box.bind("<<ComboboxSelected>>", lambda event: refresh())

# CLOSE APP
def close_app():
    conn.commit()
    conn.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", close_app)

refresh()
root.mainloop()