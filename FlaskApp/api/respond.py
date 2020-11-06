from functools import partial
from flask import Blueprint, request
from .schemas import ObservableSchema, ActionFormParamsSchema
from .utils import get_json, get_jwt, jsonify_data
from ..shared_code import meraki


respond_api = Blueprint('respond', __name__)

get_observables = partial(get_json, schema=ObservableSchema(many=True))
get_action_form_params = partial(get_json, schema=ActionFormParamsSchema())


@respond_api.route('/respond/observables', methods=['POST'])
def respond_observables():
    meraki_config = meraki.MerakiConfig(auth=get_jwt())
    json_refer = []

    try:
        ob = get_observables()
    except Exception:
        return jsonify_data(json_refer)

    if ob[0]["type"] == "ip":
        cli = meraki_config.find_meraki_client(client_ip=ob[0]["value"])
        if not cli:
            json_refer = [
                {
                    "id": "meraki-firewall-block",
                    "title": "Block this IP Address",
                    "description": "Add Firewall rule to block this IP in Meraki Dashboard",
                    "query-params": {
                        "observable_type": ob[0]["type"],
                        "observable_value": ob[0]["value"]
                    }
                }
            ]
        else:
            json_refer = [
                {
                    "id": "meraki-client-block",
                    "title": "Quarantine this Client",
                    "description": "Assign 'Block' Group Policy to this Client.",
                    "query-params": {
                        "client_id": cli["client"]["mac"],
                        "network_id": cli["network"]["id"],
                        "observable_type":ob[0]["type"],
                        "observable_value":ob[0]["value"]
                     }
                }
            ]

    return jsonify_data(json_refer)


@respond_api.route('/respond/trigger', methods=['POST'])
def respond_trigger():
    meraki_config = meraki.MerakiConfig(auth=get_jwt())

    ac = get_action_form_params()
    print(ac, meraki_config.org_id, meraki_config.api_key)

    return jsonify_data({'status': 'success'})
