# db_utils.py
import psycopg2
from psycopg2.extras import RealDictCursor
import os

_connection = None

def get_db_connection():
    global _connection
    if _connection is None or _connection.closed != 0:
        _connection = psycopg2.connect(
            dbname=os.getenv('AMP_DB_NAME'),
            user=os.getenv('AMP_DB_USER'),
            password=os.getenv('AMP_DB_PASSWORD'),
            host=os.getenv('AMP_DB_HOST'),  # since you're on the host
            port=os.getenv('AMP_DB_PORT')
        )
    return _connection
