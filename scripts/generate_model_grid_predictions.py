"""
Generate a grid of model inputs (Season, Solar Energy, RH) and predict water yield.

Creates a CSV file `model_grid_predictions.csv` with columns:
  - Season
  - Solar_Energy_kwh_m2
  - RH_Percent
  - Predicted Water (L/day)

Usage examples:
  # Use the built-in baseline linear predictor (no external model required):
  python -m aeroaqua.scripts.generate_model_grid_predictions --output model_grid_predictions.csv

  # Use a scikit-learn joblib model that accepts feature columns (attempts to align columns):
  python -m aeroaqua.scripts.generate_model_grid_predictions --model-path path/to/my_model.joblib --output model_grid_predictions.csv

Notes:
  - If you pass a joblib model the script will try to align feature names using
    the model's `feature_names_in_` attribute if present. It will also one-hot encode
    the `Season` column (prefix 'Season_') when needed.
  - If no model is provided the script uses the project's baseline linear regression
    implemented in `aeroaqua.model.baselinesorption.predict_water_yield`.
"""
from __future__ import annotations

import argparse
import itertools
import os
from typing import List

import numpy as np
import pandas as pd


def build_grid(solar_min=1.0, solar_max=7.0, solar_step=0.25, rh_min=50, rh_max=75):
    solar_vals = np.round(np.arange(solar_min, solar_max + 1e-12, solar_step), 6)
    rh_vals = np.arange(rh_min, rh_max + 1)
    seasons = ['Summer', 'Spring', 'Fall', 'Winter']

    rows = []
    for season, s, rh in itertools.product(seasons, solar_vals, rh_vals):
        rows.append({'Season': season, 'Solar_Energy_kwh_m2': float(s), 'RH_Percent': float(rh)})

    df = pd.DataFrame(rows)
    return df


def prepare_features_for_model(df: pd.DataFrame, feature_names: List[str]) -> pd.DataFrame:
    """Attempt to produce a DataFrame with columns in feature_names from the base df.

    This will:
      - create one-hot columns for Season (prefix 'Season_')
      - try to map common name variants for solar energy and RH
      - fill missing feature columns with zeros
    """
    df2 = df.copy()

    # create one-hot Season columns
    season_dummies = pd.get_dummies(df2['Season'], prefix='Season')
    df2 = pd.concat([df2, season_dummies], axis=1)

    # potential name variants mapping
    col_mapping = {
        'solar_energy_kwh_m2': ['Solar_Energy_kwh_m2', 'Solar_Energy_kWhr_m2', 'Solar_Energy_kWh_m2', 'solar_energy_kwh_m2', 'SolarEnergy_kwh_m2'],
        'rh_percent': ['RH_Percent', 'Relative Humidity', 'rh_percent', 'RH']
    }

    available_cols = {c.lower(): c for c in df2.columns}

    out = {}
    for fname in feature_names:
        # exact match
        if fname in df2.columns:
            out[fname] = df2[fname]
            continue

        # case-insensitive match
        if fname.lower() in available_cols:
            out[fname] = df2[available_cols[fname.lower()]]
            continue

        # season one-hot pattern
        if fname.startswith('Season') and fname in df2.columns:
            out[fname] = df2[fname]
            continue

        # map common solar/rh variants
        mapped = None
        for key, variants in col_mapping.items():
            for v in variants:
                if v == fname or v.lower() == fname.lower():
                    # pick the canonical column from df2 if present
                    for cand in variants:
                        if cand in df2.columns:
                            mapped = cand
                            break
                    if mapped:
                        break
            if mapped:
                out[fname] = df2[mapped]
                break

        if mapped:
            continue

        # As a last resort, if feature expects Season_* but column missing, create zeros
        if fname.startswith('Season_'):
            out[fname] = pd.Series(0, index=df2.index)
            continue

        # Missing numeric feature -> fill with zeros and warn
        out[fname] = pd.Series(0.0, index=df2.index)

    X = pd.DataFrame(out)
    # Ensure numeric dtype for prediction
    for c in X.columns:
        if X[c].dtype == object:
            try:
                X[c] = pd.to_numeric(X[c])
            except Exception:
                # leave as-is; some models may accept categorical strings (rare)
                pass
    return X


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-path', help='Path to joblib model (optional). If omitted, uses internal baseline predictor.')
    parser.add_argument('--output', default='model_grid_predictions.csv', help='Output CSV file path')
    args = parser.parse_args()

    df = build_grid()

    if args.model_path:
        # try to load joblib model and predict
        try:
            import joblib
        except Exception as e:
            raise RuntimeError('joblib is required to load a saved model. Install scikit-learn/joblib.') from e

        model = joblib.load(args.model_path)
        # try to infer feature names
        feature_names = None
        if hasattr(model, 'feature_names_in_'):
            feature_names = list(model.feature_names_in_)
        elif hasattr(model, 'n_features_in_') and model.n_features_in_ == 2:
            # assume standard two-feature ordering: Solar_Energy_kwh_m2, RH_Percent
            feature_names = ['Solar_Energy_kwh_m2', 'RH_Percent']
        else:
            # fallback: attempt common names
            feature_names = ['Solar_Energy_kwh_m2', 'RH_Percent']

        X = prepare_features_for_model(df, feature_names)
        preds = model.predict(X)
        df['Predicted Water (L/day)'] = preds
    else:
        # use baseline predictor
        try:
            from aeroaqua.model.baselinesorption import predict_water_yield
        except Exception as e:
            raise RuntimeError('Could not import baseline predictor from aeroaqua.model.baselinesorption') from e

        df['Predicted Water (L/day)'] = df.apply(lambda r: predict_water_yield(r['Solar_Energy_kwh_m2'], r['RH_Percent']), axis=1)

    # Persist CSV
    out_path = args.output
    df.to_csv(out_path, index=False)
    print(f'Wrote predictions to: {os.path.abspath(out_path)} (rows={len(df)})')


if __name__ == '__main__':
    main()
