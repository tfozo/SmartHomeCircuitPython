import adafruit_requests as 
import socketpool
import wifi

# Make sure wifi is already configured and connected before this function is called

def get_dad_joke():
    pool = socketpool.SocketPool(wifi.radio)
    headers = {'Accept': 'application/json'}  # We ask for a JSON formatted response
    response = requests.get('https://icanhazdadjoke.com/', headers=headers, pool=pool)
    
    # Parse the JSON response
    joke_data = response.json()
    return joke_data['joke']

# Example usage
joke = get_dad_joke()
print(joke)
