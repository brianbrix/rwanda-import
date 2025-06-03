import logging
import os
import sys

sys.path.append('/opt/airflow')

from datetime import datetime, timedelta

from airflow import DAG
from airflow.decorators import dag, task

from utils.api_util import login
from utils.data_importer import (
    read_data, get_mapping, clean_start_and_end_date, clean_up_sectors,
    clean_up_title, clean_up_orgs, get_organizations, get_category_values,
    get_currencies, get_adjustment_types, get_sectors, get_amp_role,
    construct_object_and_import, is_category, process_transaction
)

# Constants
dag_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(dag_dir, '..', 'utils', 'Rwanda_NDC.xlsx')
file_path2 = os.path.join(dag_dir, '..', 'utils', 'CFIS MAPPING.xlsx')
data_file = os.path.abspath(file_path)
mapping_file = os.path.abspath(file_path2)
sheet_name = 'Partnership Plan template'
skip_rows = 1


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 4, 24),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}



@task()
def read_data_task():
    logging.info("Reading data from file: %s", data_file)
    df1, df2 = read_data(file_path=data_file, skip_rows=skip_rows, sheet_name=sheet_name)
    df2 = df2.fillna("").astype(str)
    # Save to disk or tmp location
    df1_path = "/tmp/df1.parquet"
    df2_path = "/tmp/df2.parquet"
    df1.to_parquet(df1_path)
    df2.to_parquet(df2_path)
    return {'df1_path': df1_path, 'df2_path': df2_path}

@task()
def load_mapping_task():
    logging.info("Loading mapping from %s", mapping_file)
    mapping = get_mapping(mapping_file, 1, 2, 4, 7, 6, 1)
    return {'mapping_dict': mapping}

@task()
def process_rows_task(data_from_read, mapping_from_load):
    import pandas as pd
    import json

    df1 = pd.read_parquet(data_from_read['df1_path'])
    df2 = pd.read_parquet(data_from_read['df2_path'])
    mapping_dict = mapping_from_load['mapping_dict']

    columns = list(df1.columns)
    data = df2.to_numpy()

    result = []
    agencies, groups, secondary_sectors, primary_sectors = [], [], [], []
    file_categories = {amp_title: set() for amp_title in list(mapping_dict.keys())}
    invalid_rows = 0

    for row in data:
        row_result = {}
        for idx, column in enumerate(columns):
            for amp_title, ndc_title in mapping_dict.items():
                if amp_title is None or column is None or not isinstance(column, str):
                    invalid_rows += 1
                    continue
                if amp_title.lower() in ['commitment', 'disbursement']:
                    process_transaction(amp_title, ndc_title, column, row, idx, df2, row_result)
                    continue
                if ndc_title.lower() == column.lower():
                    col_value = row[idx] if idx < len(row) else None
                    if pd.notna(col_value):
                        row_result[amp_title] = col_value
                        if amp_title.lower() in ['implementing agency', 'responsible organisation', 'donor agency']:
                            agencies.append(col_value)
                        if amp_title.lower() == 'donor agency type':
                            groups.append(col_value)
                        if amp_title.lower() == 'secondary sector':
                            secondary_sectors.append(col_value)
                        if amp_title.lower() == 'primary sector':
                            primary_sectors.append(col_value)
                        if is_category(amp_title):
                            file_categories[amp_title].add(col_value)
        if row_result:
            result.append(row_result)

    logging.info(f"Number of invalid rows: {invalid_rows}")
    logging.info(f"Number of valid rows initially: {len(result)}")
    clean_start_and_end_date(result)
    clean_up_sectors(result)
    logging.info(f"Number of valid rows after title cleanup: {len(result)}")
    result = clean_up_title(result)
    logging.info(f"Number of valid rows after title cleanup: {len(result)}")
    result = clean_up_orgs(result)
    logging.info(f"Number of valid rows after orgs cleanup: {len(result)}")

    return {
        'result': result,
        'agencies': agencies,
        'file_categories': {k: list(v) for k, v in file_categories.items()},
        'primary_sectors': primary_sectors,
    }

@task()
def import_data_task(processed_data):
    import json

    # Since we're using @task, the input is already deserialized
    result = processed_data['result']
    agencies = processed_data['agencies']
    file_categories = processed_data['file_categories']
    primary_sectors = processed_data['primary_sectors']

    all_orgs = get_organizations(agencies)
    categories = get_category_values(list(file_categories.keys()))
    all_currencies = get_currencies()
    all_adj_types = get_adjustment_types()
    sectors = get_sectors()
    amp_role = get_amp_role()[0]
    login()

    for idx, item in enumerate(result):
        logging.info(f"Importing record {idx + 1}/{len(result)}")
        construct_object_and_import(
            item, categories, all_orgs, all_currencies,
            all_adj_types, sectors, amp_role, primary_sectors
        )

@dag(default_args=default_args,
     description='A DAG to process an excel file an create/update an activity in AMP',
     dag_id='import_activities_from_excel',
     tags=["import_activities_from_excel"],
     schedule_interval=None,
     is_paused_upon_creation=False
     )
def import_from_excel():
    data = read_data_task()
    mapping = load_mapping_task()
    processed_data = process_rows_task(data, mapping)
    import_data_task(processed_data)
import_from_excel()
