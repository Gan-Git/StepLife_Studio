from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = BASE_DIR / "templates" / "track_viewer_template.html"
OUTPUT_DIR = BASE_DIR / "output"


def generate_web_viewer(output_html: str | None = None) -> str:
    if output_html is None:
        output_html = str(OUTPUT_DIR / "track_viewer.html")

    html_content = TEMPLATE_PATH.read_bytes()

    output_path = Path(output_html)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(html_content)

    return str(output_path)
