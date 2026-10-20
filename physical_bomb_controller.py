from RPLCD.i2c import CharLCD
from gpiozero import (
    DigitalInputDevice,
    DigitalOutputDevice
)
import time
import serial
import json
import board
import busio
from adafruit_ht16k33 import segments
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from evdev import UInput, ecodes


# ==========================================
# CONFIGURAÇÃO DO RELÓGIO DE TEMPO
# ==========================================
i2c = busio.I2C(board.SCL, board.SDA)
timeClock = segments.Seg7x4(i2c, address=0x70)
timeClock.brightness = 1
timeClock.colon = True



def updateTimeClock(time:str):
    try:
        timeClock.print(time)
    except:
        timeClock.print("8888")

def turnOffTimeClock():
    timeClock.fill(0)
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

def turnOffAllLeds():
    serial_json = {
        "type": "general",
        "data": {
            "turnOffAllLeds": True
        }
    }
    # 2. Converte para string JSON e adiciona o '\n' no final
    json_string = json.dumps(serial_json) + "\n"

    # 3. Envia via serial codificado em bytes
    espSerial.write(json_string.encode('utf-8'))
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
        serieNumberLCD.cursor_mode = "blink"
    else:
        serieNumberLCD.cursor_mode = "hide"
# ==========================================
# LIGAR / DESLIGAR DISPLAY E BACKLIGHT
# ==========================================

def setSerieLCDEnabled(enabled: bool):
    # Liga/desliga os caracteres
    serieNumberLCD.display_enabled = enabled

    # Liga/desliga a iluminação de fundo
    serieNumberLCD.backlight_enabled = enabled

    estado = "ligado" if enabled else "desligado"
    print(f"[LCD] Display e backlight {estado}.")

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

# ==========================================
# ADKEYBOARD / ADS1115
# ==========================================

ads = ADS.ADS1115(i2c, address=0x48)
canalTeclado = AnalogIn(ads, 0)


# ==========================================
# TECLADO VIRTUAL DO LINUX
# ==========================================

teclasPermitidas = [
    ecodes.KEY_LEFT,
    ecodes.KEY_UP,
    ecodes.KEY_DOWN,
    ecodes.KEY_RIGHT,
    ecodes.KEY_ENTER,
]

tecladoVirtual = UInput(
    {ecodes.EV_KEY: teclasPermitidas},
    name="Bomb.exe Virtual Keyboard"
)

BOTOES_TECLADO = {
    "esquerda": ecodes.KEY_LEFT,
    "cima": ecodes.KEY_UP,
    "baixo": ecodes.KEY_DOWN,
    "direita": ecodes.KEY_RIGHT,
    "selecionar": ecodes.KEY_ENTER,
}

# Tecla virtual atualmente pressionada
teclaAtual = None

# Estado usado no debounce do ADKeyboard
_botaoCandidato = None
_tempoCandidato = 0.0
_botaoEstavel = None

# Tempo mínimo para confirmar uma mudança de botão
TEMPO_DEBOUNCE = 0.04


# ==========================================
# IDENTIFICAR BOTÃO PELA TENSÃO
# ==========================================

def identificarBotao(tensao):
    if tensao > 3.1:
        return None

    if tensao < 0.15:
        return "esquerda"

    if 0.3 <= tensao < 0.7:
        return "cima"

    if 0.8 <= tensao < 1.3:
        return "baixo"

    if 1.4 <= tensao < 2.0:
        return "direita"

    if 2.1 <= tensao < 2.8:
        return "selecionar"

    # Região sem botão reconhecido
    return None


# ==========================================
# ENVIAR EVENTO AO TECLADO VIRTUAL
# ==========================================

def enviarTeclaVirtual(tecla, pressionada):
    tecladoVirtual.write(
        ecodes.EV_KEY,
        tecla,
        1 if pressionada else 0
    )
    tecladoVirtual.syn()


# ==========================================
# ATUALIZAR TECLADO VIRTUAL
# Chamar continuamente no while True
# ==========================================

def atualizarTecladoVirtual():
    global teclaAtual
    global _botaoCandidato
    global _tempoCandidato
    global _botaoEstavel

    # Lê a tensão atual do ADS1115
    try:
        tensao = canalTeclado.voltage
    except Exception as erro:
        print(f"[ADKEYBOARD] Erro na leitura: {erro}")
        return

    botaoLido = identificarBotao(tensao)
    agora = time.monotonic()

    # Detecta mudança no botão lido e inicia o debounce
    if botaoLido != _botaoCandidato:
        _botaoCandidato = botaoLido
        _tempoCandidato = agora
        return

    # Aguarda a leitura estabilizar
    if agora - _tempoCandidato < TEMPO_DEBOUNCE:
        return

    # Não houve mudança no botão estável
    if botaoLido == _botaoEstavel:
        return

    _botaoEstavel = botaoLido

    novaTecla = BOTOES_TECLADO.get(botaoLido)

    # Libera a tecla anterior antes de pressionar outra
    if teclaAtual is not None:
        enviarTeclaVirtual(teclaAtual, False)
        teclaAtual = None

    # Pressiona a nova tecla, se houver
    if novaTecla is not None:
        enviarTeclaVirtual(novaTecla, True)
        teclaAtual = novaTecla

        print(
            f"[ADKEYBOARD] {botaoLido} "
            f"(tensão: {tensao:.3f} V)"
        )


# ==========================================
# ENCERRAR TECLADO VIRTUAL
# ==========================================

def encerrarTecladoVirtual():
    global teclaAtual

    if teclaAtual is not None:
        enviarTeclaVirtual(teclaAtual, False)
        teclaAtual = None

    tecladoVirtual.close()


# Libera o dispositivo virtual quando o Python encerrar
atexit.register(encerrarTecladoVirtual)

