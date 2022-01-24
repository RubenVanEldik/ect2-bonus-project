import streamlit as st
import pandas as pd


def _import_day_ahead_prices(data):
    # Drop the first line, since 2018-01-01T23:30:00 is missing from data
    demand = pd.read_csv("input/day_ahead_prices.csv", header=None, skiprows=2)
    demand.columns = ["date", "day_ahead_price"]
    demand.index = data.index
    data["day_ahead_price"] = demand.day_ahead_price
    data["revenue"] = data.day_ahead_price * (data.production_wind + data.production_pv)


def _ask_input(parameters):
    st.sidebar.title("💸 Financial")

    parameters["financial"]["sde_enabled"] = st.sidebar.checkbox("SDE++")

    parameters["financial"]["investment"] = st.sidebar.number_input(
        label="Investment (M€)", value=62.0, min_value=1.0, max_value=200.0, step=1.0
    )
    parameters["financial"]["discount_rate"] = st.sidebar.number_input(
        label="Discount rate", value=0.07, min_value=0.01, max_value=0.2,
    )
    parameters["financial"]["deprecation_period"] = st.sidebar.number_input(
        label="Deprecation period (years)", value=20, min_value=1, max_value=40
    )


def _explain():
    st.markdown(
        """
        To calculate the financial viability of the project both the payback period (PBP) and levelized cost of
        energy (LCOE) are calculated. The day ahead prices for 2018 have been retrieved from ENTSO-E [1]. An annual O&M cost of 2% of the initial investment [2]
        and a technical availability of 98% [3] are assumed for both the wind and solar PV installation.

        The payback period is calculated by dividing the initial investment by the annual revenue, minus the operations and management costs. The annual
        revenue is the sum of the electricity price multiplied by the electricity generated for each time period. When
        SDE++ is enabled a fixed electricity price of €58 per MWh is used instead of the day ahead price.

        For both the electricity generation and electricity price we assume future years will be exactly the same
        as 2018. This is most definitely wrong, but its already hard to predict short to medium future price developments, let
        alone multi-decade price developments.
        """
    )

    st.caption(
        """
        1) Day ahead prices [ENTSO-E](https://transparency.entsoe.eu/transmission-domain/r2/dayAheadPrices/show)

        2) Perez, et al. ([10.1016/j.solener.2018.12.074](https://doi.org/10.1016/j.solener.2018.12.074))

        3) Ribrant ([XR-EE-EEK 2006:009](https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.561.2279&rep=rep1&type=pdf))
    """
    )

    st.latex(
        r"pay\ back\ period = \frac{cost_{investment}}{\sum_{t=1}^{8760} price_{electricity,t}(E_{wind,t} + E_{pv,t}) - cost_{OM}}"
    )

    st.latex(
        r"LCOE = \frac{\frac{discount\ rate}{1 - (1 + discount\ rate)^{-n}} \times cost_{investment} + cost_{OM}}{\sum_{t=1}^{8760} E_{wind,t} + E_{pv,t}}"
    )


def calculate(data, parameters):
    st.header("Question 7")

    # Import the day ahead prices and get the input parameters
    _import_day_ahead_prices(data)
    _ask_input(parameters)

    # Calculate the payback time
    investment = parameters["financial"]["investment"] * 10 ** 6
    sde_price = parameters["financial"]["sde_price"]
    electricity_production = data.production_wind.sum() + data.production_pv.sum()
    pbp = investment / data.revenue.sum()
    pbp_sde = investment / (electricity_production * sde_price)

    # Calculate the LCOE
    discount_rate = parameters["financial"]["discount_rate"]
    deprecation_period = parameters["financial"]["deprecation_period"]
    capital_recovery_factor = discount_rate / (
        1 - (1 + discount_rate) ** -deprecation_period
    )
    om_costs = 0
    lcoe = (capital_recovery_factor * investment + om_costs) / electricity_production

    sde_enabled = parameters["financial"]["sde_enabled"]
    col1, col2 = st.columns(2)
    col1.metric(
        "Payback period",
        f"{int(pbp_sde)} years" if sde_enabled else f"{int(pbp)} years",
        delta=f"{int((pbp_sde / pbp - 1) * 100)}%" if sde_enabled else None,
        delta_color="inverse",
    )
    col2.metric(
        "LCOE", f"{int(lcoe)} €/MWh",
    )
    _explain()
