import board
import neopixel
import time
import random

PIXEL_PIN = board.GP28  # our pin for data
NUM_PIXELS = 17
BRIGHTNESS = .5  #from 0 to 1

pixels = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=BRIGHTNESS, auto_write=False)


RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 150, 0)
CYAN = (0, 255, 255)
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
    for i in range(NUM_PIXELS): 
        pixels[i] = WHITEOROFF  
    pixels.show()


# the idea is to make every light show to last 8 seconds by getting the times of current and start
def clear_sky(duration=8):
    start_time = time.time()  # get start time of show
    offset = 0  #start at
    
    while True:
        current_time = time.time()  # get now time
        if current_time - start_time > duration:  # I'm checking if specified duration in seconds has been elapsed
            break  # break the loop
        
        # making clear sky
        for i in range(NUM_PIXELS):
            pixels[i] = CYAN

        #calculate positions for the three yellow LEDs based on the current offset
        #I want the Sun to be 3 leds referred gpt for help right here!
        yellow_positions = [(offset + i) % NUM_PIXELS for i in range(3)] 

        # giving the Sun its color
        for pos in yellow_positions:
            pixels[pos] = YELLOW

        pixels.show()

        offset += 1  # moving the Sun all 3 at once, every .2 sec 
        time.sleep(0.2)
#clear_sky()



def rain(intensity, thunder_frequency,duration=8):
    #use 0 thunder frequency for no thunder
    #use bigger number like .9 or 1 for rapid thunder
    start_time = time.time()
    while True:
        current_time = time.time()  
        if current_time - start_time > duration: 
            break 
        #simulating the raindrops in both ends of the strip
        for i in range(6):  # we want 6 leds at both ends to simulate rain drops
            # the middle section should show the cloudy sky
            for j in range(NUM_PIXELS):
                if 6 < j < 11:  # Middle section
                    pixels[j] = CLOUDY
                else:  # the parts where its raining should also be less cloudy
                    pixels[j] = (5, 5, 5)

            # asked chat GPT for help, on this one, it basically makes the blue rain drops move down by gravity at both ends. 
            if i < 6:
                pixels[max(0, 6 - i - 1)] = BLUE
                pixels[6 - i] = BLUE
                if 11 + i + 1 < NUM_PIXELS:
                    pixels[11 + i] = BLUE
                    pixels[11 + i + 1] = BLUE

            pixels.show()
            time.sleep(intensity) # if small number then we know the rain is heavy, if intensity time is big its showering.

        # occasionally flash lightning #I asked gpt for help here too for the random part flashes part.
        if random.random() < thunder_frequency:  # frequecy of lighnting parameter, 0 for no lightning
            for _ in range(random.randint(1, 3)):  #it could strike again and again
                for j in range(NUM_PIXELS):
                    pixels[j] = LIGHTNING
                    pixels.brightness = 1
                pixels.show()
                time.sleep(random.uniform(0.02, 0.1))  # Rapid and brief flashes
                # after flashes back to raindrops
                for j in range(NUM_PIXELS):
                    if 6 < j < 11:  #middle section
                        pixels[j] = CLOUDY
                    else:  # the parts where its raining should also be less cloudy
                        pixels[j] = (5, 5, 5)
                pixels.show()
                time.sleep(random.uniform(0.1, 0.2))  # darkness b/n flashes

#rain(.3,.0)


def thunder(thunder_frequency,duration=8):#0 no lightning, b/n 1 (more lightning)
    start_time = time.time()
    while True:
        current_time = time.time()  
        if current_time - start_time > duration: 
            break 
        
        if random.random() < thunder_frequency:
            num_flashes = random.randint(1, 5)  
            for _ in range(num_flashes):
                flash_duration = random.uniform(0.02, 0.08)  # duration of each flash
                pixels.fill(LIGHTNING) 
                pixels.show()
                time.sleep(flash_duration) 
                
                pixels.fill(SNOWCLOUD)  #back to fuzzy cloudy mode
                pixels.show()
                if _ < num_flashes - 1:  # sometimes the lightning used to froze if it occurs at the 8th sec, so I begged gpt for help here too, it makes sure this doesn't happen
                    time.sleep(random.uniform(0.1, 0.3))  #pause b/n flashes
                
            time.sleep(random.uniform(0.5, 2.0))  # longer pause b/n flashes as well

#thunder(.9)

def cloudy(): #easy money
    for i in range(NUM_PIXELS):
        pixels[i] = (5,5,5) #fuzzy white
    pixels.show()



def snow_fall(intensity, snowfall_intensity,duration=8):
    snowflakes = {}  # Dictionary to track each snowflake's position and lifespan
    start_time = time.time()
    while True:
        current_time = time.time()  
        if current_time - start_time > duration: 
            break 
        # Randomly add new snowflakes based on snowfall_intensity
        for _ in range(NUM_PIXELS): 
            if random.random() < snowfall_intensity: #adjusting the probability based on the intensity of the snowfall
                start_pos = random.randint(0, NUM_PIXELS - 1) #the snow flake emerges randomly
                lifespan = random.randint(5, 15)  # a snow flake has random life time
                snowflakes[start_pos] = lifespan

        # moving the flakes
        new_snowflakes = {}
        for pos, life in snowflakes.items(): 
            #randomly choosing which dxn to move,and position 
            move = random.choice([-1, 1, 0])  # stay in place, move forward or back
            new_pos = pos + move
            if 0 <= new_pos < NUM_PIXELS:  # make sure the life gets lower and lower and the positon is updated
                life -= 1
                if life > 0:
                    new_snowflakes[new_pos] = life

        snowflakes = new_snowflakes

        # showing the flakes
        pixels.fill(SNOWCLOUD)  # were initially cloudy
        for pos in snowflakes.keys():
            pixels[pos] = WHITE  # then we show the flakes by WHITE 
        pixels.show()

        time.sleep(intensity)

# snow_fall((intensity)how intense the snow is, (snowfall_intensity) the amount of the snow)
#snow_fall(.5,.5)

def danger(duration=8):
    start_time = time.time()
    while True:
        current_time = time.time()  
        if current_time - start_time > duration:
            break 
        for i in range(NUM_PIXELS):
            pixels[i] = RED  # Set all pixels to red
        pixels.show()
        time.sleep(0.5)
        
        for i in range(NUM_PIXELS):
            pixels[i] = OFF
        pixels.show()
        time.sleep(0.5)

#danger()