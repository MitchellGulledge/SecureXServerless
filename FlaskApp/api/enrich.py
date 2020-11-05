from functools import partial
from flask import Blueprint, request
from .schemas import ObservableSchema
from .utils import get_json, get_jwt, jsonify_data
import datetime
from .. import config
import json
import logging
import os
from ..shared_code import securex, meraki

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
    IdentitySpecification,
    ObservedRelation,
    ExternalReference,
)


enrich_api = Blueprint('enrich', __name__)
get_observables = partial(get_json, schema=ObservableSchema(many=True))


def find_observables():
    securex_config = securex.SecureXConfig()
    meraki_config = meraki.MerakiConfig()
    json_data = request.json
    # [{'value': '190.168.1.203', 'type': 'ip'}]
    # [{'value': 'db8c0fc8427546ed54664fba24bdc7aa335eedb34b21c0d9a030dbc4f2bd7aee', 'type': 'sha256'}]
    logging.info(json_data)
    search_val = json_data[0]["value"]
    search_type = json_data[0]["type"]

    in_vals = get_jwt()
    in_list = in_vals.split(":")
    ob = get_observables()
    ob_list = []
    for o in ob:
        ob_list.append(o["value"])

    ct = datetime.datetime.utcnow()
    start_time = (ct + datetime.timedelta(hours=-1)).isoformat() + 'Z'
    end_time = ct.isoformat() + 'Z'
    dev_stat = meraki_config.mdashboard.appliance.getOrganizationApplianceSecurityEvents(in_list[0], total_pages=1,
                                                                                         sortOrder="descending",
                                                                                         perPage=1000,
                                                                                         t0=start_time, t1=end_time)
    ct = datetime.datetime.utcnow()
    start_time = ct.isoformat() + 'Z'
    end_time = (ct + datetime.timedelta(minutes=1)).isoformat() + 'Z'
    things = {"indicators": {"docs": [], "count": 0}, "sightings": {"docs": [], "count": 0}, "relationships": {"docs": [], "count": 0}}
    indicator_count = 0
    sighting_count = 0
    relationship_count = 0

    indicators = {}
    clients = {}

    for d in dev_stat:
        add_item = False
        if d["eventType"] == "IDS Alert":
            src_lst = d.get("srcIp", "").split(":")
            dst_lst = d.get("destIp", "").split(":")
            if search_type == "ip" and src_lst[0] in ob_list or dst_lst[0] in ob_list:
                add_item = True
                desc = d.get("message", "event unknown")
                short_desc = d.get("ruleId", "rule unknown")
                title = short_desc
                ob_time = d.get("ts", start_time)
                ob_src = d.get("srcIp", "").split(":")[0]
                ob_dst = d.get("destIp", "").split(":")[0]
                ob_mac = d.get("clientMac")
                if ob_mac not in clients:
                    clients[ob_mac] = meraki_config.find_meraki_client(client_mac=ob_mac)
                client_ip = clients[ob_mac]["client"]["ip"]
                client_mac = clients[ob_mac]["client"]["mac"]
                if client_ip == ob_dst:
                    rel_src = ob_src
                    rel_dst = ob_dst
                else:
                    rel_src = ob_dst
                    rel_dst = ob_src
                relation = "Received_From"
        elif d["eventType"] == "File Scanned":
            if (search_type == "ip" and d.get("clientIp") in ob_list or d.get("srcIp") in ob_list or d.get("destIp") in ob_list) or \
                (search_type == "sha256" and d.get("fileHash") in ob_list):
                add_item = True
                desc = d.get("uri", "uri unknown")
                short_desc = d.get("canonicalName", "name unknown")
                title = short_desc
                ob_time = d.get("ts", start_time)
                ob_src = d.get("srcIp")
                ob_dst = d.get("destIp")
                ob_mac = d.get("clientMac")
                if ob_mac not in clients:
                    clients[ob_mac] = meraki_config.find_meraki_client(client_mac=ob_mac)
                client_ip = clients[ob_mac]["client"]["ip"]
                client_mac = clients[ob_mac]["client"]["mac"]
                if client_ip == ob_dst:
                    rel_src = ob_src
                    rel_dst = ob_dst
                else:
                    rel_src = ob_dst
                    rel_dst = ob_src
                relation = "Downloaded_From"

        if add_item:
            sighting = Sighting(
                confidence='Unknown',
                count=1,
                internal=True,
                external_references=[
                    ExternalReference(
                        source_name="Meraki Dashboard",
                        external_id="abc123",
                        url="https://dashboard.meraki.com/abc123"
                    )
                ],
                observed_time=ObservedTime(
                    start_time=ob_time,
                ),
                observables=[
                    Observable(
                        type='ip',
                        value=ob_src,
                    ),
                    Observable(
                        type='ip',
                        value=ob_dst,
                    ),
                    Observable(
                        type='mac_address',
                        value=ob_mac,
                    ),
                ],
                targets=[
                    IdentitySpecification(
                        type='endpoint',
                        observables=[
                            Observable(
                                type='ip',
                                value=client_ip
                            ),
                            Observable(
                                type='device',
                                value=clients.get(ob_mac, {}).get("device", {}).get("serial", "N/A")
                            ),
                            Observable(
                                type='mac_address',
                                value=client_mac
                            ),
                            # Observable(
                            #     type='url',
                            #     value=clients.get(ob_mac, {}).get("device", {}).get("url", "https://dashboard.meraki.com")
                            # )
                        ],
                        observed_time=ObservedTime(
                            start_time=ob_time,
                        )
                    ),
                    # IdentitySpecification(
                    #     type='network.firewall',
                    #     observables=[
                    #         Observable(
                    #             type='mac_address',
                    #             value=clients.get(ob_mac, {}).get("device", {}).get("mac", "")
                    #         ),
                    #         Observable(
                    #             type='device',
                    #             value=clients.get(ob_mac, {}).get("device", {}).get("serial", "")
                    #         )
                    #     ],
                    #     observed_time=ObservedTime(
                    #         start_time=ob_time,
                    #     )
                    # )
                ],
                relations=[
                    ObservedRelation(
                        origin='Meraki Module',
                        relation=relation,
                        source=Observable(
                            type='ip',
                            value=rel_src
                        ),
                        related=Observable(
                            type='ip',
                            value=rel_dst
                        ),
                        origin_uri=clients.get(ob_mac, {}).get("device", {}).get("url", "https://dashboard.meraki.com")
                    )
                ],
                severity='Unknown',
                timestamp=ob_time,
                tlp='amber',
            )
            things["sightings"]["docs"].append(sighting.json)
            sighting_count += 1

            if title not in indicators:
                indicator = Indicator(
                    producer='Meraki Dashboard',
                    valid_time=ValidTime(
                        start_time=start_time,
                        end_time=end_time,
                    ),
                    description=desc,
                    short_description=short_desc,
                    title=title,
                    tlp='amber',
                )
                things["indicators"]["docs"].append(indicator.json)
                indicator_count += 1
                indicators[title] = indicator
            else:
                indicator = indicators[title]

            relationship_from_sighting_to_indicator = Relationship(
                relationship_type='sighting-of',
                source_ref=sighting,
                target_ref=indicator,
                short_description=f'{sighting} is sighting-of {indicator}',
            )
            things["relationships"]["docs"].append(relationship_from_sighting_to_indicator.json)
            relationship_count += 1

    # print(json.dumps(clients))
    things["indicators"]["count"] = indicator_count
    things["sightings"]["count"] = sighting_count
    things["relationships"]["count"] = relationship_count
    return things


@enrich_api.route('/deliberate/observables', methods=['POST'])
def deliberate_observables():
    _ = get_jwt()
    _ = get_observables()
    return jsonify_data({})


@enrich_api.route('/observe/observables', methods=['POST'])
def observe_observables():
    return jsonify_data(find_observables())


@enrich_api.route('/refer/observables', methods=['POST'])
def refer_observables():
    _ = get_jwt()
    meraki_config = meraki.MerakiConfig()
    json_refer = []

    try:
        ob = get_observables()
    except Exception:
        return jsonify_data(json_refer)

    if ob[0]["type"] == "device":
        dev_url = "https://dashboard.meraki.com"
        net_devices = meraki_config.mdashboard.organizations.getOrganizationDevices(meraki_config.org_id)
        for net_device in net_devices:
            if net_device["serial"] == ob[0]["value"]:
                dev_url = net_device["url"]
                break

        json_refer = [
            {
                "id": "meraki-dashboard-link",
                "title": "View Device in Meraki Dashboard",
                "description": "Open this device in Meraki Dashboard",
                "categories": [
                    "Meraki Dashboard",
                    "Device"
                ],
                "url": dev_url
            }
        ]

    return jsonify_data(json_refer)
