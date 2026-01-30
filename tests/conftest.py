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

    # --- ここからDEBUG（migrate後に users が見えてるか確定）---
    with engine.begin() as conn:
        sp = conn.execute(text("SHOW search_path")).scalar()
        u1 = conn.execute(text("SELECT to_regclass('users')")).scalar()
        u2 = conn.execute(text("SELECT to_regclass('public.users')")).scalar()
        u3 = conn.execute(text("""
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_name = 'users'
            ORDER BY table_schema
        """)).fetchall()

        print("DEBUG search_path:", sp)
        print("DEBUG to_regclass(users):", u1)
        print("DEBUG to_regclass(public.users):", u2)
        print("DEBUG users tables:", u3)

        assert u1 is not None or u2 is not None, "users table not found after alembic upgrade"
    # --- DEBUGここまで ---

    yield

