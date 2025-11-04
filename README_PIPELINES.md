Two pipeline variants are provided to compute daily solar energy and predict water yield.

1) PVLIB pipeline (deterministic clearsky-based)

- Script: `pipeline_pvlib.py`
- Usage example (from repo root):

```powershell
python -c "from pipeline_pvlib import run_pipeline_pvlib; print(run_pipeline_pvlib('2025-11-04', rh_percent=50.0))"
```

This pipeline uses pvlib clearsky GHI integrated over the day to compute kWh/m^2 and then calls the linear regression in `baselinesorption` to predict liters/day.

2) RandomForest pipeline (data-driven GHI predictor)

- Training script: `solarenergy/train_rf_model.py`
- Pipeline: `pipeline_rf.py`

Training:

```powershell
python -m solarenergy.train_rf_model --csv path\to\usaWithWeather.csv
```

This will save `solarenergy/solar_predictor_model.joblib` by default.

Run the RF pipeline after training:

```powershell
python -c "from pipeline_rf import run_pipeline_rf; print(run_pipeline_rf('2025-11-04', cloud_type=0, rh_percent=50.0, temperature_c=20.0))"
```

Notes and assumptions
- `baselinesorption.predict_water_yield(solar_energy_kwh_m2, rh_percent)` is used for both pipelines.
- The RF pipeline expects a trained model stored at `solarenergy/solar_predictor_model.joblib` (or pass `model_path` to `run_pipeline_rf`).
- If you want per-sample RH/Temperature inputs for the RF pipeline, the pipeline can be extended to accept time-series arrays; the current implementation broadcasts scalar values across all timesteps.

Requirements
- Install dependencies from `requirements.txt`.

```powershell
pip install -r requirements.txt
```

If you want, I can run a smoke test here (installing dependencies and running both pipelines).