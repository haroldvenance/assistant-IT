import streamlit as st
from components.login import login_page
from components.sidebar import render_sidebar
from components.chat import render_chat

def main():
    st.set_page_config(
        page_title="Assistant IT",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    if "token" not in st.session_state:
        login_page()
    else:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        render_sidebar(headers)
        render_chat(headers)

if __name__ == "__main__":
    main()