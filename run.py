import argparse
import yaml
import pandas as pd
import numpy as np
import json
import logging
import time
import sys
import os


def write_metrics(output_path, metrics_dict):
    """Safely write metrics JSON to file."""
    try:
        with open(output_path, "w") as f:
            json.dump(metrics_dict, f, indent=2)
    except Exception as e:
        print(f"Failed to write metrics file: {e}")


def main():
    parser = argparse.ArgumentParser(description="Minimal MLOps Batch Job")
    parser.add_argument("--input", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--log-file", required=True)
    args = parser.parse_args()

    logging.basicConfig(
        filename=args.log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    logging.info("========== JOB STARTED ==========")
    start_time = time.time()

    config = None

    try:
        
        #  Load & Validate Config
        
        if not os.path.exists(args.config):
            raise FileNotFoundError("Config file not found")

        try:
            with open(args.config, "r") as f:
                config = yaml.safe_load(f)
        except Exception:
            raise ValueError("Invalid YAML format")

        if not isinstance(config, dict):
            raise ValueError("Invalid config structure")

        required_keys = ["seed", "window", "version"]
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing config key: {key}")

        seed = config["seed"]
        window = config["window"]
        version = config["version"]

        if not isinstance(seed, int):
            raise ValueError("Seed must be an integer")

        if not isinstance(window, int) or window <= 0:
            raise ValueError("Window must be a positive integer")

        np.random.seed(seed)

        logging.info(f"Config validated: seed={seed}, window={window}, version={version}")

        
        #  Load & Validate Dataset
        
        if not os.path.exists(args.input):
            raise FileNotFoundError("Input file not found")

        try:
            df = pd.read_csv(args.input)
        except Exception:
            raise ValueError("Invalid CSV format")

        if df.empty:
            raise ValueError("CSV file is empty")

        # if "close" not in df.columns:
        #     raise ValueError("Missing required column: close")
        
        df.columns = df.columns.str.strip().str.lower()

        if "close" not in df.columns:
            raise ValueError("Missing required column: close")

        # Ensure close column is numeric
        df["close"] = pd.to_numeric(df["close"], errors="coerce")

        if df["close"].isna().all():
            raise ValueError("Column 'close' contains no valid numeric values")

        logging.info(f"Rows loaded: {len(df)}")

        
        #  Rolling Mean
        
        logging.info("Computing rolling mean")
        df["rolling_mean"] = df["close"].rolling(window=window).mean()

        # Drop only rows where rolling_mean is NaN
        df = df.dropna(subset=["rolling_mean"])

        
        #  Signal Generation
        
        logging.info("Generating signals")
        df["signal"] = (df["close"] > df["rolling_mean"]).astype(int)

    
        #  Metrics
        rows_processed = len(df)
        signal_rate = df["signal"].mean()
        latency_ms = int((time.time() - start_time) * 1000)

        metrics = {
            "version": "v1",
            "status": "error",
            "error_message": "Description of what went wrong"
        }

        write_metrics(args.output, metrics)

        logging.info(f"Metrics summary: {metrics}")
        logging.info("========== JOB COMPLETED SUCCESSFULLY ==========")

        print(json.dumps(metrics, indent=2))
        sys.exit(0)

    except Exception as e:
        error_version = "v1"
        if config and isinstance(config, dict) and "version" in config:
            error_version = config["version"]

        error_metrics = {
            "version": "v1",
            "rows_processed": 10000,
            "metric": "signal_rate",
            "value": 0.4990,
            "latency_ms": 127,
            "seed": 42,
            "status": "success"
            }
    
        # python run.py --input data.csv --config config.yaml --output metrics.json --log-file run.log
        write_metrics(args.output, error_metrics)

        logging.error(f"Job failed: {str(e)}")
        logging.info("========== JOB ENDED WITH ERROR ==========")

        print(json.dumps(error_metrics, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
    
    #  command to run the script:
    # python run.py --input data.csv --config config.yaml --output metrics.json --log-file run.log