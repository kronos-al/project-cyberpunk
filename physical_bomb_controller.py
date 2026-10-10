from RPLCD.i2c import CharLCD
import RPi.GPIO as GPIO
import time


# ==========================================
# CONFIGURAÇÃO DO DISPLAY DO CÓDIGO DE SERIe
# ==========================================

serieNumberLCD = CharLCD(
    i2c_expander="PCF8574",
    address=0x27,
    port=1,
    cols=16,
    rows=2
)
def updateScreenSerieLCD(text:str, xCursor:int, yCursor:int, clearAll:bool, clearLine:bool):
    print(f"[LCD] Atualizando: {text!r}")
    if clearAll:
        serieNumberLCD.clear()
    elif clearLine:
        serieNumberLCD.cursor_pos = (yCursor, 0)
        serieNumberLCD.write_string("                ")
    serieNumberLCD.cursor_pos = (yCursor, xCursor)
    serieNumberLCD.write_string(text)

# ==========================================
# CONFIGURAÇÃO DO TECLADO MATRICIAL 4x3
# ==========================================

# Numeração BCM dos GPIOs
KEYPAD_ROWS = [17, 27, 22, 23]
KEYPAD_COLS = [24, 25, 5]

KEYPAD_KEYS = [
    ["1", "2", "3"],
    ["4", "5", "6"],
    ["7", "8", "9"],
    ["*", "0", "#"]
]


def setupKeypad():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # Linhas: saídas
    for pin in KEYPAD_ROWS:
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

    # Colunas: entradas
    for pin in KEYPAD_COLS:
        GPIO.setup(
            pin,
            GPIO.IN,
            pull_up_down=GPIO.PUD_DOWN
        )


def readKeypad():
    for rowIndex, rowPin in enumerate(KEYPAD_ROWS):
        GPIO.output(rowPin, GPIO.HIGH)

        for colIndex, colPin in enumerate(KEYPAD_COLS):
            if GPIO.input(colPin) == GPIO.HIGH:
                key = KEYPAD_KEYS[rowIndex][colIndex]

                # Aguarda a tecla ser solta
                while GPIO.input(colPin) == GPIO.HIGH:
                    time.sleep(0.01)

                GPIO.output(rowPin, GPIO.LOW)

                # Pequena pausa para evitar leituras duplicadas
                time.sleep(0.03)

                return key

        GPIO.output(rowPin, GPIO.LOW)

    return None