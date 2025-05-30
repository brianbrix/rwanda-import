import json

import pandas as pd
from numpy.ma.core import empty

from api_util import login, import_project
from category_util import is_category, get_category_values, insert_categories, extract_category, get_adjustment_types
from currency_utl import get_currencies
from database_utils import run_sql_file_postgres
from file_data_utils import clean_start_and_end_date, clean_up_title, extract_first_year_date, process_transaction, \
    clean_up_orgs, clean_up_sectors, get_responsible_org_list, get_implementing_org_list
from organizations_util import get_organizations, get_amp_role, insert_orgs
from sectors_util import get_sectors, add_sectors_to_db

mapping_file = 'CFIS MAPPING.xlsx'


def get_mapping(excel_file: str, ndc_column_index: int, amp_column_index: int, is_funding_column: int,
                adj_type_column: int, currency_column: int, skip_rows: int):
    # Load the Excel file (reads the first sheet by default)
    df = pd.read_excel(excel_file, skiprows=skip_rows)

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


def get_data(excel_file: str, skip_rows: int, sheet_name: str):
    # Load the Excel file (reads the first sheet by default)
    df1 = pd.read_excel(excel_file, skiprows=skip_rows, sheet_name=sheet_name)
    df2 = pd.read_excel(excel_file, skiprows=skip_rows + 1, sheet_name=sheet_name)
    mapping_dict = get_mapping(mapping_file, 1, 2, 4, 7, 6, 1)

    # headers = df1.iloc[header_row]
    columns = list(df1.columns)
    # column_b = df.iloc[:,1]

    # result_dict = dict(zip(column_a, column_b))

    # print(mapping_dict)
    # print(columns)

    result = []

    agencies = []
    groups = []
    secondary_sectors = []
    primary_sectors = []

    file_categories = {amp_title: set() for amp_title in list(mapping_dict.keys())}
    data_dict_list=df2.to_numpy()
    print("Number of rows in file: ",len(data_dict_list))


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
                    if idx < len(df2):
                        col_value = row[idx]
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
        if row_result:  # Only add non-empty rows
            result.append(row_result)
    print("Number of invalid rows: ", invalid_rows)
    print("Number of valid rows initially: ", len(result))
    clean_start_and_end_date(result)
    clean_up_sectors(result)
    print("Number of valid rows after title cleanup: ", len(result))
    result = clean_up_title(result)
    print("Number of valid rows after title cleanup: ", len(result))
    result = clean_up_orgs(result)
    print("Number of valid rows after orgs cleanup: ", len(result))

    # print("Trying to clean up db")
    # run_sql_file_postgres('delete_exisiting_records.sql')
    ###### Orgs
    # print("Inserting organisations")
    # responsible_orgs=get_responsible_org_list(result)
    # implementing_agency_and_types=get_implementing_org_list(result)
    # insert_orgs(responsible_orgs,implementing_agency_and_types)
    ####sectors
    # print("Inserting sectors")
    # add_sectors_to_db(secondary_sectors, primary_sectors)

    ####categories
    # print("Inserting categories")
    # insert_categories(file_categories)

    all_orgs = get_organizations(agencies)
    categories = get_category_values(list(mapping_dict.keys()))
    all_currencies = get_currencies()
    all_adj_types = get_adjustment_types()
    sectors = get_sectors()
    amp_role = get_amp_role()
    login()
    for idx,item in enumerate(result):
        print("Adding to api: ",idx+1, item)
        # try:
        construct_object_and_import(item, categories, all_orgs, all_currencies, all_adj_types, sectors, amp_role[0], primary_sectors)
        # except Exception as e:
        #     print("Error adding to api:", e)
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
    # print(original_object)
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
    # print(new_object)

    import_project(json.dumps(new_object))


def create_transaction(tran_type: str, lst: [], original_object=None, all_currencies=None, all_adj_types=None):
    for item in original_object[tran_type]:
        lst.append({
            "transaction_amount": item['amount'],
            "currency": all_currencies[item['currency']],
            "adjustment_type": all_adj_types[item['adj_type']],
            "transaction_date": item['date']
        })


if __name__ == "__main__":
    # get_mapping('CFIS MAPPING.xlsx',1,2,1)
    get_data('Rwanda_NDC.xlsx', 1, 'Partnership Plan template')
