# db_utils.py
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from airflow.configuration import conf

_connection = None

def get_db_connection():
    global _connection
    if _connection is None or _connection.closed != 0:
        _connection = psycopg2.connect(
            dbname=conf.get('database','database_name'),
            user=conf.get('database', 'username'),
            password=conf.get('database', 'password'),
            host=conf.get('database','database_host'),
            port=conf.get('database', 'database_port')
        )
    return _connection
