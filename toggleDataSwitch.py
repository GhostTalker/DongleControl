# toggleDataSwitch.py
import requests
import xmltodict
import sys
import argparse


def toggle_modem(host, state):
    BASE_URL = f'http://{host}'
    TOKEN_URL = '/api/webserver/SesTokInfo'
    SWITCH_URL = '/api/dialup/mobile-dataswitch'

    session = requests.Session()
    try:
        # Get session and verification tokens from the modem
        response = session.get(BASE_URL + TOKEN_URL, timeout=3)
        response_dict = xmltodict.parse(response.text).get('response', None)

        headers = {
            'Cookie': response_dict['SesInfo'],
            '__RequestVerificationToken': response_dict['TokInfo']
        }
        data = f'<?xml version="1.0" encoding="UTF-8"?><request><dataswitch>{state}</dataswitch></request>'

        # Send the toggle request
        response = session.post(BASE_URL + SWITCH_URL, data=data, headers=headers, timeout=3)
        if response.status_code == 200:
            print(f"Modem at {host} successfully toggled to state {state}.")
            return True
        else:
            print(f"Failed to toggle modem at {host}. Status Code: {response.status_code}")
            return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Toggle a modem's data switch.")
    parser.add_argument("host", help="The IP address of the modem")
    parser.add_argument("state", choices=['0', '1'], help="The state to toggle the modem to: '0' for off, '1' for on")
    args = parser.parse_args()

    toggle_modem(args.host, args.state)
