import os
import pytest
from sqlalchemy import create_engine

from app.db.base import Base  # ←ここは後で直す可能性あり

@pytest.fixture(scope="session", autouse=True)
def _create_tables():
    database_url = os.environ["DATABASE_URL"]
    engine = create_engine(database_url)

    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
