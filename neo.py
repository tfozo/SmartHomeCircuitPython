import board
import neopixel
import time
import random

# Configure the setup for a board with pin names like "GP6"
PIXEL_PIN = board.GP28  # Change D1 to GP6 for boards like Raspberry Pi Pico
NUM_PIXELS = 30  # Number of NeoPixels in the strip
BRIGHTNESS = 0.5  # Brightness level, from 0 to 1

# Initialize the NeoPixel strip
pixels = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=BRIGHTNESS, auto_write=False)

# Define some basic colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 150, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
WHITE = (255, 255, 255)
OFF = (0,0,0)
CLOUDY = (50,50,50)
SNOWCLOUD = (5,5,5)
LIGHTNING = (255, 150, 0) #YELLOWISH RED



def light(value):
    if(value==1):
        WHITEOROFF = WHITE
    else:
        WHITEOROFF = OFF
    for i in range(NUM_PIXELS):  # Iterate over each pixel in the strip
        pixels[i] = WHITEOROFF  # Set each pixel to white
    pixels.show()



def clear_sky(duration=5):
    start_time = time.time()  # Capture the start time
    offset = 0  # Initialize the offset
    
    while True:
        current_time = time.time()  # Get the current time
        if current_time - start_time > duration:  # Check if 5 seconds have elapsed
            break  # Exit the loop
        
        # Set all LEDs to blue initially
        for i in range(NUM_PIXELS):
            pixels[i] = CYAN

        # Calculate positions for the three yellow LEDs based on the current offset
        yellow_positions = [(offset + i) % NUM_PIXELS for i in range(3)]

        # Set only the three specified LEDs to yellow
        for pos in yellow_positions:
            pixels[pos] = YELLOW

        # Update the LEDs to show the new pattern
        pixels.show()

        offset += 1  # Increment the offset to move the yellow LEDs
        time.sleep(0.2)




def rain(intensity, thunder_frequency,duration=5): #use 0 thuder frequency for no thunder
    #use bigger number like .9 or 1 for rapid thunder
    start_time = time.time()
    while True:
        current_time = time.time()  # Get the current time
        if current_time - start_time > duration:  # Check if 5 seconds have elapsed
            break  # Exit the loop
        # Simulate raindrops at the ends of the strip
        for i in range(10):  # Adjust for two LEDs at a time
            # Clear the strip or set it to cloudy for non-raindrop LEDs
            for j in range(NUM_PIXELS):
                if 10 < j < 20:  # Middle section remains cloudy
                    pixels[j] = CLOUDY
                else:  # Other sections are turned off to reset the raindrops
                    pixels[j] = (5, 5, 5)

            # Set the raindrop LEDs, with two LEDs for each raindrop
            if i < 10:
                pixels[max(0, 10 - i - 1)] = BLUE
                pixels[10 - i] = BLUE
                if 20 + i + 1 < NUM_PIXELS:
                    pixels[20 + i] = BLUE
                    pixels[20 + i + 1] = BLUE

            pixels.show()
            time.sleep(intensity)

        # Occasionally flash lightning
        if random.random() < thunder_frequency:  # Adjust the likelihood of lightning
            for _ in range(random.randint(1, 3)):  # Lightning can strike multiple times
                for j in range(NUM_PIXELS):
                    pixels[j] = LIGHTNING
                    pixels.brightness = 1
                pixels.show()
                time.sleep(random.uniform(0.02, 0.1))  # Rapid and brief flashes
                # Return to cloudy with raindrops
                for j in range(NUM_PIXELS):
                    if 10 < j < 20:  # Middle section remains cloudy
                        pixels[j] = CLOUDY
                    else:  # Other sections are turned off
                        pixels[j] = (5, 5, 5)
                pixels.show()
                time.sleep(random.uniform(0.1, 0.2))  # Brief darkness between flashes

#rain(.3,.4,2)


def thunder(thunder_frequency,duration=5):#0 no lightning, b/n 1 (more lightning)
    start_time = time.time()
    while True:
        current_time = time.time()  # Get the current time
        if current_time - start_time > duration:  # Check if 5 seconds have elapsed
            break  # Exit the loop
        
        if random.random() < thunder_frequency:
            num_flashes = random.randint(1, 5)  # Choose a random number of flashes
            for _ in range(num_flashes):
                flash_duration = random.uniform(0.02, 0.08)  # Duration of each flash
                pixels.fill(LIGHTNING)  # Illuminate all pixels to simulate lightning
                pixels.show()
                time.sleep(flash_duration)  # Keep the lightning on for the flash duration
                
                pixels.fill(SNOWCLOUD)  # Return pixels to the 'cloudy' state
                pixels.show()
                if _ < num_flashes - 1:  # If not the last flash, pause before the next one
                    time.sleep(random.uniform(0.1, 0.3))  # Short pause between flashes
                
                # After a set of flashes, have a longer pause to simulate the randomness of lightning
            time.sleep(random.uniform(0.5, 2.0))  # Longer pause between sets of flashes


def cloudy():
    for i in range(NUM_PIXELS):
        pixels[i] = (5,5,5)
    pixels.show()



def snow_fall(intensity, snowfall_intensity,duration=5):
    snowflakes = {}  # Dictionary to track each snowflake's position and lifespan
    start_time = time.time()
    while True:
        current_time = time.time()  # Get the current time
        if current_time - start_time > duration:  # Check if 5 seconds have elapsed
            break  # Exit the loop
        # Randomly add new snowflakes based on snowfall_intensity
        for _ in range(NUM_PIXELS):  # Check each LED for a potential new snowflake
            if random.random() < snowfall_intensity:  # Adjust probability based on snowfall_intensity
                start_pos = random.randint(0, NUM_PIXELS - 1)
                lifespan = random.randint(5, 15)  # Random lifespan for each snowflake
                snowflakes[start_pos] = lifespan

        # Move and update existing snowflakes
        new_snowflakes = {}
        for pos, life in snowflakes.items():
            # Randomly choose the direction and whether to disappear
            move = random.choice([-1, 1, 0])  # Allow for staying in place, moving forward or backward
            new_pos = pos + move
            if 0 <= new_pos < NUM_PIXELS:  # Ensure new position is within bounds
                # Decrease lifespan and update position
                life -= 1
                if life > 0:
                    new_snowflakes[new_pos] = life

        snowflakes = new_snowflakes

        # Display the snowflakes
        pixels.fill(SNOWCLOUD)  # Set all pixels to cloudy initially
        for pos in snowflakes.keys():
            pixels[pos] = WHITE  # Set snowflake pixels
        pixels.show()

        time.sleep(intensity)

# Adjust `intensity` for snowflake movement speed, `snowfall_intensity` for amount of snowfall

def danger(duration=5):
    start_time = time.time()
    while True:
        current_time = time.time()  # Get the current time
        if current_time - start_time > duration:  # Check if 5 seconds have elapsed
            break  # Exit the loop
        for i in range(NUM_PIXELS):
            pixels[i] = RED  # Set all pixels to red
        pixels.show()
        time.sleep(0.5)  # Keep red for 0.5 seconds
        
        for i in range(NUM_PIXELS):
            pixels[i] = OFF  # Turn all pixels off
        pixels.show()
        time.sleep(0.5)  # Keep off for 0.5 seconds

