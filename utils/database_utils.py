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


def existing_activity(json_data):
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT av.amp_activity_id,av.amp_id, ag.version
            FROM amp_activity_version av
            JOIN amp_activity_group ag ON av.amp_activity_group_id = ag.amp_activity_group_id
            WHERE av.name = %s
        """, (json_data['project_title'],))
        result = cur.fetchone()
        if result:
            json_data['internal_id']=result['amp_activity_id']
            json_data['amp_id']=result['amp_id']
            json_data['activity_group']={
                'version':  result['version'],
            }
            return True
        else:
            return False
