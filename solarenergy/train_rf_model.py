"""Deprecated shim: training helper moved into the package model.train_rf_model.

Use:

    python -m aeroaqua.model.train_rf_model --csv path/to/usaWithWeather.csv

This shim raises an informative ImportError.
"""

raise ImportError(
    "train_rf_model moved to 'aeroaqua.model.train_rf_model'. "
    "Use `python -m aeroaqua.model.train_rf_model --csv path` to train a model."
)
