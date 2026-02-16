# ============================================================
# ui.py — CSS styles & sidebar + Navbar sticky + Pop-ups
#          Responsive: Desktop sidebar | Mobile drawer + bottom nav
#
# FIX v2:
#   1. Xóa toàn bộ circular import (ui.py không import chính nó)
#   2. Navigation dùng st.query_params thay vì hidden buttons
#      → loại bỏ hoàn toàn nút lặp lại / nhãn kỹ thuật lộ ra ngoài
#   3. Login CSS Glassmorphism căn giữa hoàn hảo
# ============================================================
import streamlit as st

# ─── KHÔNG import từ ui.py ở đây ────────────────────────────
# (từ app.py hoặc các page khác mới được phép import ui)


# ════════════════════════════════════════════════════════════
# NAVIGATION HELPER — dùng query_params, KHÔNG dùng hidden btn
# ════════════════════════════════════════════════════════════
def _go(page: str):
    """Chuyển trang an toàn, không tạo hidden button."""
    st.session_state.page = page
    st.rerun()


def _sync_page_from_params():
    """
    Đọc ?page=xxx từ URL và đồng bộ vào session_state.
    Gọi một lần ở đầu app.py trước khi render.
    """
    p = st.query_params.get("page", None)
    if p and st.session_state.get("page") != p:
        st.session_state.page = p


