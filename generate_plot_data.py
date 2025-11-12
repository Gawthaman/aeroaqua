import pandas as pd
import numpy as np
from pipeline_functions import run_prediction_pipeline
from tqdm import tqdm # A nice progress bar, install with `pip install tqdm`

print("Starting data generation for 3D plot...")

# --- 1. Define Toronto-specific constants ---
LAT = 43.6532  # Toronto Latitude
LON = -79.3832 # Toronto Longitude
ALT = 76       # Toronto Altitude (meters)
TZ = 'America/Toronto'

# --- 2. Define "Control" variables (typical Toronto day) ---
# We fix these so we can isolate the other two variables.
# Using annual averages for Toronto.
RH_TYPICAL = 65.0   # %
TEMP_TYPICAL = 12.0 # Celsius

# --- 3. Define the Grid Variables (our X and Y axes) ---
# X-Axis: Date (Day of Year)
# We'll sample every 5 days for the whole year
date_range = pd.date_range('2025-01-01', '2025-12-31', freq='5D')

# Y-Axis: Cloud Type
# *** CORRECTION: Using the correct integer range 0-10 ***
# We'll use all 11 integer steps from 0 to 10.
cloud_range = np.arange(0, 11) # Generates [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# --- 4. Run the loops ---
results_list = []

# Use tqdm for a progress bar
for date in tqdm(date_range, desc="Processing Dates"):
    for cloud in cloud_range:
        
        # Call the main pipeline function
        result = run_prediction_pipeline(
            date_str = date.strftime('%Y-%m-%d'),
            latitude = LAT,
            longitude = LON,
            altitude = ALT,
            timezone = TZ,
            cloud_type = float(cloud), # Ensure it's a float if model expects, but value is integer
            rh_percent = RH_TYPICAL,
            temperature_c = TEMP_TYPICAL
        )
        
        if result:
            results_list.append(result)

# --- 5. Save to CSV ---
output_df = pd.DataFrame(results_list)
output_filename = 'toronto_3d_plot_data.csv'
output_df.to_csv(output_filename, index=False)

print(f"\nSuccessfully generated {len(output_df)} data points.")
print(f"Data saved to {output_filename}")
print("You can now upload this CSV to Google Colab and run the plotting script.")