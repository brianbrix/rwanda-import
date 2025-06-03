import json
import logging
from typing import Optional, Dict, Union, List

import pandas as pd
import requests
from numpy.ma.core import empty
from pandas import DataFrame

from utils.api_util import import_project
from utils.database_utils import existing_activity
from .category_util import is_category, get_category_values, get_adjustment_types, extract_category
from .currency_util import get_currencies
from .file_data_utils import process_transaction, clean_start_and_end_date, clean_up_sectors, clean_up_title, \
    clean_up_orgs
from .organizations_util import get_organizations, get_amp_role
from .sectors_util import get_sectors, add_sectors_to_db

mapping_file = 'CFIS MAPPING.xlsx'

def read_data(file_path: str, skip_rows: int = 0, sheet_name: str = None,
              api_url: Optional[str] = None, api_params: Optional[Dict] = None,
              api_headers: Optional[Dict] = None):
    """Read data from Excel, JSON, TXT file, or API and return a DataFrame or list of dictionaries"""

    if api_url:
        try:
            response = requests.get(api_url, params=api_params, headers=api_headers)
            response.raise_for_status()
            data = response.json()

            if isinstance(data, list):
                df = pd.DataFrame(data)
                # df2 = pd.DataFrame(data[1:]) if len(data) > 1 else pd.DataFrame()
                return df, df
            elif isinstance(data, dict) and 'results' in data:
                # Handle paginated API responses
                df = pd.DataFrame(data['results'])
                # df2 = pd.DataFrame(data['results'][1:]) if len(data['results']) > 1 else pd.DataFrame()
                return df, df
            else:
                raise ValueError("API response should contain a list of dictionaries or a 'results' key")
        except Exception as e:
            raise ValueError(f"API request failed: {str(e)}")

    # File-based data sources
    if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        # Excel file
        if sheet_name:
            df1 = pd.read_excel(file_path, skiprows=skip_rows, sheet_name=sheet_name, nrows=1)#column row
            df1.columns = df1.columns.map(str)

            df2 = pd.read_excel(file_path, skiprows=skip_rows + 1, sheet_name=sheet_name)#first data row
        else:
            df1 = pd.read_excel(file_path, skiprows=skip_rows, nrows=1)
            df1.columns = df1.columns.map(str)

            df2 = pd.read_excel(file_path, skiprows=skip_rows + 1)
        df2.columns = df1.columns
        df2.columns = df2.columns.map(str)
        return df1, df2
    elif file_path.endswith('.json'):
        # JSON file
        with open(file_path, 'r') as f:
            data = json.load(f)
        if isinstance(data, list):
            df = pd.DataFrame(data)
            # df2 = pd.DataFrame(data[1:]) if len(data) > 1 else pd.DataFrame()
            return df, df
        else:
            raise ValueError("JSON file should contain a list of dictionaries")
    elif file_path.endswith('.txt'):
        # TXT file - assuming tab-delimited or CSV format
        df1 = pd.read_csv(file_path, skiprows=skip_rows, delimiter='\t' if '\t' in open(file_path).readline() else ',')
        df2 = pd.read_csv(file_path, skiprows=skip_rows + 1,
                          delimiter='\t' if '\t' in open(file_path).readline() else ',')
        return df1, df2
    else:
        raise ValueError("Unsupported file format. Please use Excel (.xlsx, .xls), JSON (.json), or TXT (.txt)")

def get_mapping(mapping_filename: str, ndc_column_index: int, amp_column_index: int,
                is_funding_column: int, adj_type_column: int, currency_column: int,
                skip_rows: int, api_url: Optional[str] = None,
                api_params: Optional[Dict] = None, api_headers: Optional[Dict] = None) -> Dict:
    """Load mapping data from Excel, JSON, TXT, or API"""

    if api_url:
        try:
            response = requests.get(api_url, params=api_params, headers=api_headers)
            response.raise_for_status()
            data = response.json()

            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict) and 'results' in data:
                df = pd.DataFrame(data['results'])
            else:
                raise ValueError("API response should contain a list of dictionaries or a 'results' key")
        except Exception as e:
            raise ValueError(f"API request failed: {str(e)}")
    elif mapping_filename.endswith('.xlsx') or mapping_filename.endswith('.xls'):
        df = pd.read_excel(mapping_filename, skiprows=skip_rows)
    elif mapping_filename.endswith('.json'):
        with open(mapping_filename, 'r') as f:
            data = json.load(f)
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            raise ValueError("JSON file should contain a list of dictionaries")
    elif mapping_filename.endswith('.txt'):
        df = pd.read_csv(mapping_filename, skiprows=skip_rows,
                         delimiter='\t' if '\t' in open(mapping_filename).readline() else ',')
    else:
        raise ValueError("Unsupported mapping source format")

    column_a = df.iloc[:, ndc_column_index]  # NDC column
    column_b = df.iloc[:, amp_column_index]  # AMP column (key)
    column_funding = df.iloc[:, is_funding_column]  # 'Yes'/'No'
    column_adj_type = df.iloc[:, adj_type_column]  # Adj type
    column_currency = df.iloc[:, currency_column]  # Currency

    mapping_dict = {}

    for idx in range(len(df)):
        b_value = column_b.iloc[idx]
        a_value = column_a.iloc[idx]

        if pd.isna(b_value):
            continue

        if str(column_funding.iloc[idx]).strip().lower() == 'yes':
            adj_type = str(column_adj_type.iloc[idx]).strip()
            currency = str(column_currency.iloc[idx]).strip()
            mapping_dict[b_value] = {
                'value': a_value,
                'adj_type': adj_type,
                'currency': currency
            }
        else:
            mapping_dict[b_value] = a_value

    return mapping_dict

