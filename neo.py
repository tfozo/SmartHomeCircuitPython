import board
import neopixel
import time

# Configure the setup for a board with pin names like "GP6"
PIXEL_PIN = board.GP28  # Change D1 to GP6 for boards like Raspberry Pi Pico
NUM_PIXELS = 5  # Number of NeoPixels in the strip
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

# A list of colors to cycle through
colors = [RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, WHITE]

def cycle_colors(wait):
    for color in colors:
        for i in range(NUM_PIXELS):
            pixels[i] = color  # Set the color
        pixels.show()  # Refresh the strip to display the current color
        time.sleep(wait)  # Wait for a bit before changing colors

while True:
    cycle_colors(1)  # Change colors every second
