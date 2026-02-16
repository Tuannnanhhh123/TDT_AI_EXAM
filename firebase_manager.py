# ============================================================
# firebase_manager.py — Firebase Auth + Firestore
# pip install firebase-admin requests
# ============================================================
import json, requests, os
import streamlit as st

# ── Firebase Admin SDK (Firestore) ────────────────────────
try:
    import firebase_admin
    from firebase_admin import credentials, firestore, auth as fb_auth

    _sa = None
    if not firebase_admin._apps:
        from config import FIREBASE_SERVICE_ACCOUNT
        if os.path.exists(FIREBASE_SERVICE_ACCOUNT):
            _sa = credentials.Certificate(FIREBASE_SERVICE_ACCOUNT)
        else:
            # Đọc từ biến môi trường dạng JSON string
            sa_json = os.environ.get("FIREBASE_SA_JSON", "")
            if sa_json:
                _sa = credentials.Certificate(json.loads(sa_json))

        if _sa:
            firebase_admin.initialize_app(_sa)

    _db = firestore.client() if firebase_admin._apps else None
    _FIREBASE_OK = _db is not None

except Exception as e:
    _FIREBASE_OK = False
    _db          = None
    print(f"[Firebase] Không kết nối được: {e}")


# ── Firebase Auth REST API (đăng ký / đăng nhập) ─────────
def _auth_url(endpoint: str) -> str:
    from config import FIREBASE_CONFIG
    key = FIREBASE_CONFIG["apiKey"]
    base = "https://identitytoolkit.googleapis.com/v1/accounts"
    return f"{base}:{endpoint}?key={key}"


def _auth_post(endpoint: str, payload: dict) -> tuple[dict, str]:
    """Gọi Firebase Auth REST. Trả về (data, error_message)."""
    try:
        r = requests.post(_auth_url(endpoint), json=payload, timeout=10)
        data = r.json()
        if "error" in data:
            msg = data["error"].get("message", "Lỗi không xác định")
            return {}, _translate_error(msg)
        return data, ""
    except Exception as e:
        return {}, f"Lỗi kết nối: {e}"


def _translate_error(msg: str) -> str:
    MAP = {
        "EMAIL_EXISTS":              "Email đã được đăng ký!",
        "INVALID_EMAIL":             "Email không hợp lệ!",
        "WEAK_PASSWORD":             "Mật khẩu quá yếu (tối thiểu 6 ký tự)!",
        "EMAIL_NOT_FOUND":           "Email chưa đăng ký!",
        "INVALID_PASSWORD":          "Mật khẩu không đúng!",
        "INVALID_LOGIN_CREDENTIALS": "Email hoặc mật khẩu không đúng!",
        "USER_DISABLED":             "Tài khoản đã bị vô hiệu hóa!",
        "TOO_MANY_ATTEMPTS_TRY_LATER":"Quá nhiều lần thử, vui lòng thử lại sau!",
    }
    for k, v in MAP.items():
        if k in msg:
            return v
    return msg


# ── Đăng ký ──────────────────────────────────────────────
def register(email: str, password: str, display_name: str,
             grade: str, favorite_subjects: list) -> tuple[bool, str]:
    """
    Đăng ký tài khoản mới.
    Trả về (success, message).
    """
    data, err = _auth_post("signUp", {
        "email": email, "password": password, "returnSecureToken": True
    })
    if err:
        return False, err

    uid = data.get("localId", "")

    # Lưu profile vào Firestore
    if _FIREBASE_OK and uid:
        try:
            _db.collection("users").document(uid).set({
                "uid":               uid,
                "email":             email,
                "display_name":      display_name,
                "grade":             grade,
                "favorite_subjects": favorite_subjects,
                "role":              "student",
                "created_at":        firestore.SERVER_TIMESTAMP,
            })
        except Exception as e:
            return False, f"Tạo profile thất bại: {e}"

    return True, "Đăng ký thành công!"


# ── Đăng nhập ─────────────────────────────────────────────
def login(email: str, password: str) -> tuple[bool, str, dict]:
    """
    Đăng nhập.
    Trả về (success, message, user_info).
    """
    data, err = _auth_post("signInWithPassword", {
        "email": email, "password": password, "returnSecureToken": True
    })
    if err:
        return False, err, {}

    uid = data.get("localId", "")

    # Lấy profile từ Firestore
    user_info = {
        "uid":           uid,
        "email":         email,
        "display_name":  data.get("displayName", email.split("@")[0]),
        "grade":         "",
        "favorite_subjects": [],
        "role":          "student",
    }

    if _FIREBASE_OK and uid:
        try:
            doc = _db.collection("users").document(uid).get()
            if doc.exists:
                profile = doc.to_dict()
                user_info.update({
                    "display_name":      profile.get("display_name", user_info["display_name"]),
                    "grade":             profile.get("grade", ""),
                    "favorite_subjects": profile.get("favorite_subjects", []),
                    "role":              profile.get("role", "student"),
                })
        except Exception as e:
            print(f"[Firebase] Lấy profile lỗi: {e}")

    return True, "Đăng nhập thành công!", user_info


# ── Đổi mật khẩu ─────────────────────────────────────────
def reset_password(email: str) -> tuple[bool, str]:
    """Gửi email đặt lại mật khẩu."""
    _, err = _auth_post("sendOobCode", {
        "requestType": "PASSWORD_RESET", "email": email
    })
    if err:
        return False, err
    return True, f"Đã gửi email đặt lại mật khẩu đến {email}!"


# ── Cập nhật profile ──────────────────────────────────────
def update_profile(uid: str, display_name: str = None,
                   grade: str = None, favorite_subjects: list = None) -> bool:
    if not (_FIREBASE_OK and uid):
        return False
    update = {}
    if display_name      is not None: update["display_name"]      = display_name
    if grade             is not None: update["grade"]             = grade
    if favorite_subjects is not None: update["favorite_subjects"] = favorite_subjects
    try:
        _db.collection("users").document(uid).update(update)
        return True
    except Exception:
        return False


def is_firebase_ok() -> bool:
    return _FIREBASE_OK