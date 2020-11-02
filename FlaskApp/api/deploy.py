from flask import request, Blueprint, render_template, jsonify, redirect
import requests
from .utils import get_jwt, jsonify_data
import meraki
import json
import os
import sys
import logging
from urllib.parse import urlparse
from .. import config


deploy_api = Blueprint('deploy', __name__)


class MerakiConfig:
    api_key = os.environ.get('meraki_api_key', '').lower()
    org_name = os.environ.get('meraki_org_name')
    org_id = None
    if not api_key or not org_name:
        logging.error("Error: you must include the Meraki API Key and Organization Name in order to continue")
        exit(1)
    mdashboard = meraki.DashboardAPI(api_key, print_console=False, suppress_logging=True, output_log=False,
                                     caller=config.meraki_user_agent)


class AzureConfig:
    subscription_id = os.environ.get('subscription_id', None)


class SecureXConfig:
    securex_client_id = os.environ.get('securex_client_id')
    securex_client_password = os.environ.get('securex_client_password')
    if not securex_client_id or not securex_client_password:
        logging.error("Error: you must include the SecureX Token ID and SecureX Token Secret in order to continue")
        exit(1)


def read_file_all(in_filename):
    pathname = os.path.dirname(sys.argv[0])
    fn = os.path.join(pathname, in_filename)
    print(fn)
    with open(fn, 'r+') as in_file:
        return in_file.read()


def get_access_token(client_id, client_pw):
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'Accept': 'application/json'}
    data = {'grant_type': 'client_credentials'}
    url = 'https://visibility.amp.cisco.com/iroh/oauth2/token'
    response = requests.post(url, data=data, headers=headers, auth=(client_id, client_pw))

    if response.ok:
        return response.json()
    else:
        return None


def get_integration_module_type(token, name_filter=None):
    url = "https://visibility.amp.cisco.com/iroh/iroh-int/module-type"
    headers = {'Content-Type': 'application/json',
               'Accept': 'application/json',
               'Authorization': 'Bearer ' + token}

    ret = requests.get(url, headers=headers)
    rjson = ret.json()

    if name_filter:
        out_res = []
        for rj in rjson:
            if rj.get("default_name", "") == name_filter:
                out_res.append(rj)
        return out_res
    else:
        return rjson


