# ============================================================
# assignment_manager.py — BẢN ĐẦY ĐỦ (Đã tối ưu SQL)
# ============================================================
import sqlite3, json
from datetime import datetime

DB_FILE = "teacher_bank.db"

def _conn():
    return sqlite3.connect(DB_FILE, timeout=10)

def init_assignments():
    """Tạo bảng assignments nếu chưa có."""
    with _conn() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS assignments (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT    NOT NULL,
                subject     TEXT    NOT NULL,
                grade       TEXT    NOT NULL,
                exam_id     INTEGER,
                deadline    TEXT,
                is_required INTEGER NOT NULL DEFAULT 1,
                is_active   INTEGER NOT NULL DEFAULT 1,
                created_by  TEXT    NOT NULL DEFAULT 'teacher',
                created_at  TEXT    NOT NULL
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS assignment_submissions (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                assignment_id INTEGER NOT NULL,
                username      TEXT    NOT NULL,
                score         INTEGER,
                total         INTEGER,
                submitted_at  TEXT,
                UNIQUE(assignment_id, username)
            )
        """)

# ── CRUD Assignment (Đã khôi phục đầy đủ cho teacher_pages.py) ───────────────────
def create_assignment(title: str, subject: str, grade: str,
                      exam_id: int = None, deadline: str = None,
                      is_required: bool = True,
                      created_by: str = "teacher") -> int:
    with _conn() as con:
        cur = con.execute(
            """INSERT INTO assignments
               (title,subject,grade,exam_id,deadline,is_required,is_active,created_by,created_at)
               VALUES (?,?,?,?,?,?,1,?,?)""",
            (title, subject, grade, exam_id, deadline,
             1 if is_required else 0, created_by, _now())
        )
        return cur.lastrowid

def deactivate_assignment(a_id: int):
    with _conn() as con:
        con.execute("UPDATE assignments SET is_active=0 WHERE id=?", (a_id,))

def delete_assignment(a_id: int):
    with _conn() as con:
        con.execute("DELETE FROM assignments WHERE id=?", (a_id,))
        con.execute("DELETE FROM assignment_submissions WHERE assignment_id=?", (a_id,))

def toggle_required(a_id: int, is_required: bool):
    with _conn() as con:
        con.execute("UPDATE assignments SET is_required=? WHERE id=?",
                    (1 if is_required else 0, a_id))

# ── Truy vấn Assignment (Đã tối ưu SQL để chạy nhanh) ───────────────────
def get_pending_assignments(username: str, subject: str = None, grade: str = None) -> list:
    """Lấy các đề chưa nộp bằng 1 câu lệnh JOIN duy nhất (Rất nhanh)."""
    now = _now()
    sql = """
        SELECT a.* FROM assignments a
        LEFT JOIN assignment_submissions s 
            ON a.id = s.assignment_id AND s.username = ?
        WHERE a.is_active = 1 AND s.id IS NULL 
    """
    params = [username]
    if subject: sql += " AND a.subject = ?"; params.append(subject)
    if grade:   sql += " AND a.grade = ?";   params.append(grade)
    sql += " AND (a.deadline IS NULL OR a.deadline >= ?) ORDER BY a.id DESC"
    
    with _conn() as con:
        rows = con.execute(sql, params).fetchall()
    return [_row_to_a(r) for r in rows]

def get_active_assignments(subject: str = None, grade: str = None) -> list:
    sql, params = "SELECT * FROM assignments WHERE is_active=1", []
    if subject: sql += " AND subject=?"; params.append(subject)
    if grade:   sql += " AND grade=?";   params.append(grade)
    sql += " ORDER BY id DESC"
    with _conn() as con:
        rows = con.execute(sql, params).fetchall()
    return [_row_to_a(r) for r in rows]

def get_all_assignments() -> list:
    with _conn() as con:
        rows = con.execute("SELECT * FROM assignments ORDER BY is_active DESC, id DESC").fetchall()
    return [_row_to_a(r) for r in rows]

# ── Nộp bài & Thống kê ────────────────────────────────────
def submit_assignment(assignment_id: int, username: str, score: int, total: int):
    with _conn() as con:
        con.execute(
            "INSERT OR REPLACE INTO assignment_submissions (assignment_id, username, score, total, submitted_at) VALUES (?,?,?,?,?)",
            (assignment_id, username, score, total, _now())
        )

def get_submission_stats(assignment_id: int) -> dict:
    with _conn() as con:
        rows = con.execute(
            "SELECT username, score, total, submitted_at FROM assignment_submissions WHERE assignment_id=? ORDER BY score DESC",
            (assignment_id,)
        ).fetchall()
    subs = [{"username": r[0], "score": r[1], "total": r[2], "pct": round(r[1]/r[2]*100) if r[2] else 0, "submitted_at": r[3]} for r in rows]
    return {"count": len(subs), "avg_pct": round(sum(s["pct"] for s in subs)/len(subs)) if subs else 0, "subs": subs}

def get_all_submission_stats() -> list:
    assignments = get_all_assignments()
    result = []
    for a in assignments:
        stats = get_submission_stats(a["id"])
        result.append({**a, "submission_stats": stats})
    return result

# ── Helpers ───────────────────────────────────────────────
def _row_to_a(row) -> dict:
    return {
        "id": row[0], "title": row[1], "subject": row[2], "grade": row[3],
        "exam_id": row[4], "deadline": row[5], "is_required": bool(row[6]),
        "is_active": bool(row[7]), "created_by": row[8], "created_at": row[9],
    }

def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")

init_assignments()
