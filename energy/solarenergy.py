import pandas as pd
import numpy as np
import pvlib


# Helper that computes solar energy (kWh/m^2) from a pvlib Location using the clearsky model.

def compute_daily_energy_from_location_date(
    latitude: float,
    longitude: float,
    altitude: float,
    timezone: str,
    date_str: str,
    freq: str = '10T',
):
    """Compute daily solar energy (kWh/m^2) using pvlib clearsky GHI.

    Returns a pandas.DataFrame with columns: ['date', 'solar_energy_kwh_m2']
    For a single date this will be a single-row dataframe.
    """
    start = f"{date_str} 00:00:00"
    end = f"{date_str} 23:59:00"
    times = pd.date_range(start=start, end=end, freq=freq, tz=timezone)

    location = pvlib.location.Location(latitude, longitude, tz=timezone, altitude=altitude)
    cs = location.get_clearsky(times)  # returns dict-like with ghi, dni, dhi

    ghi = cs['ghi']  # Series indexed by times in W/m^2

    # compute delta hours per sample (handles variable freq)
    dt = times.to_series().diff().dt.total_seconds().div(3600).fillna((pd.Timedelta(freq).total_seconds() / 3600))

    # Wh/m^2 per sample = ghi (W/m^2) * hours
    wh_per_sample = ghi * dt.values

    # total kWh/m^2 for the date
    total_kwh = wh_per_sample.sum() / 1000.0

    return pd.DataFrame([{'date': pd.to_datetime(date_str).date(), 'solar_energy_kwh_m2': total_kwh}])


if __name__ == '__main__':
    # example quick-run
    df_energy = compute_daily_energy_from_location_date(43.64, -79.39, 76, 'America/Toronto', '2025-11-04')
    print(df_energy)
