# ============================================================
# ui.py — CSS styles & sidebar + Navbar sticky + Pop-ups
# ============================================================
import streamlit as st
from config import GRADE_CONFIG, GROQ_MODEL

# ── CSS toàn cục ─────────────────────────────────────────
CSS = """
<style>
/* ── Reset & base ── */
    .main-title  { font-size:2.4rem; font-weight:800; color:#1a73e8; text-align:center; }
    .sub-title   { font-size:1rem; color:#555; text-align:center; margin-bottom:1rem; }
    .q-box       { background:#f0f4ff; border-left:4px solid #1a73e8;
                   border-radius:8px; padding:1rem 1.2rem; margin-bottom:.8rem; }
    .correct     { color:#1e8e3e; font-weight:600; }
    .wrong       { color:#d93025; font-weight:600; }
    .explain-box { background:#e8f5e9; border-radius:6px; padding:.6rem 1rem;
                   font-size:.88rem; color:#2e7d32; margin-top:.4rem; }
    .timer-box   { font-size:1.3rem; font-weight:700; text-align:center;
                   padding:.5rem; border-radius:8px; }
    .stButton > button { width:100%; border-radius:8px; font-weight:600; padding:.5rem 1rem; }
    .source-badge{ font-size:.72rem; padding:.2rem .6rem; border-radius:99px;
                   font-weight:600; display:inline-block; margin-bottom:.4rem; }
    .badge-ai    { background:#e8f0fe; color:#1a73e8; }
    .badge-local { background:#fce8e6; color:#d93025; }
    .level-tag   { display:inline-block; padding:.15rem .5rem; border-radius:4px;
                   font-size:.75rem; font-weight:700; margin-left:.4rem; }
    .tag-primary { background:#e8f0fe; color:#1565c0; }
    .tag-middle  { background:#e8f5e9; color:#2e7d32; }
    .tag-high    { background:#fff3e0; color:#e65100; }
    .tag-uni     { background:#fce4ec; color:#880e4f; }

/* ── Navbar sticky ── */
.top-navbar {
    position: fixed;
    top: 0; left: 0; right: 0;
    z-index: 9999;
    background: #fff;
    border-bottom: 1px solid #e0e7ff;
    box-shadow: 0 2px 12px rgba(26,115,232,.08);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 1.5rem;
    height: 52px;
    gap: 1rem;
}
.navbar-logo {
    display: flex; align-items: center; gap: .5rem;
    font-size: 1rem; font-weight: 800; color: #1a73e8;
    white-space: nowrap; text-decoration: none;
    cursor: pointer;
}
.navbar-logo .logo-icon {
    font-size: 1.3rem;
}
.navbar-menu {
    display: flex; align-items: center; gap: .25rem;
    flex: 1; justify-content: center;
}
.navbar-btn {
    background: none; border: none;
    padding: .35rem .75rem; border-radius: 6px;
    font-size: .82rem; font-weight: 600; color: #444;
    cursor: pointer; white-space: nowrap;
    transition: background .15s, color .15s;
    text-decoration: none;
}
.navbar-btn:hover { background: #f0f4ff; color: #1a73e8; }
.navbar-btn.active { background: #e8f0fe; color: #1a73e8; }

.navbar-right {
    display: flex; align-items: center; gap: .6rem;
    flex-shrink: 0;
}
.navbar-avatar {
    width: 32px; height: 32px; border-radius: 50%;
    background: linear-gradient(135deg,#1a73e8,#0d47a1);
    display: flex; align-items: center; justify-content: center;
    font-size: .8rem; font-weight: 700; color: white;
    cursor: pointer; flex-shrink: 0;
}
.navbar-uname {
    font-size: .82rem; font-weight: 600; color: #1a1a2e;
    max-width: 100px; overflow: hidden;
    text-overflow: ellipsis; white-space: nowrap;
}
.navbar-notif {
    position: relative; cursor: pointer;
    width: 32px; height: 32px; display: flex;
    align-items: center; justify-content: center;
    border-radius: 50%; transition: background .15s;
}
.navbar-notif:hover { background: #f0f4ff; }
.notif-badge {
    position: absolute; top: 2px; right: 2px;
    width: 14px; height: 14px; border-radius: 50%;
    background: #d93025; color: white;
    font-size: .6rem; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
    border: 2px solid white;
}

/* ── Spacer để nội dung không bị navbar che ── */
.navbar-spacer { height: 60px; }

/* ── Pop-up toast ── */
.popup-toast {
    position: fixed;
    bottom: 1.5rem; right: 1.5rem;
    z-index: 9998;
    display: flex; flex-direction: column; gap: .6rem;
    max-width: 320px;
}
.toast {
    background: white;
    border-radius: 12px;
    padding: .75rem 1rem;
    box-shadow: 0 4px 20px rgba(0,0,0,.12);
    border-left: 4px solid #1a73e8;
    display: flex; align-items: flex-start; gap: .6rem;
    animation: slideIn .3s ease;
    font-size: .85rem;
    line-height: 1.4;
}
.toast.toast-success { border-color: #1e8e3e; }
.toast.toast-warning { border-color: #f4a300; }
.toast.toast-error   { border-color: #d93025; }
.toast.toast-info    { border-color: #1a73e8; }
.toast-icon { font-size: 1.2rem; flex-shrink: 0; margin-top: .05rem; }
.toast-content { flex: 1; }
.toast-title { font-weight: 700; color: #1a1a2e; margin-bottom: .15rem; }
.toast-msg   { color: #555; font-size: .8rem; }
.toast-close {
    cursor: pointer; color: #aaa; font-size: 1rem;
    line-height: 1; padding: 0 .2rem;
    flex-shrink: 0;
}
.toast-close:hover { color: #444; }

/* ── Chat support bubble ── */
.chat-fab {
    position: fixed;
    bottom: 1.5rem; left: 1.5rem;
    z-index: 9997;
    width: 48px; height: 48px;
    background: linear-gradient(135deg,#1a73e8,#7c3aed);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem; cursor: pointer;
    box-shadow: 0 4px 16px rgba(26,115,232,.35);
    transition: transform .15s, box-shadow .15s;
    border: none;
}
.chat-fab:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 20px rgba(26,115,232,.45);
}
.chat-fab-tooltip {
    position: fixed;
    bottom: 1.5rem; left: 4.5rem;
    z-index: 9996;
    background: #1a1a2e; color: white;
    padding: .35rem .75rem; border-radius: 6px;
    font-size: .78rem; font-weight: 600;
    white-space: nowrap; pointer-events: none;
    opacity: 0; transition: opacity .2s;
}
.chat-fab:hover + .chat-fab-tooltip { opacity: 1; }

@keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to   { transform: translateX(0);    opacity: 1; }
}
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)
    try:
        from settings_page import apply_settings_css
        apply_settings_css()
    except Exception:
        pass


# ── Render navbar ─────────────────────────────────────────
def render_navbar():
    """Navbar sticky cố định trên cùng."""
    uname   = st.session_state.get("username", "")
    cur     = st.session_state.get("page", "home")
    remind  = st.session_state.get("remind_assignments", [])
    notif_n = len(remind)

    initials = "".join(w[0].upper() for w in uname.split()[:2]) if uname else "?"

    # Các mục menu
    menu_items = [
        ("🏠 Trang chủ", "home"),
        ("🚀 Làm bài",   "select"),
        ("📋 Lịch sử",   "history"),
        ("💬 Chat AI",   "chatbox"),
        ("👤 Hồ sơ",     "profile"),
        ("⚙️ Cài đặt",   "settings"),
    ]

    notif_html = ""
    if notif_n > 0:
        notif_html = (
            f'<div class="navbar-notif" title="{notif_n} đề cần làm">'
            f'🔔<div class="notif-badge">{notif_n}</div></div>'
        )

    menu_html = "".join(
        f'<span class="navbar-btn {"active" if cur == page else ""}"'
        f' onclick="void(0)">{label}</span>'
        for label, page in menu_items
    )

    st.markdown(f"""
    <div class="top-navbar">
        <div class="navbar-logo">
            <span class="logo-icon">🎓</span>
            AI Exam Generator
        </div>
        <div class="navbar-menu">{menu_html}</div>
        <div class="navbar-right">
            {notif_html}
            <div class="navbar-avatar" title="{uname}">{initials}</div>
            <span class="navbar-uname">{uname}</span>
        </div>
    </div>
    <div class="navbar-spacer"></div>
    """, unsafe_allow_html=True)

    # Buttons Streamlit ẩn để xử lý click (navbar dùng HTML thuần)
    # Đặt trong container ẩn bằng CSS
    st.markdown('<div style="display:none">', unsafe_allow_html=True)
    for label, page in menu_items:
        if st.button(label, key=f"nav2_{page}"):
            st.session_state.page = page; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ── Pop-up toasts ─────────────────────────────────────────
def render_popups():
    """Hiển thị các pop-up thông báo theo tình huống."""
    toasts = []
    page   = st.session_state.get("page", "")

    # 📢 Thông báo đề mới từ GV
    remind = st.session_state.get("remind_assignments", [])
    if remind and page == "home":
        for a in remind[:2]:  # tối đa 2 thông báo
            dl = f" — hạn {a['deadline']}" if a.get("deadline") else ""
            toasts.append(("toast-warning", "📢",
                           "Đề mới từ giáo viên",
                           f"{a['title']}{dl}"))

    # 🎉 Chúc mừng khi đạt điểm cao
    if page == "result":
        score = st.session_state.get("score", 0)
        total = len(st.session_state.get("questions", [1]))
        pct   = round(score / total * 100) if total else 0
        if pct == 100:
            toasts.append(("toast-success", "🎉",
                           "Xuất sắc! Điểm tuyệt đối!",
                           "Bạn trả lời đúng tất cả câu hỏi!"))
        elif pct >= 80:
            toasts.append(("toast-success", "🥇",
                           f"Kết quả tốt! {pct}%",
                           "Tiếp tục phát huy nhé!"))

    # ⚠️ Nhắc nhở câu chưa làm (khi đang confirm nộp)
    if page == "exam" and st.session_state.get("confirm_submit"):
        qs         = st.session_state.get("questions", [])
        unanswered = [i+1 for i in range(len(qs))
                      if st.session_state.get("answers", {}).get(i) is None]
        if unanswered:
            toasts.append(("toast-error", "⚠️",
                           f"{len(unanswered)} câu chưa làm",
                           "Câu " + ", ".join(str(n) for n in unanswered[:5])
                           + ("..." if len(unanswered) > 5 else "")))

    if not toasts:
        return

    items_html = ""
    for cls, icon, title, msg in toasts:
        items_html += f"""
        <div class="toast {cls}">
            <div class="toast-icon">{icon}</div>
            <div class="toast-content">
                <div class="toast-title">{title}</div>
                <div class="toast-msg">{msg}</div>
            </div>
        </div>"""

    st.markdown(f'<div class="popup-toast">{items_html}</div>',
                unsafe_allow_html=True)


# ── Chat support FAB ──────────────────────────────────────
def render_chat_fab():
    """Nút chat hỗ trợ nổi góc trái dưới."""
    page = st.session_state.get("page", "")
    if page in ("chatbox", "exam"):
        return  # Không hiện khi đang chat hoặc làm bài

    st.markdown("""
    <div style="position:fixed;bottom:1.5rem;left:1.5rem;z-index:9997">
        <div style="position:relative;display:inline-flex;align-items:center;gap:.6rem">
            <div class="chat-fab" title="Chat hỗ trợ AI">💬</div>
            <div style="background:#1a1a2e;color:white;padding:.3rem .7rem;
                        border-radius:6px;font-size:.78rem;font-weight:600;
                        white-space:nowrap;box-shadow:0 2px 8px rgba(0,0,0,.15)">
                Cần hỗ trợ?
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Nút ẩn để trigger navigation
    st.markdown('<div style="position:fixed;bottom:1.5rem;left:1.5rem;'
                'z-index:9998;opacity:0;width:48px;height:48px">',
                unsafe_allow_html=True)
    if st.button("💬", key="fab_chat_btn", help="Mở chat hỗ trợ AI"):
        st.session_state.page = "chatbox"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────
