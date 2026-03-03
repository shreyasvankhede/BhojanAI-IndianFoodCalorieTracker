import streamlit as st
from Auth import AuthManager

auth = AuthManager()


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = None


st.title("AI Calorie Tracker")

if not st.session_state.logged_in:

    tab1, tab2 = st.tabs(["Login", "Register"])

    # ---------------- LOGIN ----------------
    with tab1:
        u = st.text_input("", placeholder="Username", key="login_user")
        p = st.text_input("", placeholder="Password", type="password", key="login_pass")

        if st.button("Login"):
            if auth.login(u, p):
                st.session_state.logged_in = True
                st.session_state.username = u

                st.success("Login successfull")
                st.switch_page("pages/Food_Detection.py")
            else:
                st.error("Invalid credentials")

    # ---------------- REGISTER ----------------
    with tab2:
        u = st.text_input("", placeholder="Username", key="reg_name")

        p = st.text_input("", placeholder="Password", type="password", key="reg_pass")

        confirm_p = st.text_input(
            "",
            placeholder="Confirm Password",
            type="password",
            key="C_reg_pass"
        )

        if p and confirm_p and p != confirm_p:
            st.warning("Passwords do not match")

        if st.button("Register"):
            if not u or not p:
                st.error("Please fill all fields")

            elif p != confirm_p:
                st.error("Passwords do not match")

            else:
                if auth.register(u, p):
                    st.success("User created! You are being logged in")
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.switch_page("pages/Food_Detection.py")
                else:
                    st.error("User already exists")

else:
    st.success("You are already logged in,redirecting")
    st.switch_page("pages/Food_Detection.py")
