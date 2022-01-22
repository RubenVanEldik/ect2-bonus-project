import streamlit as st
import wind
import pv


def calculate(data, parameters):
    st.header("Question 1")

    # Get the input parameters
    wind.ask_input(parameters)
    pv.ask_input(parameters)

    # Calculate the annual wind and solar PV production
    data["production_wind"] = wind.calculate(data, parameters)
    data["production_pv"] = pv.calculate(data, parameters)

    # Show the total annually generated wind and solar PV production
    col1, col2 = st.columns(2)
    col1.metric("Wind production", f"{int(data.production_wind.sum() / 1000)} GWh/year")
    col2.metric("PV production", f"{int(data.production_pv.sum() / 1000)} GWh/year")