def get_data(file_path: str = None, mapping_filename: str=None, skip_rows: int = 0, sheet_name: str = None,
             api_url: str = None, api_params: Dict = None, api_headers: Dict = None):
    """Main function to process data from various sources"""
    try:
        df1, df2 = read_data(file_path, skip_rows, sheet_name, api_url, api_params, api_headers)
    except Exception as e:
        logging.info(f"Error reading data source: {e}")
        return

    # mapping_dict = get_mapping(mapping_file, 1, 2, 4, 7, 6, 1)
    # Excel
    mapping_dict = get_mapping(mapping_filename, 1, 2, 4, 7, 6, 1)

    # JSON file
    # mapping_dict = get_mapping('mapping_config.json', 1, 2, 4, 7, 6, 1)

    # API
    # mapping_dict = get_mapping('', 1, 2, 4, 7, 6, 1,
    #                       api_url=api_url,
    #                       api_params={"format": "json"},
    #                       api_headers={"Authorization": "Bearer token"})
    # headers = df1.iloc[header_row]
    columns = list(df1.columns)
    # column_b = df.iloc[:,1]

    # result_dict = dict(zip(column_a, column_b))

    # logging.info(mapping_dict)
    # logging.info(columns)

    result = []

    agencies = []
    groups = []
    secondary_sectors = []
    primary_sectors = []

    file_categories = {amp_title: set() for amp_title in list(mapping_dict.keys())}
    # data_dict_list = df2.to_dict('records') if isinstance(df2, pd.DataFrame) else df2
    data_dict_list=df2.to_numpy() if isinstance(df2, pd.DataFrame) else df2
    logging.info("Number of rows in file: ", len(data_dict_list))


    # Go through each list element and its index
    invalid_rows = 0
    for row in data_dict_list:
        row_result = {}
        for idx, column in enumerate(columns):
            for amp_title, ndc_title in mapping_dict.items():
                # file_categories[amp_title]=[]
                if amp_title is None or column is None:
                    invalid_rows+=1
                    continue
                if not isinstance(column, str):
                    invalid_rows+=1
                    continue
                #map for commitments and disbursements
                if amp_title.lower() in ['commitment', 'disbursement']:
                    process_transaction(amp_title, ndc_title, column, row, idx, df2, row_result)
                    continue
                if ndc_title.lower() == column.lower():
                    col_value = row.get(column) if isinstance(row, dict) else row[idx] if idx < len(row) else None
                    if pd.notna(col_value):
                        row_result[amp_title] = col_value
                        if amp_title.lower() == 'implementing agency':
                            agencies.append(col_value)
                        if amp_title.lower() == 'responsible organisation':
                            agencies.append(col_value)
                        if amp_title.lower() == 'donor agency type':
                            groups.append(col_value)
                        if amp_title.lower() == 'donor agency':
                            agencies.append(col_value)
                        if amp_title.lower() == 'secondary sector':
                            secondary_sectors.append(col_value)
                        if amp_title.lower() == 'primary sector':
                            primary_sectors.append(col_value)
                        if is_category(amp_title):
                            file_categories[amp_title].add(col_value)
        if row_result:
            result.append(row_result)
    logging.info("Number of invalid rows: ", invalid_rows)
    logging.info("Number of valid rows initially: ", len(result))
    clean_start_and_end_date(result)
    clean_up_sectors(result)
    logging.info("Number of valid rows after title cleanup: ", len(result))
    result = clean_up_title(result)
    logging.info("Number of valid rows after title cleanup: ", len(result))
    result = clean_up_orgs(result)
    logging.info("Number of valid rows after orgs cleanup: ", len(result))

    # logging.info("Trying to clean up db")
    # run_sql_file_postgres('delete_exisiting_records.sql')
    ###### Orgs
    # logging.info("Inserting organisations")
    # responsible_orgs=get_responsible_org_list(result)
    # implementing_agency_and_types=get_implementing_org_list(result)
    # insert_orgs(responsible_orgs,implementing_agency_and_types)
    ####sectors
    # logging.info("Inserting sectors")
    # add_sectors_to_db(secondary_sectors, primary_sectors)

    ####categories
    # logging.info("Inserting categories")
    # insert_categories(file_categories)

    all_orgs = get_organizations(agencies)
    categories = get_category_values(list(mapping_dict.keys()))
    all_currencies = get_currencies()
    all_adj_types = get_adjustment_types()
    sectors = get_sectors()
    amp_role = get_amp_role()
    # login()
    for idx,item in enumerate(result):
        logging.info("Adding to api: ",idx+1, item)
        # try:
        construct_object_and_import(item, categories, all_orgs, all_currencies, all_adj_types, sectors, amp_role[0], primary_sectors)
        # except Exception as e:
        #     logging.info("Error adding to api:", e)
        #     break


