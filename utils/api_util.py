import json
import logging
from http import HTTPStatus
from numbers import Number

from airflow.configuration import conf

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


def login():
    """
    Initializes the global auth_cookie.
    """

    global auth_cookie
    login_url = conf.get('api', 'baseurl')+'/rest/security/user'
    username =  conf.get('api', 'username')
    password = conf.get('api','password')
    workspace_id =int(conf.get('api', 'workspaceid'))

    logging.info("Login URL", login_url)
    logging.info("Username", username)
    logging.info("Password", password)
    logging.info("Workspace ID", workspace_id)

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


def import_project(json_data, is_existing):
    """
    Imports a project using the provided JSON data.
    """
    logging.info(json_data)
    post_url = conf.get('api', 'baseurl')+'/rest/activity?can-downgrade-to-draft=true'
    if is_existing:
        logging.info("Updating project with id: %s and title %s", json_data['internal_id'], json_data['project_title'])
        post_url = conf.get('api', 'baseurl')+'/rest/activity/'+str(json_data['internal_id'])+'?can-downgrade-to-draft=true'
    response = post_with_cookie(post_url, json.dumps(json_data))
    logging.info(response)
