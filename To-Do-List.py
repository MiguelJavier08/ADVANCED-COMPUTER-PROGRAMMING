import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import os, sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ---------------- File Path Setup ----------------
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # for PyInstaller
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# .exe file
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(BASE_DIR, "tasks.txt")

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        pass

# ---------------- File Operations ----------------
def read_all_tasks():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if "|" in line]
    tasks = [line.split("|") for line in lines if len(line.split("|")) == 5]
    return tasks

def save_tasks():
    tasks = []
    for row in tree.get_children():
        values = tree.item(row)["values"]
        tasks.append("|".join(str(v) for v in values))
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(tasks))

def load_tasks(filtered=None):
    tree.delete(*tree.get_children())
    tasks = read_all_tasks()
    if filtered:
        tasks = [t for t in tasks if t[4] == filtered]
    for i, task in enumerate(tasks):
        status = task[4]
        if status == "Done":
            status_tag = "done_task" 
        else: # Pending
            status_tag = "pending_task"
        tree.insert("", "end", values=task, tags=(status_tag,))

# ---------------- Root Window ----------------
root = tk.Tk()
root.title("TASKMASTER")
root.geometry("900x800")
root.config(bg="#f5f5dc")

try:
    root.iconbitmap(resource_path("task.ico"))
except Exception:
    pass

# ---------------- Style ----------------
style = ttk.Style(root)
style.theme_use("clam")

style.configure("Treeview",
                background="white", foreground="#333",
                rowheight=30, fieldbackground="white",
                font=("Segoe UI", 12)) 
style.configure("Treeview.Heading",
                background="#228B22", foreground="white",
                font=("Segoe UI", 11, "bold"))
style.map("Treeview", background=[("selected", "#7CC47F")])

# ---------------- Title ----------------
tk.Label(root, text="TASKMASTER",
          font=("Segoe UI", 24, "bold"),
          bg="#f5f5dc", fg="#228B22").pack(pady=10)

# ---------------- Input Frame ----------------
frame_top = tk.Frame(root, bg="#f5f5dc")
frame_top.pack(pady=8)

task_var = tk.StringVar()
task_entry = tk.Entry(frame_top, textvariable=task_var,
                      font=("Segoe UI", 12), width=25, relief="solid", bd=1)
task_entry.grid(row=0, column=0, padx=5)

category_var = tk.StringVar()
category_menu = ttk.Combobox(frame_top, textvariable=category_var,
                             values=["School", "Work", "Personal", "Others"],
                             width=15, font=("Segoe UI", 11))
category_menu.set("General")
category_menu.grid(row=0, column=1, padx=5)

due_date = DateEntry(frame_top, width=14, background="#228B22",
                      foreground="white", borderwidth=2, font=("Segoe UI", 11))
due_date.grid(row=0, column=2, padx=5)

priority_var = tk.StringVar()
priority_menu = ttk.Combobox(frame_top, textvariable=priority_var,
                             values=["High", "Medium", "Low"],
                             state="readonly", width=10, font=("Segoe UI", 11))
priority_menu.current(1)
priority_menu.grid(row=0, column=3, padx=5)

# ---------------- Buttons ----------------
BTN_COLOR = "#228B22"
BTN_HOVER = "#2E8B57"

def styled_btn(parent, text, command):
    btn = tk.Button(parent, text=text, command=command,
                    bg=BTN_COLOR, fg="white",
                    font=("Segoe UI", 10, "bold"),
                    relief="flat", padx=10, pady=5)
    btn.grid(padx=5)
    btn.bind("<Enter>", lambda e: btn.config(bg=BTN_HOVER))
    btn.bind("<Leave>", lambda e: btn.config(bg=BTN_COLOR))
    return btn

# ---------------- Functions ----------------
def add_task():
    task = task_var.get().strip()
    category = category_var.get()
    date = due_date.get()
    priority = priority_var.get()
    status = "Pending"

    if task:
        tree.insert("", "end",
                    values=(task, category, date, priority, status),
                    tags=("pending_task",))
        task_var.set("")
        save_tasks()
    else:
        messagebox.showwarning("Warning", "Please enter a task.")

def delete_task():
    selected = tree.selection()
    if not selected:
        return
    item = tree.item(selected[0])
    status = item["values"][4]
    if status != "Done":
        messagebox.showwarning("Warning", "You can only delete tasks marked as Done.")
        return
    tree.delete(selected[0])
    save_tasks()

