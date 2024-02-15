import board,busio
from lcd.lcd import LCD
from lcd.i2c_pcf8574_interface import I2CPCF8574Interface
import time
from lcd.lcd import CursorMode

# Talk to the LCD at I2C address 0x27.
# The number of rows and columns defaults to 4x20, so those
# arguments could be omitted in this case.
lcd = LCD(I2CPCF8574Interface(busio.I2C(board.GP1, board.GP0), 0x27), num_rows=2, num_cols=16)

#lcd.print("abc ")
#lcd.print("This is quite long and will wrap onto the next line automatically.")

#time.sleep(1)
# Start at the second line, fifth column (numbering from zero).
#lcd.set_cursor_pos(1, 4)
#lcd.print("Here I am")
#col = 0
#row = 0
def marquee(text, row, width, delay):
    padded_text = ' ' * width + text + ' ' * width  # Add spaces before and after the text
    for i in range(len(padded_text) - width):
        lcd.clear() 
        lcd.set_cursor_pos(row, 0)
        lcd.print(padded_text[i:i+width])  # Print a substring of the text
        time.sleep(delay)
        if i == len(padded_text) - width - 1:
            i = width  # Reset the counter to start the marquee again
    lcd.clear()



def quicktext(text,delay):
    lcd.clear()
    lcd.set_cursor_pos(1,0)
    lcd.print(text)
    time.sleep(delay)
    lcd.clear()
# Assuming your LCD is 16 columns wide
#marquee("This is quite long and will wrap onto the next line automatically.", 0, 16, 0.3)

# Make the cursor visible as a line.
#lcd.set_cursor_mode(CursorMode.LINE)