"""Functionality related to interactions with the CleanSMRs API."""

import requests


def get_auth_token(base_url, username, password):
    """Requests a JSON Web Token from the API using the configured credentials.

    Args:
        url (str): The API URL.
        username (str): The API username.
        password (str): The API password.

    Returns:
        dict: A dictionary containing a JSON Web Token and expiry datetime.
    """

    login_url = f"{base_url}/login"

    # Make a request to the API's login endpoint using the provided credentials
    # to request a JWT.
    response = requests.get(url=login_url, auth=(username, password), timeout=5)

    # Raise an exception if the request was unsuccessful.
    response.raise_for_status()

    # Return the JWT from the response JSON.
    return response.json()