def mark_done():
    selected = tree.selection()
    if not selected:
        return
    item_id = selected[0]
    item = tree.item(item_id)
    values = list(item["values"])
    values[4] = "Done"
    
    tree.item(item_id, values=values, tags=("done_task",))
    save_tasks()

def edit_task():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select a task to edit.")
        return
    
    item_id = selected[0]
    item = tree.item(item_id)
    values = item["values"]
    current_tags = item["tags"]

    edit_win = tk.Toplevel(root)
    edit_win.title("Edit Task")
    edit_win.geometry("350x300")
    edit_win.config(bg="#f5f5dc")

    tk.Label(edit_win, text="Task:", bg="#f5f5dc", font=("Segoe UI", 11)).pack(pady=5)
    task_edit = tk.Entry(edit_win, font=("Segoe UI", 11))
    task_edit.insert(0, values[0])
    task_edit.pack(pady=5)

    tk.Label(edit_win, text="Category:", bg="#f5f5dc", font=("Segoe UI", 11)).pack(pady=5)
    category_edit = ttk.Combobox(edit_win, values=["School", "Work", "Personal", "Others"], font=("Segoe UI", 11))
    category_edit.set(values[1])
    category_edit.pack(pady=5)

    tk.Label(edit_win, text="Due Date:", bg="#f5f5dc", font=("Segoe UI", 11)).pack(pady=5)
    date_edit = DateEntry(edit_win, font=("Segoe UI", 11))
    try:
        date_edit.set_date(values[2])
    except Exception:
        pass
    date_edit.pack(pady=5)

    tk.Label(edit_win, text="Priority:", bg="#f5f5dc", font=("Segoe UI", 11)).pack(pady=5)
    priority_edit = ttk.Combobox(edit_win, values=["High", "Medium", "Low"], font=("Segoe UI", 11))
    priority_edit.set(values[3])
    priority_edit.pack(pady=5)

    def save_changes():
        new_values = (
            task_edit.get(),
            category_edit.get(),
            date_edit.get(),
            priority_edit.get(),
            values[4]
        )
        tree.item(item_id, values=new_values, tags=current_tags)
        save_tasks()
        edit_win.destroy()

    tk.Button(edit_win, text="💾 SAVE CHANGES", command=save_changes,
              bg=BTN_COLOR, fg="white", font=("Segoe UI", 11, "bold"),
              padx=40, pady=8, relief="flat").pack(pady=15)

# ---------------- Add Buttons ----------------
add_button = styled_btn(frame_top, "ADD TASK", add_task)
add_button.grid(row=0, column=4, padx=5)

# ---------------- Search Frame ----------------
search_frame = tk.Frame(root, bg="#f5f5dc")
search_frame.pack(pady=5)

search_var = tk.StringVar()
search_entry = tk.Entry(search_frame, textvariable=search_var,
                        font=("Segoe UI", 11), width=25, relief="solid", bd=1)
search_entry.grid(row=0, column=0, padx=5)

def search_task():
    query = search_var.get().strip().lower()
    tree.delete(*tree.get_children())
    tasks = read_all_tasks()
    results = [t for t in tasks if query in t[0].lower()]
    for i, task in enumerate(results):
        status = task[4]
        status_tag = "done_task" if status == "Done" else "pending_task"
        tree.insert("", "end", values=task, tags=(status_tag,))

styled_btn(search_frame, "SEARCH", search_task).grid(row=0, column=1, padx=5)
styled_btn(search_frame, "SHOW ALL", lambda: load_tasks(None)).grid(row=0, column=2, padx=5)

# ---------------- Task List ----------------
tree_frame = tk.Frame(root, bg="#f5f5dc")
tree_frame.pack(pady=10, fill="both", expand=True)

scrollbar_y = tk.Scrollbar(tree_frame, orient="vertical")
scrollbar_x = tk.Scrollbar(tree_frame, orient="horizontal")

columns = ("Task", "Category", "Due Date", "Priority", "Status")
tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                    height=15, yscrollcommand=scrollbar_y.set,
                    xscrollcommand=scrollbar_x.set)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=150, anchor="center")

scrollbar_y.config(command=tree.yview)
scrollbar_y.pack(side="right", fill="y")

scrollbar_x.config(command=tree.xview)
scrollbar_x.pack(side="bottom", fill="x")

