import streamlit as st
import math
import pandas as pd


def _calculate_wind_speed_hub_height(row, parameters):
    roughness_length = 0.03
    knmi_height = 10
    hub_height = parameters["wind"]["hub_height"]
    return (
        row.wind_speed
        * math.log(hub_height / roughness_length)
        / math.log(knmi_height / roughness_length)
    )


def _calculate_probability(speed, avg_speed):
    if avg_speed == 0:
        return 0

    return (
        math.pi
        * speed
        / (2 * avg_speed ** 2)
        * math.exp(-math.pi / 4 * (speed / avg_speed) ** 2)
    )


def _calculate_hourly_power(row, parameters):
    swept_area = math.pi * (parameters["wind"]["rotor_diameter"] / 2) ** 2
    avg_power = 0

    # Calculate for each possible wind speed the probability, power coefficient,
    # and wind power. This summed for all wind speeds is the total average power
    power_coefficients = parameters["wind"]["power_coefficients"]
    max_power_coefficient = power_coefficients.index.max()
    for speed in range(max_power_coefficient + 1):
        probability = _calculate_probability(speed, row.wind_speed_hub)
        wind_power = 0.5 * swept_area * 1.225 * speed ** 3
        power_coefficient = power_coefficients.at[speed, "power_coefficient"]

        avg_power += probability * power_coefficient * wind_power / 10 ** 6

    return parameters["wind"]["num_turbines"] * avg_power


def ask_input(parameters):
    st.sidebar.title("Wind power")
    rated_power = 7.5
    capacity_wind_approx = st.sidebar.number_input(
        label="Required wind power capacity (MW)",
        value=20,
        min_value=10,
        max_value=60,
        step=5,
    )
    num_turbines = math.ceil(capacity_wind_approx / rated_power)
    capacity_wind = num_turbines * rated_power

    # Show the number of installed turbines
    st.sidebar.text(f"{num_turbines} turbines for a total of {capacity_wind}MW")

    # Add the parameters
    parameters["wind"]["num_turbines"] = num_turbines
    parameters["wind"]["capacity"] = capacity_wind


@st.experimental_memo
def calculate(data, parameters):
    # Calculate the wind speed at hub height
    data["wind_speed_hub"] = data.apply(
        _calculate_wind_speed_hub_height, axis=1, parameters=parameters
    )

    # Calculate the average hourly wind power generation
    data["avg_wind_power"] = data.apply(
        _calculate_hourly_power, axis=1, parameters=parameters
    )
    return data
