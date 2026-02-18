# ============================================================
# history_manager.py — Chống trùng câu hỏi toàn diện
# Lưu vào Firestore (persist qua reload) + fallback JSON local
# Hash câu GỐC từ bank trước khi Groq paraphrase
# ============================================================
import json, os, hashlib
from datetime import datetime

HISTORY_FILE = "exam_history.json"  # Chỉ dùng làm backup offline
MAX_HISTORY  = 500


# ── Hash câu hỏi gốc (trước khi Groq paraphrase) ─────────
def _hash_question(question_text: str) -> str:
    text = question_text.strip().lower().rstrip(".?!")
    text = " ".join(text.split())
    return hashlib.md5(text.encode("utf-8")).hexdigest()[:16]


# ── Firestore helpers ─────────────────────────────────────
def _get_db():
    """Trả về (db, ok). Import lazy để tránh circular import."""
    try:
        from firebase_manager import _db, _FIREBASE_OK
        return _db, _FIREBASE_OK
    except Exception:
        return None, False


def _doc_key(subject: str, grade: str) -> str:
    return f"{subject}|{grade}".replace("/", "_").replace(" ", "_")


def _firestore_get(subject: str, grade: str) -> set:
    db, ok = _get_db()
    if not ok or not db:
        return set()
    try:
        doc = db.collection("exam_history").document(_doc_key(subject, grade)).get()
        if doc.exists:
            return set(doc.to_dict().get("hashes", []))
    except Exception:
        pass
    return set()


def _firestore_save(subject: str, grade: str, hashes: list) -> bool:
    db, ok = _get_db()
    if not ok or not db:
        return False
    try:
        db.collection("exam_history").document(_doc_key(subject, grade)).set({
            "hashes":       hashes,
            "last_updated": datetime.now().isoformat(),
        })
        return True
    except Exception:
        return False


# ── Local JSON (chỉ dùng khi Firestore không khả dụng) ───
def _local_load() -> dict:
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _local_save(data: dict):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ── API công khai ─────────────────────────────────────────
def get_used_hashes(subject: str, grade: str) -> set:
    """
    Lấy set hash câu hỏi đã dùng.
    Ưu tiên Firestore, fallback local JSON nếu offline.
    """
    fs_hashes = _firestore_get(subject, grade)
    if fs_hashes:
        return fs_hashes

    # Offline fallback
    data = _local_load()
    key  = f"{subject}|{grade}"
    return set(data.get(key, {}).get("hashes", []))


def save_exam(subject: str, grade: str, questions: list):
    """
    Lưu hash các câu hỏi GỐC vừa dùng.
    Gọi TRƯỚC khi Groq paraphrase để hash đúng câu gốc.
    - Lưu Firestore trước (primary)
    - Lưu JSON sau (backup offline)
    """
    new_hashes = [_hash_question(q["question"]) for q in questions]

    # ── PRIMARY: Firestore ────────────────────────────────
    existing = list(_firestore_get(subject, grade))
    combined = list(dict.fromkeys(existing + new_hashes))[-MAX_HISTORY:]
    saved_to_firestore = _firestore_save(subject, grade, combined)

    # ── BACKUP: Local JSON ────────────────────────────────
    # Luôn ghi để có bản backup offline
    key  = f"{subject}|{grade}"
    data = _local_load()
    if key not in data:
        data[key] = {"hashes": [], "last_updated": ""}
    combined_local = list(dict.fromkeys(data[key]["hashes"] + new_hashes))[-MAX_HISTORY:]
    data[key]["hashes"]       = combined_local
    data[key]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    _local_save(data)

    if not saved_to_firestore:
        print("[exam_history] ⚠️  Firestore không khả dụng, chỉ lưu local JSON.")


def filter_new_questions(questions: list, used_hashes: set) -> list:
    """Lọc câu chưa xuất hiện dựa trên hash câu gốc."""
    return [
        q for q in questions
        if _hash_question(q["question"]) not in used_hashes
    ]


def clear_history(subject: str = None, grade: str = None):
    """Xóa lịch sử — toàn bộ hoặc theo môn+lớp (cả Firestore lẫn local)."""
    db, ok = _get_db()

    # Xóa Firestore
    if ok and db:
        try:
            if subject and grade:
                db.collection("exam_history").document(_doc_key(subject, grade)).delete()
            else:
                for doc in db.collection("exam_history").stream():
                    doc.reference.delete()
        except Exception as e:
            print(f"[exam_history] Lỗi xóa Firestore: {e}")

    # Xóa local JSON
    data = _local_load()
    if subject and grade:
        data.pop(f"{subject}|{grade}", None)
    else:
        data = {}
    _local_save(data)


def get_history_stats() -> dict:
    """Thống kê số câu đã lưu theo môn+lớp."""
    db, ok = _get_db()

    # Lấy từ Firestore (primary)
    if ok and db:
        try:
            stats = {}
            for doc in db.collection("exam_history").stream():
                stats[doc.id.replace("_", "|", 1)] = len(doc.to_dict().get("hashes", []))
            if stats:
                return stats
        except Exception:
            pass

    # Fallback local
    data = _local_load()
    return {
        key: len(val.get("hashes", []))
        for key, val in data.items()
    }
