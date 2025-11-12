# Seasonal test results (baseline linear model)

The table below lists the input values used (solar energy in kWh/m^2 and relative humidity in %), the predicted water yield (liters/day) from the baseline linear regression in `aeroaqua.model.baselinesorption`, and a short note whether the result seems reasonable given the dataset and domain knowledge.

Generated without executing pvlib (predictions come from the embedded baseline linear model fit to the small experimental table).

## Summer
- clear: solar_energy_kwh_m2=7.0, rh_percent=55.0 => predicted_liters_per_day=5.759
  - Reasonable: Yes — high solar energy and moderate RH give one of the largest yields (within the training-range extrapolation).
- average: solar_energy_kwh_m2=6.0, rh_percent=60.0 => predicted_liters_per_day=5.155
  - Reasonable: Yes — matches the small dataset trend (around 5 L/day for ~6 kWh/m^2 and RH~60%).
- cloudy: solar_energy_kwh_m2=4.0, rh_percent=65.0 => predicted_liters_per_day=3.710
  - Reasonable: Yes — lower solar energy yields lower water production; value is within the dataset interpolation range.

## Spring
- clear: solar_energy_kwh_m2=5.0, rh_percent=55.0 => predicted_liters_per_day=4.076
  - Reasonable: Yes — mid-range energy and RH lead to moderate production.
- average: solar_energy_kwh_m2=4.0, rh_percent=60.0 => predicted_liters_per_day=3.472
  - Reasonable: Yes.
- cloudy: solar_energy_kwh_m2=3.0, rh_percent=65.0 => predicted_liters_per_day=2.869
  - Reasonable: Yes — lower energy and higher RH produce less water in this baseline model.

## Fall
- clear: solar_energy_kwh_m2=5.5, rh_percent=60.0 => predicted_liters_per_day=4.734
  - Reasonable: Yes — intermediate between spring and summer clear days.
- average: solar_energy_kwh_m2=4.5, rh_percent=65.0 => predicted_liters_per_day=4.131
  - Reasonable: Yes.
- cloudy: solar_energy_kwh_m2=3.5, rh_percent=70.0 => predicted_liters_per_day=3.526
  - Reasonable: Yes.

## Winter
- clear: solar_energy_kwh_m2=3.0, rh_percent=50.0 => predicted_liters_per_day=2.157
  - Reasonable: Marginal — winter clear days have low solar energy; model predicts small yields, often under 3 L/day.
- average: solar_energy_kwh_m2=2.0, rh_percent=55.0 => predicted_liters_per_day=1.553
  - Reasonable: Yes — small energy leads to small yield.
- cloudy: solar_energy_kwh_m2=1.0, rh_percent=60.0 => predicted_liters_per_day=0.949
  - Reasonable: Yes — nearly zero production on very low solar-energy, high-RH cloudy winter days.

---

Notes:
- The baseline linear model was fit to a small embedded dataset with solar energy values between ~5.0 and 6.66 kW
far outside that range (for example very low winter SE=1.0) are extrapolations and should be treated cautiously.
- If you want the PVLIB-based or the RF-based pipeline outputs for the same seasonal inputs, I can create a small runner that calls `run_pipeline_pvlib` or `run_pipeline_rf` — but those require `pvlib` installed (pvlib used by the pvlib pipeline) and a trained RF joblib file for the RF pipeline.
