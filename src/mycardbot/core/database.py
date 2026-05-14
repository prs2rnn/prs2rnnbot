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
                    started_at REAL DEFAULT ( strftime('%s', 'now') ),
                    is_subscribed BOOLEAN DEFAULT FALSE
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
                    return False
                except aiosqlite.IntegrityError as e:
                    return True

    async def list_users(self) -> str:
        await self.initialize()
        async with self._lock:
            async with aiosqlite.connect(self._db_path) as db:
                cursor = await db.execute(
                    'SELECT full_name, username,'
                    'strftime(\'%d.%m.%Y %H:%M\', started_at, \'unixepoch\', \'+3 hours\') '
                    'started_at, is_subscribed FROM users ORDER BY started_at DESC;'
                )
                rows = await cursor.fetchall()
                return self._format_list_of_users(rows)

    def _format_list_of_users(self, users: list[tuple[str]], limit=10) -> str:
        display_users = users[:limit]
        total = len(users)

        text = '👥 Список пользователей:\n\n'
        header = '<b>Имя</b>\t\t<b>username</b>\t\t<b>Дата регистрации</b>\t\t<b>Подписка на рассылку</b>\n\n'
        text += header

        for user in users:
            full_name, username, started_at, is_subscribed = user
            text += '\t\t'.join(
                (
                    full_name or 'нет',
                    f'@{username or 'нет'}',
                    started_at or 'нет',
                    str(is_subscribed) or 'нет',
                )
            )
            text += '\n'

        if total > limit:
            text += f'\n\n...и ещё {total - limit} человек'

        text += f'\n\nВсего пользователей: {total}'

        return text

    async def subscribe(self, user_id: str):
        await self.initialize()
        async with self._lock:
            async with aiosqlite.connect(self._db_path) as db:
                await db.execute(
                    'UPDATE users SET is_subscribed = True WHERE original_user_id = ?',
                    (user_id,),
                )
                await db.commit()

    async def unsubscribe(self, user_id: str):
        await self.initialize()
        async with self._lock:
            async with aiosqlite.connect(self._db_path) as db:
                await db.execute(
                    'UPDATE users SET is_subscribed = False WHERE original_user_id = ?',
                    (user_id,),
                )
                await db.commit()

    async def is_subscribed(self, user_id: str) -> bool | int:
        await self.initialize()
        async with self._lock:
            async with aiosqlite.connect(self._db_path) as db:
                cursor = await db.execute(
                    'SELECT is_subscribed FROM users WHERE original_user_id = ?',
                    (user_id,),
                )

                result = await cursor.fetchone()
                return result[0] if result else None

    async def get_subscribed_users(self):
        await self.initialize()
        async with self._lock:
            async with aiosqlite.connect(self._db_path) as db:
                cursor = await db.execute(
                    'SELECT original_user_id FROM users WHERE is_subscribed = ?',
                    (True,),
                )
                result = await cursor.fetchall()
                return (i[0] for i in result) if result else None


bot_db = BotDatabase()
