import os
import pytest
from sqlalchemy import create_engine

from app.models import User  # users の定義元

@pytest.fixture(scope="session", autouse=True)
def _recreate_users_table():
    engine = create_engine(os.environ["DATABASE_URL"])

    # users テーブルを確実に作り直す（列ズレを強制リセット）
    User.__table__.drop(bind=engine, checkfirst=True)
    User.__table__.create(bind=engine, checkfirst=False)

    yield

    User.__table__.drop(bind=engine, checkfirst=True)
