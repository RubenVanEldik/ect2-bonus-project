import streamlit as st

cf_explanation = "The capacity factor for wind en solar PV is calculated by dividing the sum of the output by their respective capacity and total number of hours (8760) per year."
cf_formula = r"Capacity\ factor_{source} = \frac{\sum_{t=1}^{8760} E_{source,t}}{E_{source,max} \times 8760}"

flh_explanation = "The full load hours are calculated by almost the same formula as the capacity factor, but instead of dividing the sum of the output by the capacity and number of hours in a year, it is only divided by the sum of the output."
flh_formula = r"Full\ load\ hours_{source} = \frac{\sum_{t=1}^{8760} E_{source,t}}{E_{source,max}} = 8760 \times Capacity\ factor_{source}"


def calculate(data, parameters):
    st.header("Question 3")

    capacity_wind = parameters["wind"]["capacity"]
    capacity_pv = parameters["pv"]["capacity"]
    capacity_total = capacity_wind + capacity_pv

    cf_wind = data.production_wind.sum() / (capacity_wind * 8760)
    cf_pv = data.production_pv.sum() / (capacity_pv * 8760)
    production_total = data.production_wind.sum() + data.production_pv.sum()
    cf_total = production_total / (capacity_total * 8760)

    # Capacity factor
    st.subheader("Capacity factor")
    col1, col2, col3 = st.columns(3)
    col1.metric("Wind", f"{int(cf_wind * 100)}%")
    col2.metric("Solar PV", f"{int(cf_pv * 100)}%")
    col3.metric("Combined", f"{int(cf_total * 100)}%")

    st.markdown(cf_explanation)
    st.latex(cf_formula)

    # Full load
    st.subheader("Full load hours")
    col1, col2, col3 = st.columns(3)
    col1.metric("Wind", f"{int(cf_wind * 8760)} hours")
    col2.metric("Solar PV", f"{int(cf_pv * 8760)} hours")
    col3.metric("Combined", f"{int(cf_total * 8760)} hours")

    st.markdown(flh_explanation)
    st.latex(flh_formula)
