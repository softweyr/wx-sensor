import machine
import network
import ujson
import utime
import urequests
import binascii

# Import the BME680 driver you uploaded
try:
    import bme680
except ImportError:
    print("Error: bme680.py driver not found.")
    print("Please upload the MicroPython BME680 library to your Pico W.")
    machine.reset()

# --- Configuration and Initialization ---

# I2C setup (adjust pins if needed, default for Pico/Pico W is GP4/GP5 for I2C0)
# SDA=GP4, SCL=GP5
i2c = machine.I2C(0, sda=machine.Pin(4), scl=machine.Pin(5))

# Initialize BME680 sensor
try:
    sensor = bme680.BME680_I2C(i2c)
    print("BME680 sensor initialized.")
except ValueError:
    print("Error: BME680 not found on I2C bus at address 0x77 or 0x76.")
    print("Check wiring (SDA=GP4, SCL=GP5) and sensor address.")
    machine.reset()

# Load configuration from config.json
def load_config():
    try:
        with open("config.json", "r") as f:
            config = ujson.load(f)
        print("Configuration loaded successfully.")
        return config
    except OSError:
        print("Error: config.json not found.")
        print("Please create config.json with Wi-Fi and API details.")
        return None
    except ValueError:
        print("Error: config.json is not valid JSON.")
        return None

config = load_config()
if config is None:
    machine.reset()

# --- Wi-Fi Connection ---

def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # Get the MAC address
    mac_bytes = wlan.config('mac')
    mac_str = binascii.hexlify(mac_bytes, ':').decode().upper()
    print(f"Pico W MAC Address: {mac_str}")

    if not wlan.isconnected():
        print(f"Connecting to Wi-Fi network: {ssid}...")
        wlan.connect(ssid, password)
        # Wait up to 10 seconds for connection
        max_wait = 20
        while max_wait > 0:
            if wlan.status() < 0 or wlan.status() >= 3:
                break
            max_wait -= 1
            print('.', end='')
            utime.sleep(0.5)

    if wlan.isconnected():
        status = wlan.ifconfig()
        print(f"\nConnected! IP: {status[0]}")
        return wlan, mac_str
    else:
        print(f"\nWi-Fi connection failed. Status: {wlan.status()}")
        return None, mac_str

wlan, mac_address = connect_wifi(config['wifi_ssid'], config['wifi_password'])
if wlan is None:
    print("Cannot proceed without a network connection.")
    # Blink an error code on the LED if possible, or just wait/reset
    utime.sleep(5)
    # machine.reset() # uncomment to keep retrying

# --- Sensor Sampling and POST Function ---

def sample_and_post(mac_id, api_url):
    # Read raw sensor data
    temperature = sensor.temperature
    pressure = sensor.pressure
    humidity = sensor.humidity
    gas_resistance = sensor.gas

    # Create the payload (JSON body for the POST request)
    payload = {
        "device_id": mac_id,
        "timestamp": utime.time(), # Unix epoch time
        "temperature_c": round(temperature, 2),
        "pressure_hpa": round(pressure / 100, 2), # Convert Pa to hPa
        "humidity_percent": round(humidity, 2),
        "gas_ohms": round(gas_resistance, 2)
    }

    print("\n--- New Sample ---")
    print(f"Temp: {temperature:.2f} °C, Pres: {pressure/100:.2f} hPa, Hum: {humidity:.2f} %")
    print(f"Gas: {gas_resistance:.2f} Ohms")

    # Perform the REST POST call
    try:
        headers = {'Content-Type': 'application/json'}
        response = urequests.post(api_url, json=payload, headers=headers)
        
        print(f"POST request sent to {api_url}")
        print(f"Server Response Status: {response.status_code}")
        
        # Check for success status codes (e.g., 200, 201, 202, 204)
        if 200 <= response.status_code < 300:
            print("Data posted successfully!")
        else:
            print(f"Error posting data. Server replied: {response.text}")
            
        response.close() # Always close the response object

    except Exception as e:
        print(f"An error occurred during POST request: {e}")
        
    print("------------------")


# --- Main Loop ---

# Set sampling interval to 60 seconds (one minute)
SAMPLE_INTERVAL_SECONDS = 60

print(f"\nStarting main loop. Sampling every {SAMPLE_INTERVAL_SECONDS} seconds...")

while True:
    if wlan and wlan.isconnected():
        sample_and_post(mac_address, config['api_base_url'])
    else:
        print("Wi-Fi is disconnected. Reconnecting...")
        wlan, mac_address = connect_wifi(config['wifi_ssid'], config['wifi_password'])
        
    # Wait for the next sampling interval
    utime.sleep(SAMPLE_INTERVAL_SECONDS)
