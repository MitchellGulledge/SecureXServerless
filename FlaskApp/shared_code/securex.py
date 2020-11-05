import requests
import os
from bundlebuilder.session import Session


class SecureXConfig:
    def __init__(self):
        self.securex_client_id = os.environ.get('securex_client_id')
        self.securex_client_password = os.environ.get('securex_client_password')
        if not self.securex_client_id or not self.securex_client_password:
            logging.error("Error: you must include the SecureX Token ID and SecureX Token Secret in order to continue")
            exit(1)
        # Get SecureX Token
        bearer_payload = self.get_access_token()
        self.token = bearer_payload["access_token"]
        self.headers = {'Content-Type': 'application/json',
                   'Accept': 'application/json',
                   'Authorization': 'Bearer ' + self.token}
        self.session = Session(
            external_id_prefix='meraki-tr-module',
            source='Meraki Threat Response Module',
            source_uri=(
                'https://github.com/MitchellGulledge/SecureXServerless/'
            ),
        )

    def get_access_token(self):
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Accept': 'application/json'}
        data = {'grant_type': 'client_credentials'}
        url = 'https://visibility.amp.cisco.com/iroh/oauth2/token'
        response = requests.post(url, data=data, headers=headers, auth=(self.securex_client_id, self.securex_client_password))

        if response.ok:
            return response.json()
        else:
            return None

    def ctr_indicator(self, content):
        url = 'https://intel.amp.cisco.com/ctia/indicator/search?query=' + content
        response = requests.get(url, headers=self.headers)

        if response.ok:
            indicators = response.json()
            for i in indicators:
                if i["source"] == "TALOS":
                    return i
            if len(indicators) > 0:
                return indicators[0]
            else:
                return {}
        else:
            return None

    def ctr_malware(self, content):
        url = 'https://intel.amp.cisco.com/ctia/malware/search?query=' + content
        response = requests.get(url, headers=self.headers)
        print(response.content.decode("utf-8"))

        if response.ok:
            indicators = response.json()
            for i in indicators:
                if i["source"] == "TALOS":
                    return i
            if len(indicators) > 0:
                return indicators[0]
            else:
                return {}
        else:
            return None

