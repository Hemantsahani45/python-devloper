
**Setup**

- Create a Python virtual environment (recommended) and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate    # Linux/macOS
.venv\Scripts\activate     # Windows (cmd)
pip install -r requirements.txt
```

**Local run**

Run the processing script locally (writes `metrics.json`, `metrics_processed.csv`, `metrics_stats.json`, and `run.log`):

```bash
python run.py --input data.csv --config config.yaml --output metrics.json --log-file run.log
```

After running you'll find:
- `metrics.json` — summary JSON output (requested `--output` file)
- `metrics_processed.csv` — processed CSV (derived from `metrics.json` base name)
- `metrics_stats.json` — detailed numeric stats
- `run.log` — log file

**Docker**

Build the image:

```bash
docker build -t mlops-task .
```

Run the container (writes outputs inside container):

```bash
docker run --rm mlops-task
```

To persist outputs to the host (Windows example):

```powershell
docker run --rm -v "%cd%":/app mlops-task
```

**Example `metrics.json` output**

```json
{
  "version": "v1",
  "rows_processed": 100,
  "metric": "signal_rate",
  "value": 0.5123,
  "latency_ms": 125,
  "seed": 42,
  # mlops-task

  ## Setup Instructions

  ### Install dependencies

  Run:

  ```bash
  pip install -r requirements.txt
  ```

  ## Local Execution Instructions

  ### Run locally

  Run the processing script with the example arguments below (the backslash shows a multi-line command):

  ```bash
  python run.py --input data.csv --config config.yaml \
    --output metrics.json --log-file run.log
  ```

  After a successful run the script will produce `metrics.json`, a processed CSV derived from the output base name (e.g. `metrics_processed.csv`), a stats file (e.g. `metrics_stats.json`), and `run.log`.

  ## Docker Instructions

  ### Build the Docker image

  ```bash
  docker build -t mlops-task .
  ```

  ### Run the container

  ```bash
  docker run --rm mlops-task
  ```

  When run in Docker the container will include `data.csv` and `config.yaml`, execute automatically on startup, write `metrics.json` and `run.log` inside the container, print the final metrics to stdout, and exit with code `0` on success.

  ## Expected Output

  The container/script prints the final `metrics.json` structure to stdout. Example visual representation:

  ```json
  {
    "version": "v1",
    "rows_processed": 100,
    "metric": "signal_rate",
    "value": 0.5123,
    "latency_ms": 125,
    "seed": 42,
    "status": "success"
  }
  ```

  ## Dependencies

  The project requires the following Python packages (also listed in `requirements.txt`):

  - pandas
  - numpy
  - pyyaml

  ## Notes

  - To persist output files from the container to the host, mount the current directory into `/app` when running Docker (example for Windows cmd/powershell):

  ```powershell
  docker run --rm -v "%cd%":/app mlops-task
  ```

  - If you see Docker daemon errors on Windows, ensure Docker Desktop (WSL2 backend) is installed and running.
