# ============================================================
# ui.py — CSS styles & sidebar + Navbar sticky + Pop-ups
#          Responsive: Desktop sidebar | Mobile drawer + bottom nav
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
.source-badge { font-size:.72rem; padding:.2rem .6rem; border-radius:99px;
                font-weight:600; display:inline-block; margin-bottom:.4rem; }
.badge-ai    { background:#e8f0fe; color:#1a73e8; }
.badge-local { background:#fce8e6; color:#d93025; }
.level-tag   { display:inline-block; padding:.15rem .5rem; border-radius:4px;
               font-size:.75rem; font-weight:700; margin-left:.4rem; }
.tag-primary { background:#e8f0fe; color:#1565c0; }
.tag-middle  { background:#e8f5e9; color:#2e7d32; }
.tag-high    { background:#fff3e0; color:#e65100; }
.tag-uni     { background:#fce4ec; color:#880e4f; }

/* ════════════════════════════════
   DESKTOP NAVBAR (>768px)
════════════════════════════════ */
.top-navbar {
    position:fixed; top:0; left:0; right:0; z-index:9999;
    background:#fff; border-bottom:1px solid #e0e7ff;
    box-shadow:0 2px 12px rgba(26,115,232,.08);
    display:flex; align-items:center; justify-content:space-between;
    padding:0 1.5rem; height:52px; gap:1rem;
}
.navbar-logo { display:flex; align-items:center; gap:.5rem;
    font-size:1rem; font-weight:800; color:#1a73e8; white-space:nowrap; }
.navbar-logo .logo-icon { font-size:1.3rem; }
.navbar-menu { display:flex; align-items:center; gap:.25rem; flex:1; justify-content:center; }
.navbar-btn  { background:none; border:none; padding:.35rem .75rem; border-radius:6px;
    font-size:.82rem; font-weight:600; color:#444; cursor:pointer; white-space:nowrap;
    transition:background .15s,color .15s; }
.navbar-btn:hover  { background:#f0f4ff; color:#1a73e8; }
.navbar-btn.active { background:#e8f0fe; color:#1a73e8; }
.navbar-right { display:flex; align-items:center; gap:.6rem; flex-shrink:0; }
.navbar-avatar { width:32px; height:32px; border-radius:50%;
    background:linear-gradient(135deg,#1a73e8,#0d47a1);
    display:flex; align-items:center; justify-content:center;
    font-size:.8rem; font-weight:700; color:white; }
.navbar-uname { font-size:.82rem; font-weight:600; color:#1a1a2e;
    max-width:100px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.navbar-notif { position:relative; width:32px; height:32px;
    display:flex; align-items:center; justify-content:center;
    border-radius:50%; cursor:pointer; transition:background .15s; }
.navbar-notif:hover { background:#f0f4ff; }
.notif-badge { position:absolute; top:2px; right:2px; width:14px; height:14px;
    border-radius:50%; background:#d93025; color:white; font-size:.6rem;
    font-weight:700; display:flex; align-items:center; justify-content:center;
    border:2px solid white; }
.navbar-spacer { height:60px; }

/* ════════════════════════════════
   MOBILE HEADER (≤768px)
════════════════════════════════ */
.mobile-header {
    display:none;
    position:fixed; top:0; left:0; right:0; z-index:9999;
    background:#fff; border-bottom:1px solid #e0e7ff;
    box-shadow:0 2px 8px rgba(26,115,232,.07);
    height:52px; align-items:center; justify-content:space-between; padding:0 1rem;
}
.mh-logo  { font-size:.95rem; font-weight:800; color:#1a73e8;
    display:flex; align-items:center; gap:.35rem; }
.mh-right { display:flex; align-items:center; gap:.5rem; }
.mh-avatar { width:32px; height:32px; border-radius:50%;
    background:linear-gradient(135deg,#1a73e8,#0d47a1);
    display:flex; align-items:center; justify-content:center;
    font-size:.78rem; font-weight:700; color:white; }
.mh-notif { position:relative; width:32px; height:32px;
    display:flex; align-items:center; justify-content:center;
    border-radius:50%; font-size:1.1rem; cursor:pointer; }
.mh-notif-badge { position:absolute; top:1px; right:1px; width:14px; height:14px;
    border-radius:50%; background:#d93025; color:white; font-size:.6rem;
    font-weight:700; display:flex; align-items:center; justify-content:center;
    border:2px solid white; }
.mh-burger { width:36px; height:36px; border:none; background:none;
    display:flex; flex-direction:column; align-items:center; justify-content:center;
    gap:5px; cursor:pointer; border-radius:8px; transition:background .15s; padding:0; }
.mh-burger:hover { background:#f0f4ff; }
.mh-burger span { display:block; width:20px; height:2px; background:#1a73e8;
    border-radius:2px; transition:all .25s; }
.mobile-spacer { display:none; height:52px; }

/* ════════════════════════════════
   DRAWER OVERLAY + PANEL
════════════════════════════════ */
.drawer-overlay {
    position:fixed; inset:0; background:rgba(0,0,0,.45); z-index:10000;
    backdrop-filter:blur(2px); opacity:0; transition:opacity .3s;
    pointer-events:none;
}
.drawer-overlay.open { opacity:1; pointer-events:all; }
.drawer-panel {
    position:fixed; top:0; left:0; bottom:0; width:280px; max-width:82vw;
    z-index:10001; background:#fff;
    box-shadow:4px 0 24px rgba(0,0,0,.15);
    transform:translateX(-100%); transition:transform .3s cubic-bezier(.4,0,.2,1);
    overflow-y:auto; display:flex; flex-direction:column;
}
.drawer-panel.open { transform:translateX(0); }
.drawer-header { display:flex; align-items:center; justify-content:space-between;
    padding:1rem 1.1rem .75rem; border-bottom:1px solid #e0e7ff;
    position:sticky; top:0; background:#fff; z-index:1; }
.drawer-logo { font-size:.95rem; font-weight:800; color:#1a73e8;
    display:flex; align-items:center; gap:.4rem; }
.drawer-close { width:30px; height:30px; border:none; background:#f3f4f6;
    border-radius:50%; font-size:1rem; cursor:pointer; color:#555;
    display:flex; align-items:center; justify-content:center; transition:background .15s; }
.drawer-close:hover { background:#e0e7ff; color:#1a73e8; }
.drawer-user { display:flex; align-items:center; gap:.75rem; padding:.85rem 1.1rem;
    background:linear-gradient(135deg,#f0f4ff,#e8f0fe); margin:.6rem .75rem; border-radius:12px; }
.drawer-avatar { width:42px; height:42px; border-radius:50%;
    background:linear-gradient(135deg,#1a73e8,#0d47a1);
    display:flex; align-items:center; justify-content:center;
    font-size:1rem; font-weight:700; color:white; flex-shrink:0; }
.drawer-uname { font-weight:700; font-size:.9rem; color:#1a1a2e; }
.drawer-usub  { font-size:.72rem; color:#888; margin-top:.1rem; }
.drawer-nav   { padding:.5rem .75rem; flex:1; }
.drawer-nav-item { display:flex; align-items:center; gap:.75rem;
    padding:.7rem .9rem; border-radius:10px; font-size:.9rem; font-weight:600; color:#444;
    cursor:pointer; transition:all .18s; margin-bottom:.25rem;
    border:none; background:none; width:100%; text-align:left; }
.drawer-nav-item:hover  { background:#f0f4ff; color:#1a73e8; }
.drawer-nav-item.active { background:#e8f0fe; color:#1a73e8; }
.drawer-nav-icon { font-size:1.15rem; width:24px; text-align:center; }
.drawer-divider  { height:1px; background:#e0e7ff; margin:.5rem .75rem; }
.drawer-footer   { padding:.75rem; border-top:1px solid #f0f4ff;
    position:sticky; bottom:0; background:#fff; }
.drawer-logout { display:flex; align-items:center; gap:.75rem; padding:.65rem .9rem;
    border-radius:10px; font-size:.88rem; font-weight:600; color:#d93025;
    cursor:pointer; transition:background .18s; border:none; background:none; width:100%; }
.drawer-logout:hover { background:#fce8e6; }
.drawer-version { text-align:center; color:#bbb; font-size:.68rem; margin-top:.4rem; }

/* ════════════════════════════════
   BOTTOM NAV (mobile only)
════════════════════════════════ */
.bottom-nav { display:none; position:fixed; bottom:0; left:0; right:0; z-index:9998;
    background:#fff; border-top:1px solid #e0e7ff;
    box-shadow:0 -2px 12px rgba(26,115,232,.08);
    height:60px; align-items:center; justify-content:space-around; padding:0 .25rem; }
.bn-item { display:flex; flex-direction:column; align-items:center; justify-content:center;
    gap:2px; flex:1; padding:.35rem 0; border:none; background:none;
    cursor:pointer; border-radius:10px; transition:background .15s; min-width:0; }
.bn-item:hover { background:#f0f4ff; }
.bn-icon  { font-size:1.35rem; line-height:1; }
.bn-label { font-size:.6rem; font-weight:600; color:#888; white-space:nowrap; }
.bn-item.active .bn-label { color:#1a73e8; font-weight:700; }
.bottom-nav-spacer { display:none; height:64px; }

/* ════════════════════════════════
   TOAST
════════════════════════════════ */
.popup-toast { position:fixed; bottom:1.5rem; right:1.5rem; z-index:9997;
    display:flex; flex-direction:column; gap:.6rem; max-width:320px; }
.toast { background:white; border-radius:12px; padding:.75rem 1rem;
    box-shadow:0 4px 20px rgba(0,0,0,.12); border-left:4px solid #1a73e8;
    display:flex; align-items:flex-start; gap:.6rem;
    animation:slideIn .3s ease; font-size:.85rem; line-height:1.4; }
.toast.toast-success { border-color:#1e8e3e; }
.toast.toast-warning { border-color:#f4a300; }
.toast.toast-error   { border-color:#d93025; }
.toast-icon    { font-size:1.2rem; flex-shrink:0; margin-top:.05rem; }
.toast-content { flex:1; }
.toast-title   { font-weight:700; color:#1a1a2e; margin-bottom:.15rem; }
.toast-msg     { color:#555; font-size:.8rem; }

/* ════════════════════════════════
   CHAT FAB
════════════════════════════════ */
.chat-fab { position:fixed; bottom:1.5rem; left:1.5rem; z-index:9996;
    width:48px; height:48px; background:linear-gradient(135deg,#1a73e8,#7c3aed);
    border-radius:50%; display:flex; align-items:center; justify-content:center;
    font-size:1.3rem; cursor:pointer; box-shadow:0 4px 16px rgba(26,115,232,.35);
    transition:transform .15s,box-shadow .15s; border:none; }
.chat-fab:hover { transform:scale(1.1); box-shadow:0 6px 20px rgba(26,115,232,.45); }

@keyframes slideIn {
    from { transform:translateX(100%); opacity:0; }
    to   { transform:translateX(0);    opacity:1; }
}

/* ════════════════════════════════
   MEDIA QUERIES
════════════════════════════════ */
@media (max-width:768px) {
    /* Ẩn tất cả liên quan đến Streamlit sidebar */
    section[data-testid="stSidebar"]             { display:none !important; }
    [data-testid="stSidebarCollapsedControl"]     { display:none !important; }
    button[data-testid="collapsedControl"]        { display:none !important; }
    [data-testid="stSidebarNavItems"]             { display:none !important; }

    /* Reset main block */
    [data-testid="stAppViewContainer"] > section.main { margin-left:0 !important; }
    .main .block-container,
    [data-testid="stMainBlockContainer"] {
        max-width:100% !important; width:100% !important;
        padding:0 .75rem 5rem !important; margin-left:0 !important;
    }

    /* Mobile header & spacer */
    .mobile-header  { display:flex !important; }
    .mobile-spacer  { display:block !important; }

    /* Drawer & bottom nav */
    .bottom-nav         { display:flex !important; }
    .bottom-nav-spacer  { display:block !important; }

    /* Toast */
    .popup-toast { left:.75rem; right:.75rem; bottom:68px; max-width:100%; }

    /* FAB lên trên bottom nav */
    .chat-fab { bottom:68px; left:1rem; width:42px; height:42px; font-size:1.1rem; }

    /* Content */
    .main-title { font-size:1.6rem !important; }
    .sub-title  { font-size:.88rem !important; }
    .timer-box  { font-size:1.05rem !important; }
    .stButton > button { font-size:.88rem !important; }
}

@media (min-width:769px) {
    /* Ẩn mobile-only elements trên desktop */
    .mobile-header      { display:none !important; }
    .mobile-spacer      { display:none !important; }
    .drawer-overlay,
    .drawer-panel       { display:none !important; }
    .bottom-nav         { display:none !important; }
    .bottom-nav-spacer  { display:none !important; }
    /* Navbar desktop */
    .top-navbar         { display:flex !important; }
    .navbar-spacer      { display:block !important; }
}

body.drawer-open { overflow:hidden; }
</style>

<script>
/* ── Drawer open/close ── */
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

    /* Click overlay để đóng */
    document.addEventListener('click', function(e){
        var ov = document.getElementById('drawerOverlay');
        if(ov && e.target === ov) closeDrawer();
    });

    /* Swipe trái để đóng drawer */
    var startX = 0;
    document.addEventListener('touchstart', function(e){ startX = e.touches[0].clientX; }, {passive:true});
    document.addEventListener('touchend', function(e){
        var panel = document.getElementById('drawerPanel');
        if(panel && panel.classList.contains('open') && (startX - e.changedTouches[0].clientX) > 60)
            closeDrawer();
    }, {passive:true});

    /* Ẩn sidebar Streamlit bằng JS (backup cho CSS) */
    function hideST(){
        var sels = [
            'section[data-testid="stSidebar"]',
            '[data-testid="stSidebarCollapsedControl"]',
            'button[data-testid="collapsedControl"]'
        ];
        if(window.innerWidth <= 768){
            sels.forEach(function(s){
                document.querySelectorAll(s).forEach(function(el){
                    el.style.setProperty('display','none','important');
                });
            });
        }
    }
    hideST();
    new MutationObserver(hideST).observe(document.body,{childList:true,subtree:true});
    window.addEventListener('resize', hideST);
})();
</script>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)
    try:
        from settings_page import apply_settings_css
        apply_settings_css()
    except Exception:
        pass


# ─────────────────────────────────────────────────────────
# NAVBAR (Desktop only — mobile dùng mobile-header)
# ─────────────────────────────────────────────────────────
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
        f'<span class="navbar-btn {"active" if cur == p else ""}">{lbl}</span>'
        for lbl, p in menu_items
    )
    st.markdown(f"""
    <div class="top-navbar">
        <div class="navbar-logo"><span class="logo-icon">🎓</span>AI Exam Generator</div>
        <div class="navbar-menu">{menu_html}</div>
        <div class="navbar-right">
            {notif_html}
            <div class="navbar-avatar">{initials}</div>
            <span class="navbar-uname">{uname}</span>
        </div>
    </div>
    <div class="navbar-spacer"></div>
    <div class="mobile-header">
        <button class="mh-burger" onclick="window._openDrawer()" aria-label="Menu">
            <span></span><span></span><span></span>
        </button>
        <div class="mh-logo">🎓 AI Exam</div>
        <div class="mh-right">
            {'<div class="mh-notif">🔔<div class="mh-notif-badge">' + str(notif_n) + '</div></div>' if notif_n else ''}
            <div class="mh-avatar">{initials}</div>
        </div>
    </div>
    <div class="mobile-spacer"></div>
    """, unsafe_allow_html=True)

    # Hidden buttons cho desktop navbar (display:none)
    st.markdown('<div style="display:none">', unsafe_allow_html=True)
    for lbl, page in menu_items:
        if st.button(lbl, key=f"nav2_{page}"):
            st.session_state.page = page; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# DRAWER (Mobile only)
# ─────────────────────────────────────────────────────────
def render_drawer():
    uname    = st.session_state.get("username", "")
    email    = st.session_state.get("email", "")
    grade    = st.session_state.get("grade", "")
    role     = st.session_state.get("role", "student")
    cur      = st.session_state.get("page", "home")
    initials = "".join(w[0].upper() for w in uname.split()[:2]) or "?"
    sub_lbl  = email or grade or ("Học sinh" if role == "student" else "Giáo viên")

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

    nav_html = "".join(
        f'<button class="drawer-nav-item {"active" if cur == pg else ""}" '
        f'data-page="{pg}" onclick="window._drawerNav(this)">'
        f'<span class="drawer-nav-icon">{ic}</span>{lbl}'
        f'</button>'
        for ic, lbl, pg in nav_items
    )

    st.markdown(f"""
    <div class="drawer-overlay" id="drawerOverlay"></div>
    <div class="drawer-panel"   id="drawerPanel">
        <div class="drawer-header">
            <div class="drawer-logo">🎓 AI Exam Generator</div>
            <button class="drawer-close" onclick="window._closeDrawer()">✕</button>
        </div>
        <div class="drawer-user">
            <div class="drawer-avatar">{initials}</div>
            <div>
                <div class="drawer-uname">{uname}</div>
                <div class="drawer-usub">{sub_lbl}</div>
            </div>
        </div>
        <div class="drawer-nav">{nav_html}</div>
        <div class="drawer-footer">
            <button class="drawer-logout" onclick="window._drawerLogout()">🚪 Đăng xuất</button>
            <div class="drawer-version">v8.0 · Groq AI</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Hidden Streamlit buttons — drawer điều hướng tới đây
    st.markdown('<div style="display:none" id="drawerHiddenBtns">', unsafe_allow_html=True)
    for ic, lbl, pg in nav_items:
        if st.button(lbl, key=f"drw_{pg}"):
            st.session_state.page = pg; st.rerun()
    if st.button("__logout__", key="drw_logout"):
        _do_logout()
    st.markdown('</div>', unsafe_allow_html=True)

    # JS map drawer buttons → Streamlit hidden buttons
    page_list = [pg for _, _, pg in nav_items]
    st.markdown(f"""
    <script>
    window._drawerNav = function(btn){{
        window._closeDrawer();
        var pg = btn.getAttribute('data-page');
        /* Tìm hidden button có text khớp với label của page */
        var allBtns = document.querySelectorAll('#drawerHiddenBtns button, [style*="display:none"] button');
        allBtns.forEach(function(b){{
            var pages = {page_list};
            pages.forEach(function(p){{
                if(pg === p && b.getAttribute('data-testid') && b.innerText){{
                    b.click();
                }}
            }});
        }});
        /* Fallback: post Streamlit event trực tiếp */
        setTimeout(function(){{
            var ev = new CustomEvent('streamlit:render', {{detail:{{page:pg}}}});
            document.dispatchEvent(ev);
        }}, 100);
    }};
    window._drawerLogout = function(){{
        window._closeDrawer();
        document.querySelectorAll('[data-testid="baseButton-secondary"]').forEach(function(b){{
            if(b.closest('[style*="none"]') && b.innerText.includes('logout')) b.click();
        }});
    }};
    </script>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# BOTTOM NAV (Mobile only)
# ─────────────────────────────────────────────────────────
def render_bottom_nav():
    cur  = st.session_state.get("page", "home")
    role = st.session_state.get("role", "student")

    items = [
        ("🏠", "Trang chủ", "home"),
        ("🚀", "Làm bài",   "select"),
        ("📚", "Khóa học",  "courses") if role == "student" else ("📋", "Lịch sử", "history"),
        ("💬", "Chat",      "chatbox"),
        ("👤", "Hồ sơ",     "profile"),
    ]

    html = "".join(
        f'<button class="bn-item {"active" if cur == pg else ""}" data-page="{pg}" onclick="window._bnNav(this)">'
        f'<span class="bn-icon">{ic}</span><span class="bn-label">{lbl}</span></button>'
        for ic, lbl, pg in items
    )
    st.markdown(f'<div class="bottom-nav">{html}</div><div class="bottom-nav-spacer"></div>',
                unsafe_allow_html=True)

    # Hidden Streamlit buttons
    st.markdown('<div style="display:none" id="bnHiddenBtns">', unsafe_allow_html=True)
    for ic, lbl, pg in items:
        if st.button(f"bn_{lbl}", key=f"bn_{pg}"):
            st.session_state.page = pg; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    page_list = [pg for _, _, pg in items]
    st.markdown(f"""
    <script>
    window._bnNav = function(btn){{
        var pg = btn.getAttribute('data-page');
        var btns = document.querySelectorAll('#bnHiddenBtns button');
        btns.forEach(function(b){{ if(b.innerText.includes('bn_')) b.click(); }});
    }};
    </script>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# TOASTS
# ─────────────────────────────────────────────────────────
def render_popups():
    toasts = []
    page   = st.session_state.get("page", "")

    remind = st.session_state.get("remind_assignments", [])
    if remind and page == "home":
        for a in remind[:2]:
            dl = f" — hạn {a['deadline']}" if a.get("deadline") else ""
            toasts.append(("toast-warning","📢","Đề mới từ giáo viên", f"{a['title']}{dl}"))

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
        ua = [i+1 for i in range(len(qs))
              if st.session_state.get("answers", {}).get(i) is None]
        if ua:
            toasts.append(("toast-error","⚠️",f"{len(ua)} câu chưa làm",
                "Câu " + ", ".join(str(n) for n in ua[:5]) + ("..." if len(ua)>5 else "")))

    if not toasts:
        return

    html = "".join(
        f'<div class="toast {cls}"><div class="toast-icon">{ic}</div>'
        f'<div class="toast-content"><div class="toast-title">{t}</div>'
        f'<div class="toast-msg">{m}</div></div></div>'
        for cls,ic,t,m in toasts
    )
    st.markdown(f'<div class="popup-toast">{html}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# CHAT FAB
# ─────────────────────────────────────────────────────────
def render_chat_fab():
    if st.session_state.get("page") in ("chatbox", "exam"):
        return
    st.markdown("""
    <div style="position:fixed;bottom:1.5rem;left:1.5rem;z-index:9996;display:flex;align-items:center;gap:.6rem">
        <div class="chat-fab" title="Chat hỗ trợ AI" id="chatFabBtn">💬</div>
        <div class="fab-tooltip">Cần hỗ trợ?</div>
    </div>
    <style>
    .fab-tooltip { background:#1a1a2e;color:white;padding:.3rem .7rem;border-radius:6px;
        font-size:.78rem;font-weight:600;white-space:nowrap;box-shadow:0 2px 8px rgba(0,0,0,.15); }
    @media (max-width:768px){ .fab-tooltip { display:none; } }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div style="position:fixed;bottom:1.5rem;left:1.5rem;z-index:9997;opacity:0;width:48px;height:48px">',
                unsafe_allow_html=True)
    if st.button("💬", key="fab_chat_btn", help="Mở chat hỗ trợ AI"):
        st.session_state.page = "chatbox"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# SIDEBAR (Desktop only)
# ─────────────────────────────────────────────────────────
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
        st.session_state.update({"questions":[],"answers":{},"remind_assignments":[],"confirm_submit":False})
    st.rerun()


def render_sidebar():
    """Chỉ render trên desktop — mobile dùng drawer."""
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
                f'<div style="display:flex;align-items:center;gap:.7rem;padding:.5rem 0;margin-bottom:.3rem">'
                f'<div style="width:38px;height:38px;border-radius:50%;'
                f'background:linear-gradient(135deg,#1a73e8,#0d47a1);'
                f'display:flex;align-items:center;justify-content:center;'
                f'font-size:.95rem;font-weight:700;color:white;flex-shrink:0">{initials}</div>'
                f'<div><div style="font-weight:600;font-size:.9rem">{uname}</div>'
                f'<div style="font-size:.72rem;color:#888">{email or grade}</div>'
                f'</div></div>', unsafe_allow_html=True)
        st.markdown("---")

        if st.session_state.get("page") == "chatbox":
            if st.button("✏️ Hội thoại mới", use_container_width=True, type="primary", key="btn_new_ui_sidebar"):
                from chatbox_page import _new_conversation
                _new_conversation(); st.rerun()
            st.markdown("---")

        cur = st.session_state.get("page", "home")
        def nav_btn(lbl, pg, key):
            if st.button(lbl, key=key, use_container_width=True,
                         type="primary" if cur == pg else "secondary"):
                st.session_state.page = pg; st.rerun()

        nav_btn(get_label("home"),     "home",     "nav_home")
        nav_btn(get_label("start"),    "select",   "nav_select")
        if role == "student":
            nav_btn("📚 Khóa học",     "courses",  "nav_courses")
        nav_btn(get_label("history"),  "history",  "nav_history")
        nav_btn(get_label("chatbox"),  "chatbox",  "nav_chat")
        nav_btn(get_label("profile"),  "profile",  "nav_profile")
        nav_btn(get_label("settings"), "settings", "nav_settings")

        st.markdown("---")
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

        if cur == "exam" and st.session_state.get("questions"):
            answered = sum(1 for v in st.session_state.answers.values() if v not in (None, ""))
            total = len(st.session_state.questions)
            st.progress(answered / total if total else 0)
            st.caption(f"Tiến độ: {answered}/{total} câu")
            st.markdown("---")

        if st.button(get_label("logout"), use_container_width=True, key="sb_logout"):
            _do_logout()
        st.caption("v8.0 · Groq AI")


# ─────────────────────────────────────────────────────────
# RENDER ALL
# ─────────────────────────────────────────────────────────
def render_all_ui():
    """Gọi sau inject_css() ở đầu mỗi trang."""
    render_navbar()      # Desktop navbar + Mobile header (CSS ẩn/hiện tự động)
    render_drawer()      # Mobile drawer (CSS display:none trên desktop)
    render_bottom_nav()  # Mobile bottom nav (CSS display:none trên desktop)
    render_popups()
    render_chat_fab()
