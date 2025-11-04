"""Deprecated top-level shim.

This module was moved to the package `aeroaqua.solar.solar_toronto_spa`.
Import from `aeroaqua.solar` instead:

    from aeroaqua.solar import get_solar_positions_for_date

This shim raises an informative ImportError to avoid accidental imports of the old module.
"""

raise ImportError(
    "solar_toronto_spa moved to 'aeroaqua.solar.solar_toronto_spa'. "
    "Import from 'aeroaqua.solar' instead."
)
