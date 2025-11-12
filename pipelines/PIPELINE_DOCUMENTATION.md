## Pipeline inputs, outputs and a Toronto sample run

This document summarizes the inputs required by the two pipelines in `aeroaqua.pipelines` and shows a worked example using typical Toronto conditions. It also notes dependencies and whether the numeric output seems reasonable.

---

### Pipelines covered

- `run_pipeline_pvlib` (pvlib-based clearsky energy -> baseline linear regression)
- `run_pipeline_rf` (RandomForest GHI predictor -> integrate -> baseline linear regression)

### Shared location defaults

These defaults are defined in `aeroaqua.solar`:

- DEFAULT_LATITUDE = 43.64  (Toronto Harbourfront)
- DEFAULT_LONGITUDE = -79.39
- DEFAULT_ALTITUDE = 76  (meters)
- DEFAULT_TZ = 'America/Toronto'

### run_pipeline_pvlib: required inputs

- date_str (str): 'YYYY-MM-DD' — date for which to compute daily energy
- rh_percent (float): relative humidity in percent (0-100) — used by the final regression
- freq (str, optional): sample frequency for solar position / clearsky (default '10T')
- latitude, longitude, altitude, timezone (optional): location parameters; defaults above are used if not provided

Behavior / outputs:
- Uses `aeroaqua.energy.compute_daily_energy_from_location_date` (pvlib clearsky) to compute daily solar energy kWh/m^2.
- Calls `aeroaqua.model.predict_water_yield(solar_energy_kwh_m2, rh_percent)` to return predicted liters/day.
- Returns a dict with keys: `date`, `solar_energy_kwh_m2`, `rh_percent`, `predicted_liters_per_day`.

Dependencies: `pvlib`, `pandas`.

### run_pipeline_rf: required inputs

- date_str (str): 'YYYY-MM-DD'
- cloud_type (float): cloud encoding used by the RF model (defaults to 0.0). The training CSV expected a `Cloud Type` column — check your training data to see how values are encoded.
- rh_percent (float): relative humidity (0-100)
- temperature_c (float): ambient temperature in Celsius
- model_path (str, optional): path to a trained RandomForest joblib file (if None, pipeline will search common fallback locations)
- freq, latitude, longitude, altitude, timezone: as above

Behavior / outputs:
- Uses `aeroaqua.solar.get_solar_positions_for_date` to compute solar zenith/zenith values at each timestamp.
- Builds a feature DataFrame with columns used by the RF model: `['Cloud Type', 'Solar Zenith Angle', 'Relative Humidity', 'Temperature', 'Month', 'Day', 'Hour']`.
- Loads the RandomForest model and predicts GHI (W/m^2) per sample, integrates over the day to get kWh/m^2.
- Calls `aeroaqua.model.predict_water_yield(total_kwh, rh_percent)` to return liters/day.
- Returns a dict with keys: `date`, `solar_energy_kwh_m2`, `rh_percent`, `predicted_liters_per_day`.

Dependencies: `joblib`, a trained `solar_predictor_model.joblib` produced by `model/train_rf_model.py` (or your own equivalent), `pandas`, `pvlib`.

Note: if the RF model file is not available the pipeline raises a FileNotFoundError and instructs how to train the model.

---

### Baseline regression (water yield)

The small linear model in `aeroaqua.model.baselinesorption` was fit to a small experimental dataset. It accepts two inputs:

- solar_energy_kwh_m2 (float) — daily solar energy in kWh per m^2
- rh_percent (float) — relative humidity in percent

and returns predicted liters/day (float). The training table contains solar energy values roughly in the 5.0–6.66 kWh/m^2 range and liters/day values roughly 2.5–6.0 in that small dataset.

Because the training data is small, treat predictions as a rough baseline or proof-of-concept rather than a high-fidelity engineering estimate.

---

### Typical Toronto example (worked example)

We choose a representative warm summer day for Toronto (mid-July). Example inputs:

