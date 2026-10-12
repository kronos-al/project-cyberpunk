from RPLCD.i2c import CharLCD
from gpiozero import LED as GpioLED
from bomb_logic import CONFIGURACOES_LED

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


# ==========================================
# CONFIGURAÇÃO DOS LEDS FÍSICOS
# ==========================================

# GPIOs em ordem: LED lógico 0 até LED lógico 9
GPIOS = [17, 27, 22, 23, 24, 25, 5, 6, 16, 26]

ledsFisicos = [GpioLED(gpio) for gpio in GPIOS]


# ==========================================
# LIGAR OU DESLIGAR TODOS OS LEDS
# ==========================================

def setAllLEDs(estado: bool):
    for led in ledsFisicos:
        led.on() if estado else led.off()


# ==========================================
# APLICAR CONFIGURAÇÃO DA BÚSSOLA
# ==========================================

def setCompassLEDs(configuracao: str):
    if configuracao not in CONFIGURACOES_LED:
        raise ValueError(
            f"Configuração de LEDs inválida: {configuracao}"
        )

    for led in CONFIGURACOES_LED[configuracao]:
        # O número da classe corresponde ao índice do GPIO
        ledFisico = ledsFisicos[led.numero]

        if led.ligado:
            ledFisico.on()
        else:
            ledFisico.off()

    print(f"[LEDs] Configuração aplicada: {configuracao}")