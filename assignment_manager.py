# ============================================================
# assignment_manager.py — Đã tối ưu SQL (Truy vấn 1 lần)
# ============================================================
import sqlite3, json
from datetime import datetime

DB_FILE = "teacher_bank.db"

def _conn():
    # Thêm timeout để tránh việc DB bị lock khi nhiều người dùng cùng lúc
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

# ... (Các hàm create_assignment, deactivate_assignment, delete_assignment giữ nguyên) ...

def get_pending_assignments(username: str, subject: str = None, grade: str = None) -> list:
    """
    TỐI ƯU: Sử dụng LEFT JOIN để lấy các đề chưa nộp trong 1 lần truy vấn duy nhất.
    """
    now = _now()
    
    # Câu lệnh SQL thông minh: 
    # Lấy các bài tập (A) mà KHÔNG có bản ghi tương ứng trong bảng nộp bài (S) của user này.
    sql = """
        SELECT a.* FROM assignments a
        LEFT JOIN assignment_submissions s 
            ON a.id = s.assignment_id AND s.username = ?
        WHERE a.is_active = 1 
          AND s.id IS NULL 
    """
    params = [username]

    if subject:
        sql += " AND a.subject = ?"
        params.append(subject)
    if grade:
        sql += " AND a.grade = ?"
        params.append(grade)
        
    # Lọc thêm deadline ngay trong SQL để nhanh hơn nữa
    sql += " AND (a.deadline IS NULL OR a.deadline >= ?)"
    params.append(now)
    
    sql += " ORDER BY a.id DESC"

    try:
        with _conn() as con:
            rows = con.execute(sql, params).fetchall()
        return [_row_to_a(r) for r in rows]
    except Exception as e:
        print(f"SQL Error: {e}")
        return []

def _has_submitted(assignment_id: int, username: str) -> bool:
    # Hàm này giữ lại để tương thích các chỗ cũ, nhưng đã tối ưu connect
    with _conn() as con:
        row = con.execute(
            "SELECT 1 FROM assignment_submissions WHERE assignment_id=? AND username=? LIMIT 1",
            (assignment_id, username)
        ).fetchone()
    return row is not None

# ── Giữ nguyên các hàm helper bên dưới ──────────────────────
def _row_to_a(row) -> dict:
    return {
        "id":          row[0],
        "title":       row[1],
        "subject":     row[2],
        "grade":       row[3],
        "exam_id":     row[4],
        "deadline":    row[5],
        "is_required": bool(row[6]),
        "is_active":   bool(row[7]),
        "created_by":  row[8],
        "created_at":  row[9],
    }

def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")

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

# Tự động init
init_assignments()

