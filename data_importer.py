import json

import pandas as pd

from api_util import login, import_project
from category_util import is_category, get_category_values, insert_categories, extract_category, get_adjustment_types
from currency_utl import get_currencies
from database_utils import run_sql_file_postgres
from file_data_utils import clean_start_and_end_date, clean_up_title, extract_first_year_date, process_transaction
from organizations_util import get_organizations
from sectors_util import get_sectors, add_sectors_to_db

mapping_file='CFIS MAPPING.xlsx'
def get_mapping(excel_file: str, ndc_column_index: int, amp_column_index: int, is_funding_column: int, adj_type_column: int, currency_column: int, skip_rows: int):
    # Load the Excel file (reads the first sheet by default)
    df = pd.read_excel(excel_file, skiprows=skip_rows)

    column_a = df.iloc[:, ndc_column_index]        # NDC column
    column_b = df.iloc[:, amp_column_index]        # AMP column (key)
    column_funding = df.iloc[:, is_funding_column] # 'Yes'/'No'
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

def get_data(excel_file: str, skip_rows: int, sheet_name:str):
    # Load the Excel file (reads the first sheet by default)
    df1 = pd.read_excel(excel_file, skiprows=skip_rows, sheet_name=sheet_name)
    df2 = pd.read_excel(excel_file, skiprows=skip_rows+1, sheet_name=sheet_name)
    mapping_dict = get_mapping(mapping_file, 1, 2, 4,7,6,1)

    # headers = df1.iloc[header_row]
    columns = list(df1.columns)
    # column_b = df.iloc[:,1]

    # result_dict = dict(zip(column_a, column_b))

    # print(mapping_dict)
    # print(columns)

    result = []

    agencies=[]
    groups =[]
    sectors =[]
    file_categories={amp_title:set() for amp_title in list(mapping_dict.keys()) }

# Go through each list element and its index
    for row in df2.to_numpy():
        row_result = {}
        for idx, column in enumerate(columns):
            for amp_title,ndc_title in mapping_dict.items():
                # file_categories[amp_title]=[]
                if amp_title is None or column is None:
                    continue
                if not isinstance(column, str) :
                    continue
                #map for commitments and disbursements
                if amp_title.lower() in ['commitment', 'disbursement']:
                    process_transaction(amp_title,ndc_title,column,row,idx,df2,row_result)
                    continue
                if ndc_title.lower() == column.lower():
                    if idx < len(df2):
                        col_value = row[idx]
                        if pd.notna(col_value):
                            row_result[amp_title] = col_value
                            if amp_title.lower()=='implementing agency':
                                agencies.append(col_value)
                            if amp_title.lower()=='donor agency type':
                                groups.append(col_value)
                            if amp_title.lower()=='donor agency':
                                agencies.append(col_value)
                            if amp_title.lower() == 'secondary sector':
                                sectors.append(col_value)
                            if is_category(amp_title):
                                file_categories[amp_title].add(col_value)
        if row_result:  # Only add non-empty rows
            result.append(row_result)
    clean_start_and_end_date(result)
    result = clean_up_title(result)
    categories = get_category_values(list(mapping_dict.keys()))

    all_orgs = get_organizations(agencies)
    # run_sql_file_postgres('insert_orgs.sql')
    # add_sectors_to_db(sectors)
    # insert_categories(file_categories)
    all_currencies = get_currencies()
    all_adj_types = get_adjustment_types()
    sectors =get_sectors()
    login()
    for item in result:
        print("Adding to api", item)
        try:
            construct_object_and_import(item, categories, all_orgs, all_currencies, all_adj_types, sectors)
        except:
            print("Error adding to api")
            break

def construct_object_and_import(original_object:{}, all_categories, all_organizations, all_currencies, all_adj_types, all_sectors):
    new_object = {}
    new_object["project_title"] = original_object['Project Title']
    new_object["is_draft"]=True
    new_object["actual_start_date"]= original_object['Actual start date']
    new_object["actual_end_date"]= original_object['Actual end date']
    new_object["donor_organization"]=all_organizations[original_object['Donor Agency']]
    new_object["responsible_organization"]=all_organizations[original_object['Implementing agency']]
    new_object["a_c_chapter"] = extract_category(all_categories,'A.C. Chapter',original_object['A.C. Chapter'])
    new_object["activity_status"]= extract_category(all_categories,'Activity status', original_object['Activity status'])
    new_object["procurement_system"]= extract_category(all_categories, 'Procurement System', original_object['Procurement System'])
    fundings =[]
    commitments=[]
    disbursements=[]
    create_transaction('Commitment', commitments, original_object, all_currencies, all_adj_types)
    create_transaction('Disbursement', disbursements, original_object, all_currencies, all_adj_types)



    fundings.append({
        "donor_organization_id":new_object['donor_organization'][0]['organization'],
        "financing_instrument":extract_category(all_categories,'Financing Instrument',original_object['Financing Instrument']),
        "type_of_assistance":extract_category(all_categories,'Type of Assistance',original_object['Type of Assistance']),
        "commitments":commitments,
        "disbursements":disbursements
    })
    new_object["fundings"]=fundings
    new_object["secondary_sectors"]=[
        {
            "sector":all_sectors[original_object['Secondary sector']]
        }
    ]
    print(new_object)
    import_project(json.dumps(new_object))
    return new_object

def create_transaction(tran_type:str, lst:[], original_object=None, all_currencies=None, all_adj_types=None):
    for item in original_object[tran_type]:
        lst.append({
            "transaction_amount":item['amount'],
            "currency":all_currencies[item['currency']],
            "adjustment_type":all_adj_types[item['adj_type']],
            "transaction_date":item['date']
        })

if __name__ == "__main__":
    # get_mapping('CFIS MAPPING.xlsx',1,2,1)
    get_data('Rwanda_NDC.xlsx', 1, 'Partnership Plan template')