def create_update_integration_module_type(token, update_id=None):
    url = "https://visibility.amp.cisco.com/iroh/iroh-int/module-type"
    headers = {'Content-Type': 'application/json',
               'Accept': 'application/json',
               'Authorization': 'Bearer ' + token}
    payload = {
        "title": "Meraki Dashboard Test",
        "default_name": "Meraki Dashboard",
        "short_description": "Meraki Dashboard is a cloud-based network infrastructure management platform",
        "description": "Meraki Dashboard is a cloud-based network infrastructure management platform. This platform enables the efficient management of policies and configurations in branch offices and other highly distributed environments to achieve a consistent network implementation.",
        "configuration_spec": [
            {
                "key": "url",
                "type": "string",
                "label": "URL",
                "required": True,
                "tooltip": "The base URL of the Serverless Relay"
            },
            {
                "key": "basic-auth-user",
                "type": "string",
                "label": "Organization ID",
                "required": True
            },
            {
                "key": "basic-auth-password",
                "type": "password",
                "label": "API Key",
                "required": True
            }
        ],
        "capabilities": [
            {
                "id": "health",
                "description": ""
            },
            {
                "id": "deliberate",
                "description": ""
            },
            {
                "id": "observe",
                "description": ""
            },
            {
                "id": "refer",
                "description": ""
            },
            {
                "id": "respond",
                "description": ""
            }
        ],
        "properties": {
            "supported-apis": [
                "health",
                "observe/observables",
                "deliberate/observables",
                "refer/observables",
                "respond/observables",
                "respond/trigger",
                "tiles",
                "tiles/tile",
                "tiles/tile-data"
            ],
            "auth-type": "basic"
        },
        "flags": [
            "serverless"
        ],
        "logo": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIiB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCI+Cgk8c3R5bGU+CgkJdHNwYW4geyB3aGl0ZS1zcGFjZTpwcmUgfQoJCS5zaHAwIHsgZmlsbDogIzk1YTVhNiB9IAoJCS5zaHAxIHsgZmlsbDogIzdmOGM4ZCB9IAoJPC9zdHlsZT4KCTxnIGlkPSJMYXllciI+CgkJPHBhdGggaWQ9IkxheWVyIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiIGNsYXNzPSJzaHAwIiBkPSJNMTcuNTkgMTEuNjdMMjYuNDMgMTQuNThMMjcuMDcgMTVDMjguNSAxNC4xNyAyOS45OCAxMy4zMyAzMS40OSAxMi41TDMxLjIyIDExLjY3TDMyLjk3IDIuNUw0MS4wNyAwLjQyTDQ3LjI0IDcuNUw0Ny40MiA4LjMzQzQ5LjE1IDcuOTIgNTAuODUgNy45MiA1Mi41OCA4LjMzTDUyLjc2IDcuNUw1OC45MyAwLjQyTDY3LjAzIDIuNUw2OC43OCAxMS42N0w2OC41MSAxMi41QzcwLjAyIDEzLjMzIDcxLjUgMTQuMTcgNzIuOTMgMTVMNzMuNTcgMTQuNThMODIuNDEgMTEuNjdMODguMyAxNy41TDg1LjM1IDI2LjI1TDg0LjcxIDI3LjA4Qzg1LjY1IDI4LjMzIDg2LjU0IDMwIDg3LjI5IDMxLjI1TDg4LjEyIDMxLjI1TDk3LjIzIDMyLjkyTDk5LjQ0IDQwLjgzTDkyLjM1IDQ3LjA4TDkxLjYyIDQ3LjA4QzkxLjczIDQ5LjE3IDkxLjczIDUwLjgzIDkxLjYyIDUyLjVMOTIuMzUgNTIuNUw5OS40NCA1OC43NUw5Ny4yMyA2Ny4wOEw4OC4xMiA2OC43NUw4Ny4yOSA2OC4zM0M4Ni41NCA3MCA4NS42NSA3MS4yNSA4NC43MSA3Mi45Mkw4NS4zNSA3My4zM0w4OC4zIDgyLjA4TDgyLjQxIDg4LjMzTDczLjU3IDg1TDcyLjkzIDg0LjU4QzcxLjUgODUuNDIgNzAuMDIgODYuMjUgNjguNTEgODcuMDhMNjguNzggODcuOTJMNjcuMDMgOTcuMDhMNTguOTMgOTkuMTdMNTIuNzYgOTIuMDhMNTIuNTggOTEuNjdMNDcuNDIgOTEuNjdMNDcuMjQgOTIuMDhMNDEuMDcgOTkuMTdMMzIuOTcgOTcuMDhMMzEuMjIgODcuOTJMMzEuNDkgODcuMDhDMjkuOTggODYuMjUgMjguNSA4NS40MiAyNy4wNyA4NC41OEwyNi40MyA4NUwxNy41OSA4OC4zM0wxMS43IDgyLjA4TDE0LjY0IDczLjMzTDE1LjI5IDcyLjkyQzE0LjM0IDcxLjI1IDEzLjQ2IDcwIDEyLjcxIDY4LjMzTDExLjg4IDY4Ljc1TDIuNzcgNjcuMDhMMC41NiA1OC43NUw3LjY1IDUyLjVMOC4zOCA1Mi41QzguMjggNTAuODMgOC4yOCA0OS4xNyA4LjM4IDQ3LjA4TDcuNjUgNDcuMDhMMC41NiA0MC44M0wyLjc3IDMyLjkyTDExLjg4IDMxLjI1TDEyLjcxIDMxLjI1QzEzLjQ2IDMwIDE0LjM0IDI4LjMzIDE1LjI5IDI3LjA4TDE0LjY0IDI2LjI1TDExLjcgMTcuNUwxNy41OSAxMS42N0wxNy41OSAxMS42N1pNMjkuMzggMjkuMTdDMTcuOTkgNDAuNDIgMTcuOTkgNTkuMTcgMjkuMzggNzAuNDJDNDAuNzcgODEuNjcgNTkuMjMgODEuNjcgNzAuNjMgNzAuNDJDODIuMDEgNTkuMTcgODIuMDEgNDAuNDIgNzAuNjMgMjkuMTdDNTkuMjMgMTcuOTIgNDAuNzcgMTcuOTIgMjkuMzggMjkuMTdaIiAvPgoJCTxwYXRoIGlkPSJMYXllciIgZmlsbC1ydWxlPSJldmVub2RkIiBjbGFzcz0ic2hwMSIgZD0iTTI2LjQzIDI2LjI1QzM5LjQ1IDEzLjMzIDYwLjU1IDEzLjMzIDczLjU3IDI2LjI1Qzg2LjU5IDM5LjE3IDg2LjU5IDYwLjQyIDczLjU3IDczLjMzQzYwLjU1IDg2LjI1IDM5LjQ1IDg2LjI1IDI2LjQzIDczLjMzQzEzLjQxIDYwLjQyIDEzLjQxIDM5LjE3IDI2LjQzIDI2LjI1TDI2LjQzIDI2LjI1Wk00MS42MiAzNS40MkM0NS4zMSAzMy4zMyA0OS41MiAzMi41IDUzLjU5IDMzLjc1TDU5LjM5IDIyLjA4QzUwLjQ3IDE5LjE3IDQwLjQzIDIwLjgzIDMyLjYgMjYuNjdMNDEuNjIgMzUuNDJaTTI2LjcxIDMyLjVDMjAuODUgNDAuNDIgMTkuMzUgNTAuNDIgMjIuMzggNTkuMTdMMzMuNyA1My4zM0MzMi44IDQ5LjE3IDMzLjU1IDQ1IDM1LjczIDQxLjY3TDI2LjcxIDMyLjVaTTQ0LjExIDQzLjc1QzQwLjg1IDQ3LjA4IDQwLjg1IDUyLjUgNDQuMTEgNTUuODNDNDcuMzYgNTkuMTcgNTIuNjQgNTkuMTcgNTUuODkgNTUuODNDNTkuMTUgNTIuNSA1OS4xNSA0Ny4wOCA1NS44OSA0My43NUM1Mi42NCA0MC44MyA0Ny4zNiA0MC44MyA0NC4xMSA0My43NVpNNjYuNzYgMjYuMjVMNjAuOTYgMzcuNUM2MS4yMiAzNy41IDYxLjUzIDM3LjkyIDYxLjc4IDM3LjkyQzY0LjY2IDQwLjgzIDY2LjIzIDQ0LjU4IDY2LjU3IDQ4LjMzTDc5LjEgNTAuNDJDNzkuMTkgNDIuNSA3Ni40MSAzNSA3MC42MyAyOS4xN0M2OS40MiAyNy45MiA2OC4xIDI3LjA4IDY2Ljc2IDI2LjI1Wk0yOS4zOCA3MC40MkMzNS4xNiA3Ni4yNSA0Mi43OCA3OS4xNyA1MC4zNyA3OC43NUw0OC41MiA2Ni4yNUM0NC43NyA2Ni4yNSA0MS4wOSA2NC41OCAzOC4yMSA2MS42N0MzNy45NiA2MS4yNSAzNy44IDYxLjI1IDM3LjU3IDYwLjgzTDI2LjI1IDY2LjY3QzI3LjE5IDY3LjkyIDI4LjE4IDY5LjE3IDI5LjM4IDcwLjQyWk02MS43OCA2MS42N0M2MC4yNiA2My4zMyA1OC40OSA2NC4xNyA1Ni42MyA2NUw1OC41NiA3Ny45MkM2Mi45NyA3Ni4yNSA2Ny4xNCA3My43NSA3MC42MyA3MC40MkM3NC4xMSA2Ny4wOCA3Ni41NSA2Mi45MiA3Ny45IDU4LjMzTDY1LjI4IDU2LjY3QzY0LjQ4IDU4LjMzIDYzLjMxIDYwIDYxLjc4IDYxLjY3WiIgLz4KCTwvZz4KPC9zdmc+"
    }

    if update_id:
        ret = requests.patch(url + "/" + update_id, headers=headers, json=payload)
    else:
        ret = requests.post(url, headers=headers, json=payload)

    return ret.json()


