"""
Downloader for monthly 511 historical datafeeds (zipped GTFS bundles).

Given a period [start, end] inclusive (by month), this script downloads
`511_data_YYYY-MM.zip` files to a target directory (default: `trial`).

These archives can be used by the analysis notebook to load
`stop_observations.txt` from each zip and concatenate them.

Usage (PowerShell):
    python .\api_req_2.py

Customize the parameters in the __main__ guard as needed.
"""

import requests
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta

def get_datafeeds(api_key, operator_id, period_start, period_end, output_dir):
    """Download monthly 511 datafeed archives for a given operator.

    Parameters:
    - api_key: str – 511 API key.
    - operator_id: str – Agency/operator code (e.g., 'CT' for Caltrain).
    - period_start: datetime – Inclusive start (only year/month used).
    - period_end: datetime – Inclusive end (only year/month used).
    - output_dir: str – Directory to save `511_data_YYYY-MM.zip` files.

    Notes:
    - The endpoint expects the `historic` query param in 'YYYY-MM' format.
    - HTTP failures are logged; successful responses are written to disk.
    """
    os.makedirs(output_dir, exist_ok=True)
    current = period_start
    while current <= period_end:
        ym = current.strftime('%Y-%m')
        fname = f"511_data_{ym}.zip"
        url = f"http://api.511.org/transit/datafeeds?api_key={api_key}&operator_id={operator_id}&historic={ym}"
        path = os.path.join(output_dir, fname)
        print(f"Downloading: {url}")
        resp = requests.get(url)
        if resp.ok:
            with open(path, 'wb') as f:
                f.write(resp.content)
            print(f"Saved {fname}")
        else:
            print(f"Failed for {ym}: {resp.status_code}")
        current += relativedelta(months=1)

if __name__ == "__main__":
    # Example usage:
    api_key = "96791879-a293-4ebc-80ca-1543dc9be3a2"
    operator_id = "CT"
    period_start = datetime(2018, 1, 1)
    period_end = datetime(2025, 12, 1)
    output_dir = "trial"
    get_datafeeds(api_key, operator_id, period_start, period_end, output_dir)
