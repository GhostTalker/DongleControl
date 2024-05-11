#!/usr/bin/env /bin/python3
#
# RebootMadDevices
# Script to restart ATV devices which are not responsible
#
__author__ = "GhostTalker"
__copyright__ = "Copyright 2023, The GhostTalker project"
__version__ = "0.0.1"
__status__ = "DEV"

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
            r = self.session.get(self.base_url + self.TOKEN_URL, timeout=3)
            _dict = xmltodict.parse(r.text).get('response', None)
            headers = {
                'Cookie': _dict['SesInfo'],
                '__RequestVerificationToken': _dict['TokInfo']
            }
            data = '<?xml version="1.0" encoding="UTF-8"?><request><dataswitch>' + state + '</dataswitch></request>'
            r = self.session.post(self.base_url + self.SWITCH_URL, data=data, headers=headers, timeout=3)
            return r.status_code == 200
        except Exception as ex:
            print(f"Failed to switch modem at {self.host}: {ex}")
            return False


def load_configuration():
    config = configparser.ConfigParser()
    config.read('config.ini')
    dongles = {key: config['DONGLES'][key] for key in config['DONGLES']}
    proxys = {key: config['PROXYS'][key] for key in config['PROXYS']}
    associations = {key: proxys[config['ASSOCIATIONS'][key]] for key in config['ASSOCIATIONS']}
    dongle_statuses = {dongle: {'IP': ip, 'Proxy': associations[dongle]} for dongle, ip in dongles.items()}

    for dongle_id, details in dongle_statuses.items():
        ext_ip = get_public_ip(details['Proxy'])
        details['extIP'] = ext_ip if ext_ip else "Unavailable"

    return dongle_statuses


def get_public_ip(proxy):
    try:
        proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
        response = requests.get('https://wtfismyip.com/text', proxies=proxies, timeout=5)
        return response.text.strip()
    except requests.RequestException as e:
        print(f"Failed to get public IP through proxy {proxy}: {e}")
        return None


def main():
    dongle_statuses = load_configuration()
    print(dongle_statuses)


if __name__ == "__main__":
    main()
