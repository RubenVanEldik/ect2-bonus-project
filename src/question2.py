import streamlit as st
import pandas as pd
from matplotlib import pyplot as plt


def calculate_metric(value, capacity, relative):
    if relative:
        return f"{int(value / capacity * 100)}%"
    return str(round(value, 1))


def create_table(data, parameters):
    # Define shorter variables
    production_wind = data.production_wind
    capacity_wind = parameters["wind"]["capacity"]
    production_pv = data.production_pv
    capacity_pv = 1
    production_total = production_wind + production_pv
    capacity_total = capacity_wind + capacity_pv

    # Create a table with the statistical values
    relative = st.checkbox("Show values relative to installed capacity")
    unit = "%" if relative else "MW"

    st.table(
        pd.DataFrame(
            {
                "Wind": [
                    calculate_metric(production_wind.min(), capacity_wind, relative),
                    calculate_metric(production_wind.mean(), capacity_wind, relative),
                    calculate_metric(production_wind.max(), capacity_wind, relative),
                    calculate_metric(production_wind.std(), capacity_wind, relative),
                ],
                "Solar": [
                    calculate_metric(production_pv.min(), capacity_pv, relative),
                    calculate_metric(production_pv.mean(), capacity_pv, relative),
                    calculate_metric(production_pv.max(), capacity_pv, relative),
                    calculate_metric(production_pv.std(), capacity_pv, relative),
                ],
                "Combined": [
                    calculate_metric(production_total.min(), capacity_total, relative),
                    calculate_metric(production_total.mean(), capacity_total, relative),
                    calculate_metric(production_total.max(), capacity_total, relative),
                    calculate_metric(production_total.std(), capacity_total, relative),
                ],
            },
            columns=["Wind", "Solar", "Combined"],
            index=[
                f"Minimum ({unit})",
                f"Avarage ({unit})",
                f"Maximum ({unit})",
                f"Standard deviation ({unit})",
            ],
        )
    )


def calculate(data, parameters):
    st.header("Question 2")

    create_table(data, parameters)
