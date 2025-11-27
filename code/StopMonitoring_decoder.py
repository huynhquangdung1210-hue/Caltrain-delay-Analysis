"""
StopMonitoring decoder: convert 511 StopMonitoring JSON to a flat CSV.

Reads `sample/StopMonitoring.json`, extracts a minimal set of useful fields,
and writes `sample/StopMonitoring.csv`.

This script is a simple example; adjust the fields in `extract_monitored_stop_visits`
to suit your needs or extend the schema.
"""

import json
import pandas as pd

def extract_monitored_stop_visits(monitored_list):
    """Flatten a list of MonitoredStopVisit objects into rows for a DataFrame.

    Parameters:
    - monitored_list: list[dict] – The `MonitoredStopVisit` array from the JSON.

    Returns:
    - list[dict]: Each dict corresponds to a CSV row with selected fields.
    """
    rows = []
    for visit in monitored_list:
        journey = visit["MonitoredVehicleJourney"]
        call = journey["MonitoredCall"]
        vehicle_location = journey.get("VehicleLocation", {})
        row = {
            "RecordedAtTime": visit.get("RecordedAtTime"),
            "MonitoringRef": visit.get("MonitoringRef"),
            "LineRef": journey.get("LineRef"),
            "DirectionRef": journey.get("DirectionRef"),
            "VehicleRef": journey.get("VehicleRef"),
            "OriginName": journey.get("OriginName"),
            "DestinationName": journey.get("DestinationName"),
            "StopPointName": call.get("StopPointName"),
            "VehicleLocation.Latitude": vehicle_location.get("Latitude"),
            "VehicleLocation.Longitude": vehicle_location.get("Longitude"),
            "AimedArrivalTime": call.get("AimedArrivalTime"),
            "ExpectedArrivalTime": call.get("ExpectedArrivalTime"),
            "AimedDepartureTime": call.get("AimedDepartureTime"),
            "ExpectedDepartureTime": call.get("ExpectedDepartureTime"),
        }
        rows.append(row)
    return rows

# Input JSON -> DataFrame -> CSV
with open('sample/StopMonitoring.json') as f:
    js = json.load(f)

monitored_list = js['ServiceDelivery']['StopMonitoringDelivery']['MonitoredStopVisit']
rows = extract_monitored_stop_visits(monitored_list)
df = pd.DataFrame(rows)
df.to_csv('sample/StopMonitoring.csv', index=False)
