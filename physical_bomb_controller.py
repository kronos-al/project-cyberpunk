from RPLCD.i2c import CharLCD
from gpiozero import (
    DigitalInputDevice,
    DigitalOutputDevice
)
import time
import serial
import json

# ==========================================
# COMUNICAÇÃO SERIAL
# ==========================================

espSerial = serial.Serial('/dev/serial0', baudrate=9600, timeout=1)

def updateFalhas(falhas):
    serial_json = {
        "type": "falhas",
        "data": {
            "fails": falhas
        }
    }
    # 2. Converte para string JSON e adiciona o '\n' no final
    json_string = json.dumps(serial_json) + "\n"

    # 3. Envia via serial codificado em bytes
    espSerial.write(json_string.encode('utf-8'))
    return

def updatePuzzleLeds(leds):
    serial_json = {
        "type": "puzzle_leds",
        "data": {
            "leds": [
                {
                    "numero": led.numero,
                    "ligado": led.ligado
                }
                for led in leds
            ]
        }
    }

    # Converte para JSON e adiciona a quebra de linha
    json_string = json.dumps(serial_json) + "\n"

    # Envia para a ESP32
    espSerial.write(json_string.encode("utf-8"))

# ==========================================
# CONFIGURAÇÃO DO DISPLAY DO CÓDIGO DE SERIE
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


def blinkLCDCursor(blink: bool):
    if blink:
        serieNumberLCD.blink()
    else:
        serieNumberLCD.blink_off()
# ==========================================
# LIGAR / DESLIGAR DISPLAY E BACKLIGHT
# ==========================================

#def setSerieLCDEnabled(enabled: bool):
#    # Liga/desliga os caracteres
#    serieNumberLCD.display_enabled = enabled
#
#    # Liga/desliga a iluminação de fundo
#    serieNumberLCD.backlight_enabled = enabled
#
#    estado = "ligado" if enabled else "desligado"
#    print(f"[LCD] Display e backlight {estado}.")

# ==========================================
# CONFIGURAÇÃO DO TECLADO MATRICIAL 4x3
# GPIOs no padrão BCM
# ==========================================

LINHAS = [27, 5, 25, 23]
COLUNAS = [22, 17, 24]

TECLAS = [
    ["1", "2", "3"],
    ["4", "5", "6"],
    ["7", "8", "9"],
    ["*", "0", "#"]
]


# Objetos do teclado
_keypadRows = []
_keypadCols = []

_keypadConfigured = False
_keypadKeyHeld = False


# ==========================================
# INICIALIZAR TECLADO
# Chamar apenas uma vez por execução
# ==========================================

def setupKeypad():
    global _keypadRows, _keypadCols
    global _keypadConfigured

    # Evita configurar os GPIOs novamente
    if _keypadConfigured:
        return

    # Linhas: saídas digitais
    _keypadRows = [
        DigitalOutputDevice(
            pin,
            active_high=True,
            initial_value=False
        )
        for pin in LINHAS
    ]

    # Colunas: entradas com pull-down
    _keypadCols = [
        DigitalInputDevice(
            pin,
            pull_up=False
        )
        for pin in COLUNAS
    ]

    _keypadConfigured = True

    print("[KEYPAD] Teclado matricial 4x3 inicializado.")


# ==========================================
# LER UMA TECLA
# Retorna "0"..."9", "*" ou "#".
# Retorna None quando nenhuma tecla nova é lida.
# ==========================================

def readKeypad():
    global _keypadKeyHeld

    if not _keypadConfigured:
        raise RuntimeError(
            "Teclado não inicializado. Chame setupKeypad()."
        )

    teclaDetectada = None

    # Ativa uma linha por vez
    for rowIndex, row in enumerate(_keypadRows):
        row.on()

        # Pequena estabilização do sinal
        time.sleep(0.001)

        for colIndex, col in enumerate(_keypadCols):
            if col.is_active:
                teclaDetectada = TECLAS[rowIndex][colIndex]
                break

        row.off()

        if teclaDetectada is not None:
            break

    # Nenhuma tecla pressionada: permite uma nova leitura
    # na próxima pressão.
    if teclaDetectada is None:
        _keypadKeyHeld = False
        return None

    # Evita repetir a mesma tecla enquanto ela está pressionada
    if _keypadKeyHeld:
        return None

    _keypadKeyHeld = True

    # Debounce básico
    time.sleep(0.02)

    print(f"[KEYPAD] Tecla pressionada: {teclaDetectada}")

    return teclaDetectada