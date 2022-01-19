import streamlit as st
import math
import pandas as pd


def _calculate_wind_speed_hub_height(row, params):
    roughness_length = 0.03
    knmi_height = 10
    return (
        row.wind_speed
        * math.log(params["hub_height"] / roughness_length)
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


def _calculate_hourly_power(row, params):
    swept_area = math.pi * (params["rotor_diameter"] / 2) ** 2
    avg_power = 0

    # Calculate for each possible wind speed the probability, power coefficient,
    # and wind power. This summed for all wind speeds is the total average power
    for speed in range(params["power_coefficients"].index.max() + 1):
        probability = _calculate_probability(speed, row.wind_speed_hub)
        wind_power = 0.5 * swept_area * 1.225 * speed ** 3
        power_coefficient = params["power_coefficients"].at[speed, "power_coefficient"]

        avg_power += probability * power_coefficient * wind_power / 10 ** 6

    return avg_power


@st.experimental_memo
def calculate(data):
    # Parameters
    params = {
        "rotor_diameter": 127,
        "hub_height": 135,
        "power_coefficients": pd.read_csv(
            "input/power_coefficients", index_col="wind_speed"
        ),
    }

    # Calculate the wind speed at hub height
    data["wind_speed_hub"] = data.apply(
        _calculate_wind_speed_hub_height, axis=1, params=params
    )

    # Calculate the average hourly wind power generation
    data["wind_turbine_power"] = data.apply(
        _calculate_hourly_power, axis=1, params=params
    )

    return data
