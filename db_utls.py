# db_utls.py
import psycopg2
from psycopg2.extras import RealDictCursor
import os

_connection = None

def get_db_connection():
    global _connection
    if _connection is None or _connection.closed != 0:
        _connection = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB", "amp"),
            user=os.getenv("POSTGRES_USER", "amp"),
            password=os.getenv("POSTGRES_PASSWORD", "amp"),
            host=os.getenv("POSTGRES_HOST", "amp-rwanda-pr-4394.stg.ampsite.net-db"),  # since you're on the host
            port=os.getenv("POSTGRES_PORT", 5432),
            cursor_factory=RealDictCursor
        )
    return _connection
