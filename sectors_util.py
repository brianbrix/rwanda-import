from psycopg2.extras import RealDictCursor

from database_utils import run_sql_file_postgres
from db_utls import get_db_connection


def get_sectors():
    # Connect to PostgreSQL
    conn = get_db_connection()

    # Get all organizations from database
    results={}
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT amp_sector_id, name FROM amp_sector")
        rows = cur.fetchall()
        for row in rows:
            results[row['name']] = row['amp_sector_id']
    print(results)
    return results

def add_sectors_to_db(sector_names: []):
    run_sql_file_postgres('insert_sectors.sql')
    query = """
        INSERT INTO amp_sector (amp_sector_id, amp_sec_scheme_id, name)
        SELECT nextval('AMP_SECTOR_seq'), 
               (SELECT amp_sec_scheme_id FROM amp_sector_scheme WHERE sec_scheme_code = 'PBS' LIMIT 1),
               %s
        WHERE NOT EXISTS (
            SELECT 1 FROM amp_sector WHERE name = %s
        );
    """
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        for name in sector_names:
            cur.execute(query, (name, name))  # pass `name` twice for %s
        conn.commit()
