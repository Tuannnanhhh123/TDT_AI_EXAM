# ============================================================
# config.py — Cấu hình toàn cục
# ============================================================
import os

# ── GROQ API ──────────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
GROQ_MODEL   = "llama-3.3-70b-versatile"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_HEADERS = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}

# ── ĐỀ THI ────────────────────────────────────────────────
NUM_QUESTIONS   = 10
SUBJECT_OPTIONS = ["Toán", "Ngữ Văn", "Tiếng Anh", "Vật Lý", "Hóa Học", "Sinh Học"]

# ── MÃ GIÁO VIÊN ─────────────────────────────────────────
TEACHER_CODE = os.environ.get("TEACHER_CODE", "GV@2025")

# ── CẤU HÌNH LỚP HỌC ─────────────────────────────────────
GRADE_CONFIG = {
    "Lớp 9 (THCS)":       {"level":"THCS",    "tag":"tag-middle", "emoji":"🎯", "time":20,
                            "desc":"Toán, Văn, Anh cơ bản THCS",
                            "subjects":["Toán","Ngữ Văn","Tiếng Anh"]},
    "Lớp 10 (THPT)":      {"level":"THPT",    "tag":"tag-high",   "emoji":"📊", "time":25,
                            "desc":"Đầy đủ 6 môn, nền tảng THPT",
                            "subjects":["Toán","Ngữ Văn","Tiếng Anh","Vật Lý","Hóa Học","Sinh Học"]},
    "Lớp 11 (THPT)":      {"level":"THPT",    "tag":"tag-high",   "emoji":"📡", "time":25,
                            "desc":"Nâng cao, luyện thi THPT",
                            "subjects":["Toán","Ngữ Văn","Tiếng Anh","Vật Lý","Hóa Học","Sinh Học"]},
    "Lớp 12 (THPT)":      {"level":"THPT",    "tag":"tag-high",   "emoji":"🏆", "time":25,
                            "desc":"Ôn thi THPT Quốc gia",
                            "subjects":["Toán","Ngữ Văn","Tiếng Anh","Vật Lý","Hóa Học","Sinh Học"]},
    "Đại học / Nâng cao": {"level":"Đại học", "tag":"tag-uni",    "emoji":"🎓", "time":30,
                            "desc":"Kiến thức đại học, chuyên sâu",
                            "subjects":["Toán","Tiếng Anh","Vật Lý","Hóa Học","Sinh Học"]},
}

# ── MAPPING ĐỘ KHÓ ───────────────────────────────────────
DIFFICULTY_MAP = {
    "Lớp 9 (THCS)":       "Trung bình",
    "Lớp 10 (THPT)":      "Khó",
    "Lớp 11 (THPT)":      "Khó",
    "Lớp 12 (THPT)":      "Khó",
    "Đại học / Nâng cao": "Khó",
}

# ── FIREBASE CONFIG ───────────────────────────────────────
# Điền thông tin Firebase project của bạn vào đây
# hoặc set biến môi trường tương ứng
FIREBASE_CONFIG = {
    "apiKey":            os.environ.get("FB_API_KEY",        "AIzaSyBiVioCqpImimXvyOza463H_nbxnVhfzRE"),
    "authDomain":        os.environ.get("FB_AUTH_DOMAIN",    "sanpham-7fdd6.firebaseapp.com"),
    "projectId":         os.environ.get("FB_PROJECT_ID",     "sanpham-7fdd6"),
    "storageBucket":     os.environ.get("FB_STORAGE_BUCKET", "sanpham-7fdd6.firebasestorage.app"),
    "messagingSenderId": os.environ.get("FB_MESSAGING_ID",   "636364696646"),
    "appId":             os.environ.get("FB_APP_ID",         "1:636364696646:web:f324707fc41d9be00d2e47"),
    "measurementId":     "G-S60LRKVQE8",
}

# Service Account JSON path (dùng cho Firestore Admin SDK)
FIREBASE_SERVICE_ACCOUNT = os.environ.get(
    "FIREBASE_SERVICE_ACCOUNT", "firebase_service_account.json"
)