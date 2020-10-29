import logging
import os
import meraki
import requests
from __app__.shared_code import shared


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
    api_key = os.environ.get('meraki_api_key', '').lower()
    org_name = os.environ.get('meraki_org_name')
    org_id = None
    if not api_key or not org_name:
        logging.error("Error: you must include the Meraki API Key and Organization Name in order to continue")
        exit(1)
    mdashboard = meraki.DashboardAPI(api_key)


class AzureConfig:
    subscription_id = os.environ.get('subscription_id', None)


class SecureXConfig:
    securex_client_id = os.environ.get('securex_client_id')
    securex_client_password = os.environ.get('securex_client_password')
    if not securex_client_id or not securex_client_password:
        logging.error("Error: you must include the SecureX Token ID and SecureX Token Secret in order to continue")
        exit(1)


def main():
    # Obtain Meraki Org ID for API Calls
    result_org_id = MerakiConfig.mdashboard.organizations.getOrganizations()
    for x in result_org_id:
        if x['name'] == MerakiConfig.org_name:
            MerakiConfig.org_id = x['id']

    if not MerakiConfig.org_id:
        logging.error("Could not find Meraki Organization Name.")
        return

    # Get access token to authenticate to Azure
    if AzureConfig.subscription_id:
        access_token = get_bearer_token(_AZURE_MGMT_URL)
        if access_token is None:
            return
        header_with_bearer_token = {'Authorization': f'Bearer {access_token}'}

    # Deploy
    bearer_payload = shared.get_access_token(SecureXConfig.securex_client_id, SecureXConfig.securex_client_password)
    token = bearer_payload["access_token"]
    logging.debug(token)
    # mod_type = shared.create_integration_module(token)
    # logging.debug("Module Type ID=", mod_type["id"])
    # mod_inst = shared.create_integration_module_instance(token, mod_type["id"], app_url, MerakiConfig.org_id, MerakiConfig.api_key)
    # logging.debug(mod_inst)


if __name__ == '__main__':
    main()
