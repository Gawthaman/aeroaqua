import pandas as pd
import numpy as np
import pvlib


# This module used to train a RandomForest model. For the pipeline we
# provide a small helper that computes solar energy (kWh/m^2) from
# a pvlib Location using the clearsky model. The original training
# script is left out of the automated flow but can still be used
# for model training offline.


def compute_daily_energy_from_location_date(
    latitude: float,
    longitude: float,
    altitude: float,
    """Deprecated shim: the energy helpers are now in `aeroaqua.energy` package.

    Import the new helper from:

        from aeroaqua.energy import compute_daily_energy_from_location_date

    This shim raises an informative ImportError to avoid accidental imports of the old module.
    """

    raise ImportError(
        "solarenergy helpers moved to 'aeroaqua.energy.solarenergy'. "
        "Import from 'aeroaqua.energy' instead."
    )