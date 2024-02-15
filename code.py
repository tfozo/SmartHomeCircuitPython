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
from display import marquee,quicktext
from neo import light,clear_sky,rain,cloudy,snow_fall,thunder,danger
#from joke import get_dad_joke

# Get wifi details from a settings.toml file
print(os.getenv("test_env_file"))
ssid = os.getenv("WIFI_SSID")
password = os.getenv("WIFI_PASSWORD")
telegrambot = os.getenv("botToken")
weatherAPI = os.getenv("weatherAPI")

# Telegram API url.
API_URL = "https://api.telegram.org/bot" + telegrambot

# Buzzer

buzzer = board.GP18


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

def get_dad_joke():
    url = "https://icanhazdadjoke.com/"
    headers = {'Accept': 'application/json'}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:  # HTTP OK
            joke = response.json().get('joke', 'No joke found.')
        else:
            joke = "Failed to fetch joke - server returned non-OK status."
    except Exception as e:
        print(f"Failed to fetch joke due to an error: {e}")
        joke = "Failed to fetch joke due to a network or connection error."
    return joke    






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


#weather
def get_weather_by_city(city_name):
    api_key = weatherAPI  
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}appid={api_key}&q={city_name}&units=metric"  # 'units=metric' to get temperature in Celsius
    response = requests.get(complete_url)
    if response.status_code == 200:
        data = response.json()
        main_data = data['main']
        temperature = main_data['temp']
        weather_id = data['weather'][0]['id'] #will use this for my lights show
        weather_description = data['weather'][0]['description']
        
        return temperature, weather_description, weather_id
    else:
        return None, None, None

waiting_for_city = False  # New state variable to track if we're waiting for a city name
last_chat_id = None  # Keep track of the last chat ID to respond correctly


def handle_city_temp_request(chat_id):
    global waiting_for_city, last_chat_id
    send_message(chat_id, "Which City? Text me the name.")
    waiting_for_city = True  # Set the flag to true as we're now waiting for a city name
    last_chat_id = chat_id  # Remember the chat ID to respond to later



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
            if waiting_for_city:
                # If we're waiting for a city name, assume the next message is the city
                city_name = message_in  # The city name is the current message
                temperature, description, weather_id = get_weather_by_city(city_name)
                if temperature is not None and description is not None:
                    response_message = f"{city_name}: {temperature}*C {description}"
                else:
                    response_message = "Can't find city."
                send_message(chat_id, response_message)
                marquee(response_message, 0, 16, 0.3)
                waiting_for_city = False
                #light,clear_sky,rain,cloudy,snow_fall
                if weather_id == 800:
                    clear_sky()
                elif weather_id in [300,301,302,310,311,312,313,314,321,500,501,511,520,521,531]: #applies for [entire drizzle family] light, moderate, freezing, light intensity shower, shower,ragged
                    rain(0.3,0)
                elif weather_id in [502,503,504,522,200,201,202,230,231,232]: #applies for heavy intensity,very heavy,extreme,heavy intensity shower ,[thunderstorm with all rain and all drizzle]
                    rain(0.7,0.5)
                elif weather_id in [210,211,212,221]: #all thunder with out rain and drizzle (thunder only)
                    thunder(0.4)
                elif weather_id in [600,601,611,612,613,615,616,620,621]:#snow light,snow,sleet,light shower, shower, with light rain, rain and snow
                    snow_fall(.6, .3)
                elif weather_id in [602,622]:
                    snow_fall(.3, .8) #snow fall speed and intensity (amount)
                elif weather_id in [801,802,803,804]:
                    cloudy()
                else:
                    danger()                
                
            elif message_in == "/start":
                greet_msg = f"Welcome Home {user_name}! Choose an option:" #TODO: greet by name
                
                keyboard = {
                    "keyboard": [[{"text": "LED ON"}, {"text": "LED OFF"}], [{"text": "City TEMP"},{"text": "CPU TEMP"}],[{"text": "Dad Jokes"}]],
                    "resize_keyboard": True,
                    "is_persistent":True,
                }
                send_message(chat_id, greet_msg, reply_markup=json.dumps(keyboard))
                simpleio.tone(board.GP18, NOTE_G4, duration=0.1)
                simpleio.tone(board.GP18, NOTE_C5, duration=0.1)
            elif message_in == "LED ON":
                light(1)
                send_message(chat_id, "Light on.")
                quicktext('Light On',1)
            elif message_in == "LED OFF":
                light(0)
                send_message(chat_id, "Light off.")
                quicktext('Light Off',1)
            elif message_in == "City TEMP":
                handle_city_temp_request(chat_id)        
            elif message_in == "CPU TEMP":
                temp = readIntTemp()
                send_message(chat_id, temp)
                quicktext(f'CPU: {temp[13:18]} *C',2) #default deg(symbol) becomes '-' thus I had to interfere
                #marquee("LED is on my boy!", 0, 16, 0.3)
            elif message_in == "Dad Jokes":
                joke = get_dad_joke()
                send_message(chat_id, joke)
                marquee(joke, 0, 16, 0.3)
            else:
                send_message(chat_id, "Command is not available.")
        else:
            time.sleep(1)
        
    except OSError as e:
        print("Failed!\n", e)
        microcontroller.reset()
