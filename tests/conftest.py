import os
import pytest
from sqlalchemy import create_engine, text

from app.models import User  # users の定義元

@pytest.fixture(scope="session", autouse=True)
def _recreate_users_table():
    engine = create_engine(os.environ["DATABASE_URL"])

    with engine.begin() as conn:
        # 既存のズレた users を必ず消す
        conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
        # モデル定義どおりに作り直す（name列を含む想定）
        User.__table__.create(bind=conn)

        # デバッグ：実際の列をログに出す（Actionsで確認できる）
        cols = conn.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """)).fetchall()
        print("DEBUG users columns:", [c[0] for c in cols])

    yield
