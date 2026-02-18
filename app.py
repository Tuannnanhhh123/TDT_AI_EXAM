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

st.set_page_config(page_title="AI Exam Generator", page_icon="🎓", layout="wide")

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
    "first_login_done":   False, # Cờ tối ưu Cách 2
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

def _restore_session():
    if st.session_state.get("uid"): return
    params = st.query_params
    uid, role = params.get("uid"), params.get("role")
    if not uid or not role: return
    if role == "teacher":
        st.session_state.update({"uid": uid, "username": params.get("uname", "Giáo viên"), "role": "teacher", "page": "teacher"})
        return
    try:
        from firebase_manager import _db, _FIREBASE_OK
        if _FIREBASE_OK and _db:
            doc = _db.collection("users").document(uid).get()
            if doc.exists:
                p = doc.to_dict()
                st.session_state.update({"uid": uid, "email": p.get("email",""), "username": p.get("display_name",""),
                    "role": p.get("role","student"), "grade": p.get("grade",""), "favorite_subjects": p.get("favorite_subjects",[]), "page": "home"})
    except: st.query_params.clear()

def _save_session():
    uid, role = st.session_state.get("uid"), st.session_state.get("role")
    if uid and role and st.query_params.get("uid") != uid:
        p = {"uid": uid, "role": role}
        if role == "teacher": p["uname"] = st.session_state.get("username","")
        st.query_params.update(p)

def _clear_session():
    st.query_params.clear()

_restore_session()
_save_session()

_ROUTER = { "home": show_home, "select": show_select, "exam": show_exam, "result": show_results, 
            "history": show_history, "profile": show_profile, "settings": show_settings, 
            "chatbox": show_chatbox, "courses": show_courses }

def _show_urgent_exam():
    from ai_engine import generate_exam
    from teacher_manager import get_exam_questions, get_teacher_exams
    a = st.session_state.get("current_assignment")
    if not a: st.session_state.page = "home"; st.rerun(); return
    if st.session_state.page in ("exam","result"): render_sidebar(); _ROUTER[st.session_state.page](); return
    st.markdown(f'<div style="background:#fce8e6;border-left:5px solid #d93025;padding:1rem;border-radius:8px;margin-bottom:1.5rem">🔴 <b>Đề bắt buộc:</b> {a["title"]}</div>', unsafe_allow_html=True)
    if st.button("▶ Bắt đầu làm bài", type="primary", use_container_width=True):
        if a.get("exam_id"):
            exam_info = next((e for e in get_teacher_exams() if e["id"] == a["exam_id"]), None)
            qs = get_exam_questions(exam_info["q_ids"]) if exam_info else []
            source = "local"
        else: qs, source = generate_exam(a["subject"], a["grade"])
        now = time.time()
        st.session_state.update({"subject": a["subject"], "grade": a["grade"], "questions": qs, "answers": {}, "submitted": False, "score": 0, "start_time": now, "exam_start_ts": now, "exam_source": source, "page": "exam"})
        st.rerun()

