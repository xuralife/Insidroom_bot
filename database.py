# =========================================
#  XURALIFE BOT — MA'LUMOTLAR BAZASI (SQLite)
# =========================================
# Boshlash uchun SQLite yetarli (o'rnatish shart emas).
# Jamoa kattalashsa, shu faylni PostgreSQL'ga almashtirish mumkin —
# funksiyalarning nomi va argumentlari saqlanib qoladi, faqat ichi o'zgaradi.

import sqlite3
from datetime import datetime, date

from config import DB_PATH


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            full_name TEXT,
            is_admin INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            deadline TEXT,
            assigned_to INTEGER,
            status TEXT DEFAULT 'yangi',
            created_by INTEGER,
            created_at TEXT,
            FOREIGN KEY (assigned_to) REFERENCES employees (id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            employee_id INTEGER,
            stage TEXT,
            comment TEXT,
            photo_file_id TEXT,
            created_at TEXT,
            FOREIGN KEY (task_id) REFERENCES tasks (id),
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        )
    """)

    conn.commit()
    conn.close()


# ---------- XODIMLAR ----------

def upsert_employee(telegram_id, username, full_name, is_admin):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM employees WHERE telegram_id = ?", (telegram_id,))
    row = c.fetchone()
    if row:
        c.execute(
            "UPDATE employees SET username=?, full_name=? WHERE telegram_id=?",
            (username, full_name, telegram_id),
        )
    else:
        c.execute(
            "INSERT INTO employees (telegram_id, username, full_name, is_admin, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (telegram_id, username, full_name, int(is_admin), datetime.now().isoformat()),
        )
    conn.commit()
    conn.close()


def get_employee_by_tg(telegram_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM employees WHERE telegram_id = ?", (telegram_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_employee_by_id(emp_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM employees WHERE id = ?", (emp_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def list_employees(exclude_admins=False):
    conn = get_conn()
    c = conn.cursor()
    if exclude_admins:
        c.execute("SELECT * FROM employees WHERE is_admin = 0 ORDER BY full_name")
    else:
        c.execute("SELECT * FROM employees ORDER BY full_name")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------- VAZIFALAR ----------

def add_task(title, description, deadline, assigned_to, created_by):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO tasks (title, description, deadline, assigned_to, status, created_by, created_at) "
        "VALUES (?, ?, ?, ?, 'yangi', ?, ?)",
        (title, description, deadline, assigned_to, created_by, datetime.now().isoformat()),
    )
    conn.commit()
    task_id = c.lastrowid
    conn.close()
    return task_id


def get_task(task_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def list_active_tasks_for_employee(employee_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM tasks WHERE assigned_to = ? AND status != 'tugallangan' ORDER BY id DESC",
        (employee_id,),
    )
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def list_all_active_tasks():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM tasks WHERE status != 'tugallangan' ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_task_status(task_id, status):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
    conn.commit()
    conn.close()


# ---------- HISOBOTLAR ----------

def add_report(task_id, employee_id, stage, comment, photo_file_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO reports (task_id, employee_id, stage, comment, photo_file_id, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (task_id, employee_id, stage, comment, photo_file_id, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_today_reports():
    today_str = date.today().isoformat()
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        """
        SELECT r.*, e.full_name, e.username, t.title AS task_title
        FROM reports r
        JOIN employees e ON r.employee_id = e.id
        JOIN tasks t ON r.task_id = t.id
        WHERE r.created_at LIKE ?
        ORDER BY r.created_at ASC
        """,
        (f"{today_str}%",),
    )
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]
