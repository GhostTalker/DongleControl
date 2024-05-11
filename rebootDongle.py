import requests
import xmltodict

def reboot_modem(host):
    BASE_URL = f'http://{host}'
    TOKEN_URL = '/api/webserver/SesTokInfo'
    SWITCH_URL = '/api/device/control'

    session = requests.Session()
    try:
        response = session.get(BASE_URL + TOKEN_URL, timeout=3)
        response_dict = xmltodict.parse(response.text).get('response', None)
        headers = {
            'Cookie': response_dict['SesInfo'],
            '__RequestVerificationToken': response_dict['TokInfo']
        }
        data = f'<?xml version="1.0" encoding="UTF-8"?><request><Control>1</Control></request>'
        response = session.post(BASE_URL + SWITCH_URL, data=data, headers=headers, timeout=3)
        if response.status_code == 200:
            print(f"Modem at {host} successfully rebooted.")
            return True
        else:
            print(f"Failed to reboot modem at {host}. Status Code: {response.status_code}")
            return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
