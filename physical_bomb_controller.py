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
from pynput.keyboard import Key, Controller



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


# Instâncias globais do teclado
_keyboard = Controller()
_canal_ads = None
_botao_anterior = None

# Mapeamento dos botões analógicos para as teclas virtuais do sistema
MAPEAMENTO_TECLAS = {
    "S1": {"nome": "Esquerda", "tecla": Key.left},
    "S2": {"nome": "Cima", "tecla": Key.up},
    "S3": {"nome": "Baixo", "tecla": Key.down},
    "S4": {"nome": "Direita", "tecla": Key.right},
    "S5": {"nome": "Enter", "tecla": Key.enter}
}


def inicializarTecladoVirtual(i2c_bus=None):
    """
    Inicializa o conversor ADS1115 no canal A0.
    Você pode passar o objeto 'i2c' existente ou a função criará um novo.
    """
    global _canal_ads
    try:
        if i2c_bus is None:
            i2c_bus = busio.I2C(board.SCL, board.SDA)

        ads = ADS.ADS1115(i2c_bus)
        _canal_ads = AnalogIn(ads, 0)
        print("[Bomb Exe Virtual Keyboard] ADS1115 inicializado no canal A0.")
    except Exception as e:
        print(f"[Bomb Exe Virtual Keyboard] Erro ao inicializar hardware ADS1115: {e}")

inicializarTecladoVirtual(i2c)


def _identificar_botao(tensao: float):
    """Identifica o código do botão com base na leitura da tensão em 3.3V."""
    if tensao > 3.1:
        return None
    elif tensao < 0.15:
        return "S1"
    elif 0.3 <= tensao < 0.7:
        return "S2"
    elif 0.8 <= tensao < 1.3:
        return "S3"
    elif 1.4 <= tensao < 2.0:
        return "S4"
    elif 2.1 <= tensao < 2.8:
        return "S5"
    else:
        return None


def processarTecladoVirtual():
    """
    Função para chamar DENTRO do seu loop principal (uma única iteração).

    Lê a tensão no A0, faz a identificação do botão, gerencia o debounce/transição
    e simula o pressionamento da tecla no sistema operacional.

    Retorna a tecla disparada ("S1"..."S5") ou None se nenhuma ação ocorreu.
    """
    global _botao_anterior, _canal_ads

    if _canal_ads is None:
        return None

    try:
        tensao_atual = _canal_ads.voltage
        print("Tensao atual", tensao_atual)
        botao_atual = _identificar_botao(tensao_atual)

        # Detecta o momento exato em que um novo botão é pressionado (Borda de Subida)
        if botao_atual and botao_atual != _botao_anterior:
            info = MAPEAMENTO_TECLAS.get(botao_atual)
            if info:
                tecla = info["tecla"]
                _keyboard.press(tecla)
                _keyboard.release(tecla)
                print(f"[Bomb Exe Keyboard] Tecla {info['nome']} ({tecla}) enviada! ({tensao_atual:.3f} V)")

            _botao_anterior = botao_atual
            return botao_atual

        # Se soltou o botão, reseta a trava do clique anterior
        if botao_atual is None:
            _botao_anterior = None

    except Exception as e:
        print(f"[Bomb Exe Keyboard] Erro ao ler porta analógica: {e}")

    return None

