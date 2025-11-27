import json
import pandas as pd

def save_monitored_visits_to_csv(json_input, column_decode output_csv_path):
    """
    Fully decode and flatten nested JSON `ServiceDelivery -> StopMonitoringDelivery -> MonitoredStopVisit` to a DataFrame and save as CSV.
    Args:
        json_input: Either a dict (parsed JSON) or a filepath to a JSON file.
        output_csv_path: Filepath to save the resulting CSV.
    """
    # Load JSON if given a file path
    if isinstance(json_input, str):
        with open(json_input, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
    else:
        data = json_input

    # Navigate to the monitored visits
    try:
        visits = data['ServiceDelivery']['StopMonitoringDelivery']['MonitoredStopVisit']
    except KeyError as e:
        raise ValueError(f"Missing expected key in JSON: {e}")

    # Flatten nested dicts into columns
    df = pd.json_normalize(visits, sep='.')

    # Save to CSV
    df.to_csv(output_csv_path, index=False)
    print(f"Saved monitored stop visits to {output_csv_path}")


save_monitored_visits_to_csv('stopplaces.json', 'stopplaces.csv')
