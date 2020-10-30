from functools import partial
from flask import Blueprint
from .schemas import ObservableSchema
from .utils import get_json, get_jwt, jsonify_data
import meraki
import datetime
from .. import config
import json

from bundlebuilder.models.entity import BaseEntity
from bundlebuilder.models.primary import (
    Bundle,
    Sighting,
    Judgement,
    Indicator,
    Relationship,
    Verdict,
)
from bundlebuilder.models.secondary import (
    ObservedTime,
    Observable,
    ValidTime,
)
from bundlebuilder.session import Session


enrich_api = Blueprint('enrich', __name__)
get_observables = partial(get_json, schema=ObservableSchema(many=True))


def find_observable():
    session = Session(
        external_id_prefix='meraki-tr-module',
        source='Meraki Threat Response Module',
        source_uri=(
            'https://github.com/joshand/meraki-tr-module'
        ),
    )

    in_vals = get_jwt()
    in_list = in_vals.split(":")
    ob = get_observables()
    ob_list = []
    for o in ob:
        ob_list.append(o["value"])

    dashboard = meraki.DashboardAPI(base_url=config.meraki_base_url, api_key=in_list[1], print_console=False,
                                    output_log=False,
                                    caller=config.meraki_user_agent, suppress_logging=True)

    ct = datetime.datetime.utcnow()
    start_time = (ct + datetime.timedelta(hours=-1)).isoformat() + 'Z'
    end_time = ct.isoformat() + 'Z'
    dev_stat = dashboard.appliance.getOrganizationApplianceSecurityEvents(in_list[0], total_pages=10,
                                                                          sortOrder="descending", perPage=1000,
                                                                          t0=start_time, t1=end_time)

    for d in dev_stat:
        if d["eventType"] == "IDS Alert":
            src_lst = d.get("srcIp", "").split(":")
            dst_lst = d.get("destIp", "").split(":")
            if src_lst[0] in ob_list or dst_lst[0] in ob_list:
                print(d)
        elif d["eventType"] == "File Scanned":
            if d.get("clientIp") in ob_list or d.get("srcIp") in ob_list or d.get("descIp") in ob_list:
                print(d)

    return {}


@enrich_api.route('/deliberate/observables', methods=['POST'])
def deliberate_observables():
    _ = get_jwt()
    _ = get_observables()
    return jsonify_data({})


@enrich_api.route('/observe/observables', methods=['POST'])
def observe_observables():
    return jsonify_data(find_observable())


@enrich_api.route('/refer/observables', methods=['POST'])
def refer_observables():
    _ = get_jwt()
    _ = get_observables()
    return jsonify_data([])