# ════════════════════════════════════════════════════════════
# CSS TOÀN CỤC
# ════════════════════════════════════════════════════════════
CSS = """
<style>
/* ── Reset & typography ── */
*, *::before, *::after { box-sizing: border-box; }

/* ── Utility classes ── */
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

/* ════════════════════════════════════════
   ẨN SIDEBAR STREAMLIT MẶC ĐỊNH (mobile)
════════════════════════════════════════ */
@media (max-width: 768px) {
    section[data-testid="stSidebar"] { display: none !important; }
    .main .block-container {
        max-width: 100% !important;
        padding: 0 .75rem 5rem !important;
    }
}

/* ════════════════════════════════════════
   NAVBAR STICKY — Desktop
════════════════════════════════════════ */
.top-navbar {
    position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
    background: rgba(255,255,255,.95);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid #e0e7ff;
    box-shadow: 0 2px 12px rgba(26,115,232,.08);
    display: flex; align-items: center;
    justify-content: space-between;
    padding: 0 1.5rem; height: 52px; gap: 1rem;
}
.navbar-logo {
    display: flex; align-items: center; gap: .5rem;
    font-size: 1rem; font-weight: 800; color: #1a73e8;
    white-space: nowrap; cursor: pointer; text-decoration: none;
}
.navbar-logo .logo-icon { font-size: 1.3rem; }
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
    text-decoration: none; display: inline-block;
}
.navbar-btn:hover  { background: #f0f4ff; color: #1a73e8; }
.navbar-btn.active { background: #e8f0fe; color: #1a73e8; }
.navbar-right { display: flex; align-items: center; gap: .6rem; flex-shrink: 0; }
.navbar-avatar {
    width: 32px; height: 32px; border-radius: 50%;
    background: linear-gradient(135deg,#1a73e8,#0d47a1);
    display: flex; align-items: center; justify-content: center;
    font-size: .8rem; font-weight: 700; color: white; cursor: pointer;
}
.navbar-uname {
    font-size: .82rem; font-weight: 600; color: #1a1a2e;
    max-width: 100px; overflow: hidden;
    text-overflow: ellipsis; white-space: nowrap;
}
.navbar-notif {
    position: relative; cursor: pointer;
    width: 32px; height: 32px;
    display: flex; align-items: center; justify-content: center;
    border-radius: 50%; transition: background .15s;
}
.navbar-notif:hover { background: #f0f4ff; }
.notif-badge {
    position: absolute; top: 2px; right: 2px;
    width: 14px; height: 14px; border-radius: 50%;
    background: #d93025; color: white; font-size: .6rem; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
    border: 2px solid white;
}
@media (max-width: 768px) { .top-navbar { display: none !important; } }
.navbar-spacer { height: 60px; }
@media (max-width: 768px) { .navbar-spacer { height: 0; } }

/* ════════════════════════════════════════
   MOBILE HEADER
════════════════════════════════════════ */
.mobile-header {
    display: none;
    position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
    background: rgba(255,255,255,.97);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid #e0e7ff;
    box-shadow: 0 2px 8px rgba(26,115,232,.07);
    height: 52px; align-items: center;
    justify-content: space-between; padding: 0 1rem;
}
@media (max-width: 768px) { .mobile-header { display: flex; } }
.mh-logo {
    font-size: .95rem; font-weight: 800; color: #1a73e8;
    display: flex; align-items: center; gap: .35rem;
}
.mh-right { display: flex; align-items: center; gap: .5rem; }
.mh-avatar {
    width: 32px; height: 32px; border-radius: 50%;
    background: linear-gradient(135deg,#1a73e8,#0d47a1);
    display: flex; align-items: center; justify-content: center;
    font-size: .78rem; font-weight: 700; color: white;
}
.mh-notif {
    position: relative; width: 32px; height: 32px;
    display: flex; align-items: center; justify-content: center;
    border-radius: 50%; font-size: 1.1rem; cursor: pointer;
}
.mh-notif-badge {
    position: absolute; top: 1px; right: 1px;
    width: 14px; height: 14px; border-radius: 50%;
    background: #d93025; color: white; font-size: .6rem; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
    border: 2px solid white;
}
.mh-burger {
    width: 36px; height: 36px; border: none; background: none;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    gap: 5px; cursor: pointer; border-radius: 8px;
    transition: background .15s; padding: 0;
}
.mh-burger:hover { background: #f0f4ff; }
.mh-burger span {
    display: block; width: 20px; height: 2px;
    background: #1a73e8; border-radius: 2px; transition: all .25s;
}
.mobile-spacer { display: none; height: 52px; }
@media (max-width: 768px) { .mobile-spacer { display: block; } }

/* ════════════════════════════════════════
   DRAWER — Mobile sidebar
════════════════════════════════════════ */
.drawer-overlay {
    display: none; position: fixed; inset: 0;
    background: rgba(0,0,0,.45); z-index: 10000;
    backdrop-filter: blur(2px); opacity: 0; transition: opacity .3s;
}
.drawer-overlay.open { opacity: 1; }
.drawer-panel {
    display: none; position: fixed; top: 0; left: 0; bottom: 0;
    width: 280px; max-width: 82vw; z-index: 10001;
    background: #fff; box-shadow: 4px 0 24px rgba(0,0,0,.15);
    transform: translateX(-100%);
    transition: transform .3s cubic-bezier(.4,0,.2,1);
    overflow-y: auto; flex-direction: column;
}
.drawer-panel.open { transform: translateX(0); }
@media (max-width: 768px) {
    .drawer-overlay { display: block; }
    .drawer-panel   { display: flex; }
}
.drawer-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 1rem 1.1rem .75rem; border-bottom: 1px solid #e0e7ff;
    position: sticky; top: 0; background: #fff; z-index: 1;
}
.drawer-logo {
    font-size: .95rem; font-weight: 800; color: #1a73e8;
    display: flex; align-items: center; gap: .4rem;
}
.drawer-close {
    width: 30px; height: 30px; border: none;
    background: #f3f4f6; border-radius: 50%;
    font-size: 1rem; cursor: pointer; color: #555;
    display: flex; align-items: center; justify-content: center;
    transition: background .15s;
}
.drawer-close:hover { background: #e0e7ff; color: #1a73e8; }
.drawer-user {
    display: flex; align-items: center; gap: .75rem;
    padding: .85rem 1.1rem;
    background: linear-gradient(135deg,#f0f4ff,#e8f0fe);
    margin: .6rem .75rem; border-radius: 12px;
}
.drawer-avatar {
    width: 42px; height: 42px; border-radius: 50%;
    background: linear-gradient(135deg,#1a73e8,#0d47a1);
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; font-weight: 700; color: white; flex-shrink: 0;
}
.drawer-uname { font-weight: 700; font-size: .9rem; color: #1a1a2e; }
.drawer-usub  { font-size: .72rem; color: #888; margin-top: .1rem; }
.drawer-nav   { padding: .5rem .75rem; flex: 1; }
.drawer-nav-item {
    display: flex; align-items: center; gap: .75rem;
    padding: .7rem .9rem; border-radius: 10px;
    font-size: .9rem; font-weight: 600; color: #444;
    cursor: pointer; transition: all .18s; margin-bottom: .25rem;
    border: none; background: none; width: 100%; text-align: left;
}
.drawer-nav-item:hover  { background: #f0f4ff; color: #1a73e8; }
.drawer-nav-item.active { background: #e8f0fe; color: #1a73e8; }
.drawer-nav-icon { font-size: 1.15rem; width: 24px; text-align: center; }
.drawer-divider  { height: 1px; background: #e0e7ff; margin: .5rem .75rem; }
.drawer-footer {
    padding: .75rem; border-top: 1px solid #f0f4ff;
    position: sticky; bottom: 0; background: #fff;
}
.drawer-logout {
    display: flex; align-items: center; gap: .75rem;
    padding: .65rem .9rem; border-radius: 10px;
    font-size: .88rem; font-weight: 600; color: #d93025;
    cursor: pointer; transition: background .18s;
    border: none; background: none; width: 100%;
}
.drawer-logout:hover { background: #fce8e6; }
.drawer-version { text-align: center; color: #bbb; font-size: .68rem; margin-top: .4rem; }

/* ════════════════════════════════════════
   BOTTOM NAV — Mobile
════════════════════════════════════════ */
.bottom-nav {
    display: none; position: fixed; bottom: 0; left: 0; right: 0;
    z-index: 9998; background: rgba(255,255,255,.97);
    backdrop-filter: blur(12px);
    border-top: 1px solid #e0e7ff;
    box-shadow: 0 -2px 12px rgba(26,115,232,.08);
    height: 60px; align-items: center; justify-content: space-around;
    padding: 0 .25rem;
}
@media (max-width: 768px) { .bottom-nav { display: flex; } }
.bn-item {
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    gap: 2px; flex: 1; padding: .35rem 0;
    border: none; background: none;
    cursor: pointer; border-radius: 10px; transition: background .15s;
}
.bn-item:hover { background: #f0f4ff; }
.bn-icon  { font-size: 1.35rem; line-height: 1; }
.bn-label { font-size: .6rem; font-weight: 600; color: #888; white-space: nowrap; }
.bn-item.active .bn-icon  { filter: drop-shadow(0 0 4px rgba(26,115,232,.4)); }
.bn-item.active .bn-label { color: #1a73e8; font-weight: 700; }
.bottom-nav-spacer { display: none; height: 64px; }
@media (max-width: 768px) { .bottom-nav-spacer { display: block; } }

/* ════════════════════════════════════════
   TOAST POP-UP
════════════════════════════════════════ */
.popup-toast {
    position: fixed; bottom: 1.5rem; right: 1.5rem; z-index: 9997;
    display: flex; flex-direction: column; gap: .6rem; max-width: 320px;
}
@media (max-width: 768px) {
    .popup-toast { left:.75rem; right:.75rem; bottom:70px; max-width:100%; }
}
.toast {
    background: white; border-radius: 12px; padding: .75rem 1rem;
    box-shadow: 0 4px 20px rgba(0,0,0,.12); border-left: 4px solid #1a73e8;
    display: flex; align-items: flex-start; gap: .6rem;
    animation: slideIn .3s ease; font-size: .85rem; line-height: 1.4;
}
.toast.toast-success { border-color: #1e8e3e; }
.toast.toast-warning { border-color: #f4a300; }
.toast.toast-error   { border-color: #d93025; }
.toast-icon    { font-size: 1.2rem; flex-shrink: 0; margin-top: .05rem; }
.toast-content { flex: 1; }
.toast-title   { font-weight: 700; color: #1a1a2e; margin-bottom: .15rem; }
.toast-msg     { color: #555; font-size: .8rem; }

/* ════════════════════════════════════════
   LOGIN PAGE — Glassmorphism
════════════════════════════════════════ */
.login-bg {
    position: fixed; inset: 0; z-index: 0;
    background: linear-gradient(135deg, #1a73e8 0%, #0d47a1 40%, #7c3aed 100%);
    overflow: hidden;
}
.login-bg::before {
    content: '';
    position: absolute; width: 600px; height: 600px;
    background: radial-gradient(circle, rgba(255,255,255,.15) 0%, transparent 70%);
    top: -150px; right: -100px; border-radius: 50%;
}
.login-bg::after {
    content: '';
    position: absolute; width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(124,58,237,.3) 0%, transparent 70%);
    bottom: -100px; left: -80px; border-radius: 50%;
}
.login-wrapper {
    position: relative; z-index: 1;
    min-height: 100vh;
    display: flex; align-items: center; justify-content: center;
    padding: 1.5rem;
}
.login-card {
    width: 100%; max-width: 420px;
    background: rgba(255,255,255,.12);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,.25);
    border-radius: 24px;
    padding: 2.5rem 2rem;
    box-shadow: 0 24px 64px rgba(0,0,0,.25), inset 0 1px 0 rgba(255,255,255,.2);
}
.login-logo {
    text-align: center; margin-bottom: 1.5rem;
}
.login-logo .logo-emoji { font-size: 3rem; display: block; }
.login-logo h1 {
    font-size: 1.5rem; font-weight: 800;
    color: #fff; margin: .4rem 0 .2rem;
}
.login-logo p {
    font-size: .85rem; color: rgba(255,255,255,.75); margin: 0;
}
/* Override Streamlit input trong login card */
.login-card .stTextInput input {
    background: rgba(255,255,255,.15) !important;
    border: 1px solid rgba(255,255,255,.3) !important;
    border-radius: 10px !important;
    color: #fff !important;
    backdrop-filter: blur(8px);
}
.login-card .stTextInput input::placeholder { color: rgba(255,255,255,.6) !important; }
.login-card .stTextInput input:focus {
    border-color: rgba(255,255,255,.7) !important;
    box-shadow: 0 0 0 3px rgba(255,255,255,.15) !important;
    background: rgba(255,255,255,.2) !important;
}
.login-card label { color: rgba(255,255,255,.9) !important; font-weight: 600 !important; }
.login-card .stButton > button {
    background: linear-gradient(135deg,#fff 0%,#e8f0fe 100%) !important;
    color: #1a73e8 !important;
    border: none !important;
    font-weight: 700 !important;
    font-size: .95rem !important;
    padding: .65rem 1rem !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 16px rgba(0,0,0,.15) !important;
    transition: transform .15s, box-shadow .15s !important;
}
.login-card .stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(0,0,0,.2) !important;
}
/* Ẩn thanh trắng thừa phía trên (header Streamlit mặc định) */
[data-testid="stHeader"] { display: none !important; }
header[data-testid="stHeader"] { display: none !important; }
#MainMenu { display: none !important; }
footer    { display: none !important; }

/* ════════════════════════════════════════
   CHAT FAB
════════════════════════════════════════ */
.chat-fab {
    position: fixed; bottom: 1.5rem; left: 1.5rem; z-index: 9996;
    width: 48px; height: 48px;
    background: linear-gradient(135deg,#1a73e8,#7c3aed);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem; cursor: pointer;
    box-shadow: 0 4px 16px rgba(26,115,232,.35);
    transition: transform .15s, box-shadow .15s; border: none;
}
.chat-fab:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 20px rgba(26,115,232,.45);
}
.chat-fab-label {
    background: #1a1a2e; color: white; padding: .3rem .7rem;
    border-radius: 6px; font-size: .78rem; font-weight: 600;
    white-space: nowrap; box-shadow: 0 2px 8px rgba(0,0,0,.15);
}
@media (max-width: 768px) {
    .chat-fab { bottom: 68px; left: 1rem; width: 42px; height: 42px; font-size: 1.1rem; }
    .chat-fab-label { display: none; }
}

@keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to   { transform: translateX(0);    opacity: 1; }
}

/* ════════════════════════════════════════
   RESPONSIVE
════════════════════════════════════════ */
@media (max-width: 768px) {
    .main-title { font-size: 1.6rem !important; }
    .sub-title  { font-size: .88rem !important; }
    .q-box      { padding: .75rem .9rem !important; }
    .stButton > button { padding: .55rem .75rem !important; font-size: .88rem !important; }
    .timer-box  { font-size: 1.05rem !important; }
}

body.drawer-open { overflow: hidden; }
</style>

<script>
/* ── Drawer logic ── */
(function(){
    function openDrawer(){
        document.getElementById('drawerOverlay').classList.add('open');
        document.getElementById('drawerPanel').classList.add('open');
        document.body.classList.add('drawer-open');
    }
    function closeDrawer(){
        document.getElementById('drawerOverlay').classList.remove('open');
        document.getElementById('drawerPanel').classList.remove('open');
        document.body.classList.remove('drawer-open');
    }
    window._openDrawer  = openDrawer;
    window._closeDrawer = closeDrawer;

    document.addEventListener('click', function(e){
        var ov = document.getElementById('drawerOverlay');
        if(ov && e.target === ov) closeDrawer();
    });

    /* Swipe-to-close drawer */
    var sx = 0;
    document.addEventListener('touchstart', function(e){ sx = e.touches[0].clientX; }, {passive:true});
    document.addEventListener('touchend', function(e){
        var panel = document.getElementById('drawerPanel');
        if(panel && panel.classList.contains('open') && sx - e.changedTouches[0].clientX > 60)
            closeDrawer();
    }, {passive:true});
})();

/* ── Navigation via query_params ── */
window._navTo = function(page){
    var url = new URL(window.location.href);
    url.searchParams.set('page', page);
    window.location.href = url.toString();
};
</script>
"""


