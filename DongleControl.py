#!/usr/bin/env /bin/python3
#
# DongleControl
# Script to restart a 4G dongle
#
__author__ = "GhostTalker"
__copyright__ = "Copyright 2023, The GhostTalker project"
__version__ = "0.0.2"
__status__ = "DEV"

import requests
import schedule
import time
import configparser
from toggleDataSwitch import toggle_modem

# Globale Variable
dongle_statuses = {}

def load_configuration():
    global dongle_statuses
    config = configparser.ConfigParser()
    config.read('config.ini')
    dongles = {key: config['DONGLES'][key] for key in config['DONGLES']}
    proxys = {key: config['PROXYS'][key] for key in config['PROXYS']}
    associations = {key: proxys[config['ASSOCIATIONS'][key]] for key in config['ASSOCIATIONS']}
    dongle_statuses = {dongle: {'IP': ip, 'Proxy': associations[dongle]} for dongle, ip in dongles.items()}

    for dongle_id, details in dongle_statuses.items():
        ext_ip = get_public_ip(details['Proxy'])
        details['extIP'] = ext_ip if ext_ip else "Unavailable"

def get_public_ip(proxy):
    try:
        proxies = {
            'http': f'http://{proxy}'
        }
        headers = {
            'User-Agent': 'curl/7.64.1'
        }
        response = requests.get('http://api.ipify.org', headers=headers, proxies=proxies, timeout=10)
        if response.status_code == 200:
            return response.text.strip()
        else:
            print(f"Response returned with status code: {response.status_code}, response: {response.text}")
            return "Response Error"
    except requests.RequestException as e:
        print(f"Failed to get public IP through proxy {proxy}: {e}")
        return None

def toggle_dataswitch(dongle_id):
    global dongle_statuses
    toggle_modem(dongle_statuses[dongle_id]['IP'], '0')
    time.sleep(10)
    toggle_modem(dongle_statuses[dongle_id]['IP'], '1')
    time.sleep(10)
    update_extIP(dongle_id)

def update_extIP(dongle_id):
    global dongle_statuses
    ext_ip = get_public_ip(dongle_statuses[dongle_id]['Proxy'])
    dongle_statuses[dongle_id]['extIP'] = ext_ip if ext_ip else "Unavailable"

def main():
    global dongle_statuses
    load_configuration()
    for dongle_id in dongle_statuses:
        toggle_dataswitch(dongle_id)
    print(dongle_statuses)

if __name__ == "__main__":
    main()
