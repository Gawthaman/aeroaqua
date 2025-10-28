import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib  # Import joblib for saving

# --- 1. Load Data ---
print("Loading data...")
df = pd.read_csv('usaWithWeather.csv')

# --- 2. Feature Selection (Define X and y) ---
# Use the same features as before
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

# IMPORTANT: Train on ALL data now
# Since we've validated the model, we now train it on the 
# entire dataset to make it as accurate as possible.
X = df[input_features]
y = df[target_variable]

# --- 3. Model Training ---
print("Training the full model...")
model = RandomForestRegressor(
    n_estimators=100,
    max_depth=15,
    min_samples_leaf=5,
    n_jobs=-1,
    random_state=42
)
model.fit(X, y)
print("Model training complete.")

# --- 4. Save the Model to a File ---
model_filename = 'solar_predictor_model.joblib'
joblib.dump(model, model_filename)

print(f"\nSUCCESS: Your 'Model 1' has been trained and saved as '{model_filename}'")