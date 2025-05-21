from datetime import datetime
import re

import pandas as pd


def clean_start_and_end_date(data_list: [{}]):
    """
    Cleans up 'actual start date' and 'actual end date' fields from messy strings.
    Formats dates to yyyy-MM-dd. Removes invalid entries.
    """
    for data in data_list:
        for key in ['Actual start date', 'Actual end date']:
            value = data.get(key)
            if not value or not isinstance(value, str):
                data.pop(key, None)
                continue
            # Split based on "End date:"
            if "End date:" in value:
                parts = value.split("End date:")
            else:
                parts = [value]

            if key.lower() == 'actual start date':
                match = re.search(r'Start date:\s*([\d]{2}/[\d]{2}/[\d]{4}|\d{4})', parts[0])
            elif key.lower() == 'actual end date':
                # Check if second part exists, otherwise reuse the whole string
                end_text = parts[1] if len(parts) > 1 else parts[0]
                match = re.search(r'(\d{2}/\d{2}/\d{4}|\d{4})', end_text)
            else:
                match = None

            if match:
                date_str = match.group(1).strip()
                try:
                    # Parse full date or construct from year only
                    if re.match(r'\d{2}/\d{2}/\d{4}', date_str):
                        dt = datetime.strptime(date_str, "%d/%m/%Y")
                    elif re.match(r'\d{4}', date_str):
                        dt = datetime.strptime("12/12/" + date_str, "%d/%m/%Y")
                    else:
                        raise ValueError("Invalid date")
                    data[key] = dt.strftime("%Y-%m-%d")
                except Exception:
                    data.pop(key, None)  # Remove if parsing fails
            else:
                data.pop(key, None)  # Remove if no match found
def clean_up_orgs(data_list:[{}]):
    clean_data=[]
    for idx,data in enumerate(data_list):
        donor = data.get('Donor Agency')
        if donor is None and (data.get('Commitment') is not None or data.get('Disbursement') is not None):
            data['Donor Agency'] = 'Government of Rwanda'
        donor = data.get('Donor Agency')
        if donor is not None and len(donor)>0:
            if data.get('Type of Assistance') is None or len(data.get('Type of Assistance'))<1:
                data['Type of Assistance']='Grant'
            if data.get('Financing Instrument') is None or len(data.get('Financing Instrument'))<1:
                data['Financing Instrument']='Project'
        clean_data.append(data)
    return clean_data


def clean_up_title(data_list:[{}]):
    """
    Cleans up the 'title' field by removing unwanted characters and formatting.
    :param data_list: A list of dictionaries containing the data.
    """
    cleaned_list = []
    for idx,data in enumerate(data_list):
        title = data.get('Project Title')
        if not title or not isinstance(title, str):
            continue
        title = title.strip()
        if len(title)<1:
            continue
        if "project to be developed" == title.lower():
            continue
        cleaned_list.append(data)
    return cleaned_list


def extract_first_year_date(text: str):
    """
    Extracts the first year from a string like 'US$ Disbursed (2020-2021)'
    and returns it in 'yyyy-MM-dd' format using 12/12 as the default day/month.

    Returns None if no valid year is found.
    """
    if not text or not isinstance(text, str):
        return None

    # Extract a 4-digit year using regex
    match = re.search(r'(\d{4})', text)
    if not match:
        return None

    year = match.group(1)

    try:
        # Construct date from the year
        date = datetime.strptime(f"{year}-12-12", "%Y-%m-%d")
        return date.strftime("%Y-%m-%d")
    except ValueError:
        return None


def create_transaction_object(date, amount,adj_type,currency):
    return {
        'date': date,
        'amount': amount,
        'adj_type': adj_type,
        'currency': currency
    }

def process_transaction(amp_title,ndc_title, column, row, idx, df2, row_result):
    # Initialize list if key doesn't exist
    row_result.setdefault(amp_title, [])

    # Early returns if conditions aren't met
    if not (column.lower() in ndc_title['value'].lower() and
            idx < len(df2) and
            pd.notna(row[idx])):
        return

    col_value = row[idx]
    amp_title_lower = amp_title.lower()

    transaction_dates = {
        'commitment': '2020-01-01',
        'disbursement': extract_first_year_date(column)
    }

    if amp_title_lower in transaction_dates:
        transaction = create_transaction_object(
            date=transaction_dates[amp_title_lower],
            amount=col_value,
            adj_type= ndc_title['adj_type'],
            currency=ndc_title['currency']
        )
        row_result[amp_title].append(transaction)
