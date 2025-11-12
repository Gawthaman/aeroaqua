import pandas as pd
import pvlib
import joblib
import numpy as np
import os
import warnings

# --- 1. Load the RandomForest Model ---
# We'll try to find the model in common locations.
def get_solar_model(model_path=None):
    """Loads the solar_predictor_model.joblib file."""
    search_paths = [
        model_path,
        'solar_predictor_model.joblib',
        './solar_predictor_model.joblib',
        '../solar_predictor_model.joblib'
    ]
    
    for path in search_paths:
        if path and os.path.exists(path):
            try:
                model = joblib.load(path)
                print(f"Successfully loaded model from: {path}")
                return model
            except Exception as e:
                print(f"Error loading model from {path}: {e}")
    
    warnings.warn("*** WARNING: Could not find or load 'solar_predictor_model.joblib'. ***")
    warnings.warn("Pipeline will run with a DUMMY model. Predictions will be incorrect.")
    # Return a dummy_model if the real one isn't found, so the code can still run
    class DummyModel:
        def predict(self, X):
            # A simple dummy: returns 800W/m^2 for low zenith, 0 for high
            return np.where(X['zenith'] < 85, 800 * (1 - X['cloud_type']), 0)
            
    return DummyModel()

# Load the model ONCE when this module is imported
SOLAR_RF_MODEL = get_solar_model()

# --- 2. Define the Linear Regression Coefficients ---
# These values are from your provided image (image_8e4a5e.png)
COEF_SOLAR_ENERGY = 0.803
COEF_RH_PERCENT = 0.001
INTERCEPT = 0.117

def run_prediction_pipeline(
    date_str: str,
    latitude: float,
    longitude: float,
    altitude: float,
    timezone: str,
    cloud_type: float,
    rh_percent: float,
    temperature_c: float,
    freq: str = '10T'
):
    """
    Runs the full 2-stage pipeline for a single day and single set of weather inputs.
    """
    
    # --- STAGE 1: PVLIB ZENITH ---
    
    # Create the location object
    location = pvlib.location.Location(
        latitude=latitude, 
        longitude=longitude, 
        tz=timezone, 
        altitude=altitude
    )
    
    # Create the time range for the specified date in a pandas-version-robust way
    # Some pandas versions don't accept a `tz` argument to `to_datetime`, so
    # parse first then localize or convert as needed.
    start = pd.to_datetime(date_str)
    if start.tzinfo is None:
        # localize naive timestamp to the requested timezone
        start = pd.Timestamp(start).tz_localize(timezone)
    else:
        # convert aware timestamp to the requested timezone
        start = pd.Timestamp(start).tz_convert(timezone)

    # The end is 24 hours later (exclusive).
    end = start + pd.Timedelta(days=1)
    
    # Create the 10-minute interval time series
    times = pd.date_range(start=start, end=end, freq=freq, inclusive='left')

    if times.empty:
        # Handle case for very short frequencies / edge cases
        return None

    # Get solar position for the entire time series
    solar_pos = location.get_solarposition(times)
    
    # We only care about apparent zenith. Clip at 90 degrees (nighttime).
    zenith = solar_pos['apparent_zenith'].clip(lower=0, upper=90)

    # --- STAGE 2: RANDOMFOREST GHI REGRESSOR ---
    
    # Build the feature DataFrame that the RF model used during training.
    # Use the exact column names and additional temporal features (Month/Day/Hour).
    X_features = pd.DataFrame(index=times)
    X_features['Solar Zenith Angle'] = zenith
    X_features['Cloud Type'] = float(cloud_type)
    X_features['Relative Humidity'] = float(rh_percent)
    X_features['Temperature'] = float(temperature_c)
    X_features['Month'] = X_features.index.month
    X_features['Day'] = X_features.index.day
    X_features['Hour'] = X_features.index.hour

    # Fill NaNs conservatively
    X_features = X_features.fillna(0)

    # Feature ordering must match training-time columns
    feature_cols = ['Cloud Type', 'Solar Zenith Angle', 'Relative Humidity', 'Temperature', 'Month', 'Day', 'Hour']
    ghi_predictions_w_m2 = SOLAR_RF_MODEL.predict(X_features[feature_cols])

    # Ensure GHI is 0 during nighttime (when solar zenith angle is 90)
    ghi_predictions_w_m2[X_features['Solar Zenith Angle'] >= 90] = 0
    # Ensure GHI is not negative
    ghi_predictions_w_m2[ghi_predictions_w_m2 < 0] = 0
    
    # Integrate GHI (W/m^2) to get daily Solar Energy (kWh/m^2)
    # 1. Get the frequency interval in hours
    freq_in_hours = pd.to_timedelta(freq).total_seconds() / 3600.0
    
    # 2. Sum all (W/m^2) predictions and multiply by (hours per interval) -> Wh/m^2
    total_wh_m2 = ghi_predictions_w_m2.sum() * freq_in_hours
    
    # 3. Convert Wh/m^2 to kWh/m^2
    solar_energy_kwh_m2 = total_wh_m2 / 1000.0
    
    # --- STAGE 3: LINEAR REGRESSION WATER YIELD ---
    
    # Predict liters per day using the coefficients from your model
    predicted_liters = (
        (solar_energy_kwh_m2 * COEF_SOLAR_ENERGY) +
        (rh_percent * COEF_RH_PERCENT) +
        INTERCEPT
    )
    
    # --- OUTPUT ---
    
    return {
        'date': start.date(),
        'latitude': latitude,
        'cloud_type': cloud_type,
        'rh_percent': rh_percent,
        'temperature_c': temperature_c,
        'solar_energy_kwh_m2': solar_energy_kwh_m2,
        'predicted_liters_per_day': predicted_liters
    }