import os
import pytest
from sqlalchemy import create_engine

from app.models import User  # ★ここが重要：Userが所属するmetadataを使う

@pytest.fixture(scope="session", autouse=True)
def _create_tables():
    engine = create_engine(os.environ["DATABASE_URL"])

    # ★既存の users（列違いでもOK）を落として作り直す
    User.metadata.drop_all(bind=engine)
    User.metadata.create_all(bind=engine)

    yield

    User.metadata.drop_all(bind=engine)
