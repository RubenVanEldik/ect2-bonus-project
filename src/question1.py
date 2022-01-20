import streamlit as st
import wind


def calculate(data):
    st.header("Question 1")
    wind_inputs = wind.ask_input()
    wind.calculate(data, wind_inputs)
