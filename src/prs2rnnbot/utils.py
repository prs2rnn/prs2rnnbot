import re
from pathlib import Path


def load_html_content(section: str) -> str:
    file_path = Path(__file__).parent / f'content/{section}.html'
    return file_path.read_text(encoding='utf-8') if file_path.exists() else ''
