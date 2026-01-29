import os
from dotenv import load_dotenv
import sqlalchemy as sa

load_dotenv()

url = (
    f"postgresql+psycopg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
print("URL=", url)

engine = sa.create_engine(url, pool_pre_ping=True)
with engine.connect() as conn:
    print("SELECT 1 ->", conn.execute(sa.text("SELECT 1")).scalar_one())
