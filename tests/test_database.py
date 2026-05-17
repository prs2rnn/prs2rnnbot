import aiosqlite
import pytest
import pytest_asyncio

from src.mycardbot.core.database import BotDatabase


@pytest_asyncio.fixture
async def db(tmp_path):
    database = BotDatabase(db_name='test.db')
    database._db_path = tmp_path / 'test.db'
    await database.connect()
    await database.initialize()

    yield database

    await database.close()

    assert database._db is None


class TestBotDatabase:

    @pytest.mark.asyncio
    async def test_add_user(self, db: BotDatabase):
        is_added = await db.add_user(
            full_name='John Doe', username='johndoe', original_user_id='123'
        )

        assert is_added

    @pytest.mark.asyncio
    async def test_add_duplicate_user(self, db: BotDatabase):
        await db.add_user(
            full_name='John Doe', username='johndoe', original_user_id='123'
        )
        is_added = await db.add_user(
            full_name='John Doe', username='johndoe', original_user_id='123'
        )

        assert not is_added

    @pytest.mark.asyncio
    async def test_subscribe_user(self, db: BotDatabase):
        await db.add_user(
            full_name='John Doe', username='johndoe', original_user_id='123'
        )
        await db.subscribe('123')
        result = await db.is_subscribed('123')
        assert result == 1

    @pytest.mark.asyncio
    async def test_unsubscribe_user(self, db: BotDatabase):
        await db.add_user(
            full_name='John Doe', username='johndoe', original_user_id='123'
        )
        await db.subscribe('123')
        await db.unsubscribe('123')
        result = await db.is_subscribed('123')
        assert result == 0

    @pytest.mark.asyncio
    async def test_get_subscribed_users(self, db: BotDatabase):
        await db.add_user(
            full_name='John Doe', username='johndoe', original_user_id='123'
        )
        await db.subscribe('123')
        users = list(await db.get_subscribed_users())
        assert '123' in users
