import asyncio
from pathlib import Path

import aiosqlite


class BotDatabase:
    def __init__(self, db_name: str = 'bot.db'):
        Path('data').mkdir(exist_ok=True)
        self._db_path = Path('data') / db_name
        self._lock = asyncio.Lock()
        self._initialized = False

    async def initialize(self):
        if self._initialized:
            return
        async with self._lock:
            async with aiosqlite.connect(self._db_path) as db:
                await db.execute(
                    '''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT,
                    username TEXT UNIQUE,
                    original_user_id TEXT UNIQUE NOT NULL,
                    started_at REAL DEFAULT ( strftime('%s', 'now') )
                );
                '''
                )
                await db.commit()
                self._initialized = True

    async def add_user(self, full_name: str, username: str, original_user_id: str):
        await self.initialize()
        async with self._lock:
            async with aiosqlite.connect(self._db_path) as db:
                try:
                    await db.execute(
                        'INSERT INTO users (full_name, username, original_user_id) '
                        'VALUES (?, ?, ?);',
                        (
                            full_name,
                            username,
                            original_user_id,
                        ),
                    )
                    await db.commit()
                    return True
                except aiosqlite.IntegrityError as e:
                    return False

    async def list_users(self) -> str:
        await self.initialize()
        async with self._lock:
            async with aiosqlite.connect(self._db_path) as db:
                cursor = await db.execute(
                    'SELECT full_name, username,'
                    'strftime(\'%d.%m.%Y %H:%M\', started_at, \'unixepoch\', \'+3 hours\') '
                    'started_at FROM users ORDER BY started_at DESC;'
                )
                rows = await cursor.fetchall()
                return self._format_list_of_users(rows)

    def _format_list_of_users(self, users: list[tuple[str]], limit=10) -> str:
        display_users = users[:limit]
        total = len(users)

        text = '👥 Список пользователей:\n\n'
        header = '<b>Имя</b>\t\t<b>username</b>\t\t<b>Дата регистрации</b>\n\n'
        text += header

        for user in users:
            full_name, username, started_at = user
            text += '\t\t'.join(
                (full_name or 'нет', f'@{username or 'нет'}', started_at or 'нет')
            )
            text += '\n'

        if total > limit:
            text += f'\n\n...и ещё {total - limit} человек'

        text += f'\n\nВсего пользователей: {total}'

        return text


bot_db = BotDatabase()
if __name__ == '__main__':

    async def main():
        data = await bot_db.list_users()
        print(data)

    asyncio.run(main())
