import asyncio
import logging
from pathlib import Path

import httpx


def load_html_content(section: str) -> str:
    file_path = Path(__file__).parent.parent / f'content/{section}.html'
    text = file_path.read_text(encoding='utf-8')
    return text if file_path.exists() else ''


async def fetch_json(url: str):
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except (httpx.TimeoutException, httpx.HTTPStatusError, httpx.RequestError) as e:
        logging.error(f'Error occurred in fetch_json: {e}')
    except Exception as e:
        logging.error(f'Unexpected error occurred in fetch_json: {e}')


async def get_changelog():
    url = 'https://api.github.com/repos/prs2rnn/mycardbot/releases'
    data = await fetch_json(url)
    if not data:
        return []

    data = [
        {'version': r.get('name', 'unknown'), 'text': r.get('body', '')} for r in data
    ][:5]
    return data


if __name__ == '__main__':

    async def main():
        result = await get_changelog()
        print(result)

    asyncio.run(main())
