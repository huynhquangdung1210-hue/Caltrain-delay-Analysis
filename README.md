# 511 Transit Data Pipeline & Delay Analysis

**Automated data acquisition, transformation, and visualization toolkit for SF Bay Area 511 Transit API with focus on Caltrain service reliability metrics.**

## Project Overview

Production-grade Python pipeline for:
- **Data Collection**: Automated download of 14 distinct 511 API endpoints (GTFS-Realtime protobuf + SIRI JSON)
- **Historical Archives**: Batch retrieval of 70+ monthly GTFS datafeeds spanning January 2018 to December 2025 (~11 GB compressed)
- **ETL Processing**: Memory-efficient chunked parsing with early filtering, handling 350K+ stop observations
- **Statistical Analysis**: Kernel Density Estimation (KDE) and departure delay quantification by route and time-of-day

### Key Metrics
- **Data Volume**: 70 monthly archives totaling 11.02 GB (as of current workspace state)
- **API Coverage**: 14 endpoint types including real-time vehicle positions, stop monitoring, and timetables
- **Target Operator**: Caltrain (CT) with extensibility to 20+ Bay Area transit agencies
- **Processing Efficiency**: Chunked streaming (100K rows/chunk) with dtype optimization to handle memory-constrained environments

---

## System Requirements

### Dependencies
Install required packages via pip:

```powershell
python -m pip install requests pandas gtfs-realtime-bindings python-dateutil seaborn matplotlib numpy
```

**Version Requirements:**
- Python 3.8+
- pandas ≥1.3.0 (for `on_bad_lines` parameter)
- matplotlib ≥3.4.0
- seaborn ≥0.11.0