def get_integration_module_instance(token, name_filter=None):
    url = "https://visibility.amp.cisco.com/iroh/iroh-int/module-instance"
    headers = {'Content-Type': 'application/json',
               'Accept': 'application/json',
               'Authorization': 'Bearer ' + token}

    ret = requests.get(url, headers=headers)
    rjson = ret.json()

    if name_filter:
        out_res = []
        for rj in rjson:
            if rj.get("name", "") == name_filter:
                out_res.append(rj)
        return out_res
    else:
        return rjson


def create_update_integration_module_instance(token, type_id, appurl, orgid, apikey, update_id=None):
    url = "https://visibility.amp.cisco.com/iroh/iroh-int/module-instance"
    headers = {'Content-Type': 'application/json',
               'Accept': 'application/json',
               'Authorization': 'Bearer ' + token}
    payload = {
        "name": "Meraki Dashboard",
        "module_type_id": type_id,
        "settings": {
          "basic-auth-password": apikey,
          "basic-auth-user": orgid,
          "url": appurl
        },
        "visibility": "org"
    }

    if update_id:
        del payload["visibility"]
        ret = requests.patch(url + "/" + update_id, headers=headers, json=payload)
    else:
        ret = requests.post(url, headers=headers, json=payload)

    return ret.json()


@deploy_api.route('/deploy', methods=['GET'])
def deploy():
    logging.info(MerakiConfig.org_name)
    # Obtain Meraki Org ID for API Calls
    result_org_id = MerakiConfig.mdashboard.organizations.getOrganizations()
    for x in result_org_id:
        if x['name'] == MerakiConfig.org_name:
            MerakiConfig.org_id = x['id']

    if not MerakiConfig.org_id:
        logging.error("Could not find Meraki Organization Name.")
        return jsonify({'status': 'error'})

    app_url = str(request.url)
    logging.info(app_url)
    o = urlparse(request.base_url)

    # Get SecureX Token
    bearer_payload = get_access_token(SecureXConfig.securex_client_id, SecureXConfig.securex_client_password)
    token = bearer_payload["access_token"]

    # See if module already exists...
    cur_mod = get_integration_module_type(token, "Meraki Dashboard")
    if len(cur_mod) > 0:
        # Update Integration Module Type in SecureX
        mod_type = create_update_integration_module_type(token, update_id=cur_mod[0]["id"])
        logging.info("(Existing) Module Type ID=" + str(mod_type["id"]))
    else:
        # Create Integration Module Type in SecureX
        mod_type = create_update_integration_module_type(token)
        logging.info("(New) Module Type ID=" + str(mod_type["id"]))

    if o.hostname == "localhost":
        return jsonify({"status": "error: not creating or update module instance since URL is from localhost"})

    # See if instance already exists...
    cur_inst = get_integration_module_instance(token, "Meraki Dashboard")
    if len(cur_inst) > 0:
        # Update Integration Module Instance in SecureX
        mod_inst = create_update_integration_module_instance(token, mod_type["id"], app_url, MerakiConfig.org_id,
                                                             MerakiConfig.api_key, update_id=cur_inst[0]["id"])
        logging.info("(Existing) Module Instance ID=" + str(mod_inst))
    else:
        # Create Integration Module Instance in SecureX
        mod_inst = create_update_integration_module_instance(token, mod_type["id"], app_url, MerakiConfig.org_id,
                                                             MerakiConfig.api_key)
        logging.info("(New) Module Instance ID=" + str(mod_inst))


    return redirect("https://securex.us.security.cisco.com")
    # return jsonify({'status': 'ok'})


@deploy_api.route('/', methods=['GET'])
def root():
    return redirect("deploy")


# @deploy_api.route('/deploy', methods=['GET'])
# def deploy_get():
#     return render_template('landing.html')


@deploy_api.route('/orgs', methods=['GET'])
def getmerakiorgs():
    apikey = request.headers.get("X-Cisco-Meraki-API-Key")
    baseurl = request.headers.get("X-Cisco-Meraki-API-URL")

    try:
        dashboard = meraki.DashboardAPI(base_url=baseurl, api_key=apikey,
                                        print_console=False, output_log=False)
        orgs = dashboard.organizations.getOrganizations()
        orgs_sorted = sorted(orgs, key=lambda i: i['name'])
        return jsonify(orgs_sorted)
    except Exception:
        return jsonify({})
