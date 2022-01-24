import streamlit as st
import pandas as pd

explanation = """
        The total curtailed energy is calculated by summing the curtailed electricity for each timestep.
        There is only curtailed electricity in each timestep if there is more wind and solar PV  production than demand.

        The unserved electricity is calculated in the same manner, except that production and demand are switched.
    """
formula = r"""
        E_{curtailed} = \sum_{t=1}^{8760} max\{E_{wind,t} + E_{pv,t} - E_{demand,t}, 0\} \\ \ \\
        E_{unserved} = \sum_{t=1}^{8760} max\{E_{demand,t} - E_{wind,t} - E_{pv,t}, 0\}
    """


def _calculate_curtailed_energy(row):
    return max(row.production_wind + row.production_pv - row.demand, 0)


def _calculate_unserved_energy(row):
    return max(row.demand - row.production_wind - row.production_pv, 0)


def calculate(data):
    st.header("Question 5")

    # Add the demand data
    demand = pd.read_csv("./input/demand.csv", header=None)
    demand.index = data.index
    data["demand"] = demand / 1000

    # Calculate curtailed and unserved energy
    data["curtailed"] = data.apply(_calculate_curtailed_energy, axis=1)
    data["unserved"] = data.apply(_calculate_unserved_energy, axis=1)

    # Add the metrics and explanations
    col1, col2 = st.columns(2)
    col1.metric("Curtailed energy", f"{int(data.curtailed.sum()):,} MWh")
    col2.metric("Unserved energy", f"{int(data.unserved.sum()):,} MWh")
    st.markdown(explanation)
    st.latex(formula)
