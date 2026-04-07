import webbrowser
from pathlib import Path

import folium

from utils import format_timestamp, read_track_csv


def generate_map_preview(
    csv_path: str,
    output_html: str | None = None,
    open_browser: bool = True,
    tiles: str = "CartoDB Voyager",
) -> str:
    points = read_track_csv(csv_path)
    if not points:
        raise ValueError(f"未从 {Path(csv_path).name} 读取到有效轨迹点")

    center_lat = sum(p["latitude"] for p in points) / len(points)
    center_lon = sum(p["longitude"] for p in points) / len(points)

    m = folium.Map(location=[center_lat, center_lon], tiles=tiles, zoom_start=13)

    coords = [(p["latitude"], p["longitude"]) for p in points]
    folium.PolyLine(coords, color="blue", weight=3, opacity=0.7).add_to(m)

    start = points[0]
    end = points[-1]

    start_popup = f"""
    <b>起点</b><br>
    时间: {format_timestamp(start['dataTime'])}<br>
    经度: {start['longitude']:.6f}<br>
    纬度: {start['latitude']:.6f}<br>
    速度: {start['speed']:.2f} km/h<br>
    距离: {start['distance']:.2f} m
    """
    folium.Marker(
        [start["latitude"], start["longitude"]],
        popup=folium.Popup(start_popup, max_width=250),
        icon=folium.Icon(color="green", icon="play"),
    ).add_to(m)

    end_popup = f"""
    <b>终点</b><br>
    时间: {format_timestamp(end['dataTime'])}<br>
    经度: {end['longitude']:.6f}<br>
    纬度: {end['latitude']:.6f}<br>
    速度: {end['speed']:.2f} km/h<br>
    距离: {end['distance']:.2f} m
    """
    folium.Marker(
        [end["latitude"], end["longitude"]],
        popup=folium.Popup(end_popup, max_width=250),
        icon=folium.Icon(color="red", icon="stop"),
    ).add_to(m)

    lats = [p["latitude"] for p in points]
    lons = [p["longitude"] for p in points]
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)

    if len(points) == 1:
        m.location = [lats[0], lons[0]]
        m.zoom_start = 15
    else:
        lat_padding = max((max_lat - min_lat) * 0.08, 0.002)
        lon_padding = max((max_lon - min_lon) * 0.08, 0.002)
        m.fit_bounds(
            [
                [min_lat - lat_padding, min_lon - lon_padding],
                [max_lat + lat_padding, max_lon + lon_padding],
            ],
            padding=(24, 24),
            max_zoom=15,
        )

    if output_html is None:
        csv_stem = Path(csv_path).stem
        output_html = str(Path(csv_path).parent / f"{csv_stem}_map.html")

    m.save(output_html)

    if open_browser:
        webbrowser.open(Path(output_html).as_uri())

    return output_html
