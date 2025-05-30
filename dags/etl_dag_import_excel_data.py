import logging

from airflow import DAG

from datetime import datetime

from airflow.providers.standard.operators.python import PythonOperator

from dags.utils.api_util import login
from dags.utils.data_importer import (
    read_data, get_mapping, clean_start_and_end_date, clean_up_sectors,
    clean_up_title, clean_up_orgs, get_organizations, get_category_values,
    get_currencies, get_adjustment_types, get_sectors, get_amp_role,
    construct_object_and_import, is_category, process_transaction
)

mapping_file = 'CFIS MAPPING.xlsx'
file_path = 'Rwanda_NDC.xlsx'
sheet_name = 'Partnership Plan template'
skip_rows = 1

def task_read_data(**kwargs):
    df1, df2 = read_data(file_path=file_path, skip_rows=skip_rows, sheet_name=sheet_name)
    kwargs['ti'].xcom_push(key='df1', value=df1.to_json())
    kwargs['ti'].xcom_push(key='df2', value=df2.to_json())

def task_load_mapping(**kwargs):
    mapping = get_mapping(mapping_file, 1, 2, 4, 7, 6, 1)
    kwargs['ti'].xcom_push(key='mapping_dict', value=mapping)

def task_process_rows(**kwargs):
    import pandas as pd
    import json

    df1 = pd.read_json(kwargs['ti'].xcom_pull(key='df1'))
    df2 = pd.read_json(kwargs['ti'].xcom_pull(key='df2'))
    mapping_dict = kwargs['ti'].xcom_pull(key='mapping_dict')

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

    context = {
        'result': result,
        'agencies': agencies,
        'file_categories': {k: list(v) for k, v in file_categories.items()},
        'primary_sectors': primary_sectors,
    }
    kwargs['ti'].xcom_push(key='processed_data', value=json.dumps(context))

def task_import_data(**kwargs):
    import json
    context = json.loads(kwargs['ti'].xcom_pull(key='processed_data'))
    result = context['result']
    agencies = context['agencies']
    file_categories = context['file_categories']
    primary_sectors = context['primary_sectors']

    all_orgs = get_organizations(agencies)
    categories = get_category_values(list(file_categories.keys()))
    all_currencies = get_currencies()
    all_adj_types = get_adjustment_types()
    sectors = get_sectors()
    amp_role = get_amp_role()[0]
    login(kwargs)

    for idx, item in enumerate(result):
        logging.info(f"Importing record {idx + 1}/{len(result)}")
        construct_object_and_import(item, categories, all_orgs, all_currencies, all_adj_types, sectors, amp_role, primary_sectors)

with DAG('cfis_data_ingestion',
         default_args={'start_date': datetime(2023, 1, 1)},
         schedule_interval=None,
         catchup=False,
         tags=['cfis']) as dag:

    read_data_task = PythonOperator(
        task_id='read_data',
        python_callable=task_read_data,
        provide_context=True
    )

    load_mapping_task = PythonOperator(
        task_id='load_mapping',
        python_callable=task_load_mapping,
        provide_context=True
    )

    process_rows_task = PythonOperator(
        task_id='process_rows',
        python_callable=task_process_rows,
        provide_context=True
    )

    import_data_task = PythonOperator(
        task_id='import_data',
        python_callable=task_import_data,
        provide_context=True
    )

    read_data_task >> load_mapping_task >> process_rows_task >> import_data_task
