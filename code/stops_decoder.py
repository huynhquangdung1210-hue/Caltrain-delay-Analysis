"""
Stops decoder: flatten 511 `stops.json` into a tabular CSV.

The schema extracts a subset of fields including basic metadata, location,
and validity period from the JSON structure under
`Contents -> dataObjects -> ScheduledStopPoint`.

Usage (PowerShell):
    python .\stops_decoder.py sample\stops.json sample\stops.csv
"""

import json
import pandas as pd
import argparse


def flatten_stop(stop):
    """Flatten a single stop JSON object to a row dict."""
    exts = stop.get('Extensions', {})
    valid = exts.get('ValidBetween', {})
    loc = stop.get('Location', {})
    return {
        'id': stop.get('id'),
        'Name': stop.get('Name'),
        'ParentStation': exts.get('ParentStation'),
        'Latitude': loc.get('Latitude'),
        'Longitude': loc.get('Longitude'),
        'FromDate': valid.get('FromDate'),
        'ToDate': valid.get('ToDate'),
        'StopType': stop.get('StopType'),
    }

def convert_json_to_csv(input_filename, output_filename):
    """Convert a stops JSON file to CSV with a simple flattened schema."""
    with open(input_filename) as f:
        js = json.load(f)
    stops = js['Contents']['dataObjects']['ScheduledStopPoint']
    rows = [flatten_stop(stop) for stop in stops]
    df = pd.DataFrame(rows)
    df.to_csv(output_filename, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert JSON to CSV.")
    parser.add_argument('input', help='Input JSON filename')
    parser.add_argument('output', help='Output CSV filename')
    args = parser.parse_args()
    convert_json_to_csv(args.input, args.output)
