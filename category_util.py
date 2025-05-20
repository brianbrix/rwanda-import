from typing import Dict

from psycopg2._psycopg import List
from psycopg2.extras import RealDictCursor

from db import get_db_connection


def get_category_values(fields_list):
    result = {}
    conn = get_db_connection()

    query = """
        SELECT acv.id, acv.category_value
        FROM amp_category_value acv
        JOIN amp_category_class acc ON acv.amp_category_class_id = acc.id
        WHERE LOWER(acc.category_name) = %s;
    """

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        for field in fields_list:
            cur.execute(query, (field.lower(),))
            rows = cur.fetchall()
            if len(rows) == 0:
                continue
            result[field] = [{"id": row["id"], "value": row["category_value"]} for row in rows]

    return result
def extract_category(all_categories:{},field_name:str,category_value:str):

    if field_name not in all_categories:
        return None
    for category in all_categories[field_name]:
        if category["value"] == category_value:
            return category["id"]
    return None

def is_category(name:str):
    conn = get_db_connection()
    query = """
        SELECT acc.category_name
        FROM amp_category_class acc
        WHERE LOWER(acc.category_name) = %s;
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query, (name.lower(), ))
        rows = cur.fetchall()
        if len(rows) == 0:
            return False
        return True

def get_adjustment_types():
    conn= get_db_connection()
    adj_types={}
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT id,category_value FROM amp_category_value WHERE amp_category_class_id=(SELECT id FROM amp_category_class WHERE keyname=%s LIMIT 1)"
                    ,('adjustment_type',))
        rows = cur.fetchall()
        for row in rows:
            adj_types[row['category_value']] = row['id']
    return adj_types

def insert_categories(category_class_with_values: dict):
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        for category_class, values in category_class_with_values.items():
            # Get amp_category_class_id
            cur.execute("SELECT id FROM amp_category_class WHERE LOWER(category_name) = %s LIMIT 1", (category_class.lower(),))
            result = cur.fetchone()
            if not result:
                continue

            category_class_id = result["id"]

            # Get max index_column
            cur.execute("SELECT COALESCE(MAX(index_column), -1) FROM amp_category_value WHERE amp_category_class_id = %s", (category_class_id,))
            max_index = cur.fetchone()["coalesce"]

            for value in values:
                max_index += 1
                cur.execute("""
                    INSERT INTO amp_category_value (id, amp_category_class_id, category_value, index_column)
                    SELECT nextval('AMP_CATEGORY_VALUE_seq'), %s, %s, %s
                    WHERE NOT EXISTS (
                        SELECT 1 FROM amp_category_value
                        WHERE amp_category_class_id = %s AND category_value = %s
                    );
                """, (category_class_id, value, max_index, category_class_id, value))

        conn.commit()
