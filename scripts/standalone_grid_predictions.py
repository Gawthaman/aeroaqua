"""
Standalone script to generate a grid of (Season, Solar Energy, RH) and predict water yield
using a hard-coded linear model approximation if aeroaqua package import fails.

Output: model_grid_predictions.csv in the current working directory.

Grid definition:
  Solar Energy (kWh/m^2): 1.0 .. 7.0 step 0.25
  RH (%): 50 .. 75 step 1
  Seasons: Summer, Spring, Fall, Winter

Prediction sources (fallback order):
  1. aeroaqua.model.baselinesorption.predict_water_yield
  2. Hard-coded coefficients derived from the embedded dataset (approximation)

Usage (PowerShell):
  python standalone_grid_predictions.py
  # or specify output
  python standalone_grid_predictions.py --output my_grid.csv

You can later post-process the CSV or load it into pandas.
"""
import argparse
import csv
import itertools
import math
import os
from dataclasses import dataclass

try:
    import pandas as pd  # optional but improves performance / flexibility
except Exception:
    pd = None

try:
    from aeroaqua.model.baselinesorption import predict_water_yield as baseline_predict
except Exception:
    baseline_predict = None


# Hard-coded linear model coefficients (approximation) used only if import fails.
# Obtained from fitting to the embedded dataset; formula:
# liters_per_day = intercept + B_rh * RH + B_se * SolarEnergy
HARDCODED_INTERCEPT = -1.4490
HARDCODED_RH_COEF = 0.0605
HARDCODED_SOLAR_COEF = 0.4883


def fallback_predict(solar_energy_kwh_m2: float, rh_percent: float) -> float:
    return HARDCODED_INTERCEPT + HARDCODED_RH_COEF * rh_percent + HARDCODED_SOLAR_COEF * solar_energy_kwh_m2


def get_predict_fn():
    if baseline_predict is not None:
        return baseline_predict
    return fallback_predict


def build_grid():
    seasons = ['Summer', 'Spring', 'Fall', 'Winter']
    solar_vals = [round(x, 2) for x in frange(1.0, 7.0, 0.25)]
    rh_vals = list(range(50, 76))
    for season, se, rh in itertools.product(seasons, solar_vals, rh_vals):
        yield season, se, rh


def frange(start, stop, step):
    x = start
    # ensure floating point rounding issues don't overshoot
    while x <= stop + 1e-9:
        yield x
        x += step


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='model_grid_predictions.csv', help='Output CSV filename')
    args = parser.parse_args()

    predict_fn = get_predict_fn()

    rows = []
    for season, se, rh in build_grid():
        pred = predict_fn(se, rh)
        rows.append({
            'Season': season,
            'Solar_Energy_kwh_m2': se,
            'RH_Percent': rh,
            'Predicted Water (L/day)': round(float(pred), 4)
        })

    # Write CSV manually (works without pandas). Use pandas if available for convenience.
    out_path = os.path.abspath(args.output)
    fieldnames = ['Season', 'Solar_Energy_kwh_m2', 'RH_Percent', 'Predicted Water (L/day)']

    try:
        with open(out_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    except Exception as e:
        raise SystemExit(f"Failed to write CSV: {e}")

    print(f"Wrote {len(rows)} rows to {out_path}")
    # Basic summary
    preds = [r['Predicted Water (L/day)'] for r in rows]
    print(f"Predicted min={min(preds):.3f}, max={max(preds):.3f}, mean={sum(preds)/len(preds):.3f}")


if __name__ == '__main__':
    main()
