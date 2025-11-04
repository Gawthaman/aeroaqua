from aeroaqua.solar import get_solar_positions_for_date, DEFAULT_LATITUDE, DEFAULT_LONGITUDE, DEFAULT_ALTITUDE, DEFAULT_TZ
from aeroaqua.energy import compute_daily_energy_from_location_date
from aeroaqua.model import predict_water_yield


def run_pipeline_pvlib(
    date_str: str = '2025-11-04',
    rh_percent: float = 50.0,
    freq: str = '10T',
    latitude: float = DEFAULT_LATITUDE,
    longitude: float = DEFAULT_LONGITUDE,
    altitude: float = DEFAULT_ALTITUDE,
    timezone: str = DEFAULT_TZ,
):
    """Run the pvlib-based pipeline.

    Steps:
    1. Compute solar position (for traceability).
    2. Use pvlib clearsky GHI to compute daily solar energy (kWh/m^2).
    3. Predict water yield via baseline regression using RH and computed solar energy.

    Returns a dict with keys: date, solar_energy_kwh_m2, rh_percent, predicted_lpd
    """
    solpos = get_solar_positions_for_date(date_str=date_str, freq=freq, latitude=latitude, longitude=longitude, altitude=altitude, timezone=timezone)

    energy_df = compute_daily_energy_from_location_date(latitude, longitude, altitude, timezone, date_str, freq=freq)
    solar_energy = float(energy_df.iloc[0]['solar_energy_kwh_m2'])

    predicted = predict_water_yield(solar_energy, rh_percent)

    return {
        'date': energy_df.iloc[0]['date'],
        'solar_energy_kwh_m2': solar_energy,
        'rh_percent': rh_percent,
        'predicted_liters_per_day': predicted,
    }


if __name__ == '__main__':
    out = run_pipeline_pvlib(date_str='2025-11-04', rh_percent=50.0)
    print('PVLIB Pipeline result:')
    print(out)
