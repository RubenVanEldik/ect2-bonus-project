import config
import knmi
import question1

# Initialize the Streamlit configs
config.initialize()

# Import the core data
data = knmi.import_data("./input/weather.csv", 2018)

# Calculate all questions
question1.calculate(data)
