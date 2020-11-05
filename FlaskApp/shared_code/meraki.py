import meraki
from meraki.exceptions import APIError
import os
from .. import config
import logging


class MerakiConfig:
    def __init__(self):
        self.api_key = os.environ.get('meraki_api_key', '').lower()
        self.org_name = os.environ.get('meraki_org_name')
        self.org_id = None
        if not self.api_key or not self.org_name:
            logging.error("Error: you must include the Meraki API Key and Organization Name in order to continue")
            exit(1)
        self.mdashboard = meraki.DashboardAPI(self.api_key, print_console=False, suppress_logging=True, output_log=False,
                                              caller=config.meraki_user_agent)
        result_org_id = self.mdashboard.organizations.getOrganizations()
        for x in result_org_id:
            if x['name'] == self.org_name:
                self.org_id = x['id']

    def find_meraki_client(self, client_mac=None, client_ip=None):
        net_client = None

        org_nets = self.mdashboard.organizations.getOrganizationNetworks(self.org_id)

        for net in org_nets:
            # if searching by MAC, we can run the networkclient with that as an arg
            if client_mac:
                try:
                    net_client = self.mdashboard.networks.getNetworkClient(net["id"], client_mac)
                except APIError as e:
                    continue
            # if searching by IP, we can't assume that track-by-ip is enabled, so let's get all clients and iterate
            elif client_ip:
                try:
                    net_clients = self.mdashboard.networks.getNetworkClients(net["id"])
                except APIError as e:
                    continue

                for net_client_item in net_clients:
                    # if the client's ip matches the ip being searched for, exit the loop
                    if net_client_item["ip"] == client_ip:
                        net_client = net_client_item
                        break

            if isinstance(net_client, dict):
                # net_device = self.mdashboard.organizations.getOrganizationInventoryDevices(self.org_id, search=net_client["recentDeviceMac"])
                # if isinstance(net_device, list) and len(net_client) > 0:
                net_devices = self.mdashboard.organizations.getOrganizationDevices(self.org_id)
                for net_device in net_devices:
                    if net_device.get("mac") == net_client["recentDeviceMac"]:
                        dev_mod = net_device.get("model", "")
                        if dev_mod[:2] == "MX" or dev_mod[:3] == "vMX" or dev_mod[:1] == "Z":
                            return {"client": net_client, "device": net_device, "network": net}

        return None
