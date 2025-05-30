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
            results[row['name']] = {
                'sector': row['amp_sector_id'],
                'sector_percentage': 100.0
            }
    return results

def add_sectors_to_db(secondary_sector_names: [], primary_sectors:[]):
    run_sql_file_postgres('insert_sectors.sql')
    secondary_sector_names = set(secondary_sector_names)
    primary_sectors = set(primary_sectors)
    query = """
        INSERT INTO amp_sector (amp_sector_id, amp_sec_scheme_id, name)
        SELECT nextval('AMP_SECTOR_seq'), 
               (SELECT amp_sec_scheme_id FROM amp_sector_scheme WHERE sec_scheme_code = %s LIMIT 1),
               %s
        WHERE NOT EXISTS (
            SELECT 1 FROM amp_sector WHERE name = %s
        );
    """
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        for name in secondary_sector_names:
            if name in primary_sectors:
                name = name+"-2"
            cur.execute(query, ('NST',name, name))  # pass `name` twice for %s
        for name in primary_sectors:
            cur.execute(query, ('PS',name, name))  # pass `name` twice for %s
        conn.commit()
    logging.info("Added sectors to database")
