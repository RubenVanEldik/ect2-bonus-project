import streamlit as st
import wind


def calculate(data, parameters):
    st.header("Question 1")
    wind.ask_input(parameters)
    wind.calculate(data, parameters)
