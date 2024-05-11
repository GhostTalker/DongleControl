#!/usr/bin/env /bin/python3
#
# RebootMadDevices
# Script to restart ATV devices which are not responsable
#
__author__ = "GhostTalker"
__copyright__ = "Copyright 2023, The GhostTalker project"
__version__ = "0.0.1"
__status__ = "DEV"

# generic/built-in and other libs
import sys
import requests
import xmltodict
import schedule
import time
import configparser

import sys
import requests
import xmltodict
import schedule
import time
import configparser

class HuaweiE3372(object):
    BASE_URL = 'http://{host}'
    TOKEN_URL = '/api/webserver/SesTokInfo'
    SWITCH_URL = '/api/dialup/mobile-dataswitch'
    session = None

    def __init__(self, host):
        self.host = host
        self.base_url = self.BASE_URL.format(host=host)
        self.session = requests.Session()

    def switch_modem(self, state='1'):
        try:
            # Get session and verification tokens from the modem
            r = self.session.get(self.base_url + self.TOKEN_URL, timeout=3)
            _dict = xmltodict.parse(r.text).get('response', None)

            # Build the switch request
            headers = {
                'Cookie': _dict['SesInfo'],
                '__RequestVerificationToken': _dict['TokInfo']
            }

            data = '<?xml version="1.0" encoding="UTF-8"?><request><dataswitch>' + state + '</dataswitch></request>'

            r = self.session.post(self.base_url + self.SWITCH_URL, data=data, headers=headers, timeout=3)
            if r.status_code == 200:
                return True
            else:
                return False

        except Exception as ex:
            print("Failed to switch modem..")
            print(ex)
            return False

def load_configuration():
    config = configparser.ConfigParser()
    config.read('modems.ini')
    dongles = {key: config['DONGLES'][key] for key in config['DONGLES']}
    proxys = {key: config['PROXYS'][key] for key in config['PROXYS']}
    associations = {key: proxys[config['ASSOCIATIONS'][key]] for key in config['ASSOCIATIONS']}
    return {dongle: {'IP': ip, 'Proxy': associations[dongle]} for dongle, ip in dongles.items()}

def get_public_ip(proxy):
    try:
        proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
        response = requests.get('https://wtfismyip.com/text', proxies=proxies, timeout=5)
        return response.text.strip()
    except requests.RequestException as e:
        print(f"Failed to get public IP through proxy {proxy}.")
        print(e)
        return None

def load_modem_ips():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return [ip for key, ip in config['DONGLES'].items()]

def switch_all_modems():
    modem_ips = load_modem_ips()
    for ip in modem_ips:
        modem = HuaweiE3372(ip)
        modem.switch_modem('1')  # Restarting the modem
        print(f"Modem at {ip} has been switched.")

def switch_and_check_ips(dongle_statuses):
    for dongle_id, details in dongle_statuses.items():
        modem = HuaweiE3372(details['IP'])
        if modem.switch_modem('1'):  # Restarting the modem
            print(f"Modem at {details['IP']} has been switched. Checking IP...")
            old_ip = get_public_ip(details['Proxy'])
            new_ip = get_public_ip(details['Proxy'])
            if old_ip and new_ip and old_ip != new_ip:
                print(f"IP change verified for {dongle_id}: {old_ip} -> {new_ip}")
            else:
                print(f"No IP change for {dongle_id}. Old: {old_ip}, New: {new_ip}")
        else:
            print(f"Failed to switch {dongle_id} at IP {details['IP']}.")


def main():
    dongle_statuses = load_configuration()
    print(dongle_statuses)
    #schedule.every(10).minutes.do(switch_all_modems)  # Scheduling the task for every 10 minutes

    #while True:
    #    schedule.run_pending()
    #    time.sleep(1)

if __name__ == "__main__":
    main()