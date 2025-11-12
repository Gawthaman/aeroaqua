"""
Run baseline water-yield predictions for a set of seasonal sample inputs.
Prints a simple markdown-friendly table to stdout.
"""
import json
from datetime import date

try:
    from aeroaqua.model.baselinesorption import predict_water_yield
except Exception as e:
    print("ERROR_IMPORT", e)
    raise

# Seasonal samples: for each season we provide three sample days (clear/average/cloudy)
samples = {
    'summer': [
        {'label': 'clear', 'solar_energy_kwh_m2': 7.0, 'rh_percent': 55.0},
        {'label': 'average', 'solar_energy_kwh_m2': 6.0, 'rh_percent': 60.0},
        {'label': 'cloudy', 'solar_energy_kwh_m2': 4.0, 'rh_percent': 65.0},
    ],
    'spring': [
        {'label': 'clear', 'solar_energy_kwh_m2': 5.0, 'rh_percent': 55.0},
        {'label': 'average', 'solar_energy_kwh_m2': 4.0, 'rh_percent': 60.0},
        {'label': 'cloudy', 'solar_energy_kwh_m2': 3.0, 'rh_percent': 65.0},
    ],
    'fall': [
        {'label': 'clear', 'solar_energy_kwh_m2': 5.5, 'rh_percent': 60.0},
        {'label': 'average', 'solar_energy_kwh_m2': 4.5, 'rh_percent': 65.0},
        {'label': 'cloudy', 'solar_energy_kwh_m2': 3.5, 'rh_percent': 70.0},
    ],
    'winter': [
        {'label': 'clear', 'solar_energy_kwh_m2': 3.0, 'rh_percent': 50.0},
        {'label': 'average', 'solar_energy_kwh_m2': 2.0, 'rh_percent': 55.0},
        {'label': 'cloudy', 'solar_energy_kwh_m2': 1.0, 'rh_percent': 60.0},
    ],
}

results = {}
for season, entries in samples.items():
    results[season] = []
    for e in entries:
        pred = predict_water_yield(e['solar_energy_kwh_m2'], e['rh_percent'])
        results[season].append({
            'label': e['label'],
            'solar_energy_kwh_m2': e['solar_energy_kwh_m2'],
            'rh_percent': e['rh_percent'],
            'predicted_liters_per_day': round(float(pred), 3),
        })

# Write a compact markdown file as requested by the user
out_lines = []
out_lines.append('# Seasonal test results')
out_lines.append(f'# generated: {date.today().isoformat()}')
for season in ['summer', 'spring', 'fall', 'winter']:
    out_lines.append(f'\n## {season.capitalize()}')
    for entry in results[season]:
        out_lines.append(f"- {entry['label']}: solar_energy_kwh_m2={entry['solar_energy_kwh_m2']}, rh_percent={entry['rh_percent']}, predicted_liters_per_day={entry['predicted_liters_per_day']}")

md = '\n'.join(out_lines)
print(md)

# Also dump a JSON file for easier consumption
with open('c:\\\\Users\\\\Gawtham\\\\Desktop\\\\aeroaqua\\\\aeroaqua\\\\pipelines\\\\SEASONAL_RESULTS.json', 'w') as f:
    json.dump(results, f, indent=2)

# And write the simplified markdown-only file requested
with open('c:\\\\Users\\\\Gawtham\\\\Desktop\\\\aeroaqua\\\\aeroaqua\\\\pipelines\\\\SEASONAL_RESULTS.md', 'w') as f:
    f.write(md)

print('\nWrote SEASONAL_RESULTS.json and SEASONAL_RESULTS.md to the pipelines folder.')
