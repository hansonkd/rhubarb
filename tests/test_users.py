import pytest
import pytest_asyncio
from psycopg.errors import UniqueViolation

from rhubarb import Registry, table, save
from rhubarb.contrib.users.config import UserConfig
from rhubarb.contrib.users.models import User, set_password, set_email, user_registry, verify_email, register
from rhubarb.crud import reload
from rhubarb.migrations.data import MigrationStateDatabase, CreateTable
from rhubarb.migrations.utils import fast_forward, find_diffs, reset_db_and_fast_forward

migrations_registry = Registry()
migrations_registry.link(user_registry)


@table(registry=migrations_registry)
class MyUser(User):
    pass


EMPTY_STATE = MigrationStateDatabase()


@pytest.fixture
def user_config(patch_config):
    with patch_config(users=UserConfig(user_model=MyUser)):
        yield

@pytest_asyncio.fixture
async def user_table(postgres_connection, user_config):
    async with postgres_connection.transaction(force_rollback=True):
        await reset_db_and_fast_forward(postgres_connection, migrations_registry)
        yield


@pytest_asyncio.fixture
async def user(postgres_connection, user_table) -> MyUser:
    yield await save(MyUser(username="la@example.com"), postgres_connection).execute()


@pytest.mark.asyncio
async def test_create_user_table(postgres_connection, user_config):
    ref_state = MigrationStateDatabase.from_registry(migrations_registry)

    diffs = find_diffs(old_state=EMPTY_STATE, new_state=ref_state)
    assert len(diffs) == 4
    assert isinstance(diffs[0], CreateTable)
    async with postgres_connection.transaction(force_rollback=True):
        await fast_forward(postgres_connection, EMPTY_STATE, ref_state)


@pytest.mark.asyncio
async def test_user_password(postgres_connection, user):
    user = await set_password(postgres_connection, user, "pass123")
    assert user.password.check("pass123")
    assert not user.password.check("pass1234")


@pytest.mark.asyncio
async def test_verification_mixin(postgres_connection, user):
    verification = await set_email(postgres_connection, user, "e@example.com")
    verification_2 = await set_email(postgres_connection, user, "b@example.com")

    assert verification.code != verification_2.code

    verification = await reload(verification, postgres_connection).one()
    assert verification.canceled
    assert not verification_2.canceled


@pytest.mark.asyncio
async def test_verification_success(postgres_connection, user):
    verification = await set_email(postgres_connection, user, "e@example.com")
    await verify_email(postgres_connection, verification.id, verification.code)
    assert user.email is None


@pytest.mark.asyncio
async def test_verification_success_update_user(postgres_connection, user):
    verification = await set_email(postgres_connection, user, "e@example.com")
    user = await verify_email(postgres_connection, verification.id, verification.code, update_user=True)
    assert user.email == "e@example.com"


@pytest.mark.asyncio
async def test_register(postgres_connection, user_table):
    result = await register(postgres_connection, username="123")
    assert result.user
    assert not result.phone_verification
    assert not result.email_verification


@pytest.mark.asyncio
async def test_register_phone(postgres_connection, user_table):
    result = await register(postgres_connection, username="123", phone_number="+18884151234")
    assert result.user
    assert result.phone_verification
    assert not result.email_verification


@pytest.mark.asyncio
async def test_register_email(postgres_connection, user_table):
    result = await register(postgres_connection, username="123", email="user@example.com")
    assert result.user
    assert not result.phone_verification
    assert result.email_verification


@pytest.mark.asyncio
async def test_register_both(postgres_connection, user_table):
    result = await register(postgres_connection, username="123", phone_number="+18884156789", email="user@example.com")
    assert result.user
    assert result.phone_verification
    assert result.email_verification


@pytest.mark.asyncio
async def test_register_fails(postgres_connection, user):
    with pytest.raises(UniqueViolation):
        await register(postgres_connection, username=user.username)
