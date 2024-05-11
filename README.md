# DongleControl

## Overview

DongleControl is a Python script for managing and monitoring 4G dongles. It allows for the automatic restarting of dongles and monitoring of their public IP addresses. Additionally, the script tracks the time of the last IP change to ensure that the dongles always have a current and functioning connection.

## Main Features

- **Automatic Restarting**: Automated powering on and off of the 4G dongles.
- **IP Monitoring**: Checking and updating the public IP addresses of the dongles.
- **Timestamp Tracking**: Logging the time of the last successful IP change.
- **Regular Checks**: Automated checks to determine if the last IP change occurred more than 5 minutes ago, ensuring that the dongles remain active and connected.

## System Requirements

- Python 3.6 or higher
- Additional Python packages: `requests`, `xmltodict`, `schedule`, `configparser`
  - These can be installed via `pip install -r requirements.txt`, where `requirements.txt` contains the required packages.

## Setup Instructions

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/yourusername/DongleControl.git
    cd DongleControl
    ```

2. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Create Configuration File**:
    - Create a `config.ini` file in the main directory with the following content:
      ```ini
      [DONGLES]
      dongle_01=192.168.1.100
      dongle_02=192.168.1.101

      [PROXYS]
      proxy_01=192.168.2.100:8081
      proxy_02=192.168.2.101:8082

      [ASSOCIATIONS]
      dongle_01=proxy_01
      dongle_02=proxy_02
      ```
    - Adjust the IP addresses and proxy settings according to your network configuration.

4. **Run the Script**:
    ```bash
    python3 DongleControl.py
    ```

## Usage

After starting the script, it will automatically check every 5 minutes to see if an IP change is necessary. Each change will be logged in the terminal, and the script will attempt to automatically resolve issues by restarting the dongles if necessary.

## Troubleshooting

- Check the proxy settings if IP addresses are not being retrieved correctly.
- Ensure that your network allows external connections to `api.ipify.org`.
- Consult the script's log outputs for information on actions performed and possible errors.

## License

This project is licensed under the MIT License. Details can be found in the `LICENSE` file.
