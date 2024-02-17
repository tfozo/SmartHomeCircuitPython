import board,busio
from lcd.lcd import LCD
from lcd.i2c_pcf8574_interface import I2CPCF8574Interface
import time
from lcd.lcd import CursorMode

#I got this library for the display in github, it helps me set up the lcd in circuit python,
#https://github.com/dhalbert/CircuitPython_LCD

# Talk to the LCD at I2C address 0x27.
# Here I had to literally go to every forum to get this thing working, setting up the LCD initially was tought for CircuitPython
#as the documentation kinda was old.
#rows 2, and columns are 16 and connected to pins, and adress is 0x27(scanned to find that)
lcd = LCD(I2CPCF8574Interface(busio.I2C(board.GP1, board.GP0), 0x27), num_rows=2, num_cols=16)


def marquee(text, row, width, delay):
    #making sure we give it a padding so the text doesn't jump into the screen right of the bat
    padded_text = ' ' * width + text + ' ' * width  #giving it space first and last
    for i in range(len(padded_text) - width):
        lcd.clear() 
        lcd.set_cursor_pos(row, 0) #writes at first row 
        lcd.print(padded_text[i:i+width])  #I asked gpt for help here cuz I couldn't ge the logic to marqee it like in old HTML
        time.sleep(delay)
        if i == len(padded_text) - width - 1:
            i = width  # Reset the counter to start the marquee again
    lcd.clear()

#marquee('Novastella benny boy!', 0,16,.3)

def quicktext(text,delay):
    lcd.clear()
    lcd.set_cursor_pos(1,0) #now its at the second row and first column, if over flown it automatically goes to available space, so u can change this to accomodate the wrapping effect to (0,0)
    lcd.print(text)
    time.sleep(delay)
    lcd.clear()
#quicktext('Abenezer',.6)
# Make the cursor visible as a line.
#lcd.set_cursor_mode(CursorMode.LINE)