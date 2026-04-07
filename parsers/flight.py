import csv
from pathlib import Path

from utils import calculate_distance, format_number


def convert_flight_csv(input_path: str) -> list[dict]:
    rows = []
    previous = None
    cumulative_distance = 0.0

    with open(input_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for item in reader:
            utc_timestamp = int(float(item["Time"]))
            beijing_timestamp = utc_timestamp + 8 * 3600
            longitude = float(item["Longitude"])
            latitude = float(item["Latitude"])

            if previous is not None:
                cumulative_distance += calculate_distance(previous[0], previous[1], longitude, latitude)

            rows.append(
                {
                    "dataTime": beijing_timestamp,
                    "locType": 1,
                    "longitude": format_number(longitude),
                    "latitude": format_number(latitude),
                    "heading": int(float(item.get("Angle", 0) or 0)),
                    "accuracy": -20,
                    "speed": format_number(float(item.get("Speed", 0) or 0)),
                    "distance": format_number(cumulative_distance),
                    "isBackForeground": 1,
                    "stepType": 0,
                    "altitude": format_number(float(item.get("Height", 0) or 0)),
                }
            )
            previous = (longitude, latitude)
    if not rows:
        raise ValueError(f"未从 {Path(input_path).name} 读取到任何航班数据")
    return rows
