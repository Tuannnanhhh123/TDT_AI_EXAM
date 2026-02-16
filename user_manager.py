# ============================================================
# user_manager.py — Quản lý người dùng & lưu bài làm
# Lưu vào users.json (local)
# ============================================================
import json, os
from datetime import datetime

USERS_FILE = "users.json"


# ── Đọc / ghi file ───────────────────────────────────────
def _load() -> dict:
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save(data: dict):
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ── Người dùng ────────────────────────────────────────────
def get_all_users() -> list[str]:
    """Trả về danh sách tên người dùng đã có."""
    return sorted(_load().keys())


def user_exists(name: str) -> bool:
    return name.strip() in _load()


def create_user(name: str):
    """Tạo người dùng mới nếu chưa tồn tại."""
    name = name.strip()
    if not name:
        return
    data = _load()
    if name not in data:
        data[name] = {"created_at": _now(), "exams": []}
        _save(data)


# ── Lưu bài làm ──────────────────────────────────────────
def save_exam_result(username: str, subject: str, grade: str,
                     score: int, total: int,
                     questions: list, answers: dict,
                     elapsed_seconds: int, source: str):
    """Lưu kết quả bài thi của người dùng."""
    data = _load()
    if username not in data:
        create_user(username)
        data = _load()

    record = {
        "id":        _make_id(username),
        "date":      _now(),
        "subject":   subject,
        "grade":     grade,
        "score":     score,
        "total":     total,
        "pct":       round(score / total * 100) if total else 0,
        "time_sec":  elapsed_seconds,
        "source":    source,   # 'ai' hoặc 'local'
        "detail": [
            {
                "no":        i + 1,
                "question":  q["question"],
                "correct":   q["answer"],
                "user_ans":  answers.get(i, "—"),
                "is_right":  answers.get(i) == q["answer"],
            }
            for i, q in enumerate(questions)
        ],
    }

    data[username]["exams"].append(record)
    _save(data)
    return record["id"]


# ── Truy vấn lịch sử ─────────────────────────────────────
def get_user_exams(username: str) -> list:
    """Lấy toàn bộ lịch sử bài thi của một người dùng."""
    data = _load()
    return data.get(username, {}).get("exams", [])


def get_user_stats(username: str) -> dict:
    """Thống kê tổng hợp theo môn của người dùng."""
    exams = get_user_exams(username)
    if not exams:
        return {}

    stats: dict = {}
    for e in exams:
        key = e["subject"]
        if key not in stats:
            stats[key] = {"count": 0, "total_pct": 0, "best": 0}
        stats[key]["count"]     += 1
        stats[key]["total_pct"] += e["pct"]
        stats[key]["best"]       = max(stats[key]["best"], e["pct"])

    for k in stats:
        stats[k]["avg"] = round(stats[k]["total_pct"] / stats[k]["count"])
    return stats


def delete_user(username: str):
    data = _load()
    data.pop(username, None)
    _save(data)


# ── Helpers ───────────────────────────────────────────────
def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def _make_id(username: str) -> str:
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{username[:4].upper()}_{ts}"