tree.pack(fill="both", expand=True)

# Done tasks
tree.tag_configure("done_task", 
                   background="#D4EDDA", 
                   foreground="#007F3F", 
                   font=("Segoe UI", 12, "bold")) 

# Pending tasks
tree.tag_configure("pending_task", 
                   background="#F8D7DA", 
                   foreground="#842029",
                   font=("Segoe UI", 12, "bold")) 


# ---------------- Analytics Window ----------------
def open_analytics_window():
    tasks = read_all_tasks()
    total = len(tasks)
    done_count = sum(1 for t in tasks if t[4] == "Done")
    pending_count = sum(1 for t in tasks if t[4] != "Done")

    if total == 0:
        messagebox.showinfo("Analytics", "No tasks available to analyze.")
        return

    # Create window
    win = tk.Toplevel(root)
    win.title("DATA ANALYTICS")
    win.geometry("1000x700")
    win.config(bg="#f5f5dc")
    win.iconbitmap(resource_path("task.ico"))

    tk.Label(win, text="DATA ANALYTICS", font=("Segoe UI", 18, "bold"),
             bg="#f5f5dc", fg="#228B22").pack(pady=10)

    # Stats summary
    stats_frame = tk.Frame(win, bg="#f5f5dc")
    stats_frame.pack(pady=10)

    tk.Label(stats_frame, text=f"Total Tasks: {total}", font=("Segoe UI", 14),
             bg="#f5f5dc").grid(row=0, column=0, padx=20)
    tk.Label(stats_frame, text=f"Done: {done_count}", font=("Segoe UI", 14),
             bg="#f5f5dc").grid(row=0, column=1, padx=20)
    tk.Label(stats_frame, text=f"Pending: {pending_count}", font=("Segoe UI", 14),
             bg="#f5f5dc").grid(row=0, column=2, padx=20)

    # --- Pie chart (Done vs Pending) ---
    fig1 = plt.Figure(figsize=(4, 4), dpi=100)
    ax1 = fig1.add_subplot(111)
    labels = ['Done', 'Pending']
    sizes = [done_count, pending_count]
    # avoid matplotlib error when one slice is 0: show but with 0.
    ax1.pie(sizes, labels=labels, autopct=lambda p: ('%1.1f%%' % p) if p > 0 else '0.0%')
    ax1.set_title('Done vs Pending')

    canvas1 = FigureCanvasTkAgg(fig1, master=win)
    canvas1.draw()
    canvas1.get_tk_widget().pack(side="left", padx=20, pady=10, fill="both", expand=False)

    # --- Bar chart (Tasks per Category) ---
    # Build category counts from tasks list
    category_counts = {}
    for t in tasks:
        cat = t[1] or "Uncategorized"
        category_counts[cat] = category_counts.get(cat, 0) + 1

    fig2 = plt.Figure(figsize=(6, 4), dpi=100)
    ax2 = fig2.add_subplot(111)
    cats = list(category_counts.keys())
    vals = list(category_counts.values())
    ax2.bar(cats, vals)
    ax2.set_title('Tasks per Category')
    ax2.set_ylabel('Count')
    ax2.set_xticklabels(cats, rotation=30, ha='right')

    canvas2 = FigureCanvasTkAgg(fig2, master=win)
    canvas2.draw()
    canvas2.get_tk_widget().pack(side="right", padx=20, pady=10, fill="both", expand=True)

# ---------------- Bottom Buttons ----------------
frame_bottom = tk.Frame(root, bg="#f5f5dc")
frame_bottom.pack(pady=10)

styled_btn(frame_bottom, "MARK DONE", mark_done).grid(row=0, column=0, padx=5)
styled_btn(frame_bottom, "EDIT", edit_task).grid(row=0, column=1, padx=5)
styled_btn(frame_bottom, "DELETE", delete_task).grid(row=0, column=2, padx=5)
styled_btn(frame_bottom, "SHOW PENDING", lambda: load_tasks("Pending")).grid(row=0, column=3, padx=5)
styled_btn(frame_bottom, "SHOW DONE", lambda: load_tasks("Done")).grid(row=0, column=4, padx=5)
# DATA ANALYTICS button added here (as requested)
styled_btn(frame_bottom, "DATA ANALYTICS", open_analytics_window).grid(row=0, column=5, padx=5)

# ---------------- Exit ----------------
load_tasks()

def on_closing():
    save_tasks()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
