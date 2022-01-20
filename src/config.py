import streamlit as st


def initialize():
    st.set_page_config(
        page_title="ECT2 - Bonus Project",
        page_icon="🌤️",
        menu_items={"Get Help": None, "Report a bug": None, "About": None,},
    )

    st.title("Bonus Project")
