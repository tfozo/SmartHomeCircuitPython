"""
SmartHomeSystem with Telegram Bot and using CircuitPython on Raspberry Pi Pico W, and DadJokes API as well as OpenWeatherMap
  - CircuitPython version 8.0.0

In this page we used 
  https://circuitpython.org/libraries
  - adafruit_requests.mpy - for http request of our API's
  - simpleio.mpy - for default settings


--The A5 team--
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



# Get wifi details from a settings.toml file
# we developed a good habit of hiding sensitive information from the code and keep it in secured env.
print(os.getenv("test_env_file"))
ssid = os.getenv("WIFI_SSID")
password = os.getenv("WIFI_PASSWORD")
telegrambot = os.getenv("botToken")
weatherAPI = os.getenv("weatherAPI")

# Telegram API url.
API_URL = "https://api.telegram.org/bot" + telegrambot


buzzer = board.GP19


update_id = 0  # Initialize update_id for telegram
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

def read_message(): #we heavily relied on the Telegram Bot API documentation for this part, it is a well written documentation
    global update_id
    get_url = API_URL + "/getUpdates?limit=1&allowed_updates=[\"message\",\"callback_query\"]"
    get_url += "&offset={}".format(update_id + 1)

    r = requests.get(get_url)
    try:
        if r.json()['result']:
            update = r.json()['result'][0]
            update_id = update['update_id'] 
            if 'message' in update:
                message = update['message']['text']
                chat_id = update['message']['chat']['id']
                first_name = update['message']['from'].get('first_name', '')
                print(f"Message - Chat ID: {chat_id} Update_id: {update_id} Message: {message}")
                return chat_id, message, first_name, None  # Added a None here for consistency
            elif 'callback_query' in update:
                message = update['callback_query']['data']  # This is the data from the button.
                chat_id = update['callback_query']['message']['chat']['id']
                message_id = update['callback_query']['message']['message_id']
                print(f"Callback Query - Chat ID: {chat_id} Update_id: {update_id} Message: {message}")
                return chat_id, message, None, message_id  # message_id is needed for editing messages
    except (IndexError, KeyError):
        print("No new messages or error parsing response")
    return False, False, '', None

#This is circuit python documentation, we don't really fully understand what it is for
#BUT if it works don't touch it! lol :)
NOTE_G4 = 392
NOTE_C5 = 523

#sending message from telegram bot to the raspberry pi pico again Telegram Bot API
def send_message(chat_id, message, reply_markup=None): #sends message via chatid based on the message request
    get_url = API_URL
    get_url += "/sendMessage?chat_id={}&text={}".format(chat_id, message)
    if reply_markup is not None:
        get_url += "&reply_markup=" + reply_markup
    r = requests.get(get_url)
    


#Connect to Wi-Fi info log
#This is our commitment to make sure that our SmartHome is connected fully to the internet
# with a home wife as we are trying to demonstrate the IOT principle here.
print(f"Initializing...")
wifi.radio.connect(ssid, password)
print("connected!\n") #checked
pool = socketpool.SocketPool(wifi.radio)
print("IP Address: {}".format(wifi.radio.ipv4_address))
print("Connecting to WiFi '{}' ... ".format(ssid), end="") 
requests = adafruit_requests.Session(pool, ssl.create_default_context())


if init_bot() == False: #if bot initialization fails
    print("\nTelegram bot initialization failed.")
else:
    print("\nTelegram bot ready!\n")
    #again part of the CircuitPython Documentation it works don't touch it.
    #pin GP19 is free, I mean nothing is connected to it. You can use any GPIO pin that is free
    simpleio.tone(board.GP19, NOTE_G4, duration=0.1)
    simpleio.tone(buzzer, NOTE_C5, duration=0.1)
    fetch_latest_update_id()

while True:
    try: #if wifi connection fails, keeps on trying to reconnect
        while not wifi.radio.ipv4_address or "0.0.0.0" in repr(wifi.radio.ipv4_address): #Doc
            print(f"Reconnecting to WiFi...")
            wifi.radio.connect(ssid, password) #Doc
            
        chat_id, message_in, user_name, message_id = read_message()
        if chat_id and message_in:
            if message_in == "/start":
                greet_msg = f"Hello {user_name}! Choose an option:" #TODO: greet by name
                
                keyboard = {
                    "keyboard": [[{"text": "Study Mode"}, {"text": "Alarm Mode"}],[{"text": "Game Mode"}]],
                    "resize_keyboard": True,
                    "is_persistent": True,
                }
                send_message(chat_id, greet_msg, reply_markup=json.dumps(keyboard))
                simpleio.tone(board.GP19, NOTE_G4, duration=0.1)
                simpleio.tone(board.GP19, NOTE_C5, duration=0.1)
            if message_in == "Study Mode":
                caption_text = "Unlock productivity with Pomodoro! Choose your focus journey!"
                inline_keyboard = {
                    "inline_keyboard": [
                        [{"text": "30' study - 5' break", "callback_data": "30-5"}],[{"text": "60' study - 10' break", "callback_data": "60-10"}]
                    ]
                }
                send_message(chat_id, caption_text, reply_markup=json.dumps(inline_keyboard))
                
            elif message_in == "30-5" and message_id:
            # This is where you handle the callback for the inline keyboard
            #TODO: screen countdown function for 30-5
                send_message(chat_id, "Pomodoro timer confirmed for 30'-5'. Tunnel vision!")
                
            elif message_in == "60-10" and message_id:
            # This is where you handle the callback for the inline keyboard
            #TODO: screen countdown function for 60-10
                send_message(chat_id, "Pomodoro timer confirmed for 60'-10'. Tunnel vision!")
            
            else:
                send_message(chat_id, "Command is not available.")
        else:
            time.sleep(1)
        
    except OSError as e: #catching errors wohhooo! lol
        print("Failed!\n", e)
        microcontroller.reset()

