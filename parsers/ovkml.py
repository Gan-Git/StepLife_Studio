from utils import build_rows, interpolate_timestamps, parse_beijing_time, parse_coordinate_pairs


def convert_ovkml(input_path: str, start_time: str, end_time: str) -> list[dict]:
    with open(input_path, "r", encoding="utf-8") as f:
        xml_text = f.read()

    points = parse_coordinate_pairs(xml_text)
    timestamps = interpolate_timestamps(
        parse_beijing_time(start_time),
        parse_beijing_time(end_time),
        len(points),
    )
    return build_rows(points, timestamps)
