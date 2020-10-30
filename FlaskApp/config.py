import os


meraki_base_url = "https://api.meraki.com/api/v1"
meraki_user_agent = "threat-response-module"


class Config:
    VERSION = '0.1'
    SECRET_KEY = os.environ.get('SECRET_KEY', '')
