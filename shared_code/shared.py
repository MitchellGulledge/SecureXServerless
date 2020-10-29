import requests


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


def create_integration_module(token):
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

    ret = requests.post(url, headers=headers, json=payload)
    return ret.json()


def create_integration_module_instance(token, type_id, appurl, orgid, apikey):
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
    ret = requests.post(url, headers=headers, json=payload)
    return ret.json()
