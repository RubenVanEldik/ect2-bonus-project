import streamlit as st
import pandas as pd
from matplotlib import pyplot as plt

table_explanation = """
        The table below shows the statistical indicators for the produced energy for each energy source. The checkbox allows you to switch between absolute and relative values.

        The relative standard deviation of the combined solar and wind power output is smaller, which indicates that the variability of wind and solar PV are (at least partially) uncorrelated, which helps to create a more consistent output.
    """
annual_plot_explanation = "The annual plot below shows the produced electricity by energy source throughout the year. The slider allows you to change the number of days that are used in the rolling average. A small number of days gives a more detailed look throughout the year, whereas a larger number creates a better overview of the trends."


def calculate_metric(value, capacity, relative):
    if relative:
        return f"{int(value / capacity * 100)}%"
    return str(round(value, 1))


def create_annual_plot(data):
    st.markdown(annual_plot_explanation)

    # Window input slider
    label = "Window of the rolling average (days)"
    window = st.slider(label, value=30, min_value=1, max_value=60)

    # Prepare the plot data
    plot_data = data[["production_wind", "production_pv"]]
    plot_data["production_total"] = data.production_wind + data.production_pv

    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(plot_data.resample("D").mean().rolling(window=window).mean())
    ax.set_ylabel("Power (MW)")
    ax.legend(["Wind", "Solar PV", "Total"])

    st.pyplot(fig)


def create_table(data, parameters):
    # Define shorter variables
    production_wind = data.production_wind
    capacity_wind = parameters["wind"]["capacity"]
    production_pv = data.production_pv
    capacity_pv = 1
    production_total = production_wind + production_pv
    capacity_total = capacity_wind + capacity_pv

    # Create a table with the statistical values
    st.markdown(table_explanation)
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
    create_annual_plot(data)
