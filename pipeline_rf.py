import os
import joblib
import pandas as pd
import numpy as np
from solar_toronto_spa import get_solar_positions_for_date, DEFAULT_LATITUDE, DEFAULT_LONGITUDE, DEFAULT_ALTITUDE, DEFAULT_TZ
from baselinesorption.baselinesorption import predict_water_yield


MODEL_DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'solarenergy', 'solar_predictor_model.joblib')
# note: if running from repo root, path may instead be './solarenergy/solar_predictor_model.joblib'
MODEL_FALLBACK_PATHS = [
    os.path.join(os.path.dirname(__file__), 'solarenergy', 'solar_predictor_model.joblib'),
    os.path.join(os.getcwd(), 'solarenergy', 'solar_predictor_model.joblib'),
    os.path.join(os.getcwd(), 'solarenergy', 'solar_predictor_model.joblib')
]


def _find_model(path_hint: str = None):
    if path_hint and os.path.exists(path_hint):
        return path_hint
    for p in MODEL_FALLBACK_PATHS:
        if os.path.exists(p):
            return p
    return None


def run_pipeline_rf(
    date_str: str = '2025-11-04',
    cloud_type: float = 0.0,
    rh_percent: float = 50.0,
    temperature_c: float = 20.0,
    model_path: str = None,
    freq: str = '10T',
    latitude: float = DEFAULT_LATITUDE,
    longitude: float = DEFAULT_LONGITUDE,
    altitude: float = DEFAULT_ALTITUDE,
    timezone: str = DEFAULT_TZ,
):
    """Run the RF-based pipeline.

    Steps:
    1. Compute solar positions for the date to get Solar Zenith Angle and timestamps.
    2. Assemble feature dataframe expected by the RF model using provided scalars (cloud_type, RH, temperature)
       which are broadcast to every time sample.
    3. Load the trained RandomForest model and predict GHI (W/m^2) per sample.
    4. Integrate predicted GHI over the day to get daily solar energy (kWh/m^2).
    5. Feed daily solar energy and RH into baselinesorption.predict_water_yield to get liters/day.

    Returns a dict with keys: date, solar_energy_kwh_m2, rh_percent, predicted_lpd
    """
    # 1. solar positions
    solpos = get_solar_positions_for_date(date_str=date_str, freq=freq, latitude=latitude, longitude=longitude, altitude=altitude, timezone=timezone)
    times = solpos.index

    # 2. features DataFrame
    df_feat = pd.DataFrame(index=times)
    # use apparent_zenith (degrees) as 'Solar Zenith Angle'
    if 'apparent_zenith' in solpos.columns:
        df_feat['Solar Zenith Angle'] = solpos['apparent_zenith']
    elif 'zenith' in solpos.columns:
        df_feat['Solar Zenith Angle'] = solpos['zenith']
    else:
        raise RuntimeError('Solar position table does not contain zenith columns')

    df_feat['Cloud Type'] = float(cloud_type)
    df_feat['Relative Humidity'] = float(rh_percent)
    df_feat['Temperature'] = float(temperature_c)
    """Deprecated top-level shim.

    This file was moved to the package `aeroaqua.pipelines.pipeline_rf`.
    Import from there instead. This shim raises an informative ImportError.
    """

    raise ImportError(
        "pipeline_rf has moved to 'aeroaqua.pipelines.pipeline_rf'. "
        "Import from 'aeroaqua.pipelines' or use the CLI wrappers in 'aeroaqua.scripts'."
    )

