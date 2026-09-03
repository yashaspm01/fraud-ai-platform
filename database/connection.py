import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = quote_plus(os.getenv("POSTGRES_PASSWORD"))
DB_NAME = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("POSTGRES_HOST", "127.0.0.1")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
print("DEBUG - Using:", DATABASE_URL)
# Engine: manages a pool of DB connections. Created ONCE at module load —
# never inside a request/function — so connections are reused, not
# re-established on every query.
engine = create_engine(DATABASE_URL, echo=True)

# Session factory: each session is one "unit of work" / one transaction.
# autocommit=False -> you decide when to save (db.commit()), not automatic.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Yields a DB session, guarantees it's closed afterward — even on error.
    FastAPI will use this as a dependency later (Week 1 API step).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
