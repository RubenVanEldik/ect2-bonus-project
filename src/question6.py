import streamlit as st


def _ask_input(parameters):
    st.sidebar.title("🔋 Battery storage")
    rated_power = 7.5
    power_rating = st.sidebar.number_input(
        label="Power rating(MW)", value=5, min_value=1, max_value=60,
    )
    energy_rating = st.sidebar.number_input(
        label="Energy rating(MWh)", value=5, min_value=1, max_value=120,
    )

    # Show the minimum (dis)charge time
    charge_time = energy_rating / power_rating * 60
    st.sidebar.caption(
        f"This system is able to (dis)charge for {int(charge_time)} minutes at full power."
    )

    # Add the parameters
    parameters["storage"]["power_rating"] = power_rating
    parameters["storage"]["energy_rating"] = energy_rating


def _calculate_battery_performance(data, parameters):
    battery_soc_prev = 0

    def calculate_row(row):
        nonlocal battery_soc_prev
        energy_rating = parameters["storage"]["energy_rating"]
        power_rating = parameters["storage"]["power_rating"]
        efficiency = parameters["storage"]["efficiency"]

        potential_flow = (row.curtailed - row.unserved) * efficiency
        potential_flow = min(max(potential_flow, -power_rating), power_rating)

        potential_soc_change = potential_flow / energy_rating
        battery_soc = min(max(battery_soc_prev + potential_soc_change, 0), 1)
        actual_flow = (battery_soc - battery_soc_prev) * energy_rating
        battery_soc_prev = battery_soc
        return battery_soc, actual_flow

    new_columns = ["battery_soc", "battery_flow"]
    data[new_columns] = data.apply(calculate_row, axis=1, result_type="expand")


def _calculate_curtailed_energy(row):
    production = row.production_wind + row.production_pv
    return max(production - row.demand - row.battery_flow, 0)


def _calculate_unserved_energy(row):
    production = row.production_wind + row.production_pv
    return max(row.demand + row.battery_flow - production, 0)


def _calculate_metric(column):
    return f"{int(column.sum()):,} MWh"


def _calculate_delta(column1, column2):
    return round((1 - (column2.sum() / column1.sum())) * 100, 1)


def calculate(data, parameters):
    st.header("Question 6")
    _ask_input(parameters)

    # Calculate the battery performance and add it to the data DataFrame
    _calculate_battery_performance(data, parameters)

    # Calculate curtailed and unserved energy
    data["curtailed_w_storage"] = data.apply(_calculate_curtailed_energy, axis=1)
    data["unserved_w_storage"] = data.apply(_calculate_unserved_energy, axis=1)

    # Calculate the reductions in curtailment and unserved energy
    curtailment_reduction = _calculate_delta(data.curtailed, data.curtailed_w_storage)
    unserved_reduction = _calculate_delta(data.unserved, data.unserved_w_storage)

    # Add the metrics and explanations
    col1, col2 = st.columns(2)
    col1.metric(
        "Curtailed energy",
        _calculate_metric(data.curtailed_w_storage),
        delta=f"-{curtailment_reduction}%",
        delta_color="inverse",
    )
    col2.metric(
        "Unserved energy",
        _calculate_metric(data.unserved_w_storage),
        delta=f"-{unserved_reduction}%",
        delta_color="inverse",
    )

    roundtrip_efficiency = parameters["storage"]["efficiency"] ** 2
    st.markdown(
        f"""
        This battery system has a roundtrip efficiency of {roundtrip_efficiency * 100}% and could reduce the curtailment by {curtailment_reduction}% and the unserved energy by {unserved_reduction}%.

        The battery charging and discharging is calculated by the three formulas below. I won't explain them since its boring and I should actually study for the final.
        """
    )
    st.latex(
        r"P_{battery\ max,t} = min\{max\{\eta_{battery}(P_{curtailed,t} - P_{unserved,t}), -P_{battery\ rated}\}, P_{battery\ rated}\}"
    )
    st.latex(
        r"SOC_t = min\{max\{SOC_{t-1} + \frac{\Delta T \times P_{battery\ max,t}}{E_{battery}}, 0\}, 1\}"
    )
    st.latex(r"P_{battery,t} = (SOC_t - SOC_{t-1}) \times E_{battery}")
