import streamlit as st
import pandas as pd
import math
import pvlib


@st.experimental_memo
def _import_module(type):
    modules = pd.read_excel("input/modules.xlsx", index_col="Parameters")
    return modules[type]


@st.experimental_memo
def _calculate_irradiance(data, latitude, longitude):
    weather = data[["wind_speed", "temperature", "ghi"]]
    position = pvlib.solarposition.ephemeris(data.index, latitude, longitude)
    irradiance = pvlib.irradiance.erbs(weather.ghi, position.zenith, position.index)

    return pd.concat([weather, position, irradiance], axis=1)


def _get_ac_from_dc(power_dc, nominal_power_ac, *, efficiency_nom=0.96):
    # Return 0 if the DC power is 0
    if power_dc == 0:
        return 0

    # Calculate the rated DC power
    nominal_power_dc = nominal_power_ac / efficiency_nom

    # Return the rated power of the inverter if the DC power is larger or equal to the rated DC power
    if power_dc >= nominal_power_dc:
        return nominal_power_ac

    # Calculate the efficiency
    zeta = power_dc / nominal_power_dc
    efficiency = -0.0162 * zeta - (0.0059 / zeta) + 0.9858

    # Return the efficiency of the inverter times the DC power
    return efficiency * power_dc


def _calculate_production(irradiance, module, *, tilt, azimuth):
    # Define some variables
    wind = irradiance.wind_speed
    temp_air = irradiance.temperature
    zenith = irradiance.zenith
    azimuth = irradiance.azimuth
    apparent_zenith = irradiance.apparent_zenith
    dni = irradiance.dni
    ghi = irradiance.ghi
    dhi = irradiance.dhi

    # Get the POA for this specific facade
    poa = pvlib.irradiance.get_total_irradiance(
        tilt, azimuth, zenith, azimuth, dni, ghi, dhi
    )

    # Calculate the temperature of the cell
    temp_cell = pvlib.temperature.sapm_cell(
        poa.poa_global, temp_air, wind, module.A, module.B, module.DTC
    )

    # Calculate the relative and absolute airmass
    relative_airmass = pvlib.atmosphere.get_relative_airmass(apparent_zenith)
    absolute_airmass = pvlib.atmosphere.get_absolute_airmass(relative_airmass)

    # Calculate the Angle of Incidence
    aoi = pvlib.irradiance.aoi(tilt, azimuth, zenith, azimuth)

    # Calculate the effective irradiance
    effective_irradiance = pvlib.pvsystem.sapm_effective_irradiance(
        poa.poa_direct, poa.poa_diffuse, absolute_airmass, aoi, module
    )

    # Calculate the performance of the cell
    performance = pvlib.pvsystem.sapm(effective_irradiance, temp_cell, module)

    # Calculate the total and relative annual yield
    return performance.p_mp.apply(_get_ac_from_dc, args=(module.Wp,))


def ask_input(parameters):
    st.sidebar.title("🌤️ Solar power")

    # Get the capacity input
    capacity_approx = st.sidebar.number_input(
        label="Required solar PV power capacity (MW)",
        value=35,
        min_value=0,
        max_value=60,
        step=5,
    )

    # Calculate the number of panels and total capacity
    rated_power = parameters["pv"]["rated_power"] / 10 ** 6
    num_panels = math.ceil(capacity_approx / rated_power)
    capacity_pv = num_panels * rated_power

    # Show the number of installed PV panels
    st.sidebar.caption(
        f"{num_panels:,} PV panels will be installed for a total of {round(capacity_pv, 2)}MW"
    )

    # Get the tilt and azimuth input
    tilt = st.sidebar.slider(
        label="Tilt panels (°)", value=35, min_value=0, max_value=90
    )
    azimuth = st.sidebar.slider(
        label="Azimuth panels (°)", value=180, min_value=0, max_value=360
    )

    # Add the parameters
    parameters["pv"]["num_panels"] = num_panels
    parameters["pv"]["capacity"] = capacity_pv
    parameters["pv"]["tilt"] = tilt
    parameters["pv"]["azimuth"] = azimuth


# @st.experimental_memo
def calculate(data, parameters):
    latitude = parameters["location"]["lat"]
    longitude = parameters["location"]["lon"]
    tilt = parameters["pv"]["tilt"]
    azimuth = parameters["pv"]["azimuth"]
    num_panels = parameters["pv"]["num_panels"]

    module = _import_module("HIT")
    irradiance = _calculate_irradiance(data, latitude=latitude, longitude=longitude)
    output = _calculate_production(irradiance, module, tilt=tilt, azimuth=azimuth)
    return output * num_panels / 10 ** 6
