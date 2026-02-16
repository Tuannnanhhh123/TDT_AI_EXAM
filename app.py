# ============================================================
# app.py — Entry point  |  streamlit run app.py
# ============================================================
import time
import streamlit as st

from ui              import inject_css, render_sidebar
from support_popup   import render_support_popup
from courses_page    import show_courses, show_teacher_courses
from pages         import show_home, show_select, show_exam, show_results, show_history
from teacher_pages import show_teacher_dashboard
from profile_page  import show_profile
from settings_page import show_settings
from chatbox_page  import show_chatbox

st.set_page_config(page_title="AI Exam Generator", page_icon="🎓", layout="wide")

# ── Session state defaults ────────────────────────────────
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
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


def _restore_session():
    if st.session_state.get("uid"):
        return
    params = st.query_params
    uid  = params.get("uid")
    role = params.get("role")
    if not uid or not role:
        return
    if role == "teacher":
        uname = params.get("uname", "Giáo viên")
        st.session_state.update({"uid": uid, "username": uname, "role": "teacher", "page": "teacher"})
        return
    try:
        from firebase_manager import _db, _FIREBASE_OK
        if _FIREBASE_OK and _db:
            doc = _db.collection("users").document(uid).get()
            if doc.exists:
                p = doc.to_dict()
                st.session_state.update({
                    "uid": uid, "email": p.get("email", ""),
                    "username": p.get("display_name", ""),
                    "role": p.get("role", "student"),
                    "grade": p.get("grade", ""),
                    "favorite_subjects": p.get("favorite_subjects", []),
                    "page": "home",
                })
    except Exception:
        st.query_params.clear()

def _save_session():
    uid  = st.session_state.get("uid")
    role = st.session_state.get("role")
    if not uid or not role:
        return
    params = {"uid": uid, "role": role}
    if role == "teacher":
        params["uname"] = st.session_state.get("username", "")
    st.query_params.update(params)

def _clear_session():
    st.query_params.clear()

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


def _show_urgent_exam():
    from ai_engine       import generate_exam
    from teacher_manager import get_exam_questions, get_teacher_exams
    a = st.session_state.get("current_assignment")
    if not a:
        st.session_state.page = "home"; st.rerun(); return
    if st.session_state.page in ("exam", "result"):
        render_sidebar(); _ROUTER[st.session_state.page](); return
    dl_str = f"<br>⏰ Hạn nộp: <b>{a['deadline']}</b>" if a.get("deadline") else ""
    st.markdown(
        f'<div style="background:#fce8e6;border-left:5px solid #d93025;'
        f'padding:1rem 1.2rem;border-radius:8px;margin-bottom:1.5rem">'
        f'🔴 <b>Đề bắt buộc từ giáo viên</b><br>'
        f'📌 {a["title"]}<br>📚 {a["subject"]} — {a["grade"]}{dl_str}</div>',
        unsafe_allow_html=True)
    if st.button("▶ Bắt đầu làm bài ngay", type="primary", use_container_width=True):
        if a.get("exam_id"):
            exam_info = next((e for e in get_teacher_exams() if e["id"] == a["exam_id"]), None)
            qs = get_exam_questions(exam_info["q_ids"]) if exam_info else []
            source = "local"
        else:
            qs, source = generate_exam(a["subject"], a["grade"])
        if not qs:
            st.error("Không lấy được câu hỏi. Vui lòng thử lại!"); return
        now = time.time()
        st.session_state.update({
            "subject": a["subject"], "grade": a["grade"],
            "questions": qs, "answers": {}, "submitted": False,
            "score": 0, "start_time": now, "exam_start_ts": now,
            "exam_source": source, "page": "exam",
        })
        st.rerun()


# ═══════════════════════════════════════════════════════════
# LOGIN PAGE — chỉ inject khi page == "login"
# inject_css() của ui.py KHÔNG được gọi ở trang này
# ═══════════════════════════════════════════════════════════
if st.session_state.page == "login":
    from firebase_manager import login, register, reset_password, is_firebase_ok
    from config           import TEACHER_CODE, GRADE_CONFIG, SUBJECT_OPTIONS

    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

