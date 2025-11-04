import os
import argparse
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib


def train_and_save(csv_path: str, model_path: str = None):
    """Train RandomForest on provided CSV and save model.

    Expects the CSV to contain these columns:
        'Cloud Type', 'Solar Zenith Angle', 'Relative Humidity', 'Temperature', 'Month', 'Day', 'Hour', 'GHI'

    Args:
        csv_path: path to the CSV file used to train the model.
        model_path: path to save the trained joblib model. If None, saves to model/solar_predictor_model.joblib

    Returns:
        path to saved model
    """
    if model_path is None:
        model_path = os.path.join(os.path.dirname(__file__), 'solar_predictor_model.joblib')

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(csv_path)

    input_features = [
        'Cloud Type',
        'Solar Zenith Angle',
        'Relative Humidity',
        'Temperature',
        'Month',
        'Day',
        'Hour'
    ]
    target_variable = 'GHI'

    missing = [c for c in input_features + [target_variable] if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in CSV: {missing}")

    X = df[input_features]
    y = df[target_variable]

    print("Training RandomForest model...")
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        min_samples_leaf=5,
        n_jobs=-1,
        random_state=42
    )
    model.fit(X, y)

    joblib.dump(model, model_path)
    print(f"Model saved to: {model_path}")
    return model_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train and save RandomForest GHI predictor')
    parser.add_argument('--csv', required=True, help='Path to usaWithWeather.csv (training data)')
    parser.add_argument('--out', required=False, help='Output model path (joblib)')
    args = parser.parse_args()

    train_and_save(args.csv, args.out)
