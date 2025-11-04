"""Simple CLI wrapper to run the RF pipeline."""
from aeroaqua.pipelines.pipeline_rf import run_pipeline_rf
import argparse


if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Run RF pipeline')
    p.add_argument('--date', default='2025-11-04')
    p.add_argument('--cloud', type=float, default=0.0)
    p.add_argument('--rh', type=float, default=50.0)
    p.add_argument('--temp', type=float, default=20.0)
    p.add_argument('--model', type=str, default=None, help='Path to trained RF model')
    args = p.parse_args()
    out = run_pipeline_rf(date_str=args.date, cloud_type=args.cloud, rh_percent=args.rh, temperature_c=args.temp, model_path=args.model)
    print(out)
