# ============================================================
# app.py — Entry point (Optimized)
# ============================================================
import time
import streamlit as st

from ui              import inject_css, render_sidebar, render_all_ui
from support_popup   import render_support_popup
from courses_page    import show_courses, show_teacher_courses
from pages           import show_home, show_select, show_exam, show_results, show_history
from teacher_pages   import show_teacher_dashboard
from profile_page    import show_profile
from settings_page   import show_settings, get_label
from chatbox_page    import show_chatbox

# IMPORT THÊM ĐỂ TỐI ƯU
from assignment_manager import get_pending_assignments

st.set_page_config(page_title="AI Exam Generator", page_icon="🎓", layout="wide")

# --- TỐI ƯU 1: Cache các truy vấn nặng từ Firebase ---
@st.cache_data(ttl=300)  # Lưu kết quả trong 5 phút
def get_pending_assignments_cached(username):
    return get_pending_assignments(username)

@st.cache_data(ttl=600)  # Lưu thông tin user trong 10 phút
def get_user_data_cached(uid):
    from firebase_manager import _db, _FIREBASE_OK
    if _FIREBASE_OK and _db:
        doc = _db.collection("users").document(uid).get()
        return doc.to_dict() if doc.exists else None
    return None

_DEFAULTS = {
    "page":               "login",
    "username":           None,
    "uid":                None,
    "email":              None,
    "role":               None,
    "grade":              None,
    "favorite_subjects":  [],
    "subject":            None,
    "questions":          [],
    "answers":            {},
    "submitted":          False,
    "score":              0,
    "start_time":         None,
    "exam_source":        None,
    "ai_error":           None,
    "verify_summary":     None,
    "dup_filtered":       0,
    "exam_start_ts":      None,
    "current_assignment": None,
    "remind_assignments": [],
    "teacher_tab":        "dashboard",
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

def _restore_session():
    # TỐI ƯU 2: Nếu đã có data trong session thì không gọi Firebase/URL nữa
    if st.session_state.get("uid") and st.session_state.get("username"):
        return

    params = st.query_params
    uid  = params.get("uid")
    role = params.get("role")
    if not uid or not role:
        return

    if role == "teacher":
        uname = params.get("uname", "Giáo viên")
        st.session_state.update({
            "uid": uid, "username": uname,
            "role": "teacher", "page": "teacher",
        })
        return

    # Sử dụng hàm cache để lấy data user từ Firebase
    p = get_user_data_cached(uid)
    if p:
        st.session_state.update({
            "uid": uid, "email": p.get("email",""),
            "username": p.get("display_name",""),
            "role": p.get("role","student"),
            "grade": p.get("grade",""),
            "favorite_subjects": p.get("favorite_subjects",[]),
            "page": "home",
        })

def _save_session():
    # Chỉ update query_params nếu thực sự thay đổi để tránh rerun thừa
    uid  = st.session_state.get("uid")
    role = st.session_state.get("role")
    if not uid or not role: return
    
    current_params = st.query_params
    if current_params.get("uid") != uid:
        params = {"uid": uid, "role": role}
        if role == "teacher":
            params["uname"] = st.session_state.get("username","")
        st.query_params.update(params)

def _clear_session():
    st.query_params.clear()
    st.cache_data.clear() # Xóa cache khi logout

_restore_session()
_save_session()

_ROUTER = {
    "home":     show_home,
    "select":   show_select,
    "exam":     show_exam,
    "result":   show_results,
    "history":  show_history,
    "profile":  show_profile,
    "settings": show_settings,
    "chatbox":  show_chatbox,
    "courses":  show_courses,
}

# ... (Giữ nguyên các đoạn code CSS và Hero Panel của bạn) ...

# ═══════════════════════════════════════════════════════════
# LOGIN PAGE (Giữ nguyên giao diện của bạn)
# ═══════════════════════════════════════════════════════════
if st.session_state.page == "login":
    # (Đoạn này giữ nguyên hoàn toàn code giao diện của bạn)
    # ... 
    # [Phần xử lý đăng nhập Student - Sửa Spinner để đồng bộ]
    if st.button("▶ Đăng nhập", type="primary", use_container_width=True, key="btn_login"):
        if not email_l or not pass_l:
            st.error("Vui lòng nhập đầy đủ thông tin!")
        else:
            with st.spinner("Đang xác thực..."):
                from firebase_manager import login
                ok, msg, user = login(email_l.strip(), pass_l)
            if ok:
                st.session_state.update({
                    "uid": user["uid"], "email": user["email"],
                    "username": user["display_name"], "role": "student",
                    "grade": user.get("grade",""),
                    "favorite_subjects": user.get("favorite_subjects",[]),
                    "page": "home",
                })
                _save_session(); st.rerun()
            else:
                st.error(f"❌ {msg}")
    # ... (Giữ nguyên phần còn lại của form)
    st.stop()

# ═══════════════════════════════════════════════════════════
# Các trang sau login
# ═══════════════════════════════════════════════════════════
inject_css()

# ── GIÁO VIÊN ────────────────────────────────────────────
if st.session_state.role == "teacher":
    # (Giữ nguyên code Sidebar giáo viên của bạn)
    # ...
    st.stop()

# ── HỌC SINH ─────────────────────────────────────────────
if st.session_state.role == "student":
    # TỐI ƯU 3: Sử dụng hàm Cached để không quét Firebase liên tục mỗi khi Click
    pending = get_pending_assignments_cached(st.session_state.username)
    
    if pending:
        required = [a for a in pending if a.get("is_required")]
        remind   = [a for a in pending if not a.get("is_required")]
        st.session_state["remind_assignments"] = remind
        
        # Chỉ chuyển trang nếu chưa ở trong bài thi
        if required and st.session_state.page not in ("exam","result","urgent_exam"):
            st.session_state["current_assignment"] = required[0]
            st.session_state.page = "urgent_exam"
            st.rerun()

if st.session_state.page == "urgent_exam":
    render_sidebar()
    render_all_ui()
    _show_urgent_exam()
    st.stop()

render_sidebar()
render_all_ui()
_ROUTER.get(st.session_state.page, show_home)()
render_support_popup()
