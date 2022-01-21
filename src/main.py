import pandas as pd

import config
import knmi
import question1
import question2
import question3
import question5
import question6
import question7

# Initialize the Streamlit configs
config.initialize()

# Import the core data
data = knmi.import_data("input/weather.csv", 2018)

# Set the default parameters
parameters = {
    "wind": {
        "rated_power": 7.5,
        "rotor_diameter": 127,
        "hub_height": 135,
        "power_coefficients": pd.read_csv(
            "input/power_coefficients", index_col="wind_speed"
        ),
    },
    "storage": {"efficiency": 0.9},
    "financial": {"sde_price": 58},
}

# Calculate all questions
question1.calculate(data, parameters)
question2.calculate(data, parameters)
question3.calculate(data, parameters)
question5.calculate(data)
question6.calculate(data, parameters)
question7.calculate(data, parameters)
