import requests

# Global session variable
session = None

def login_to_backend(login_url, username, password, workspace_id):
    """
    Logs in to the backend and returns a session object if successful.
    """
    s = requests.Session()
    payload = {
        'username': username,
        'password': password,
        'workspaceId': workspace_id
    }

    response = s.post(login_url, json=payload)

    if response.status_code == 200:
        print("Login successful.")
        return s
    else:
        raise Exception(f"Login failed with status code {response.status_code}: {response.text}")


def login():
    """
    Initializes the global session.
    """
    global session
    if session is None:
        login_url = 'https://amp-rwanda-pr-4394.stg.ampsite.net/rest/security/user'
        username = 'atl@amp.org'
        password = ''
        workspace_id = 67

        session = login_to_backend(login_url, username, password, workspace_id)


def post_with_session(post_url, data, headers=None):
    """
    Makes a POST request using the global session.
    """
    if session is None:
        raise Exception("Session not initialized. Call login() first.")
    headers = {'Content-type': 'application/json'}
    response = session.post(post_url, data=data, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"POST request failed: {response.status_code} - {response.text}")


def import_project(json_data):
    """
    Imports a project using the provided JSON data.
    """
    print(json_data)
    post_url = 'https://amp-rwanda-develop.stg.ampsite.net/rest/activity?can-downgrade-to-draft=true'
    response = post_with_session(post_url, json_data)
    print(response)
