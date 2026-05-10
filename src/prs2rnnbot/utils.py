import re
from pathlib import Path


def load_html_content(section: str, user_name: str) -> str:
    file_path = Path(__file__).parent / f'content/{section}.html'
    text = file_path.read_text(encoding='utf-8')
    return text if file_path.exists() else ''
