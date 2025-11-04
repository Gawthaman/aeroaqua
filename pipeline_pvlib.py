"""Deprecated top-level shim.

This file was moved to the package `aeroaqua.pipelines.pipeline_pvlib`.
Import from there instead. This shim raises an informative ImportError.
"""

raise ImportError(
    "pipeline_pvlib has moved to 'aeroaqua.pipelines.pipeline_pvlib'. "
    "Import from 'aeroaqua.pipelines' or use the CLI wrappers in 'aeroaqua.scripts'."
)
