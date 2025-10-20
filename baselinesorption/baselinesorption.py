import pandas as pd
from sklearn.linear_model import LinearRegression
from io import StringIO

# Step 1: Load the dataset from the paper's appendix
csv_data = """RH_Percent,Solar_Energy_kWhr_m2,Liters_Per_Day
20,5,2.5
30,5,3.0
40,5,3.5
50,5,4.0
60,5,4.0
70,5,4.5
20,5.41,3.0
30,5.41,3.5
40,5.41,4.0
50,5.41,4.0
60,5.41,4.5
70,5.41,5.0
20,5.83,3.0
30,5.83,3.5
40,5.83,4.0
50,5.83,4.5
60,5.83,5.0
70,5.83,5.5
20,6.25,3.0
30,6.25,4.0
40,6.25,4.5
50,6.25,5.0
60,6.25,5.5
70,6.25,6.0
20,6.66,3.5
30,6.66,4.0
40,6.66,5.0
50,6.66,5.5
60,6.66,6.0
70,6.66,6.0
"""

df = pd.read_csv(StringIO(csv_data))

# Step 2: Define the features (X) and the target variable (y)
features = ['RH_Percent', 'Solar_Energy_kWhr_m2']
target = 'Liters_Per_Day'

X = df[features]
y = df[target]

# Step 3: Create and train the linear regression model
model = LinearRegression()
model.fit(X, y)

# Step 4: Display the model's intercept and coefficients to verify
print("Model Verification:")
print(f"Intercept (B0): {model.intercept_:.4f}")
print(f"RH_Percent Coefficient (B1): {model.coef_[0]:.4f}")
print(f"Solar_Energy Coefficient (B2): {model.coef_[1]:.4f}")