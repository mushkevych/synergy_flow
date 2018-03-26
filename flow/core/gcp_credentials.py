import io
import json

from google.auth import compute_engine
from google.oauth2 import service_account


def gcp_credentials(service_account_file):
    if service_account_file:
        with io.open(service_account_file, 'r', encoding='utf-8') as json_fi:
            credentials_info = json.load(json_fi)
        credentials = service_account.Credentials.from_service_account_info(credentials_info)
    else:
        # Explicitly use Compute Engine credentials. These credentials are
        # available on Compute Engine, App Engine Flexible, and Container Engine.
        credentials = compute_engine.Credentials()
    return credentials
