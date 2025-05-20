from decimal import Decimal, ROUND_HALF_UP

import Levenshtein

import re

from psycopg2.extras import RealDictCursor

from db_utls import get_db_connection



def extract_bracket_contents(text):
    res = re.findall(r'\((.*?)\)', text)
    if len(res) > 0:
        return res[0]
    return None
def extract_text_before_bracket(text):
    res = text.split('(')
    if len(res) > 0:
        return res[0]
    return None

def get_best_match(raw_name, db_names):
    """Find the best matching organization from database"""

    # First try exact match (case insensitive)
    for db_id, db_name_and_code in db_names.items():
        if db_name_and_code[0] == raw_name:
            return db_id, db_name_and_code[0]

    # Then try partial matches
    best_match = (None, None)
    for db_id, db_name_and_code in db_names.items():
        name = db_name_and_code[0]
        code = db_name_and_code[1]
        raw_code = extract_bracket_contents(raw_name)
        raw_name_without_bracket = extract_text_before_bracket(raw_name)
        db_name_without_bracket = extract_text_before_bracket(name)
        if raw_code is None:
            raw_code = ""
        if raw_code.strip().lower()==code.strip().lower():
            return db_id, name
        if raw_name.strip().lower() == code.strip().lower():
            return db_id, name
        if raw_name.strip().lower() == name.strip().lower():
            return db_id, name
        if raw_name_without_bracket is not None and raw_name_without_bracket.strip().lower() == code.strip().lower():
            return db_id, name
        if raw_name_without_bracket is not None and raw_name_without_bracket.strip().lower() == name.strip().lower():
            return db_id, name
        if db_name_without_bracket is not None and raw_name_without_bracket is not None:
            if raw_name_without_bracket.strip().lower() == db_name_without_bracket.strip().lower():
                return db_id, name

        distance =Levenshtein.distance(name, raw_name)
        if distance <= 3:
                best_match = (distance, name)


    return best_match  # Only return if good enough match

def process_organization_list(raw_list):
    # Connect to PostgreSQL
    conn = get_db_connection()

    # Get all organizations from database
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT amp_org_id, name, org_code FROM amp_organisation")
        rows = cur.fetchall()
        db_names = {}
        for row in rows:
            db_names[row['amp_org_id']] = [row['name'], row['org_code']]

    results = {}

    for raw_name in raw_list:
        results[raw_name] = []

        # Split combined names by common separators
        sub_names = re.split(r'\s*(?:[,&/-]|\bthrough\b|\bvia\b)\s*', raw_name, flags=re.IGNORECASE)
        matches = []

        for sub_name in sub_names:
            if not sub_name.strip():
                continue
            org_id, matched_name = get_best_match(sub_name, db_names)
            if org_id:
                matches.append(org_id)

        # Calculate equal percentage
        count = len(matches)
        if count > 0:
            percentage = Decimal(100) / count
            percentage = percentage.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            for org_id in matches:
                results[raw_name].append({
                    'organization': org_id,
                    'percentage': float(percentage)
                })
        if len(results)==0:
            results[raw_name].append({
                'organization': list(db_names.keys())[0],
                'percentage': 100
            })

    conn.close()
    return results



def get_organizations(raw_org_list):
    matches = process_organization_list(raw_org_list)
    return matches

def get_amp_role():
    conn= get_db_connection()
    db_names = []
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT amp_role_id FROM amp_role where LOWER(name) =%s LIMIT 1",('donor',))
        rows = cur.fetchall()
        for row in rows:
            db_names.append(row['amp_role_id'])
    return db_names
