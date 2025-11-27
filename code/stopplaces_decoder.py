"""
Stop Places decoder: flatten 511 `stopplaces.json` into CSV.

This script targets the path:
`Siri -> ServiceDelivery -> DataObjectDelivery -> dataObjects -> SiteFrame -> stopPlaces -> StopPlace`.

Usage (PowerShell):
    python .\stopplaces_decoder.py --input sample\stopplaces.json
    # Output defaults to sample\stopplaces.csv (or specify --output)
"""

import json
import csv
import argparse
import os

def get_nested(d, path, default=None):
    """Safely get a nested value using dot-path notation."""
    for key in path.split('.'):
        if isinstance(d, dict):
            d = d.get(key, default)
        else:
            return default
    return d

FIELDS = [
    "@id", "Name", "PublicCode", "TransportMode",
    "Centroid.Location.Latitude", "Centroid.Location.Longitude",
    "PostalAddress.AddressLine1", "PostalAddress.Town"
]

def flatten(stop):
    """Flatten a StopPlace dict into a row list matching FIELDS order."""
    return [
        stop.get('@id'),
        stop.get('Name'),
        stop.get('PublicCode'),
        stop.get('TransportMode'),
        get_nested(stop, 'Centroid.Location.Latitude'),
        get_nested(stop, 'Centroid.Location.Longitude'),
        get_nested(stop, 'PostalAddress.AddressLine1'),
        get_nested(stop, 'PostalAddress.Town')
    ]

def convert_json_to_csv(input_filename, output_filename):
    """Convert stop places JSON to CSV with selected fields."""
    with open(input_filename) as f:
        js = json.load(f)
    # Update this path if your JSON structure changes
    stop_places = js['Siri']['ServiceDelivery']['DataObjectDelivery']['dataObjects']['SiteFrame']['stopPlaces']['StopPlace']

    with open(output_filename, 'w', newline='') as fo:
        writer = csv.writer(fo)
        writer.writerow(FIELDS)
        for stop in stop_places:
            writer.writerow(flatten(stop))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert stop places JSON to CSV.")
    parser.add_argument('--input', required=True, help='Input JSON file (e.g. stopplaces.json)')
    parser.add_argument('--output', required=False, help='Output CSV file (e.g. stopplaces.csv)')
    args = parser.parse_args()
    output_file = args.output or os.path.splitext(args.input)[0] + '.csv'
    convert_json_to_csv(args.input, output_file)
    print(f"Converted {args.input} to {output_file}.")
