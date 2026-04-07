import csv
import os
import re
from datetime import datetime
from math import atan2, cos, radians, sin, sqrt, degrees
from typing import Iterable, List, Sequence

OUTPUT_HEADERS = [
    "dataTime",
    "locType",
    "longitude",
    "latitude",
    "heading",
    "accuracy",
    "speed",
    "distance",
    "isBackForeground",
    "stepType",
    "altitude",
]


def parse_beijing_time(time_str: str) -> int:
    normalized = (
        time_str.strip()
        .replace("：", ":")
        .replace("（", "(")
        .replace("）", ")")
    )
    dt = datetime.strptime(normalized, "%Y-%m-%d %H:%M")
    return int(dt.timestamp())


def interpolate_timestamps(start_ts: int, end_ts: int, count: int) -> List[int]:
    if count <= 0:
        return []
    if count == 1:
        return [start_ts]
    if end_ts < start_ts:
        raise ValueError("结束时间不能早于开始时间")

    step = (end_ts - start_ts) / (count - 1)
    return [int(round(start_ts + step * i)) for i in range(count)]


def extract_coordinates_text(xml_text: str) -> str:
    match = re.search(r"<coordinates>(.*?)</coordinates>", xml_text, re.S)
    if not match:
        raise ValueError("未找到 coordinates 节点")
    return match.group(1).strip()


def parse_coordinate_pairs(xml_text: str) -> List[tuple[float, float, float]]:
    coordinates_text = extract_coordinates_text(xml_text)
    points = []
    for item in coordinates_text.split():
        parts = item.split(",")
        if len(parts) < 2:
            continue
        lon = float(parts[0])
        lat = float(parts[1])
        alt = float(parts[2]) if len(parts) >= 3 and parts[2] else 0.0
        points.append((lon, lat, alt))
    if not points:
        raise ValueError("未解析到任何坐标点")
    return points


def calculate_distance(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """计算两点间距离（米），使用 Haversine 公式"""
    R = 6371000
    phi1 = radians(lat1)
    phi2 = radians(lat2)
    delta_phi = radians(lat2 - lat1)
    delta_lambda = radians(lon2 - lon1)

    a = sin(delta_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(delta_lambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def calculate_heading(prev_lon: float, prev_lat: float, lon: float, lat: float) -> int:
    if prev_lon == lon and prev_lat == lat:
        return 0

    lon1 = radians(prev_lon)
    lat1 = radians(prev_lat)
    lon2 = radians(lon)
    lat2 = radians(lat)

    dlon = lon2 - lon1
    x = sin(dlon) * cos(lat2)
    y = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)
    bearing = degrees(atan2(x, y))
    return int(round((bearing + 360) % 360))


def build_rows(points: Sequence[tuple[float, float, float]], timestamps: Sequence[int]) -> List[dict]:
    if len(points) != len(timestamps):
        raise ValueError("坐标点数量与时间戳数量不一致")

    rows = []
    previous = None
    cumulative_distance = 0.0

    for (lon, lat, alt), ts in zip(points, timestamps):
        heading = 0
        distance_from_prev = 0.0
        speed_kmh = 0.0

        if previous is not None:
            prev_lon, prev_lat, prev_ts = previous
            heading = calculate_heading(prev_lon, prev_lat, lon, lat)
            distance_from_prev = calculate_distance(prev_lon, prev_lat, lon, lat)
            cumulative_distance += distance_from_prev

            time_diff = ts - prev_ts
            if time_diff > 0:
                speed_ms = distance_from_prev / time_diff
                speed_kmh = speed_ms * 3.6

        rows.append(
            {
                "dataTime": ts,
                "locType": 1,
                "longitude": f"{lon:.8f}",
                "latitude": f"{lat:.8f}",
                "heading": heading,
                "accuracy": -20,
                "speed": format_number(speed_kmh),
                "distance": format_number(cumulative_distance),
                "isBackForeground": 1,
                "stepType": 0,
                "altitude": format_number(alt),
            }
        )
        previous = (lon, lat, ts)
    return rows


def format_number(value: float | int) -> str:
    if isinstance(value, int):
        return str(value)
    text = f"{value:.8f}".rstrip("0").rstrip(".")
    return text if text else "0"


def read_track_csv(csv_path: str) -> List[dict]:
    points: List[dict] = []
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            longitude = row.get("longitude")
            latitude = row.get("latitude")
            data_time = row.get("dataTime")
            if not longitude or not latitude or not data_time:
                continue
            try:
                points.append(
                    {
                        "dataTime": int(float(data_time)),
                        "longitude": float(longitude),
                        "latitude": float(latitude),
                        "heading": float(row.get("heading", 0) or 0),
                        "speed": float(row.get("speed", 0) or 0),
                        "distance": float(row.get("distance", 0) or 0),
                        "altitude": float(row.get("altitude", 0) or 0),
                    }
                )
            except ValueError:
                continue
    points.sort(key=lambda item: item["dataTime"])
    return points


def format_timestamp(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def write_output(rows: Iterable[dict], output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_HEADERS)
        writer.writeheader()
        for row in rows:
            normalized = {key: row.get(key, "") for key in OUTPUT_HEADERS}
            writer.writerow(normalized)
