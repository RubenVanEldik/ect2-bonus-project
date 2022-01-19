import pandas as pd

columns = {
    "YYYYMMDD": "date",
    "   HH": "hour",
    "   DD": "wind_direction",
    "   FH": "wind_speed",
    "    T": "temperature",
    "    P": "air_pressure",
    "    Q": "ghi",
}


def import_data(filename, year):
    """
    Get and transform the KNMI dataset.

    Returns:
        DataFrame: DataFrame with the KNMI weather data
    """
    # Import the CSV file and set the column names
    knmi = pd.read_csv(filename, skiprows=range(0, 31))
    knmi = knmi[columns.keys()]
    knmi.columns = columns.values()

    # Fix datetime index
    knmi.date = knmi.date.astype(str)
    knmi.hour = knmi.hour.apply(lambda hour: str(hour).zfill(2))
    knmi.hour = knmi.hour.replace("24", "00")
    knmi["datetime"] = knmi.date + knmi.hour + "00"
    knmi.datetime = pd.to_datetime(knmi.datetime, format="%Y%m%d%H%M")
    knmi.datetime = knmi.datetime + pd.Timedelta(hours=-1, minutes=30)

    # Filter to the current year
    knmi = knmi[knmi.datetime.dt.year == year]

    # Fix the units
    knmi.wind_speed = knmi.wind_speed.astype(int) / 10
    knmi.temperature = knmi.temperature.astype(int) / 10
    knmi.air_pressure = knmi.air_pressure.astype(int) * 10
    knmi.ghi = knmi.ghi.astype(int) * 100 ** 2 / 60 / 60  # J/cm2 to kW/m2

    # Set the datetime as index and keep only the relevant columns
    knmi.index = knmi.datetime
    knmi = knmi[["wind_direction", "wind_speed", "temperature", "ghi", "air_pressure",]]

    # Return the DataFrame
    return knmi
