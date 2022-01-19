import streamlit as st
import pandas as pd
import knmi
import wind

st.set_page_config(
    page_title="ECT2 - Bonus Project",
    page_icon="🌤️",
    menu_items={"Get Help": None, "Report a bug": None, "About": None,},
)

st.title("Bonus Project")


# Import the KNMI weather data
data = knmi.import_data("./input/weather.csv", 2018)


# Add a table with the input data
with st.expander("Input data"):
    input_data = data.astype(str)
    input_data.columns = [
        "Wind direction (°N)",
        "Wind speed (m/s)",
        "Temperature (°C)",
        "GHI (W/m2)",
        "Air pressure (bar)",
    ]
    st.write(input_data)


st.header("Question 1")
wind_inputs = wind.ask_input()
data = wind.calculate(data, wind_inputs)
