import requests

# Global variable to hold the session cookie
auth_cookie = None

def login_to_backend(login_url, username, password, workspace_id):
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
        print("Login successful.")

        # Try to extract JSESSIONID (or the main auth cookie)
        cookie_jar = session.cookies.get_dict()
        if not cookie_jar:
            raise Exception("Login succeeded but no cookies were returned.")

        # You can inspect cookie_jar if needed
        print("Cookies received:", cookie_jar)

        # For example, if it uses JSESSIONID
        if 'JSESSIONID' in cookie_jar:
            return f"JSESSIONID={cookie_jar['JSESSIONID']}"
        else:
            # Use the first cookie as fallback
            name, value = next(iter(cookie_jar.items()))
            return f"{name}={value}"
    else:
        raise Exception(f"Login failed with status code {response.status_code}: {response.text}")


def login():
    """
    Initializes the global auth_cookie.
    """
    global auth_cookie
    if auth_cookie is None:
        login_url = 'https://amp-rwanda-pr-4394.stg.ampsite.net/rest/security/user'
        username = 'atl@amp.org'
        password = ''
        workspace_id = 67

        auth_cookie = login_to_backend(login_url, username, password, workspace_id)


def post_with_cookie(post_url, data, headers=None):
    """
    Makes a POST request using the auth cookie set in the 'Cookie' header.
    """
    if auth_cookie is None:
        raise Exception("Auth cookie not initialized. Call login() first.")

    default_headers = {
        'Content-type': 'application/json',
        'Cookie': auth_cookie
    }

    if headers:
        default_headers.update(headers)

    response = requests.post(post_url, data=data, headers=default_headers)

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
    response = post_with_cookie(post_url, json_data)
    print(response)
