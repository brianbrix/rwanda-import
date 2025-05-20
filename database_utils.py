from psycopg2.extras import RealDictCursor

from db import get_db_connection




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

        print("SQL executed successfully.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")


