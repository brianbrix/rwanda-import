from psycopg2.extras import RealDictCursor

from db import get_db_connection


def get_currencies():
    conn = get_db_connection()
    currencies = {}
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT amp_currency_id, currency_code FROM amp_currency")
        rows = cur.fetchall()
        for row in rows:
            currencies[row['currency_code']] = row['amp_currency_id']
    return currencies