### API Access
Obtain a 511 API key from [511.org/developers](https://511.org/developers). Free tier supports:
- 1,000 requests/day
- Historical datafeed access (unlimited monthly archives)
- Real-time feeds updated every 30-60 seconds

---

## Quick Start

### 1. Download Historical Data (2018-2025)
Retrieve 96 months of Caltrain GTFS archives:

```powershell
# Edit api_req_2.py line 54 to insert your API key
python .\api_req_2.py
```

**Expected Output:**
- 70+ zip files in `trial/` directory (varies by 511 data availability)
- Naming convention: `511_data_YYYY-MM.zip`
- Average file size: ~160 MB compressed
- Total download time: ~45-60 minutes (depends on network speed)

### 2. Download Current Real-Time Snapshots
Fetch 14 endpoint types for immediate analysis:

```powershell
# Edit api_req.py line 91 to insert your API key
python .\api_req.py
```

**Expected Output:**
- 11 JSON files (SIRI format): operators, lines, stops, monitoring feeds
- 3 protobuf files: tripupdates, vehiclepositions, servicealerts
- Output directory: `sample/`
- Execution time: ~15-20 seconds

### 3. Run Delay Analysis Notebook
Open `graph.ipynb` in Jupyter or VS Code and execute cells sequentially:

**Cell 3 (Data Loading):**
- Scans `trial/` for all `511_data_*.zip` archives
- Streams `stop_observations.txt` from each zip in 100K-row chunks
- Filters to Caltrain trips (`CT:` prefix) before concatenation
- Adds `obs_month` column for temporal analysis

**Cell 5 (Cleaning & Transformation):**
- Parses HH:MM:SS time strings to datetime
- Computes `arr_diff_min` and `dep_diff_min` (delay in minutes)
- Creates `departure_hour` (decimal hours 0-24) for time-of-day analysis
- Exports `CT_filt.csv` with cleaned dataset

**Cells 7-11 (Visualizations):**
- Scatter plots: delay vs. scheduled time colored by stop sequence, trip ID, route
- 1D KDE: departure delay distributions by route (overlay plot)
- 2D KDE: density heatmaps showing delay patterns across day (stacked subplots)

**Performance Note:** Loading 70 archives processes ~10-15 million rows. Expect 5-10 minutes runtime on typical hardware.

---

## Visualization Gallery

**Departure Delay vs Scheduled Time (colored by Route)**
![Departure Delay vs Scheduled Time (colored by Route)](visualizations/fin_Departure%20Delay%20vs%20Scheduled%20Time%20%E2%80%94%20colored%20by%20Route.png)

**1D KDE of Departure Delay by Route**
![1D KDE of Departure Delay by Route](visualizations/fin_1D%20KDE%20of%20Departure%20Delay%20by%20Route.png)

**2D KDE of Departure Delay by Route with Scatter**
![2D KDE of Departure Delay by Route with Scatter](visualizations/fin_2D%20KDE%20of%20Departure%20Delay%20by%20Route%20with%20Scatter.png)

---

## Data Transformation Scripts

### Real-Time Feed Decoders
Convert complex nested JSON to flat CSVs for analysis:

**StopMonitoring Decoder**
```powershell
python .\StopMonitoring_decoder.py
```
- **Input:** `sample/StopMonitoring.json` (SIRI ServiceDelivery format)
- **Output:** `sample/StopMonitoring.csv` with 14 columns including aimed/expected arrival times
- **Use Case:** Per-stop real-time predictions

**VehicleMonitoring Decoder**
```powershell
python .\VehicleMonitoring_decoder.py --input sample\VehicleMonitoring.json
```
- **Input:** SIRI VehicleActivity JSON
- **Output:** Flattened CSV with both MonitoredCall (current stop) and OnwardCall (future stops) rows
- **Schema:** RecordedAtTime, VehicleRef, LineRef, DirectionRef, lat/lon, aimed/expected times
- **Use Case:** Vehicle trajectory analysis and dwell time calculations

**Stops & Places Decoders**
```powershell
python .\stops_decoder.py sample\stops.json sample\stops.csv
python .\stopplaces_decoder.py --input sample\stopplaces.json
```
- **stops.json:** ScheduledStopPoint with extensions (ParentStation, ValidBetween, coordinates)
- **stopplaces.json:** NeTEx StopPlace with postal addresses and transport modes
- **Use Case:** Geocoding, service area analysis, accessibility mapping

---

## Configuration & Customization

### Modify API Request Parameters

**api_req_2.py** (lines 54-59):
```python
api_key = "YOUR_511_API_KEY"
operator_id = "CT"  # Change to SF, AC, VTA, etc.
period_start = datetime(2023, 1, 1)  # Adjust date range
period_end = datetime(2024, 12, 1)
output_dir = "data"  # Change output directory
```

### Notebook Analysis Parameters

**graph.ipynb Cell 10** (1D KDE):
```python
fig, ax = plot_kde_by_route(
    df, 
    value_col='dep_diff_min',  # or 'arr_diff_min'
    category_col='route_id',   # group by route
    top_n=6,                    # analyze top N routes by frequency
    xlim=(-5, 10)               # focus on -5 to +10 minute delays
)
```

**graph.ipynb Cell 11** (2D KDE):
```python
fig, axes = plot_2d_kde_by_route(
    df, 
    x_col='departure_hour',     # time of day (0-24)
    y_col='dep_diff_min',       # delay magnitude
    top_n=6,                     # number of routes
    levels=12,                   # contour density
    cmap='viridis',              # colormap ('pastel', 'rocket', etc.)
    ylim=(-5, 20),               # y-axis range
    subplot_height=3.5           # inches per route subplot
)
```

---

## Data Schema Reference

### stop_observations.txt (from 511 archives)
Key columns after cleaning (`CT_filt.csv`):
- `trip_id`: Format `CT:<trip_code>:<YYYYMMDD>` (e.g., `CT:102:20250101`)
- `route_id`: Route identifier (e.g., `LOCAL`, `LIMITED`, `BABY BULLET`)
- `stop_sequence`: Integer order within trip (1-based)
- `scheduled_arrival_time`, `observed_arrival_time`: HH:MM:SS format
- `scheduled_departure_time`, `observed_departure_time`: HH:MM:SS format
- `arr_diff_min`, `dep_diff_min`: Computed delays in minutes (positive = late)
- `departure_hour`: Decimal hours (e.g., 9.5 = 09:30)
- `obs_month`: YYYY-MM extraction from source archive filename

---

## Troubleshooting

### Memory Errors During Load
**Symptom:** `Unable to allocate X MiB for an array`

**Solution:** Current implementation uses chunked reading (100K rows) with early filtering. If issues persist:
1. Reduce `chunksize` in `graph.ipynb` Cell 3 (line 148): `chunksize=50_000`
2. Process archives individually by modifying `zip_paths` filter
3. Increase system swap/pagefile allocation

### Mixed Type Warnings
**Symptom:** `DtypeWarning: Columns (1,3) have mixed types`

**Resolution:** Handled via `dtype=str` and `low_memory=False` in Cell 3. Time parsing occurs in Cell 5 with `errors='coerce'`.

### Empty Dataset After Load
**Check:**
1. Archive location: Verify `trial/` or `data/` contains `511_data_*.zip` files
2. File contents: Open a sample zip and confirm `stop_observations.txt` exists (not `stop_times.txt`)
3. Trip filter: Ensure trips in archives match `CT:` prefix (for Caltrain)

---

## Performance Benchmarks

Hardware: Intel i7-10700K, 32 GB RAM, SSD storage

| Task | Duration | Output |
|------|----------|--------|
| Download 96 monthly archives | 45-60 min | 11.02 GB (70 files) |
| Notebook Cell 3 (load 70 zips) | 8-12 min | ~350K filtered rows in memory |
| Notebook Cell 5 (cleaning) | 15-30 sec | `CT_filt.csv` (varies by row count) |
| Generate all 5 plots | 30-45 sec | PNG exports |

---

## License & Attribution

Data provided by [SF Bay 511](https://511.org) via API. Review [511 Terms of Service](https://511.org/terms-conditions) for usage restrictions.

**Academic Citation:**
If using this toolkit for research, cite the 511 Open Data Portal and acknowledge the Metropolitan Transportation Commission (MTC).

---

## Support & Contributions

**Questions about metrics, analysis methods, or extending to other operators?**  
Open an issue or submit a pull request with your enhancement.

**511 API Changes:**  
Monitor [511 Developer Portal](https://511.org/developers) for schema updates. Decoder scripts may require path adjustments if SIRI/GTFS formats change.
