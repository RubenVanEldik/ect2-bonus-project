import streamlit as st
import wind


def calculate(data, parameters):
    st.header("Question 1")
    wind.ask_input(parameters)
    data["production_wind"] = wind.calculate(data, parameters)
    data["production_pv"] = 1
