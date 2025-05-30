# db_utls.py
import psycopg2
from psycopg2.extras import RealDictCursor
import os

_connection = None

def get_db_connection():
    global _connection
    if _connection is None or _connection.closed != 0:
        _connection = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB", os.getenv('AMP_DB')),
            user=os.getenv("POSTGRES_USER", os.getenv('AMP_DB_USER')),
            password=os.getenv("POSTGRES_PASSWORD", os.getenv('AMP_DB_PASSWORD')),
            host=os.getenv("POSTGRES_HOST", os.getenv('AMP_DB_HOST')),  # since you're on the host
            port=os.getenv("POSTGRES_PORT", os.getenv('AMP_DB_PORT')),
            cursor_factory=RealDictCursor
        )
    return _connection