# ═══════════════════════════════════════════════════════════
# LOGIN PAGE
# ═══════════════════════════════════════════════════════════
if st.session_state.page == "login":
    from firebase_manager import login, register, reset_password, is_firebase_ok
    from config           import TEACHER_CODE, GRADE_CONFIG, SUBJECT_OPTIONS

    # GIỮ NGUYÊN TOÀN BỘ CSS CỦA BẠN
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
    html, body { margin:0 !important; padding:0 !important; overflow-x:hidden; }
    header[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"], #MainMenu, footer { display:none !important; }
    [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stMainBlockContainer"], .block-container { padding:0 !important; margin:0 !important; max-width:100% !important; font-family:'Inter',sans-serif !important; }
    @media (min-width: 769px) { [data-testid="stMainBlockContainer"] { margin-left: 50vw !important; width: 50vw !important; min-height: 100vh !important; background: #f0f4ff !important; display: flex !important; flex-direction: column !important; align-items: center !important; justify-content: center !important; padding: 2rem 2.5rem !important; box-sizing: border-box !important; } .hero-panel { position: fixed; top: 0; left: 0; width: 50vw; height: 100vh; overflow: hidden; z-index: 999; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 3rem 2.8rem; box-sizing: border-box; } }
    @media (max-width: 768px) { [data-testid="stMainBlockContainer"] { margin-left: 0 !important; width: 100% !important; min-height: 100vh !important; padding: 220px 1.25rem 2rem !important; background: #f0f4ff !important; box-sizing: border-box !important; display: flex !important; flex-direction: column !important; align-items: center !important; } .hero-panel { position: fixed !important; top: 0; left: 0; right: 0 !important; width: 100% !important; height: 210px !important; padding: 1rem 1.5rem !important; z-index: 999; display: flex !important; flex-direction: column !important; align-items: center !important; justify-content: center !important; box-sizing: border-box; overflow: hidden; } .fl, .stats, .hero-tagline { display: none !important; } .hero-logo { font-size: 2.4rem !important; } }
    .hero-bg { position:absolute; inset:-50%; width:200%; height:200%; background:linear-gradient(-45deg,#060918,#111638,#0c1a4a,#1a0a42); background-size:400% 400%; animation:gradflow 14s ease infinite; }
    @keyframes gradflow { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
    .hc{position:relative;z-index:2;text-align:center;width:100%;font-family:'Inter',sans-serif}
    .hero-logo{font-size:4.8rem; display:block; filter:drop-shadow(0 0 30px rgba(99,102,241,1)); }
    .hero-title{font-size:2.2rem;font-weight:900;color:#fff; margin-bottom:.45rem;}
    .grad-txt{background:linear-gradient(90deg,#a5b4fc,#38bdf8); -webkit-background-clip:text; -webkit-text-fill-color:transparent;}
    .fcard{background:#fff;border-radius:22px;padding:2rem 2.2rem; width:100%;max-width:420px; box-shadow:0 12px 40px rgba(67,56,202,.09); position:relative;z-index:2;}
    .fg{font-size:1.65rem;font-weight:800;color:#1e1b4b;margin-bottom:.2rem;}
    .fs{color:#9ca3af;font-size:.83rem;margin-bottom:1.4rem}
    </style>""", unsafe_allow_html=True)

    # HERO PANEL HTML
    st.markdown("""<div class="hero-panel"><div class="hero-bg"></div><div class="hc"><div class="hero-logo">🎓</div><div class="hero-title">AI Exam<br><span class="grad-txt">Generator</span></div></div></div>""", unsafe_allow_html=True)

    st.markdown('<div class="fcard">', unsafe_allow_html=True)
    role_choice = st.radio("role", ["🎒 Học sinh", "👩‍🏫 Giáo viên"], horizontal=True, label_visibility="collapsed")
    
    if role_choice == "👩‍🏫 Giáo viên":
        st.markdown('<div class="fg">Xin chào, Thầy/Cô 👋</div>', unsafe_allow_html=True)
        name = st.text_input("Tên giáo viên", key="t_name")
        code = st.text_input("Mã giáo viên", type="password", key="t_code")
        if st.button("🔓 Đăng nhập", type="primary", use_container_width=True):
            if code == TEACHER_CODE:
                st.session_state.update({"uid": f"t_{name}", "username": name, "role": "teacher", "page": "teacher"})
                st.rerun()
            else: st.error("Mã sai!")
    else:
        st.markdown('<div class="fg">Chào mừng! 👋</div>', unsafe_allow_html=True)
        tab_l, tab_r, tab_rs = st.tabs(["🔑 Đăng nhập", "📝 Đăng ký", "🔒 Quên"])
        
        with tab_l:
            e_l = st.text_input("📧 Email", key="l_email")
            p_l = st.text_input("🔒 Mật khẩu", type="password", key="l_pass")
            if st.button("▶ Đăng nhập", type="primary", use_container_width=True):
                with st.spinner("Đang xác thực..."):
                    ok, msg, user = login(e_l.strip(), p_l)
                if ok:
                    # CÁCH 2: Cập nhật session và chuyển trang ngay lập tức
                    st.session_state.update({"uid": user["uid"], "email": user["email"], "username": user["display_name"], 
                                            "role": "student", "grade": user.get("grade",""), "page": "home", "first_login_done": False})
                    _save_session(); st.rerun()
                else: st.error(msg)
        
        with tab_r:
            r_n = st.text_input("Họ tên", key="r_name")
            r_e = st.text_input("Email", key="r_email")
            r_p = st.text_input("Mật khẩu", type="password", key="r_pass")
            if st.button("✅ Đăng ký", type="primary", use_container_width=True):
                ok, msg = register(r_e, r_p, r_n, "12", [])
                if ok: st.success("Xong! Hãy đăng nhập.")
                else: st.error(msg)
        
        with tab_rs:
            rst_e = st.text_input("Email nhận link", key="rst_email")
            if st.button("Gửi link", use_container_width=True):
                ok, msg = reset_password(rst_e)
                st.info(msg)

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ═══════════════════════════════════════════════════════════
# SAU ĐĂNG NHẬP
# ═══════════════════════════════════════════════════════════
inject_css()

if st.session_state.role == "teacher":
    render_all_ui()
    show_teacher_dashboard()
    st.stop()

if st.session_state.role == "student":
    # CÁCH 2: Lazy Loading - Chỉ chạy create_user 1 lần sau khi vào app
    if not st.session_state.get("first_login_done"):
        from user_manager import create_user
        try: create_user(st.session_state.username)
        except: pass
        st.session_state["first_login_done"] = True

    # Chỉ quét bài tập khi thực sự cần (Giảm lag)
    if st.session_state.page in ["home", "urgent_exam"]:
        from assignment_manager import get_pending_assignments
        # Dùng session để lưu tránh gọi đi gọi lại
        if "cached_pending" not in st.session_state:
            st.session_state.cached_pending = get_pending_assignments(st.session_state.username)
        
        pending = st.session_state.cached_pending
        if pending:
            required = [a for a in pending if a.get("is_required")]
            st.session_state["remind_assignments"] = [a for a in pending if not a.get("is_required")]
            if required and st.session_state.page not in ("exam","result","urgent_exam"):
                st.session_state["current_assignment"] = required[0]
                st.session_state.page = "urgent_exam"
                st.rerun()

render_sidebar()
render_all_ui()
_ROUTER.get(st.session_state.page, show_home)()
render_support_popup()

