import os
import pytest
from sqlalchemy import create_engine

import app.models  # ★これが重要：Userを読み込んでBase.metadataに登録する
from app.db import Base  # さっき直した import に合わせる（Baseがここにある前提）

@pytest.fixture(scope="session", autouse=True)
def _create_tables():
    engine = create_engine(os.environ["DATABASE_URL"])

    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
