import time
import board
import busio
from digitalio import DigitalInOut, Direction
import adafruit_espatcontrol


# Get wifi details and more from a settings.py file
try:
    from settings import settings
except ImportError:
    print("WiFi settings are kept in settings.py, please add them there!")
    raise



URL = "https://io.adafruit.com/api/v2/webhooks/feed/"+settings['aio_feed_webhook']+"?value="

# for Particle Argon
RX = board.ESP_TX
TX = board.ESP_RX
uart = busio.UART(TX, RX, timeout=0.1)

esp_boot = DigitalInOut(board.ESP_BOOT_MODE)
esp_boot.direction = Direction.OUTPUT
esp_boot.value = True
rtspin = DigitalInOut(board.ESP_CTS)
resetpin = DigitalInOut(board.ESP_WIFI_EN)

print("Post to a URL", URL)

esp = adafruit_espatcontrol.ESP_ATcontrol(uart, 115200, reset_pin=resetpin,
                                          run_baudrate = 115200, rts_pin=rtspin, debug=True)
print("Resetting ESP module")
esp.hard_reset()
print("Connected to AT software version", esp.get_version())

counter = 0
while True:
    try:
        # Connect to WiFi if not already
        while not esp.is_connected:
            print("Connecting...")
            esp.connect(settings)
        print("Connected to", esp.remote_AP)
        # great, lets get the data
        print("Posting request URL...", end='')
        header, body = esp.request_url(URL+str(counter), request_type = "POST")
        counter = counter + 1
        print("OK")
    except (RuntimeError, adafruit_espatcontrol.OKError) as e:
        print("Failed to get data, retrying\n", e)
        continue
    header = body = None
    time.sleep(15)
