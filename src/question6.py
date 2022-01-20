import streamlit as st


def ask_input(parameters):
    st.sidebar.title("🔋 Battery storage")
    rated_power = 7.5
    power_rating = st.sidebar.number_input(
        label="Power rating(MW)", value=5, min_value=1, max_value=20,
    )
    energy_rating = st.sidebar.number_input(
        label="Energy rating(MWh)", value=5, min_value=1, max_value=20,
    )

    # Show the minimum (dis)charge time
    charge_time = energy_rating / power_rating * 60
    st.sidebar.caption(
        f"This system is able to (dis)charge for {int(charge_time)} minutes at full power."
    )

    # Add the parameters
    parameters["storage"]["power_rating"] = power_rating
    parameters["storage"]["energy_rating"] = energy_rating


def calculate_battery_performance(data, parameters):
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


def calculate_curtailed_energy(row):
    production = row.production_wind + row.production_pv
    return max(production - row.demand - row.battery_flow, 0)


def calculate_unserved_energy(row):
    production = row.production_wind + row.production_pv
    return max(row.demand + row.battery_flow - production, 0)


def calculate_metric(column):
    return f"{int(column.sum()):,} MWh"


def calculate_delta(column1, column2):
    return round((1 - (column2.sum() / column1.sum())) * 100, 1)


def calculate(data, parameters):
    st.header("Question 6")
    ask_input(parameters)

    # Calculate the battery performance and add it to the data DataFrame
    calculate_battery_performance(data, parameters)

    # Calculate curtailed and unserved energy
    data["curtailed_w_storage"] = data.apply(calculate_curtailed_energy, axis=1)
    data["unserved_w_storage"] = data.apply(calculate_unserved_energy, axis=1)

    # Calculate the reductions in curtailment and unserved energy
    curtailment_reduction = calculate_delta(data.curtailed, data.curtailed_w_storage)
    unserved_reduction = calculate_delta(data.unserved, data.unserved_w_storage)

    # Add the metrics and explanations
    col1, col2 = st.columns(2)
    col1.metric(
        "Curtailed energy",
        calculate_metric(data.curtailed_w_storage),
        delta=f"-{curtailment_reduction}%",
        delta_color="inverse",
    )
    col2.metric(
        "Unserved energy",
        calculate_metric(data.unserved_w_storage),
        delta=f"-{unserved_reduction}%",
        delta_color="inverse",
    )

    roundtrip_efficiency = parameters["storage"]["efficiency"] ** 2
    st.markdown(
        f"This battery system has a roundtrip efficiency of {roundtrip_efficiency * 100}% and could reduce the curtailment by {curtailment_reduction}% and the unserved energy by {unserved_reduction}%."
    )
