import datetime as dt
import json
import logging
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timedelta
from io import BytesIO
from operator import itemgetter
import time
import azure.functions as func
import meraki
import requests
from IPy import IP
from __app__.shared_code.appliance import Appliance

_AZURE_MGMT_URL = "https://management.azure.com"
_BLOB_HOST_URL = "blob.core.windows.net"
_YES = "Yes"
_NO = "No"

def _get_microsoft_network_base_url(mgmt_url, sub_id, rg_name=None, provider="Microsoft.Network"):
    if rg_name:
        return "{0}/subscriptions/{1}/resourceGroups/{2}/providers/{3}".format(mgmt_url, sub_id, rg_name, provider)

    return "{0}/subscriptions/{1}/providers/{2}".format(mgmt_url, sub_id, provider)


def get_bearer_token(resource_uri):
    access_token = None
    try:
        identity_endpoint = os.environ['IDENTITY_ENDPOINT']
        identity_header = os.environ['IDENTITY_HEADER']
    except:
        logging.error("Could not obtain authentication token for Azure. Please ensure "
                      "System Assigned identities have been enabled on the Azure Function.")
        return None

    token_auth_uri = f"{identity_endpoint}?resource={resource_uri}&api-version=2017-09-01"
    head_msi = {'secret': identity_header}
    try:
        resp = requests.get(token_auth_uri, headers=head_msi)
        access_token = resp.json()['access_token']
    except Exception as e:
        logging.error("Could not obtain access token to manage other Azure resources.")
        logging.error(e)

    return access_token

class MerakiConfig:
    api_key = os.environ['meraki_api_key'].lower()
    org_name = os.environ['meraki_org_name']
    tag_placeholder_network = 'tag-placeholder'
    org_id = None

class AzureConfig:
    subscription_id = os.environ['subscription_id']
    

# Obtain Meraki Org ID for API Calls
mdashboard = meraki.DashboardAPI(MerakiConfig.api_key)
result_org_id = mdashboard.organizations.getOrganizations()
for x in result_org_id:
    if x['name'] == MerakiConfig.org_name:
        MerakiConfig.org_id = x['id']

if not MerakiConfig.org_id:
    logging.error("Could not find Meraki Organization Name.")
    return

# Get access token to authenticate to Azure
access_token = get_bearer_token(_AZURE_MGMT_URL)
if access_token is None:
    return
header_with_bearer_token = {'Authorization': f'Bearer {access_token}'}
