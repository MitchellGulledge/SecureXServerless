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
    _ = get_jwt()
    meraki_config = meraki.MerakiConfig()
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
                    "query-params": {}
                }
            ]
        else:
            json_refer = [
                {
                    "id": "meraki-client-block",
                    "title": "Quarantine this Client",
                    "description": "Assign 'Block' Group Policy to this Client.",
                    "query-params": {}
                }
            ]

    return jsonify_data(json_refer)


@respond_api.route('/respond/trigger', methods=['POST'])
def respond_trigger():
    _ = get_jwt()
    _ = get_action_form_params()
    return jsonify_data({'status': 'success'})
