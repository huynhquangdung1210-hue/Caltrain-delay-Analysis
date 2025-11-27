"""
API fetch utilities for 511 SF Bay Transit endpoints.

This script downloads a representative set of 511 endpoints for a given
operator (e.g., Caltrain "CT"). It saves JSON responses prettified and
GTFS-Realtime protobuf feeds as .pb files under the output directory.

Usage (PowerShell):
    python .\api_req.py

Notes:
- Update the example API key and parameters at the bottom for your environment.
- Network failures or non-OK HTTP responses are logged to the console.
- JSON responses are decoded with UTF-8 (BOM-safe) and saved with indentation.

Files produced under the output directory:
- *.json: JSON endpoints
- *.pb: Protobuf endpoints (tripupdates, vehiclepositions, servicealerts)
"""

import requests
import pandas as pd
import os
import json
from google.transit import gtfs_realtime_pb2

def download_511_data(api_key, operator_id, line_id, stop_id, output_dir='./sample'):
    """Download a selection of 511 transit endpoints for a specific operator.

    Parameters:
    - api_key: str – 511 API key.
    - operator_id: str – Agency/operator code (e.g., 'CT' for Caltrain).
    - line_id: str – Line identifier used in some endpoints.
    - stop_id: str – Stop identifier used in StopMonitoring/StopTimeTable endpoints.
    - output_dir: str – Directory to write output files (created if missing).

    Behavior:
    - Determines whether each endpoint is JSON or GTFS-Realtime protobuf.
    - Saves JSON to *.json with pretty formatting; protobuf to *.pb as raw bytes.
    - Logs warnings on failures but continues processing other endpoints.
    """
    # Map URLs to response format: True if protobuf GTFS-Realtime, False if JSON
    endpoints = {
        f"http://api.511.org/transit/gtfsoperators?api_key={api_key}": False,
        f"http://api.511.org/transit/datafeeds?api_key={api_key}&operator_id={operator_id}": False,
        f"http://api.511.org/transit/tripupdates?api_key={api_key}&agency={operator_id}": True,
        f"http://api.511.org/transit/vehiclepositions?api_key={api_key}&agency={operator_id}": True,
        f"http://api.511.org/transit/servicealerts?api_key={api_key}&agency={operator_id}": True,
        f"http://api.511.org/transit/StopMonitoring?api_key={api_key}&agency={operator_id}": False,
        f"http://api.511.org/transit/VehicleMonitoring?api_key={api_key}&agency={operator_id}": False,
        f"http://api.511.org/transit/operators?api_key={api_key}": False,
        f"http://api.511.org/transit/lines?api_key={api_key}&operator_id={operator_id}": False,
        f"http://api.511.org/transit/stops?api_key={api_key}&operator_id={operator_id}": False,
        f"http://api.511.org/transit/stopplaces?api_key={api_key}&operator_id={operator_id}": False,
        f"http://api.511.org/transit/patterns?api_key={api_key}&operator_id={operator_id}&line_id={line_id}": False,
        f"http://api.511.org/transit/timetable?api_key={api_key}&operator_id={operator_id}&line_id={line_id}": False,
        f"http://api.511.org/transit/stoptimetable?api_key={api_key}&operatorref={operator_id}&monitoringref={stop_id}": False
    }

    os.makedirs(output_dir, exist_ok=True)

    for url, is_protobuf in endpoints.items():
        endpoint_name = url.split('/transit/')[1].split('?')[0]
        response = requests.get(url)
        # Save JSON response to file (pretty-printed) or protobuf bytes
        if response.ok:
            try:
                if is_protobuf:
                    feed = gtfs_realtime_pb2.FeedMessage()
                    feed.ParseFromString(response.content)
                    file_path = os.path.join(output_dir, f"{endpoint_name}.pb")
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    print(f"Saved protobuf data to {file_path}")
                else:
                    # Decode raw bytes safely (skip BOM if present) and pretty dump
                    raw_bytes = response.content
                    # Decode safely, skipping BOM if present
                    content = raw_bytes.decode('utf-8-sig')
                    # Load JSON data
                    json_obj = json.loads(content)
                    file_path = os.path.join(output_dir, f"{endpoint_name}.json")
                    with open(file_path, "w") as f:
                        json.dump(json_obj, f, indent=2)
                    print(f"Saved JSON data to {file_path}")
            except Exception as e:
                print(f"Failed to parse or save data for {endpoint_name}: {e}")
        else:
            print(f"Failed to download from {url} with status code {response.status_code}")

# Example usage
download_511_data('96791879-a293-4ebc-80ca-1543dc9be3a2', 'CT', 'LOCAL', '70221')
