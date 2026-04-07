from pathlib import Path

from map_preview import generate_map_preview
from parsers import convert_flight_csv, convert_kml, convert_ovkml
from utils import write_output
from web_viewer import generate_web_viewer

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"


def prompt_file_path(prompt: str) -> str:
    while True:
        value = input(prompt).strip().strip('"')
        if not value:
            print(f"输入不能为空，请重新输入。可直接填写文件名，默认会先在 {DATA_DIR.name}/ 下查找。")
            continue
        path = Path(value)
        if not path.is_absolute():
            direct_path = BASE_DIR / path
            data_path = DATA_DIR / path
            path = direct_path if direct_path.exists() else data_path
        if not path.exists():
            print("文件不存在，请重新输入。")
            continue
        return str(path)


def prompt_time(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if not value:
            print("时间不能为空，请重新输入。")
            continue
        normalized = value.replace("：", ":")
        parts = normalized.split(" ")
        if len(parts) == 2 and len(parts[0].split("-")) == 3 and len(parts[1].split(":")) == 2:
            return normalized
        print("时间格式应为 2024-01-03 08:30，请重新输入。")


def prompt_output_name(default_name: str, suffix: str = ".csv") -> str:
    value = input(f"输出文件名（直接回车则使用 {default_name}）：").strip().strip('"')
    name = value or default_name
    if not name.lower().endswith(suffix.lower()):
        name += suffix
    return str(OUTPUT_DIR / name)


def prompt_yes_no(prompt: str) -> bool:
    value = input(prompt).strip().lower()
    return value in {"y", "yes", "是", "1"}


def maybe_preview_csv(csv_path: str) -> None:
    if not prompt_yes_no("是否立即生成地图预览？(y/N)："):
        return
    html_path = generate_map_preview(csv_path)
    print(f"地图预览已生成：{html_path}")


def handle_flight() -> None:
    input_path = prompt_file_path("请输入航班 CSV 文件路径：")
    output_path = prompt_output_name("flight_output.csv")
    rows = convert_flight_csv(input_path)
    write_output(rows, output_path)
    print(f"转换完成，共输出 {len(rows)} 行：{output_path}")
    maybe_preview_csv(output_path)


def handle_kml() -> None:
    input_path = prompt_file_path("请输入 KML 文件路径：")
    start_time = prompt_time("请输入起始时间（北京时间，格式 2024-01-03 08:30）：")
    end_time = prompt_time("请输入结束时间（北京时间，格式 2024-01-03 09:30）：")
    output_path = prompt_output_name("kml_output.csv")
    rows = convert_kml(input_path, start_time, end_time)
    write_output(rows, output_path)
    print(f"转换完成，共输出 {len(rows)} 行：{output_path}")
    maybe_preview_csv(output_path)


def handle_ovkml() -> None:
    input_path = prompt_file_path("请输入 OVKML 文件路径：")
    start_time = prompt_time("请输入起始时间（北京时间，格式 2024-01-03 08:30）：")
    end_time = prompt_time("请输入结束时间（北京时间，格式 2024-01-03 09:30）：")
    output_path = prompt_output_name("ovkml_output.csv")
    rows = convert_ovkml(input_path, start_time, end_time)
    write_output(rows, output_path)
    print(f"转换完成，共输出 {len(rows)} 行：{output_path}")
    maybe_preview_csv(output_path)


def handle_preview() -> None:
    input_path = prompt_file_path("请输入要预览的 CSV 文件路径：")
    default_name = f"{Path(input_path).stem}_map.html"
    output_path = prompt_output_name(default_name, suffix=".html")
    html_path = generate_map_preview(input_path, output_html=output_path)
    print(f"地图预览已生成：{html_path}")


def handle_web_viewer() -> None:
    output_path = prompt_output_name("track_viewer.html", suffix=".html")
    html_path = generate_web_viewer(output_path)
    print(f"轨迹回放网站已生成：{html_path}")


def main() -> None:
    actions = {
        "1": handle_flight,
        "2": handle_kml,
        "3": handle_ovkml,
        "4": handle_preview,
        "5": handle_web_viewer,
    }

    while True:
        print("\n===== 一生足迹轨迹转换工具 =====")
        print("1. 航班 CSV 转换（飞常准）")
        print("2. 火车 KML 转换")
        print("3. 奥维地图 OVKML 转换")
        print("4. 预览 CSV 地图")
        print("5. 生成轨迹回放网站")
        print("6. 退出")

        choice = input("请选择（1-6）：").strip()
        if choice == "6":
            print("已退出。")
            return
        action = actions.get(choice)
        if action is None:
            print("无效选项，请重新输入。")
            continue

        try:
            action()
        except Exception as exc:
            print(f"转换失败：{exc}")


if __name__ == "__main__":
    main()
