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
    
print("test")
