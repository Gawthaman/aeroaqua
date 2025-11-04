"""Simple CLI wrapper to run the pvlib pipeline."""
from aeroaqua.pipelines.pipeline_pvlib import run_pipeline_pvlib
import argparse


if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Run pvlib pipeline')
    p.add_argument('--date', default='2025-11-04')
    p.add_argument('--rh', type=float, default=50.0)
    args = p.parse_args()
    out = run_pipeline_pvlib(date_str=args.date, rh_percent=args.rh)
    print(out)
