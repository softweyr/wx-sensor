# Raspberry Pi Pico W weather sensor

That's a great project! This requires three main files:

1. `main.py`: The main application logic for sampling the sensor and posting the data.

2. `config.json`: The configuration file for Wi-Fi credentials and the API endpoint.

3. `bme680.py`: The library to communicate with the BME680 sensor (you'll need to download a MicroPython driver).

# Source Files

1. `config.json`

Replace the placeholder values with your actual network name, password, and the URL where you want to POST the data.

2. MicroPython BME680 Driver `bme680.py`

You will need a MicroPython library for the BME680 sensor. The official Adafruit MicroPython BME680 library is commonly used.

Download the driver file (usually named `bme680.py` or similar) from a reliable source like the Adafruit MicroPython bundle or GitHub.

Upload this `bme680.py` file to the root of your Pico W's filesystem alongside `main.py` and `config.json`.

3. Main Application Logic `main.py`

This file handles the configuration loading, Wi-Fi connection, sensor initialization, data sampling, and the REST POST request.

# Setup Instructions

Dependencies: Before running, you must install the urequests library for MicroPython, which is not built-in.

In Thonny (Recommended IDE for Pico W): Go to Tools -> Manage packages... and search for micropython-urequests and install it.

Files: Ensure all three files (main.py, config.json, and the BME680 driver bme680.py) are uploaded to the root directory of your Raspberry Pi Pico W.

Wiring: Connect your BME680 sensor to the Pico W (assuming I2C):

VCC → 3V3 (Pin 36)

GND → GND (Pin 38)

SDA → GP4 (Pin 6)

SCL → GP5 (Pin 7)

Run: Save and run main.py. It will connect to Wi-Fi, start sampling, and attempt to post data every 60 seconds.