def get_organization(all_orgs, key_name):
    all_keys = list(all_orgs.keys())
    if key_name in all_keys:
        org = all_orgs[key_name]
        if len(org) < 1:
            org = next(iter(all_orgs.values()))
        return org
    else:
        org = next(iter(all_orgs.values()))
        return org


def construct_object_and_import(original_object: {}, all_categories, all_organizations, all_currencies, all_adj_types,
                                all_sectors, amp_role, file_primary_sectors):
    # logging.info(original_object)
    new_object = {}
    original_keys_list = list(original_object.keys())
    donors = get_organization(all_organizations, original_object['Donor Agency'])
    implementers = get_organization(all_organizations, original_object['Implementing Agency'])
    responsible_orgs = get_organization(all_organizations, original_object['Responsible Organization'])
    new_object["project_title"] = original_object['Project Title']
    new_object["is_draft"] = False
    new_object["activity_status"] = extract_category(all_categories, 'Activity status',
                                                     original_object['Activity status'])
    if 'Actual start date' in original_keys_list:
        new_object["actual_start_date"] = original_object['Actual start date']
    if 'Actual end date' in original_keys_list:
        new_object["actual_completion_date"] = original_object['Actual end date']
    new_object["donor_organization"] = donors
    new_object["implementing_agency"] = implementers
    new_object["responsible_organization"] = responsible_orgs
    new_object["a_c_chapter"] = extract_category(all_categories, 'A.C. Chapter', original_object['A.C. Chapter'])
    if 'Procurement System' in original_keys_list:
        new_object["procurement_system"] = extract_category(all_categories, 'Procurement System',
                                                        original_object['Procurement System'])
    fundings = []
    commitments = []
    disbursements = []

    if 'Commitment' in original_keys_list or 'Disbursement' in original_keys_list:
        create_transaction('Commitment', commitments, original_object, all_currencies, all_adj_types)
        create_transaction('Disbursement', disbursements, original_object, all_currencies, all_adj_types)
        transaction_object={
            "donor_organization_id": new_object['donor_organization'][0]['organization'],
            "financing_instrument": extract_category(all_categories, 'Financing Instrument',
                                                     original_object['Financing Instrument']),
            "type_of_assistance": extract_category(all_categories, 'Type of Assistance',
                                                   original_object['Type of Assistance']),
            "source_role": amp_role
        }
        if len(commitments)>0:
            transaction_object.update({
                "commitments": commitments
            })
        if len(disbursements)>0:
            transaction_object.update({
                "disbursements": disbursements
            })
        fundings.append(transaction_object)

        new_object["fundings"] = fundings
    if 'Secondary Sector' in original_keys_list:
        sec = original_object['Secondary Sector']
        if sec in file_primary_sectors:
            sec = sec+'-2'
        new_object["secondary_sectors"] = [
            all_sectors[sec]

        ]
    if 'Primary Sector' in original_keys_list:
        new_object["primary_sectors"] = [
             all_sectors[original_object['Primary Sector']]
        ]
    logging.info(new_object)
    is_existing = existing_activity(new_object)
    import_project(new_object,is_existing)


def create_transaction(tran_type: str, lst: [], original_object=None, all_currencies=None, all_adj_types=None):
    for item in original_object[tran_type]:
        if len(item['amount'])>0 or int(item['amount'])==0:
            lst.append({
                "transaction_amount": item['amount'],
                "currency": all_currencies[item['currency']],
                "adjustment_type": all_adj_types[item['adj_type']],
                "transaction_date": item['date']
            })


if __name__ == "__main__":
    # Example usage:

    # 1. For Excel
    # get_data(file_path='Rwanda_NDC.xlsx', skip_rows=1, sheet_name='Partnership Plan template')

    # 2. For JSON:
    # get_data(file_path='data.json')

    # 3. For TXT/CSV:
    # get_data(file_path='data.txt')

    # 4. For API:
    # api_url = "https://api.example.com/data"
    # api_params = {"format": "json", "limit": 1000}
    # api_headers = {"Authorization": "Bearer YOUR_TOKEN"}
    # get_data(api_url=api_url, api_params=api_params, api_headers=api_headers)

    get_data('Rwanda_NDC.xlsx', 'CFIS MAPPING.xlsx',1, 'Partnership Plan template')
