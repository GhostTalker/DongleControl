#!/usr/bin/env /bin/python3
#
# DongleControl
# Script to restart a 4G dongle
#
__author__ = "GhostTalker"
__copyright__ = "Copyright 2023, The GhostTalker project"
__version__ = "0.1.0"
__status__ = "DEV"

import requests
import schedule
import time
import configparser
from datetime import datetime, timedelta
from toggleDataSwitch import toggle_modem
from rebootDongle import reboot_modem

# Globale Variable
dongle_statuses = {}

def log_with_timestamp(message):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{current_time}] {message}")

def load_configuration():
    config = configparser.ConfigParser()
    config.read('config.ini')
    dongles = {key: config['DONGLES'][key] for key in config['DONGLES']}
    proxys = {key: config['PROXYS'][key] for key in config['PROXYS']}
    associations = {key: proxys[config['ASSOCIATIONS'][key]] for key in config['ASSOCIATIONS']}
    global dongle_statuses
    dongle_statuses = {
        dongle: {
            'IP': ip,
            'Proxy': associations[dongle],
            'extIP': "Unavailable",
            'lastIPChange': None  # Initialisieren des Zeitstempels
        }
        for dongle, ip in dongles.items()
    }
    update_all_extIPs()

def update_all_extIPs():
    for dongle_id in dongle_statuses:
        update_extIP(dongle_id)

def get_public_ip(proxy):
    try:
        proxies = {
            'http': f'http://{proxy}'
        }
        headers = {
            'User-Agent': 'curl/7.64.1'
        }
        response = requests.get('http://api.ipify.org', headers=headers, proxies=proxies, timeout=10)
        #log_with_timestamp(response)
        if response.status_code == 200:
            return response.text.strip()
        else:
            log_with_timestamp(f"Response returned with status code: {response.status_code}, response: {response.text}")
            return "Response Error"
    except requests.RequestException as e:
        log_with_timestamp(f"Failed to get public IP through proxy {proxy}: {e}")
        return None

def toggle_dataswitch(dongle_id):
    global dongle_statuses
    toggle_modem(dongle_statuses[dongle_id]['IP'], '0')
    time.sleep(10)
    toggle_modem(dongle_statuses[dongle_id]['IP'], '1')
    time.sleep(10)
    update_extIP(dongle_id)

def update_extIP(dongle_id):
    old_ip = dongle_statuses[dongle_id]['extIP']
    new_ip = get_public_ip(dongle_statuses[dongle_id]['Proxy'])
    dongle_statuses[dongle_id]['extIP'] = new_ip if new_ip else "Unavailable"
    if old_ip != new_ip and new_ip != "Unavailable":
        dongle_statuses[dongle_id]['lastIPChange'] = datetime.now().isoformat()

def check_ip_change_interval(dongle_id):
    global dongle_statuses
    if 'lastIPChange' in dongle_statuses[dongle_id] and dongle_statuses[dongle_id]['lastIPChange']:
        last_change_time = datetime.fromisoformat(dongle_statuses[dongle_id]['lastIPChange'])
        current_time = datetime.now()
        time_difference = current_time - last_change_time
        if time_difference > timedelta(minutes=5):
            return True  # Länger als 5 Minuten her
        else:
            return False  # Weniger als 5 Minuten her
    else:
        log_with_timestamp(f"Kein gültiger Zeitstempel für IP-Änderung gefunden für {dongle_id}")
        return None  # Kein Zeitstempel vorhanden

def check_ip_change(dongle_id):
    # Überprüfung, ob der letzte IP-Wechsel länger als 5 Minuten zurückliegt
    if check_ip_change_interval(dongle_id) is True:
        return True
    elif check_ip_change_interval(dongle_id) is False:
        return False
    else:
        return None

def init_reboot_modem(dongle_id):
    log_with_timestamp(f"Reboot von {dongle_ip}")
    reboot_modem(dongle_statuses[dongle_id]['IP'])
    update_extIP(dongle_id)
    log_with_timestamp(f"Reboot von {dongle_id} durchgeführt. Neue IP ist: {dongle_statuses[dongle_id]['extIP']}")

def change_ip_adress_of_dongles():
    global dongle_statuses
    for dongle_id in dongle_statuses:
        toggle_dataswitch(dongle_id)
        if check_ip_change(dongle_id) is True:
            log_with_timestamp(f"Neustart von {dongle_id} brachte keine neue IP. Powercyle USB....")
            init_reboot_modem(dongle_statuses[dongle_id])
        elif check_ip_change(dongle_id) is False:
            log_with_timestamp(f"Neustart von {dongle_id} hat geklappt. Neue IP ist: {dongle_statuses[dongle_id]['extIP']}")
        else:
            log_with_timestamp(f"Kein IP-Wechselzeitstempel verfügbar für {dongle_id}.")

def main():
    global dongle_statuses
    load_configuration()
    schedule.every(5).minutes.do(change_ip_adress_of_dongles)
    log_with_timestamp(f"Starte Scheduler for Dongle Restart.")
    change_ip_adress_of_dongles

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)

    except KeyboardInterrupt:
        log_with_timestamp("DongleControl will be stopped")
        exit(0)

if __name__ == "__main__":
    main()
