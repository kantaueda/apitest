import os
import pytest
from sqlalchemy import create_engine

import app.models
from app.db import Base

@pytest.fixture(scope="session", autouse=True)
def _create_tables():
    engine = create_engine(os.environ["DATABASE_URL"])

    # ★ここが重要：既存のズレたテーブルを消して作り直す
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)
