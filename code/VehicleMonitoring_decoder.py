"""
VehicleMonitoring decoder: convert 511 VehicleMonitoring JSON to a flat CSV.

Supports both "MonitoredCall" (current stop) and any available "OnwardCall"
entries, emitting a unified table with a `CallType` column.

Usage (PowerShell):
    python .\VehicleMonitoring_decoder.py --input sample\VehicleMonitoring.json
    # Output defaults to sample\VehicleMonitoring.csv unless --output is provided
"""

import json
import pandas as pd
import argparse
import os

def extract_vehicle_rows(json_obj):
    """Extract rows from a VehicleMonitoring JSON object.

    Parameters:
    - json_obj: dict – Parsed JSON.

    Returns:
    - list[dict]: One row per MonitoredCall and per OnwardCall.
    """
    vehicle_activities = json_obj["Siri"]["ServiceDelivery"]["VehicleMonitoringDelivery"]["VehicleActivity"]
    rows = []
    for activity in vehicle_activities:
        journey = activity.get("MonitoredVehicleJourney", {})
        vehicle_base = {
            "RecordedAtTime": activity.get("RecordedAtTime"),
            "LineRef": journey.get("LineRef"),
            "DirectionRef": journey.get("DirectionRef"),
            "VehicleRef": journey.get("VehicleRef"),
            "OriginName": journey.get("OriginName"),
            "DestinationName": journey.get("DestinationName"),
            "VehicleLocation.Latitude": journey.get("VehicleLocation", {}).get("Latitude"),
            "VehicleLocation.Longitude": journey.get("VehicleLocation", {}).get("Longitude"),
        }
        call = journey.get("MonitoredCall", {})
        row = vehicle_base.copy()
        row.update({
            "CallType": "MonitoredCall",
            "StopPointRef": call.get("StopPointRef"),
            "StopPointName": call.get("StopPointName"),
            "AimedArrivalTime": call.get("AimedArrivalTime"),
            "ExpectedArrivalTime": call.get("ExpectedArrivalTime"),
            "AimedDepartureTime": call.get("AimedDepartureTime"),
            "ExpectedDepartureTime": call.get("ExpectedDepartureTime"),
        })
        rows.append(row)
        onward_calls = journey.get("OnwardCalls", {}).get("OnwardCall", [])
        for onward in onward_calls:
            onward_row = vehicle_base.copy()
            onward_row.update({
                "CallType": "OnwardCall",
                "StopPointRef": onward.get("StopPointRef"),
                "StopPointName": onward.get("StopPointName"),
                "AimedArrivalTime": onward.get("AimedArrivalTime"),
                "ExpectedArrivalTime": onward.get("ExpectedArrivalTime"),
                "AimedDepartureTime": onward.get("AimedDepartureTime"),
                "ExpectedDepartureTime": onward.get("ExpectedDepartureTime"),
            })
            rows.append(onward_row)
    return rows

def convert_json_to_csv(input_file, output_file):
    """Convert a VehicleMonitoring JSON file to CSV.

    Parameters:
    - input_file: str – Path to input JSON file.
    - output_file: str – Path to output CSV file.
    """
    with open(input_file) as f:
        js = json.load(f)
    rows = extract_vehicle_rows(js)
    df = pd.DataFrame(rows)
    df.to_csv(output_file, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert VehicleMonitoring JSON to CSV.")
    parser.add_argument('--input', required=True, help='Input JSON filename')
    parser.add_argument('--output', required=False, help='Output CSV filename')
    args = parser.parse_args()
    out_file = args.output or os.path.splitext(args.input)[0] + '.csv'
    convert_json_to_csv(args.input, out_file)
    print(f"Converted {args.input} to {out_file}.")
