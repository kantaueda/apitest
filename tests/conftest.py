import os
import sys
import subprocess

import pytest
from sqlalchemy import create_engine, text


@pytest.fixture(scope="session", autouse=True)
def _reset_db_and_migrate():
    engine = create_engine(os.environ["DATABASE_URL"])

    # DBを毎回“空”にする（列ズレを完全に消す）
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))

    # Alembicを適用（これがスキーマの正）
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        check=True,
        env=os.environ,
    )

    yield
