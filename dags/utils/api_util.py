import logging
from http import HTTPStatus

import requests

# Global variable to hold the session cookie
auth_cookie = None

def login_to_backend(login_url, username, password, workspace_id):
    global auth_cookie
    """
    Logs in to the backend and extracts the JSESSIONID cookie.
    """

    payload = {
        'username': username,
        'password': password,
        'workspaceId': workspace_id
    }

    session = requests.Session()
    response = session.post(login_url, json=payload)

    if response.status_code == 200:
        logging.info("Login successful.")
        auth_cookie = response.headers.get('Set-Cookie')
        return auth_cookie
    else:
        raise Exception(f"Login failed with status code {response.status_code}: {response.text}")


def login(kwargs):
    """
    Initializes the global auth_cookie.
    """
    dag_run = kwargs.get('dag_run')
    if dag_run:
        config = dag_run.conf
        print(f"DAG run config: {config}")
    else:
        print("No dag_run.conf available")
    logging.info(f'The username {dag_run.conf["username"]}')
    logging.info(f'The password {dag_run.conf["password"]}')
    logging.info(f'The workspaceId {dag_run.conf["workspaceId"]}')
    logging.info(f'The Url is {dag_run.conf["baseUrl"]}')
    global auth_cookie
    login_url = dag_run.conf["baseUrl"]+'/rest/security/user'
    username =  dag_run.conf["username"]
    password = dag_run.conf["password"]
    workspace_id = dag_run.conf["workspaceId"]

    login_to_backend(login_url, username, password, workspace_id)


def post_with_cookie(post_url, data, headers=None):
    global auth_cookie
    """
    Makes a POST request using the auth cookie set in the 'Cookie' header.
    """
    if auth_cookie is None:
        raise Exception("Auth cookie not initialized. Call login() first.")
    if auth_cookie is None:
        raise Exception("Auth cookie not initialized. Call login() first.")
    else:
        default_headers = {
            'Content-type': 'application/json',
            'Cookie': auth_cookie.split(';')[0]
        }
        logging.info("Headers", default_headers)

        if headers:
            default_headers.update(headers)

        response = requests.post(post_url, data=data, headers=default_headers)

        if response.status_code == HTTPStatus.OK or response.status_code == HTTPStatus.CREATED:
            return response.json()
        else:

            raise Exception(f"POST request failed: {response.status_code} - {response.text}")


def import_project(json_data):
    """
    Imports a project using the provided JSON data.
    """
    logging.info(json_data)
    post_url = 'https://amp-rwanda-pr-4394.stg.ampsite.net/rest/activity?can-downgrade-to-draft=true'
    response = post_with_cookie(post_url, json_data)
    logging.info(response)
