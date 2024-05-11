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
        # Setzen des Proxy
        proxies = {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }
        # Anfragen an die API ipify.org senden
        response = requests.get('https://api.ipify.org', proxies=proxies, timeout=5)
        if response.status_code == 200:
            return response.text.strip()  # Gibt die reine IP-Adresse zurück
        else:
            print(f"Response returned with status code: {response.status_code}")
            return "Response Error"
    except requests.RequestException as e:
        print(f"Failed to get public IP through proxy {proxy}: {e}")
        return None

def update_public_ip(dongle_statuses, dongle_id):
    if dongle_id in dongle_statuses:
        proxy_details = dongle_statuses[dongle_id]['Proxy']
        new_ext_ip = get_public_ip(proxy_details)
        dongle_statuses[dongle_id]['extIP'] = new_ext_ip if new_ext_ip else "Unavailable"
        return True
    return False

def main():
    dongle_statuses = load_configuration()
    print("Vor der Aktualisierung:", dongle_statuses)
    # Auswählen des spezifischen Dongles, den wir neu starten möchten
    dongle_id = 'dongle_01'
    print("extIP vor der Aktualisierung:", dongle_statuses[dongle_id]['extIP'])
    if dongle_id in dongle_statuses:
        dongle_details = dongle_statuses[dongle_id]
        # Erstellen einer Instanz des HuaweiE3372 Modems mit der IP-Adresse des Dongles
        modem = HuaweiE3372(dongle_details['IP'])

        # Versuchen, den Dongle neu zu starten
        if modem.switch_modem():  # Kein Parameter erforderlich, die Methode handhabt jetzt den Neustart komplett

            print("extIP von {dongle_id} nach der Aktualisierung:", dongle_statuses[dongle_id]['extIP'])
            print(f"Der Dongle {dongle_id} wurde erfolgreich neu gestartet.")
        else:
            print(f"Fehler beim Neustart des Dongles {dongle_id}.")
    else:
        print(f"Dongle {dongle_id} wurde nicht in der Konfiguration gefunden.")

if __name__ == "__main__":
    main()
