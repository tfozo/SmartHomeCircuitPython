"""
Telegram Bot using CircuitPython on Raspberry Pi Pico W
  - Tested with CircuitPython 8.0.0-beta.6

Additional libraries
  https://circuitpython.org/libraries
  - adafruit_requests.mpy
  - simpleio.mpy
"""

import os
import ipaddress
import wifi
import socketpool
import time
import microcontroller
import board
import digitalio
import simpleio
import adafruit_requests
import ssl
import json
from display import marquee, quicktext
#from joke import get_dad_joke

# Get wifi details from a settings.toml file
print(os.getenv("test_env_file"))
ssid = os.getenv("WIFI_SSID")
password = os.getenv("WIFI_PASSWORD")
telegrambot = os.getenv("botToken")

# Telegram API url.
API_URL = "https://api.telegram.org/bot" + telegrambot

# Buzzer

buzzer = board.GP18

#buzzer = digitalio.DigitalInOut(board.GP18)
#buzzer.direction = digitalio.Direction.OUTPUT

# Input-Output Initialization
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

#led0 = digitalio.DigitalInOut(board.GP0)
#led0.direction = digitalio.Direction.OUTPUT


update_id = 0  # Initialize update_id

def fetch_latest_update_id():
    global update_id
    get_url = API_URL + "/getUpdates?limit=1&offset=-1"  # Request the latest update
    r = requests.get(get_url)
    try:
        if r.json()['result']:
            update_id = r.json()['result'][0]['update_id']
    except (IndexError, KeyError):
        print("No new updates or error fetching the latest update_id")


def init_bot():
    get_url = API_URL
    get_url += "/getMe"
    r = requests.get(get_url)
    return r.json()['ok'] #returns bool value

def read_message():
    global update_id
    get_url = API_URL + "/getUpdates?limit=1&allowed_updates=[\"message\",\"callback_query\"]"
    get_url += "&offset={}".format(update_id + 1)

    r = requests.get(get_url)
    try:
        if r.json()['result']:
            update = r.json()['result'][0]
            update_id = update['update_id'] 
            message = update['message']['text']
            chat_id = update['message']['chat']['id']
            first_name = update['message']['from'].get('first_name', '')

            print(f"Chat ID: {chat_id} Update_id: {update_id} Message: {message}")
            
            return chat_id, message, first_name  # Return chat ID and message
    except (IndexError, KeyError):
        print("No new messages or error parsing response")
    return False, False, ''

NOTE_G4 = 392
NOTE_C5 = 523

def send_message(chat_id, message, reply_markup=None): #sends message via chatid based on the message request
    get_url = API_URL
    get_url += "/sendMessage?chat_id={}&text={}".format(chat_id, message)
    if reply_markup is not None:
        get_url += "&reply_markup=" + reply_markup
    r = requests.get(get_url)
    #print(r.json())
def readIntTemp():
    data = microcontroller.cpu.temperature
    data = "Temperature: {:.2f} °C".format(data)
    return data

#  Connect to Wi-Fi AP
print(f"Initializing...")
wifi.radio.connect(ssid, password)
print("connected!\n")
pool = socketpool.SocketPool(wifi.radio)
print("IP Address: {}".format(wifi.radio.ipv4_address))
print("Connecting to WiFi '{}' ... ".format(ssid), end="")
requests = adafruit_requests.Session(pool, ssl.create_default_context())

if init_bot() == False: #if bot initialization fails
    print("\nTelegram bot initialization failed.")
else:
    print("\nTelegram bot ready!\n")
    simpleio.tone(board.GP18, NOTE_G4, duration=0.1)
    simpleio.tone(buzzer, NOTE_C5, duration=0.1)
    fetch_latest_update_id()

while True:
    try: #if wifi connection fails, keeps on trying to reconnect
        while not wifi.radio.ipv4_address or "0.0.0.0" in repr(wifi.radio.ipv4_address):
            print(f"Reconnecting to WiFi...")
            wifi.radio.connect(ssid, password)
            
        chat_id, message_in, user_name = read_message()
        if chat_id and message_in:
            if message_in == "/start":
                greet_msg = f"Welcome Home {user_name}! Choose an option:" #TODO: greet by name
                
                keyboard = {
                    "keyboard": [[{"text": "LED ON"}, {"text": "LED OFF"}], [{"text": "Local TEMP"},{"text": "City TEMP"},{"text": "CPU TEMP"}],[{"text": "Dad Jokes"}]],
                    "resize_keyboard": True,
                    "is_persistent":True,
                }
                send_message(chat_id, greet_msg, reply_markup=json.dumps(keyboard))
                simpleio.tone(board.GP18, NOTE_G4, duration=0.1)
                simpleio.tone(board.GP18, NOTE_C5, duration=0.1)
            elif message_in == "LED ON":
                led.value = True
                send_message(chat_id, "LED turned on.")
                quicktext('Light On')
            elif message_in == "LED OFF":
                led.value = False
                send_message(chat_id, "LED turned off.")
                quicktext('Light Off')
            elif message_in == "CPU TEMP":
                temp = readIntTemp()
                send_message(chat_id, temp)
                quicktext(f'CPU: {temp[13:18]} *C') #default deg(symbol) becomes '-' thus I had to interfere
                #marquee("LED is on my boy!", 0, 16, 0.3)
            elif message_in == "Dad Jokes":
                #joke = get_dad_joke()
                send_message(chat_id, "JOKE")
                #marquee("LED is on my boy!", 0, 16, 0.3)
            else:
                send_message(chat_id, "Command is not available.")
        else:
            time.sleep(1)
        
    except OSError as e:
        print("Failed!\n", e)
        microcontroller.reset()