- date_str: '2025-07-15'
- latitude: 43.64
- longitude: -79.39
- altitude: 76
- timezone: 'America/Toronto'
- rh_percent: 60.0 (typical comfortable summer relative humidity)
- temperature_c: 24.0
- cloud_type: 0.3 (example partly-clear; RF model encoding depends on training data)

How the two pipelines would handle this example:

1) PVLIB pipeline (`run_pipeline_pvlib`)
   - pvlib clearsky GHI for a mid-July day in Toronto commonly integrates to roughly 5.5–7.0 kWh/m^2 depending on atmospheric conditions. As a conservative representative value we use 6.0 kWh/m^2.
   - Call `predict_water_yield(6.0, 60.0)` using the baseline linear regression. Looking at the embedded training table, values for Solar_Energy≈6.25 and RH=60 give ~5.5 L/day, and for Solar_Energy≈5.83 and RH=60 give ~5.0 L/day. Interpolating to 6.0 kWh/m^2 yields roughly 5.2 L/day.

   Example PVLIB-pipeline output (approximate):

   {
     'date': datetime.date(2025, 7, 15),
     'solar_energy_kwh_m2': 6.0,      # assumed/representative
     'rh_percent': 60.0,
     'predicted_liters_per_day': 5.2  # approximate (interpolated from small dataset)
   }

   Reasonableness: This sits squarely within the small dataset range used to train the baseline linear regression and therefore is plausible as a baseline estimate. The dataset itself yields liters/day values between ~3–6 for solar energies ~5–6.6 and RH 30–70, so ~5.2 L/day is reasonable for a sunny summer day.

2) RF pipeline (`run_pipeline_rf`)
   - If you provide a trained RandomForest joblib model (trained with `model/train_rf_model.py`), `run_pipeline_rf` will predict GHI at each time sample using input features that include `Cloud Type` (broadcast scalar), `Solar Zenith Angle` (from pvlib), RH, Temperature, and time-of-day fields. After integrating the model's predicted GHI across the day the pipeline calls the same `predict_water_yield` regression.
   - Example: if the RF model (trained on your CSV) predicts a daily solar energy of 5.8 kWh/m^2 for the same conditions, then `predict_water_yield(5.8, 60.0)` would return about 5.1 L/day by interpolation of the training table.

   Important: the RF pipeline requires a trained `solar_predictor_model.joblib`. Without that artifact the RF pipeline will raise an error and instruct you to train the model.

---

### How to run locally

1) PVLIB pipeline (recommended for a quick baseline):

   - Ensure `pvlib` and the project requirements are installed (`requirements.txt`).
   - From the package: `from aeroaqua.pipelines.pipeline_pvlib import run_pipeline_pvlib` then call with desired args.

2) RF pipeline (requires trained RF model):

   - Train model (example):
       python -m aeroaqua.model.train_rf_model --csv path/to/usaWithWeather.csv
     This will create `model/solar_predictor_model.joblib` (unless you pass `--out`).
   - Then call `from aeroaqua.pipelines.pipeline_rf import run_pipeline_rf` providing `model_path` if required.

---

### Notes and caveats

- The baseline linear regression model is trained on a small dataset embedded in `aeroaqua.model.baselinesorption`. Treat outputs as baseline/proof-of-concept values, not final design numbers.
- The RF pipeline can give better time-of-day-aware GHI predictions if you have a proper training CSV (the expected columns are documented in `model/train_rf_model.py`). Without a trained RF model you must use the PVLIB pipeline or train your own model.
- For production or engineering use, expand the training dataset and/or replace the baseline regression with validated physical or experimental models.

---

If you'd like, I can:

- Run a concrete local example (I can add a small runnable script that calls `run_pipeline_pvlib` and writes JSON output); or
- Try to estimate solar energy for a specific date by calling pvlib here if you want me to add a small helper or test harness (note: I cannot execute it in your environment — you'll run it locally). 

File authoring note: created by automated documentation step to summarize pipeline inputs/outputs and a Toronto worked example.
