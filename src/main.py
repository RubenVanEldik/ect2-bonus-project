import streamlit as st
import pandas as pd
import knmi

st.set_page_config(
    page_title="ECT2 - Bonus Project",
    page_icon="🌤️",
    menu_items={"Get Help": None, "Report a bug": None, "About": None,},
)

st.title("Bonus Project")


data = knmi.import_data("./input/weather.csv", 2018)

with st.expander("Input data"):
    data = data.astype(str)
    data
