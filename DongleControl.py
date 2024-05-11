#!/usr/bin/env /bin/python3
#
# DongleControl
# Script to restart a 4g dongle
#
__author__ = "GhostTalker"
__copyright__ = "Copyright 2023, The GhostTalker project"
__version__ = "0.0.1"
__status__ = "DEV"

import requests
import schedule
import time
import configparser
import subprocess


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

def call_toggle_script(host, state):
    # Pfad zur Python-Executable und Skript angeben
    result = subprocess.run(['python3', 'toggleDataSwitch.py', host, state], capture_output=True, text=True)
    if result.returncode == 0:
      print("Toggle script executed successfully.")
      print(result.stdout)
    else:
      print("Toggle script failed.")
      print(result.stderr)

def main():
    dongle_statuses = load_configuration()
    print(dongle_statuses)
    for dongle in dongle_statuses:
        call_toggle_script(dongle_statuses[dongle]['IP'], '0')

    time.sleep(10)
    for dongle in dongle_statuses:
        call_toggle_script(dongle_statuses[dongle]['IP'], '1')


if __name__ == "__main__":
  main()