def _do_logout():
    try:
        from app import _DEFAULTS, _clear_session
        _clear_session()
        for k, v in _DEFAULTS.items():
            st.session_state[k] = v
    except Exception:
        st.query_params.clear()
        for k in ["page","username","uid","email","role","grade",
                  "favorite_subjects","questions","answers","submitted",
                  "score","current_assignment","remind_assignments","confirm_submit"]:
            st.session_state[k] = None if k != "page" else "login"
        st.session_state.update({
            "questions": [], "answers": {},
            "remind_assignments": [], "confirm_submit": False
        })
    st.rerun()


def render_sidebar():
    from settings_page import get_label
    with st.sidebar:
        uname = st.session_state.get("username", "")
        grade = st.session_state.get("grade",    "")
        email = st.session_state.get("email",    "")
        role  = st.session_state.get("role",     "student")

        st.markdown("### 🎓 AI Exam Generator")
        if uname:
            initials = "".join(w[0].upper() for w in uname.split()[:2]) or "HS"
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:.7rem;'
                f'padding:.5rem 0;margin-bottom:.3rem">'
                f'<div style="width:38px;height:38px;border-radius:50%;'
                f'background:linear-gradient(135deg,#1a73e8,#0d47a1);'
                f'display:flex;align-items:center;justify-content:center;'
                f'font-size:.95rem;font-weight:700;color:white;flex-shrink:0">'
                f'{initials}</div>'
                f'<div><div style="font-weight:600;font-size:.9rem">{uname}</div>'
                f'<div style="font-size:.72rem;color:#888">{email or grade}</div>'
                f'</div></div>',
                unsafe_allow_html=True)
        st.markdown("---")

        # Nút tạo hội thoại mới khi ở chatbox
        if st.session_state.get("page") == "chatbox":
            if st.button("✏️ Hội thoại mới", use_container_width=True,
                         type="primary", key="btn_new_ui_sidebar"):
                from chatbox_page import _new_conversation
                _new_conversation(); st.rerun()
            st.markdown("---")

        cur = st.session_state.get("page", "home")

        def nav_btn(label, page, key):
            active = cur == page
            if st.button(label, key=key, use_container_width=True,
                         type="primary" if active else "secondary"):
                st.session_state.page = page; st.rerun()

        nav_btn(get_label("home"),     "home",     "nav_home")
        nav_btn(get_label("start"),    "select",   "nav_select")

        # ── Nút Khóa học (chỉ hiện cho học sinh) ──────────
        if role == "student":
            nav_btn("📚 Khóa học",     "courses",  "nav_courses")

        nav_btn(get_label("history"),  "history",  "nav_history")
        nav_btn(get_label("chatbox"),  "chatbox",  "nav_chat")
        nav_btn(get_label("profile"),  "profile",  "nav_profile")
        nav_btn(get_label("settings"), "settings", "nav_settings")

        st.markdown("---")

        # Thống kê câu hỏi đã dùng
        try:
            from history_manager import get_history_stats, clear_history
            stats = get_history_stats()
            if stats:
                st.markdown("**📊 Câu hỏi đã dùng:**")
                for key, count in stats.items():
                    subj, g = key.split("|")
                    st.caption(f"• {subj} / {g.split('(')[0].strip()}: {count} câu")
                if st.button("🗑️ Xóa lịch sử câu hỏi", use_container_width=True):
                    clear_history(); st.success("Đã xóa!"); st.rerun()
                st.markdown("---")
        except Exception:
            pass

        # Tiến độ làm bài
        if cur == "exam" and st.session_state.get("questions"):
            answered = sum(1 for v in st.session_state.answers.values()
                           if v not in (None, ""))
            total = len(st.session_state.questions)
            st.progress(answered / total if total else 0)
            st.caption(f"Tiến độ: {answered}/{total} câu")
            st.markdown("---")

        if st.button(get_label("logout"), use_container_width=True, key="sb_logout"):
            _do_logout()

        st.caption("v8.0 · Groq AI")


# ── Hàm gọi tất cả UI components ─────────────────────────
def render_all_ui():
    """
    Gọi hàm này ở đầu mỗi trang sau inject_css() để render
    navbar + popups + chat FAB cùng lúc.
    """
    render_navbar()
    render_popups()
    render_chat_fab()