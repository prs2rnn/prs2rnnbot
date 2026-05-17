import asyncio
from pathlib import Path

import aiosqlite


class BotDatabase:
    def __init__(self, db_name: str = 'bot.db'):
        Path('data').mkdir(exist_ok=True)
        self._db_path = Path('data') / db_name
        self._lock = asyncio.Lock()
        self._db = None

    async def connect(self):
        self._db = await aiosqlite.connect(self._db_path)
        await self._db.execute('PRAGMA foreign_keys = ON;')

    async def close(self):
        if self._db:
            await self._db.close()
            self._db = None

    async def initialize(self):
        async with self._lock:
            await self._db.executescript(
                '''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT,
                    username TEXT UNIQUE,
                    original_user_id TEXT UNIQUE NOT NULL,
                    started_at REAL DEFAULT ( strftime('%s', 'now') ),
                    is_subscribed BOOLEAN DEFAULT FALSE
                );

                CREATE TABLE IF NOT EXISTS reply_map (
                    group_message_id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    created_at REAL DEFAULT (
                        strftime('%s', 'now')
                    )
                );
                '''
            )
            await self._db.commit()

    async def add_user(
        self, full_name: str, username: str, original_user_id: int
    ) -> bool:
        async with self._lock:
            cursor = await self._db.execute(
                '''
                INSERT OR IGNORE
                INTO users (full_name, username, original_user_id, is_subscribed)
                VALUES (?, ?, ?, ?);
                ''',
                (full_name, username, original_user_id, False),
            )
            await self._db.commit()

            return cursor.rowcount > 0

    async def list_users(self) -> str:
        async with self._lock:
            cursor = await self._db.execute(
                '''
                SELECT full_name, username, original_user_id,
                is_subscribed, is_ban,
                strftime(\'%d.%m.%Y %H:%M\', started_at, \'unixepoch\', \'+3 hours\') as started_at
                FROM users
                ORDER BY started_at DESC;
                '''
            )
            header = [i[0] for i in cursor.description]
            rows = await cursor.fetchall()
            return self._format_list_of_users(header, rows)

    def _format_list_of_users(
        self, header: list[str], users: list[tuple[str]], limit=10
    ) -> str:
        display_users = users[:limit]
        total = len(users)

        text = '👥 Список пользователей:\n\n'
        text += ', '.join(header)
        text += '\n'
        for i, u in enumerate(users, start=1):
            text += f'{i}. '
            text += ', '.join(map(str, u))
            text += '\n'

        if total > limit:
            text += f'\n\n...и ещё {total - limit} человек'

        text += f'\n\nВсего пользователей: {total}'

        return text

    async def subscribe(self, user_id: int) -> None:
        async with self._lock:
            await self._db.execute(
                'UPDATE users SET is_subscribed = True WHERE original_user_id = ?',
                (user_id,),
            )
            await self._db.commit()

    async def unsubscribe(self, user_id: int) -> None:
        async with self._lock:
            await self._db.execute(
                'UPDATE users SET is_subscribed = False WHERE original_user_id = ?',
                (user_id,),
            )
            await self._db.commit()

    async def is_subscribed(self, user_id: int) -> bool | int:
        async with self._lock:
            cursor = await self._db.execute(
                'SELECT is_subscribed FROM users WHERE original_user_id = ?',
                (user_id,),
            )

            result = await cursor.fetchone()
            return result[0] if result else None

    async def get_subscribed_users(self):
        async with self._lock:
            cursor = await self._db.execute(
                'SELECT original_user_id FROM users WHERE is_subscribed = ?',
                (True,),
            )
            result = await cursor.fetchall()
            return (i[0] for i in result) if result else None

    async def save_reply_mapping(self, group_message_id: int, user_id: int):
        async with self._lock:
            await self._db.execute(
                '''
                INSERT INTO reply_map (group_message_id, user_id)
                VALUES (?, ?);
                ''',
                (
                    group_message_id,
                    user_id,
                ),
            )
            await self._db.commit()

    async def get_user_id(self, group_message_id: int):
        async with self._lock:
            cursor = await self._db.execute(
                '''
                SELECT user_id
                FROM reply_map
                WHERE group_message_id = ?;
                ''',
                (group_message_id,),
            )
            result = await cursor.fetchone()
            return result[0] if result else None

    async def migrate(self):
        cursor = await self._db.execute('PRAGMA table_info(users);')
        columns = await cursor.fetchall()

        column_names = [column[1] for column in columns]

        if 'is_ban' not in column_names:
            await self._db.execute(
                '''
                ALTER TABLE users
                ADD COLUMN is_ban BOOLEAN DEFAULT FALSE;
                '''
            )
            await self._db.commit()

    async def check_is_banned(self, user_id: int) -> bool:
        cursor = await self._db.execute(
            '''
            SELECT is_ban FROM users WHERE original_user_id = ?;
            ''',
            (user_id,),
        )
        result = await cursor.fetchone()

        return result[0] if result else 0

    async def ban_user(self, user_id: int) -> bool:
        async with self._lock:
            cursor = await self._db.execute(
                '''
                UPDATE users
                SET is_ban = True
                WHERE original_user_id = ?;
                ''',
                (user_id,),
            )
            await self._db.commit()

            return cursor.rowcount > 0

    async def unban_user(self, user_id: int) -> bool:
        async with self._lock:
            cursor = await self._db.execute(
                '''
                UPDATE users
                SET is_ban = False
                WHERE original_user_id = ?;
                ''',
                (user_id,),
            )
            await self._db.commit()

            return cursor.rowcount > 0


bot_db = BotDatabase()

if __name__ == '__main__':

    async def main():
        await bot_db.connect()
        await bot_db.initialize()
        await bot_db.add_user('a', 'aaa', 123)
        await bot_db.close()

    asyncio.run(main())