# ════════════════════════════════════════════════════════════
# inject_css
# ════════════════════════════════════════════════════════════
def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)
    try:
        from settings_page import apply_settings_css
        apply_settings_css()
    except Exception:
        pass


# ════════════════════════════════════════════════════════════
# NAVBAR — Desktop (pure HTML, navigate bằng window._navTo)
# ════════════════════════════════════════════════════════════
def render_navbar():
    uname   = st.session_state.get("username", "")
    cur     = st.session_state.get("page", "home")
    remind  = st.session_state.get("remind_assignments", [])
    notif_n = len(remind)
    initials = "".join(w[0].upper() for w in uname.split()[:2]) if uname else "?"

    menu_items = [
        ("🏠 Trang chủ", "home"),
        ("🚀 Làm bài",   "select"),
        ("📋 Lịch sử",   "history"),
        ("💬 Chat AI",   "chatbox"),
        ("👤 Hồ sơ",     "profile"),
        ("⚙️ Cài đặt",   "settings"),
    ]

    notif_html = (
        f'<div class="navbar-notif">🔔<div class="notif-badge">{notif_n}</div></div>'
        if notif_n > 0 else ""
    )

    menu_html = "".join(
        f'<span class="navbar-btn {"active" if cur == page else ""}" '
        f'onclick="window._navTo(\'{page}\')">{label}</span>'
        for label, page in menu_items
    )

    st.markdown(f"""
    <!-- Desktop navbar -->
    <div class="top-navbar">
        <div class="navbar-logo" onclick="window._navTo('home')">
            <span class="logo-icon">🎓</span>AI Exam Generator
        </div>
        <div class="navbar-menu">{menu_html}</div>
        <div class="navbar-right">
            {notif_html}
            <div class="navbar-avatar">{initials}</div>
            <span class="navbar-uname">{uname}</span>
        </div>
    </div>
    <div class="navbar-spacer"></div>

    <!-- Mobile header -->
    <div class="mobile-header">
        <button class="mh-burger" onclick="window._openDrawer()" aria-label="Menu">
            <span></span><span></span><span></span>
        </button>
        <div class="mh-logo">🎓 AI Exam</div>
        <div class="mh-right">
            {'<div class="mh-notif">🔔<div class="mh-notif-badge">' + str(notif_n) + '</div></div>' if notif_n > 0 else ''}
            <div class="mh-avatar">{initials}</div>
        </div>
    </div>
    <div class="mobile-spacer"></div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# DRAWER — Mobile (navigate bằng window._navTo, KHÔNG dùng hidden button)
# ════════════════════════════════════════════════════════════
def render_drawer():
    uname  = st.session_state.get("username", "")
    email  = st.session_state.get("email", "")
    grade  = st.session_state.get("grade", "")
    role   = st.session_state.get("role", "student")
    cur    = st.session_state.get("page", "home")
    initials = "".join(w[0].upper() for w in uname.split()[:2]) or "?"
    sub_label = email or grade or ("Học sinh" if role == "student" else "Giáo viên")

    nav_items = [
        ("🏠", "Trang chủ", "home"),
        ("🚀", "Làm bài",   "select"),
        ("📋", "Lịch sử",   "history"),
        ("💬", "Chat AI",   "chatbox"),
        ("👤", "Hồ sơ",     "profile"),
        ("⚙️", "Cài đặt",   "settings"),
    ]
    if role == "student":
        nav_items.insert(2, ("📚", "Khóa học", "courses"))

    # Mỗi item gọi _navTo thay vì click hidden button
    nav_html = "".join(
        f'<button class="drawer-nav-item {"active" if cur == page else ""}" '
        f'onclick="window._closeDrawer(); window._navTo(\'{page}\')">'
        f'<span class="drawer-nav-icon">{icon}</span>{label}'
        f'</button>'
        for icon, label, page in nav_items
    )

    st.markdown(f"""
    <div class="drawer-overlay" id="drawerOverlay"></div>
    <div class="drawer-panel" id="drawerPanel">
        <div class="drawer-header">
            <div class="drawer-logo">🎓 AI Exam Generator</div>
            <button class="drawer-close" onclick="window._closeDrawer()">✕</button>
        </div>
        <div class="drawer-user">
            <div class="drawer-avatar">{initials}</div>
            <div>
                <div class="drawer-uname">{uname}</div>
                <div class="drawer-usub">{sub_label}</div>
            </div>
        </div>
        <div class="drawer-nav">{nav_html}</div>
        <div class="drawer-footer">
            <button class="drawer-logout" onclick="window._navTo('logout')">
                🚪 Đăng xuất
            </button>
            <div class="drawer-version">v8.0 · Groq AI</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# BOTTOM NAV — Mobile (navigate bằng window._navTo)
# ════════════════════════════════════════════════════════════
def render_bottom_nav():
    cur  = st.session_state.get("page", "home")
    role = st.session_state.get("role", "student")

    bn_items = [
        ("🏠", "Trang chủ", "home"),
        ("🚀", "Làm bài",   "select"),
        ("📚", "Khóa học",  "courses"),
        ("💬", "Chat",      "chatbox"),
        ("👤", "Hồ sơ",     "profile"),
    ]
    if role != "student":
        bn_items[2] = ("📋", "Lịch sử", "history")

    items_html = "".join(
        f'<button class="bn-item {"active" if cur == page else ""}" '
        f'onclick="window._navTo(\'{page}\')">'
        f'<span class="bn-icon">{icon}</span>'
        f'<span class="bn-label">{label}</span>'
        f'</button>'
        for icon, label, page in bn_items
    )

    st.markdown(f"""
    <div class="bottom-nav">{items_html}</div>
    <div class="bottom-nav-spacer"></div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# TOAST POP-UPS
# ════════════════════════════════════════════════════════════
def render_popups():
    toasts = []
    page   = st.session_state.get("page", "")

    remind = st.session_state.get("remind_assignments", [])
    if remind and page == "home":
        for a in remind[:2]:
            dl = f" — hạn {a['deadline']}" if a.get("deadline") else ""
            toasts.append(("toast-warning","📢","Đề mới từ giáo viên",f"{a['title']}{dl}"))

    if page == "result":
        score = st.session_state.get("score", 0)
        total = len(st.session_state.get("questions", [1]))
        pct   = round(score / total * 100) if total else 0
        if pct == 100:
            toasts.append(("toast-success","🎉","Xuất sắc! Điểm tuyệt đối!","Bạn trả lời đúng tất cả!"))
        elif pct >= 80:
            toasts.append(("toast-success","🥇",f"Kết quả tốt! {pct}%","Tiếp tục phát huy nhé!"))

    if page == "exam" and st.session_state.get("confirm_submit"):
        qs = st.session_state.get("questions", [])
        unanswered = [i+1 for i in range(len(qs))
                      if st.session_state.get("answers", {}).get(i) is None]
        if unanswered:
            toasts.append(("toast-error","⚠️",
                f"{len(unanswered)} câu chưa làm",
                "Câu " + ", ".join(str(n) for n in unanswered[:5])
                + ("..." if len(unanswered) > 5 else "")))

    if not toasts:
        return

    items_html = "".join(
        f'<div class="toast {cls}"><div class="toast-icon">{icon}</div>'
        f'<div class="toast-content"><div class="toast-title">{title}</div>'
        f'<div class="toast-msg">{msg}</div></div></div>'
        for cls, icon, title, msg in toasts
    )
    st.markdown(f'<div class="popup-toast">{items_html}</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# CHAT FAB — navigate bằng window._navTo
# ════════════════════════════════════════════════════════════
def render_chat_fab():
    if st.session_state.get("page", "") in ("chatbox", "exam"):
        return
    st.markdown("""
    <div style="position:fixed;bottom:1.5rem;left:1.5rem;z-index:9996;
         display:inline-flex;align-items:center;gap:.6rem">
        <button class="chat-fab" onclick="window._navTo('chatbox')"
                title="Chat hỗ trợ AI">💬</button>
        <div class="chat-fab-label">Cần hỗ trợ?</div>
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# LOGIN PAGE — Glassmorphism layout helper
# Gọi ở đầu login_page.py để wrap form vào card đẹp
# ════════════════════════════════════════════════════════════
def render_login_wrapper_open():
    """Mở login wrapper + card — gọi trước khi render form."""
    st.markdown("""
    <div class="login-bg"></div>
    <div class="login-wrapper">
        <div class="login-card">
            <div class="login-logo">
                <span class="logo-emoji">🎓</span>
                <h1>AI Exam Generator</h1>
                <p>Hệ thống thi trắc nghiệm thông minh</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    # Trick: dùng CSS để override container Streamlit thành overlay lên login-card
    st.markdown("""
    <style>
    /* Đẩy toàn bộ main content lên trên login-card */
    .main .block-container {
        position: relative; z-index: 2;
        max-width: 420px !important;
        margin: 0 auto !important;
        padding: 0 !important;
        /* Căn giữa theo viewport */
        margin-top: max(5vh, 52px) !important;
    }
    /* Ẩn khoảng trắng padding đầu trang */
    .main .block-container > div:first-child { padding-top: 0 !important; }
    div[data-testid="stVerticalBlock"] { gap: .6rem !important; }
    </style>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# LOGOUT — xử lý page=logout từ query_params
# ════════════════════════════════════════════════════════════
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
            "questions":[],"answers":{},
            "remind_assignments":[],"confirm_submit":False
        })
    st.rerun()


# ════════════════════════════════════════════════════════════
# SIDEBAR — Desktop (dùng st.sidebar, KHÔNG bị lặp ra ngoài)
# ════════════════════════════════════════════════════════════
def render_sidebar():
    # Import cục bộ để tránh circular import
    try:
        from settings_page import get_label
    except Exception:
        def get_label(k):
            return {"home":"🏠 Trang chủ","start":"🚀 Làm bài",
                    "history":"📋 Lịch sử","chatbox":"💬 Chat AI",
                    "profile":"👤 Hồ sơ","settings":"⚙️ Cài đặt",
                    "logout":"🚪 Đăng xuất"}.get(k, k)

    with st.sidebar:
        uname = st.session_state.get("username", "")
        grade = st.session_state.get("grade", "")
        email = st.session_state.get("email", "")
        role  = st.session_state.get("role", "student")

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
                f'</div></div>', unsafe_allow_html=True)
        st.markdown("---")

        if st.session_state.get("page") == "chatbox":
            if st.button("✏️ Hội thoại mới", use_container_width=True,
                         type="primary", key="btn_new_ui_sidebar"):
                try:
                    from chatbox_page import _new_conversation
                    _new_conversation()
                except Exception:
                    pass
                st.rerun()
            st.markdown("---")

        cur = st.session_state.get("page", "home")

        def nav_btn(label, page, key):
            if st.button(label, key=key, use_container_width=True,
                         type="primary" if cur == page else "secondary"):
                _go(page)

        nav_btn(get_label("home"),    "home",     "nav_home")
        nav_btn(get_label("start"),   "select",   "nav_select")
        if role == "student":
            nav_btn("📚 Khóa học",    "courses",  "nav_courses")
        nav_btn(get_label("history"), "history",  "nav_history")
        nav_btn(get_label("chatbox"), "chatbox",  "nav_chat")
        nav_btn(get_label("profile"), "profile",  "nav_profile")
        nav_btn(get_label("settings"),"settings", "nav_settings")

        st.markdown("---")

        try:
            from history_manager import get_history_stats, clear_history
            stats = get_history_stats()
            if stats:
                st.markdown("**📊 Câu hỏi đã dùng:**")
                for key, count in stats.items():
                    subj, g = key.split("|")
                    st.caption(f"• {subj} / {g.split('(')[0].strip()}: {count} câu")
                if st.button("🗑️ Xóa lịch sử câu hỏi", use_container_width=True,
                             key="clear_hist_btn"):
                    clear_history()
                    st.success("Đã xóa!")
                    st.rerun()
                st.markdown("---")
        except Exception:
            pass

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


# ════════════════════════════════════════════════════════════
# RENDER ALL — gọi sau inject_css() ở đầu mỗi trang
# ════════════════════════════════════════════════════════════
def render_all_ui():
    """Gọi sau inject_css() ở đầu mỗi trang (trừ login)."""
    # Xử lý logout từ query_params (do drawer/bottom nav gọi _navTo('logout'))
    if st.query_params.get("page") == "logout":
        st.query_params.clear()
        _do_logout()
        return

    # Đồng bộ page từ URL
    _sync_page_from_params()

    render_navbar()
    render_drawer()
    render_bottom_nav()
    render_popups()
    render_chat_fab()
