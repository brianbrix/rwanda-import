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
        cur.execute("""
            SELECT av.amp_activity_id, ag.version
            FROM amp_activity_version av
            JOIN amp_activity_group ag ON av.amp_activity_group_id = ag.amp_activity_group_id
            WHERE av.name = %s
        """, (title,))
        result = cur.fetchone()
        if result:
            return result['amp_activity_id'], result['version'], title
        else:
            return None, None, None
