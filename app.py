# ============================================================
# app.py — Đã tối ưu theo Cách 2 (Lazy Loading & Single Write)
# ============================================================
import time
import streamlit as st

# Giữ nguyên các import của bạn
from ui              import inject_css, render_sidebar, render_all_ui
from support_popup   import render_support_popup
from courses_page    import show_courses, show_teacher_courses
from pages           import show_home, show_select, show_exam, show_results, show_history
from teacher_pages   import show_teacher_dashboard
from profile_page    import show_profile
from settings_page   import show_settings, get_label
from chatbox_page    import show_chatbox

# ... (Giữ nguyên các hàm _DEFAULTS, _restore_session, _save_session của bạn) ...

# ═══════════════════════════════════════════════════════════
# LOGIN PAGE (Phần xử lý đăng nhập Student đã sửa)
# ═══════════════════════════════════════════════════════════
if st.session_state.page == "login":
    # ... (Toàn bộ phần CSS và HTML Hero Panel giữ nguyên 100%) ...

    # [TÌM ĐẾN PHẦN BUTTON ĐĂNG NHẬP STUDENT - KHOẢNG DÒNG 350]
    with tab_l:
        email_l = st.text_input("📧 Email",    key="l_email", placeholder="email@example.com")
        pass_l  = st.text_input("🔒 Mật khẩu", type="password", key="l_pass", placeholder="••••••••")
        if st.button("▶ Đăng nhập", type="primary", use_container_width=True, key="btn_login"):
            if not email_l or not pass_l:
                st.error("Vui lòng nhập đầy đủ thông tin!")
            else:
                with st.spinner("Đang xác thực..."):
                    from firebase_manager import login
                    ok, msg, user = login(email_l.strip(), pass_l)
                
                if ok:
                    # TỐI ƯU CÁCH 2: 
                    # 1. Bỏ qua việc gọi create_user() tại đây để giảm độ trễ lúc bấm nút.
                    # 2. Cập nhật session nhanh nhất có thể.
                    st.session_state.update({
                        "uid": user["uid"], "email": user["email"],
                        "username": user["display_name"], "role": "student",
                        "grade": user.get("grade",""),
                        "favorite_subjects": user.get("favorite_subjects",[]),
                        "page": "home", # Cho vào trang chủ ngay
                        "first_login": True # Cờ đánh dấu để xử lý dữ liệu sau
                    })
                    _save_session(); st.rerun()
                else:
                    st.error(f"❌ {msg}")
    
    # ... (Các phần Tab Đăng ký, Quên mật khẩu giữ nguyên) ...
    st.stop()

# ═══════════════════════════════════════════════════════════
# Các trang sau login (Phần xử lý Lazy Loading)
# ═══════════════════════════════════════════════════════════
inject_css()

# ── HỌC SINH ─────────────────────────────────────────────
if st.session_state.role == "student":
    # TỐI ƯU CÁCH 2: Xử lý ghi dữ liệu User 1 lần duy nhất sau khi đã vào App
    if st.session_state.get("first_login"):
        from user_manager import create_user
        try:
            create_user(st.session_state.username)
            st.session_state.first_login = False # Tắt cờ sau khi ghi xong
        except: pass

    # TỐI ƯU CÁCH 2: Chỉ lấy bài tập chờ khi đang ở trang Home hoặc khi cần thiết
    # Thay vì quét Firebase ở mọi trang (Profile, Settings, v.v.)
    if st.session_state.page in ["home", "urgent_exam"]:
        from assignment_manager import get_pending_assignments
        
        # Chỉ quét Firebase nếu chưa có dữ liệu bài tập trong session này
        if not st.session_state.get("remind_assignments") and not st.session_state.get("current_assignment"):
            with st.spinner("Đang kiểm tra bài tập..."):
                pending = get_pending_assignments(st.session_state.username)
                
            if pending:
                required = [a for a in pending if a.get("is_required")]
                remind   = [a for a in pending if not a.get("is_required")]
                st.session_state["remind_assignments"] = remind
                
                if required and st.session_state.page not in ("exam","result","urgent_exam"):
                    st.session_state["current_assignment"] = required[0]
                    st.session_state.page = "urgent_exam"
                    st.rerun()

# ── TIẾP TỤC RENDER GIAO DIỆN ──
if st.session_state.page == "urgent_exam":
    render_sidebar()
    render_all_ui()
    _show_urgent_exam()
    st.stop()

render_sidebar()
render_all_ui()
_ROUTER.get(st.session_state.page, show_home)()
render_support_popup()
