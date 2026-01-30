import os
import pytest
from sqlalchemy import create_engine, text

@pytest.fixture(scope="session", autouse=True)
def _recreate_users_table():
    engine = create_engine(os.environ["DATABASE_URL"])

    with engine.begin() as conn:
        # 既存の users を必ず消す（列ズレを強制リセット）
        conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))

        # テストが期待している形で作る（id + name）
        conn.execute(text("""
            CREATE TABLE users (
              id   SERIAL PRIMARY KEY,
              name VARCHAR NOT NULL
            )
        """))

        # 確認ログ（Actionsで見える）
        cols = conn.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """)).fetchall()
        print("DEBUG users columns:", [c[0] for c in cols])

    yield
