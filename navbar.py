import streamlit as st

def render_navbar():
    st.write("")

    username = st.session_state.get("username", "")

    col1, col2, col3, col4 = st.columns([4, 1, 1, 1])

    with col1:
        st.markdown("## 🍽 AI Calorie Tracker")
        if username:
            st.caption(f"Hello, {username} 👋")

    with col2:
        if st.button("Log Food"):
            st.switch_page("pages/Food_Detection.py")

    with col3:
        if st.button("Reports"):
            st.switch_page("pages/report.py")

    with col4:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.switch_page("front.py")