/* ── Xoá TOÀN BỘ style Streamlit mặc định + ui.py ── */
html, body { margin:0 !important; padding:0 !important; overflow-x:hidden; }

/* Ẩn mọi chrome Streamlit */
header[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
#MainMenu, footer { display:none !important; }

/* Reset block container */
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
.block-container {
    padding:0 !important;
    margin:0 !important;
    max-width:100% !important;
    font-family:'Inter',sans-serif !important;
}

/* ── QUAN TRỌNG: override lại .stButton từ ui.py ── */
/* ui.py đặt width:100% cho mọi button — giữ nguyên OK */
.stButton > button {
    border-radius:12px !important;
    font-family:'Inter',sans-serif !important;
}

/* Form nằm nửa phải */
[data-testid="stMainBlockContainer"] {
    margin-left:50vw !important;
    width:50vw !important;
    min-height:100vh !important;
    background:#f0f4ff !important;
    display:flex !important;
    flex-direction:column !important;
    align-items:center !important;
    justify-content:center !important;
    padding:2rem 2.5rem !important;
    box-sizing:border-box !important;
}
[data-testid="stMainBlockContainer"] > div,
[data-testid="stVerticalBlock"] {
    width:100% !important;
    max-width:440px !important;
    gap:0.4rem !important;
}

/* ══════════════════════════════
   HERO PANEL — fixed nửa trái
══════════════════════════════ */
.hero-panel {
    position:fixed; top:0; left:0;
    width:50vw; height:100vh;
    overflow:hidden; z-index:999;
    display:flex; flex-direction:column;
    align-items:center; justify-content:center;
    padding:3rem 2.8rem;
    box-sizing:border-box;
}

/* Animated gradient */
.hero-bg {
    position:absolute; inset:-50%;
    width:200%; height:200%;
    background:linear-gradient(-45deg,
        #060918,#111638,#0c1a4a,
        #1a0a42,#081428,#0a2050,
        #100830,#060918);
    background-size:400% 400%;
    animation:gradflow 14s ease infinite;
}
@keyframes gradflow {
    0%  {background-position:0% 50%}
    50% {background-position:100% 50%}
    100%{background-position:0% 50%}
}

/* Grid mesh */
.hero-mesh {
    position:absolute; inset:0;
    background-image:
        linear-gradient(rgba(99,102,241,.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(99,102,241,.05) 1px, transparent 1px);
    background-size:44px 44px;
    animation:mesh-move 25s linear infinite;
}
@keyframes mesh-move {
    0%  {transform:translate(0,0)}
    100%{transform:translate(44px,44px)}
}

/* Orbs */
.orb {
    position:absolute; border-radius:50%;
    filter:blur(70px); animation:orb-float ease-in-out infinite;
}
.o1{width:400px;height:400px;background:radial-gradient(#6366f1,transparent);
    top:-120px;left:-100px;opacity:.5;animation-duration:10s}
.o2{width:300px;height:300px;background:radial-gradient(#3b82f6,transparent);
    bottom:-90px;right:-70px;opacity:.45;animation-duration:13s;animation-delay:-4s}
.o3{width:220px;height:220px;background:radial-gradient(#8b5cf6,transparent);
    top:40%;left:50%;opacity:.4;animation-duration:8s;animation-delay:-6s}
@keyframes orb-float {
    0%,100%{transform:scale(1) translate(0,0);opacity:.45}
    33%    {transform:scale(1.25) translate(12px,-18px);opacity:.7}
    66%    {transform:scale(.85) translate(-8px,14px);opacity:.5}
}

/* Particles */
.pts{position:absolute;inset:0;pointer-events:none;overflow:hidden}
.pt {
    position:absolute; border-radius:50%;
    animation:pt-rise linear infinite;
}
@keyframes pt-rise {
    0%  {transform:translateY(105vh) scale(0);opacity:0}
    8%  {opacity:1}
    92% {opacity:.25}
    100%{transform:translateY(-5vh) scale(1);opacity:0}
}

/* Hero content */
.hc {
    position:relative; z-index:2;
    text-align:center; width:100%;
    font-family:'Inter',sans-serif;
}

/* Logo + rings */
.logo-wrap {
    display:inline-block;
    position:relative; margin-bottom:1.3rem;
}
.ring {
    position:absolute; border-radius:50%;
    border:2px solid rgba(99,102,241,.35);
    animation:ring-pulse 2.8s ease-in-out infinite;
}
.ring1{inset:-14px}
.ring2{inset:-28px;border-width:1px;border-color:rgba(99,102,241,.18);animation-delay:.6s}
@keyframes ring-pulse {
    0%,100%{transform:scale(1);opacity:.7}
    50%    {transform:scale(1.08);opacity:1}
}
.hero-logo {
    font-size:4.8rem; display:block;
    filter:drop-shadow(0 0 30px rgba(99,102,241,1))
           drop-shadow(0 0 70px rgba(99,102,241,.4));
    animation:logo-in .9s cubic-bezier(.36,.07,.19,.97) both;
}
@keyframes logo-in {
    0%  {transform:scale(0) rotate(-15deg);opacity:0}
    65% {transform:scale(1.12) rotate(4deg)}
    100%{transform:scale(1) rotate(0);opacity:1}
}

/* AI badge */
.ai-badge {
    display:inline-flex; align-items:center; gap:.4rem;
    background:rgba(99,102,241,.15);
    border:1px solid rgba(99,102,241,.3);
    border-radius:999px;
    padding:.28rem .9rem;
    color:#a5b4fc; font-size:.7rem; font-weight:700;
    letter-spacing:.8px; text-transform:uppercase;
    margin-bottom:.7rem;
    backdrop-filter:blur(8px);
}
.badge-dot {
    width:6px; height:6px; border-radius:50%;
    background:#6366f1; box-shadow:0 0 8px #6366f1;
    animation:blink 1.6s ease-in-out infinite;
}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.15}}

.hero-title {
    font-size:2.2rem; font-weight:900; color:#fff;
    line-height:1.15; margin-bottom:.45rem;
    letter-spacing:-1.2px;
    text-shadow:0 0 40px rgba(99,102,241,.35);
}
.grad-txt {
    background:linear-gradient(90deg,#a5b4fc 0%,#38bdf8 45%,#818cf8 100%);
    background-size:200% auto;
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    animation:shimmer 3.5s linear infinite;
}
@keyframes shimmer{
    0%  {background-position:0% center}
    100%{background-position:200% center}
}

/* Tagline typing */
.hero-tagline {
    color:rgba(255,255,255,.55); font-size:.9rem;
    margin-bottom:2.2rem; min-height:1.5rem;
    font-weight:400; letter-spacing:.15px;
}
.cursor {
    display:inline-block;
    border-right:2px solid rgba(165,180,252,.75);
    animation:caret .75s step-end infinite;
}
@keyframes caret{0%,100%{opacity:1}50%{opacity:0}}

/* Feature cards — glassmorphism */
.fl{display:flex;flex-direction:column;gap:.65rem}
.fc {
    display:flex; align-items:center; gap:.9rem;
    background:rgba(255,255,255,.055);
    border:1px solid rgba(255,255,255,.09);
    border-radius:14px; padding:.72rem 1rem;
    backdrop-filter:blur(20px) saturate(160%);
    -webkit-backdrop-filter:blur(20px) saturate(160%);
    transition:all .3s cubic-bezier(.4,0,.2,1);
    position:relative; overflow:hidden; text-align:left;
}
/* Shimmer sweep */
.fc::after {
    content:''; position:absolute;
    top:0; left:-120%; width:60%; height:100%;
    background:linear-gradient(90deg,transparent,rgba(255,255,255,.06),transparent);
    transition:left .55s ease;
}
.fc:hover::after{left:160%}
.fc:hover {
    background:rgba(255,255,255,.1);
    border-color:rgba(165,180,252,.28);
    transform:translateX(5px);
    box-shadow:0 8px 28px rgba(0,0,0,.2),
               inset 0 1px 0 rgba(255,255,255,.08);
}
.fi {
    width:38px; height:38px; border-radius:11px;
    display:flex; align-items:center; justify-content:center;
    font-size:1.2rem; flex-shrink:0;
}
.fi-blue  {background:rgba(59,130,246,.2);border:1px solid rgba(59,130,246,.28)}
.fi-purple{background:rgba(139,92,246,.2);border:1px solid rgba(139,92,246,.28)}
.fi-cyan  {background:rgba(6,182,212,.2); border:1px solid rgba(6,182,212,.28)}
.fi-amber {background:rgba(245,158,11,.2);border:1px solid rgba(245,158,11,.28)}
.ft{color:#dde4ff;font-weight:700;font-size:.83rem;display:block;margin-bottom:.1rem}
.fd{color:rgba(255,255,255,.4);font-size:.72rem;line-height:1.4}

/* Stats */
.stats {
    display:flex; gap:0; justify-content:center;
    margin-top:1.8rem; padding-top:1.5rem;
    border-top:1px solid rgba(255,255,255,.07);
}
.stat {
    flex:1; text-align:center;
    padding:0 .5rem;
    border-right:1px solid rgba(255,255,255,.07);
}
.stat:last-child{border-right:none}
.sn{color:#a5b4fc;font-size:1.15rem;font-weight:800;display:block}
.sl{color:rgba(255,255,255,.32);font-size:.65rem;font-weight:600;
    text-transform:uppercase;letter-spacing:.6px}

.hfooter {
    position:absolute; bottom:.9rem; left:50%; transform:translateX(-50%);
    color:rgba(255,255,255,.18); font-size:.67rem; white-space:nowrap;
}

/* ══════════════════════════════
   FORM CARD — nửa phải
══════════════════════════════ */
.fcard {
    background:#fff;
    border-radius:22px;
    padding:2rem 2.2rem;
    width:100%; max-width:420px;
    box-sizing:border-box;
    box-shadow:
        0 2px 4px rgba(0,0,0,.03),
        0 12px 40px rgba(67,56,202,.09),
        0 0 0 1px rgba(67,56,202,.05);
    position:relative; z-index:2;
    font-family:'Inter',sans-serif;
}
.fg  {font-size:1.65rem;font-weight:800;color:#1e1b4b;margin-bottom:.2rem;letter-spacing:-.4px}
.fs  {color:#9ca3af;font-size:.83rem;margin-bottom:1.4rem}

/* Input overrides — đánh bại ui.py CSS */
div[data-testid="stTextInput"] label {
    font-size:.77rem !important; font-weight:600 !important;
    color:#4b5563 !important; font-family:'Inter',sans-serif !important;
}
div[data-testid="stTextInput"] > div > div > input {
    border:1.5px solid #e9eaf0 !important;
    border-radius:11px !important;
    padding:.62rem 1rem !important;
    font-size:.87rem !important;
    background:#fafbff !important;
    color:#111827 !important;
    font-family:'Inter',sans-serif !important;
    box-shadow:0 1px 3px rgba(0,0,0,.03) !important;
    transition:all .22s cubic-bezier(.4,0,.2,1) !important;
    outline:none !important;
}
div[data-testid="stTextInput"] > div > div > input:hover {
    border-color:#c7d2fe !important;
    background:#fff !important;
}
div[data-testid="stTextInput"] > div > div > input:focus {
    border-color:#4338ca !important;
    background:#fff !important;
    box-shadow:0 0 0 4px rgba(67,56,202,.11) !important;
    transform:translateY(-1px) !important;
}

/* Primary button — đánh bại .stButton > button của ui.py */
div[data-testid="stButton"] > button[kind="primary"] {
    background:linear-gradient(135deg,#4338ca,#6366f1 50%,#3b82f6) !important;
    background-size:200% auto !important;
    color:#fff !important; border:none !important;
    border-radius:12px !important;
    padding:.72rem 1rem !important;
    font-size:.9rem !important; font-weight:700 !important;
    font-family:'Inter',sans-serif !important;
    box-shadow:0 4px 16px rgba(67,56,202,.38),
               inset 0 1px 0 rgba(255,255,255,.12) !important;
    transition:all .28s cubic-bezier(.4,0,.2,1) !important;
    width:100% !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    background-position:right center !important;
    transform:translateY(-2px) !important;
    box-shadow:0 8px 24px rgba(67,56,202,.48) !important;
}
div[data-testid="stButton"] > button[kind="primary"]:active {
    transform:translateY(0) !important;
}

/* Secondary button */
div[data-testid="stButton"] > button:not([kind="primary"]) {
    border:1.5px solid #e0e7ff !important;
    border-radius:12px !important;
    color:#4338ca !important;
    background:#f5f3ff !important;
    font-weight:600 !important;
    font-family:'Inter',sans-serif !important;
    width:100% !important;
    transition:all .2s !important;
}
div[data-testid="stButton"] > button:not([kind="primary"]):hover {
    background:#ede9fe !important;
    border-color:#c4b5fd !important;
    transform:translateY(-1px) !important;
}

/* Radio */
div[data-testid="stRadio"] > div {
    display:flex; gap:.5rem;
    background:#f3f4f6; border-radius:12px; padding:4px;
}
div[data-testid="stRadio"] label {
    flex:1; text-align:center;
    padding:.5rem .4rem; border-radius:9px;
    font-size:.82rem !important; font-weight:600 !important;
    color:#6b7280; cursor:pointer;
    font-family:'Inter',sans-serif !important;
    transition:all .2s;
}
div[data-testid="stRadio"] input:checked + div {
    background:#fff; color:#4338ca;
    box-shadow:0 2px 8px rgba(67,56,202,.15);
}

/* Tabs */
div[data-testid="stTabs"] [role="tablist"] {
    background:#f3f4f6 !important;
    border-radius:12px !important; padding:4px !important;
    gap:3px !important; border-bottom:none !important;
}
div[data-testid="stTabs"] [role="tab"] {
    border-radius:9px !important; font-weight:600 !important;
    font-size:.79rem !important; color:#6b7280 !important;
    border:none !important; padding:.48rem .65rem !important;
    font-family:'Inter',sans-serif !important;
    transition:all .2s !important;
}
div[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    background:#fff !important; color:#4338ca !important;
    box-shadow:0 2px 8px rgba(67,56,202,.15) !important;
}

/* Selectbox & multiselect */
div[data-testid="stSelectbox"] > div > div,
div[data-testid="stMultiSelect"] > div > div {
    border-radius:11px !important;
    border:1.5px solid #e9eaf0 !important;
    font-family:'Inter',sans-serif !important;
    font-size:.87rem !important;
}

/* Firebase warning */
.fb-warn {
    background:linear-gradient(135deg,#fff7ed,#fef9ec);
    border:1px solid #fcd34d; border-radius:11px;
    padding:.6rem 1rem; color:#92400e; font-size:.78rem;
    display:flex; align-items:center; gap:.5rem;
    margin-bottom:.8rem; font-weight:500;
}

/* Footer */
.form-foot {
    text-align:center; margin-top:1.1rem;
    color:#9ca3af; font-size:.73rem;
}
.form-foot a{color:#6366f1;text-decoration:none;font-weight:600}
.form-foot a:hover{text-decoration:underline}
</style>
""", unsafe_allow_html=True)

    # ── Hero panel fixed bên trái ─────────────────────────
    st.markdown("""
<div class="hero-panel">
  <div class="hero-bg"></div>
  <div class="hero-mesh"></div>
  <div class="orb o1"></div>
  <div class="orb o2"></div>
  <div class="orb o3"></div>
  <div class="pts" id="hpts"></div>
  <div class="hc">
    <div class="logo-wrap">
      <span class="ring ring1"></span>
      <span class="ring ring2"></span>
      <span class="hero-logo">🎓</span>
    </div>
    <div class="ai-badge"><span class="badge-dot"></span>AI Powered Platform</div>
    <div class="hero-title">AI Exam<br><span class="grad-txt">Generator</span></div>
    <div class="hero-tagline"><span id="ttext"></span><span class="cursor"></span></div>
    <div class="fl">
      <div class="fc"><div class="fi fi-blue">🤖</div>
        <div><span class="ft">AI tạo đề thông minh</span>
             <span class="fd">Câu hỏi cá nhân hoá theo lớp &amp; môn học</span></div></div>
      <div class="fc"><div class="fi fi-purple">📊</div>
        <div><span class="ft">Phân tích tiến độ realtime</span>
             <span class="fd">Biểu đồ điểm số &amp; thống kê chi tiết</span></div></div>
      <div class="fc"><div class="fi fi-cyan">💬</div>
        <div><span class="ft">Chatbot hỗ trợ 24/7</span>
             <span class="fd">Giải đáp thắc mắc bài thi tức thì</span></div></div>
      <div class="fc"><div class="fi fi-amber">🏆</div>
        <div><span class="ft">Bài tập từ giáo viên</span>
             <span class="fd">Nhận &amp; nộp bài trực tiếp trong hệ thống</span></div></div>
    </div>
    <div class="stats">
      <div class="stat"><span class="sn" id="s1">0</span><span class="sl">Học sinh</span></div>
      <div class="stat"><span class="sn" id="s2">0</span><span class="sl">Đề thi</span></div>
      <div class="stat"><span class="sn" id="s3">0</span><span class="sl">Môn học</span></div>
    </div>
  </div>
  <div class="hfooter">© 2025 AI Exam Generator · Powered by Gemini AI</div>
</div>

<script>
(function(){
  /* Particles */
  var c=document.getElementById('hpts');
  if(c){for(var i=0;i<22;i++){var p=document.createElement('div');p.className='pt';
    var sz=Math.random()*3+1.5,h=Math.random()>.5?'220,60%,70%':'262,60%,70%';
    p.style.cssText='width:'+sz+'px;height:'+sz+'px;left:'+Math.random()*100+'%;bottom:0;'
      +'background:hsla('+h+',.55);box-shadow:0 0 '+(sz*2.5)+'px hsla('+h+',.8);'
      +'animation-duration:'+(Math.random()*14+8)+'s;animation-delay:'+(-Math.random()*16)+'s';
    c.appendChild(p);}}

  /* Typing */
  var phrases=['Hệ thống ôn thi thông minh thế hệ mới','Học thông minh hơn mỗi ngày ✨','Cá nhân hoá theo lộ trình của bạn'],
      ti=0,ci=0,del=false,el=document.getElementById('ttext');
  function type(){if(!el)return;var cur=phrases[ti];
    if(!del){el.textContent=cur.slice(0,++ci);
      if(ci===cur.length){del=true;setTimeout(type,1900);return;}setTimeout(type,44);}
    else{el.textContent=cur.slice(0,--ci);
      if(ci===0){del=false;ti=(ti+1)%phrases.length;setTimeout(type,380);return;}setTimeout(type,20);}}
  setTimeout(type,900);

  /* Count-up */
  function cu(id,tg,sfx){var e=document.getElementById(id);if(!e)return;
    var s=0,inc=tg/112;var t=setInterval(function(){s=Math.min(s+inc,tg);
    e.textContent=Math.floor(s).toLocaleString()+(sfx||'');if(s>=tg)clearInterval(t);},16);}
  setTimeout(function(){cu('s1',1200,'+');cu('s2',8500,'+');cu('s3',12,'');},700);
})();
</script>
""", unsafe_allow_html=True)

    # ── Form card — widget Streamlit nằm nửa phải ────────
    st.markdown('<div class="fcard">', unsafe_allow_html=True)

    role_choice = st.radio(
        "role", ["🎒 Học sinh", "👩‍🏫 Giáo viên"],
        horizontal=True, label_visibility="collapsed",
    )
    is_teacher = (role_choice == "👩‍🏫 Giáo viên")

    if not is_firebase_ok():
        st.markdown('<div class="fb-warn">🔥 Firebase chưa kết nối — kiểm tra file cấu hình.</div>',
                    unsafe_allow_html=True)

    # ── GIÁO VIÊN ─────────────────────────────────────────
    if is_teacher:
        st.markdown('<div class="fg">Xin chào, Thầy/Cô 👋</div>', unsafe_allow_html=True)
        st.markdown('<div class="fs">Đăng nhập bằng mã giáo viên của bạn</div>', unsafe_allow_html=True)
        name = st.text_input("Tên giáo viên", placeholder="VD: Nguyễn Thị B", key="t_name")
        code = st.text_input("Mã giáo viên",  type="password", key="t_code", placeholder="Nhập mã bảo mật")
        if st.button("🔓 Đăng nhập", type="primary", use_container_width=True, key="btn_teacher"):
            if not name.strip():       st.error("Vui lòng nhập tên!")
            elif code != TEACHER_CODE: st.error("❌ Mã giáo viên không đúng!")
            else:
                uid = f"teacher_{name.strip().replace(' ','_')}"
                st.session_state.update({"uid": uid, "username": name.strip(),
                                         "role": "teacher", "page": "teacher"})
                _save_session(); st.rerun()

    # ── HỌC SINH ──────────────────────────────────────────
    else:
        st.markdown('<div class="fg">Chào mừng trở lại! 👋</div>', unsafe_allow_html=True)
        st.markdown('<div class="fs">Đăng nhập để tiếp tục hành trình học tập</div>', unsafe_allow_html=True)

        tab_l, tab_r, tab_rs = st.tabs(["🔑 Đăng nhập", "📝 Đăng ký", "🔒 Quên mật khẩu"])

        with tab_l:
            email_l = st.text_input("📧 Email",   key="l_email", placeholder="email@example.com")
            pass_l  = st.text_input("🔒 Mật khẩu", type="password", key="l_pass", placeholder="••••••••")
            if st.button("▶ Đăng nhập", type="primary", use_container_width=True, key="btn_login"):
                if not email_l or not pass_l:
                    st.error("Vui lòng nhập đầy đủ thông tin!")
                else:
                    with st.spinner("Đang đăng nhập..."):
                        ok, msg, user = login(email_l.strip(), pass_l)
                    if ok:
                        from user_manager import create_user
                        create_user(user["display_name"])
                        st.session_state.update({
                            "uid": user["uid"], "email": user["email"],
                            "username": user["display_name"], "role": "student",
                            "grade": user.get("grade", ""),
                            "favorite_subjects": user.get("favorite_subjects", []),
                            "page": "home",
                        })
                        _save_session(); st.success(f"✅ {msg}"); st.rerun()
                    else:
                        st.error(f"❌ {msg}")

        with tab_r:
            r_name  = st.text_input("👤 Họ và tên", key="r_name",  placeholder="VD: Nguyễn Văn A")
            r_email = st.text_input("📧 Email",      key="r_email", placeholder="email@example.com")
            c1, c2  = st.columns(2)
            with c1: r_pass  = st.text_input("🔒 Mật khẩu", type="password", key="r_pass",  placeholder="≥ 6 ký tự")
            with c2: r_pass2 = st.text_input("🔒 Xác nhận", type="password", key="r_pass2", placeholder="Nhập lại")
            cg, cs = st.columns([1, 2])
            with cg: r_grade    = st.selectbox("🏫 Lớp", list(GRADE_CONFIG.keys()), key="r_grade")
            with cs: r_subjects = st.multiselect("📚 Môn yêu thích",
                                                  GRADE_CONFIG[r_grade]["subjects"], key="r_subjects")
            if st.button("✅ Tạo tài khoản", type="primary", use_container_width=True, key="btn_reg"):
                errs = []
                if not r_name.strip():  errs.append("Chưa nhập họ tên")
                if not r_email.strip(): errs.append("Chưa nhập email")
                if len(r_pass) < 6:     errs.append("Mật khẩu tối thiểu 6 ký tự")
                if r_pass != r_pass2:   errs.append("Mật khẩu xác nhận không khớp")
                if not r_subjects:      errs.append("Chọn ít nhất 1 môn yêu thích")
                if errs:
                    for e in errs: st.error(e)
                else:
                    with st.spinner("Đang tạo tài khoản..."):
                        ok, msg = register(email=r_email.strip(), password=r_pass,
                                           display_name=r_name.strip(),
                                           grade=r_grade, favorite_subjects=r_subjects)
                    if ok: st.success(f"🎉 {msg} Vui lòng đăng nhập!")
                    else:  st.error(msg)

        with tab_rs:
            st.markdown('<p style="color:#9ca3af;font-size:.82rem;margin:.4rem 0 .7rem">'
                        'Nhập email đã đăng ký, chúng tôi sẽ gửi link đặt lại mật khẩu.</p>',
                        unsafe_allow_html=True)
            rst_e = st.text_input("📧 Email đã đăng ký", key="rst_email", placeholder="email@example.com")
            if st.button("📨 Gửi email đặt lại", use_container_width=True, key="btn_reset"):
                if not rst_e.strip(): st.error("Vui lòng nhập email!")
                else:
                    ok, msg = reset_password(rst_e.strip())
                    if ok: st.success(f"✅ {msg}")
                    else:  st.error(f"❌ {msg}")

    st.markdown(
        '<div class="form-foot">Bằng cách đăng nhập, bạn đồng ý với '
        '<a href="#">Điều khoản dịch vụ</a> của chúng tôi.</div>',
        unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  # đóng .fcard
    st.stop()


# ═══════════════════════════════════════════════════════════
# Các trang còn lại — inject_css() gọi ở đây như bình thường
# ═══════════════════════════════════════════════════════════
inject_css()

if st.session_state.role == "teacher":
    with st.sidebar:
        st.markdown("### 👩‍🏫 Giáo viên")
        st.markdown(f"**{st.session_state.username}**")
        st.markdown("---")
        if st.button("📚 Khóa học", use_container_width=True,
                     type="primary" if st.session_state.get("teacher_tab") == "courses" else "secondary",
                     key="tv_courses"):
            st.session_state["teacher_tab"] = "courses"; st.rerun()
        if st.button("🚪 Đăng xuất", use_container_width=True):
            _clear_session()
            for k, v in _DEFAULTS.items():
                st.session_state[k] = v
            st.rerun()

    if st.session_state.get("teacher_tab") == "courses":
        show_teacher_courses()
    else:
        show_teacher_dashboard()
    st.stop()

if st.session_state.role == "student":
    from assignment_manager import get_pending_assignments
    pending  = get_pending_assignments(st.session_state.username)
    required = [a for a in pending if a["is_required"]]
    remind   = [a for a in pending if not a["is_required"]]
    st.session_state["remind_assignments"] = remind
    if required and st.session_state.page not in ("exam", "result", "urgent_exam"):
        st.session_state["current_assignment"] = required[0]
        st.session_state.page = "urgent_exam"
        st.rerun()

if st.session_state.page == "urgent_exam":
    _show_urgent_exam(); st.stop()

render_sidebar()
_ROUTER.get(st.session_state.page, show_home)()
render_support_popup()