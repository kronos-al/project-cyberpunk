from RPLCD.i2c import CharLCD

serieNumberLCD = CharLCD(
    i2c_expander="PCF8574",
    address=0x27,
    port=1,
    cols=16,
    rows=2
)


def updateScreenSerieLCD(text:str, xCursor:int, yCursor:int, clearAll:bool, clearLine:bool):
    if clearAll:
        serieNumberLCD.clear()
    elif clearLine:
        serieNumberLCD.cursor_pos = (0, yCursor)
        serieNumberLCD.write_string("                ")
    serieNumberLCD.cursor_pos = (xCursor, yCursor)
    serieNumberLCD.write_string(text)
