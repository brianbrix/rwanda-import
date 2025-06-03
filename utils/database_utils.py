import logging

from psycopg2.extras import RealDictCursor

from .db_utils import get_db_connection




def run_sql_file_postgres(sql_file_path):
    """
    Executes the SQL statements in the given file on a PostgreSQL database.
    :param sql_file_path: Path to the .sql file
    """
    try:
        with open(sql_file_path, 'r') as file:
            sql = file.read()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()

        logging.info("SQL executed successfully.")
        cur.close()
        conn.close()
    except Exception as e:
        logging.info(f"Error: {e}")


def existing_activity(title):
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT amp_activity_id FROM amp_activity_version WHERE name = %s", (title,))
        result = cur.fetchone()
        return result['amp_activity_id'] if result else None
