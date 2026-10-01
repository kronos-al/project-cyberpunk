import json
import string
import time
import threading
import random

from dataclasses import dataclass
from schemas import AguardandoPartidaSchema, ConfigBombSchema, ComecarPartidaSchema
from physical_bomb_controller import updateScreenSerieLCD

@dataclass
class LED:
    numero: int
    ligado: bool

CONFIGURACOES_LED = {

    # 0° - configuração 1
    "0_A": [
        LED(0, False), LED(1, False), LED(2, True),  LED(3, False), LED(4, True),
        LED(5, True),  LED(6, True),  LED(7, True),  LED(8, True),  LED(9, False)
    ],

    # 0° - configuração 2
     "0_B": [
        LED(0, True),  LED(1, False), LED(2, True),  LED(3, False), LED(4, True),
        LED(5, False), LED(6, True),  LED(7, True),  LED(8, False), LED(9, True)
    ],

    # 180° - configuração 1
    "180_A": [
        LED(0, False), LED(1, True),  LED(2, True),  LED(3, False), LED(4, False),
        LED(5, True),  LED(6, True),  LED(7, True),  LED(8, True),  LED(9, False)
    ],

    # 180° - configuração 2
    "180_B": [
        LED(0, True),  LED(1, False), LED(2, True),  LED(3, False), LED(4, True),
        LED(5, False), LED(6, True),  LED(7, False), LED(8, False), LED(9, False)
    ],

    # 270° - configuração 1
    "270_A": [
        LED(0, False), LED(1, False), LED(2, False), LED(3, False), LED(4, True),
        LED(5, True),  LED(6, False), LED(7, False), LED(8, True),  LED(9, True)
    ],

    # 270° - configuração 2
    "270_B": [
        LED(0, False), LED(1, False), LED(2, False), LED(3, False), LED(4, True),
        LED(5, False), LED(6, False), LED(7, False), LED(8, True),  LED(9, True)
    ],

    # 90° - configuração 1
    "90_A": [
        LED(0, True),  LED(1, False), LED(2, True),  LED(3, True),  LED(4, True),
        LED(5, True),  LED(6, True),  LED(7, True),  LED(8, False), LED(9, True)
    ],

     # 90° - configuração 2
    "90_B": [
        LED(0, True),  LED(1, False), LED(2, True),  LED(3, True),  LED(4, False),
        LED(5, True),  LED(6, True),  LED(7, True),  LED(8, False), LED(9, True)
    ]
}


class Partida:
    def __init__(self):
        self.estado = "AGUARDANDO_PARTIDA"
        self.id = None

        self.falhas = 0

        self.numeroDeFios = 0
        self.fios = []

        self.chosenLEDs= []
        self.chosenLEDsButtonPosition = None


        self.serialCode = None
        self.serialPassword = None

        self.tempoBomba = 300
        self.tempoBombaFormatado = "05:00"

        self.puzzle1 = False
        self.puzzle2 = False
        self.puzzle3 = False
        self.puzzle4 = False
        self.puzzle5 = False

        self.vitoria = False
        self.derrota = False

        self.timer_ativo = False
        self.loop_ativo = False

partida = Partida()
def on_mqtt_message(client, msg):
    global partida
    payload_str = msg.payload.decode("utf-8")
    try:
        dados = json.loads(payload_str)
    except json.JSONDecodeError:
        print(f"Mensagem em texto plano: {payload_str}")
        return

    # Extrai o estado (retorna None se a chave não existir)
    estado = dados.get("estado")

    # Se não tiver a chave "estado", encerra a execução
    if estado is None:
        print("Aviso: 'estado' não encontrado no JSON. Ignorando...")
        return

    # A partir daqui, o código só executa se "estado" existir
    print(f"Estado recebido: {estado}")
    match estado:
        case "AGUARDANDO_PARTIDA":
            try:
                validado = AguardandoPartidaSchema.model_validate(dados)
            except Exception:
                print("Erro: JSON não corresponde ao Schema esperado!")
                return

            partida = Partida()

            partida.estado = estado
            partida.id = int(dados["dados"]["idPartida"])

            # ========================================
            # Responde para a partida
            # ========================================

            topico_resposta = f"bombexe/{partida.id}/bomba/server"

            mensagem_resposta = {
                "estado": "AGUARDANDO_PARTIDA",
                "dados": {
                    "idPartida": partida.id
                }
            }

            client.publish(
                topico_resposta,
                json.dumps(mensagem_resposta),
                qos=1
            )
            updateScreenSerieLCD("AGUARDANDO A", 0, 0, True, False)
            updateScreenSerieLCD("PARTIDA", 0, 1, False, False)
            print(f"Publicado em: {topico_resposta}")
            print(f"Mensagem: {mensagem_resposta}")

        case "CONFIGURAR_FIOS":
            if partida.estado != "AGUARDANDO_PARTIDA":
                print("Partida não está no estado de configurar fios")
                return
            try:
                validado = ConfigBombSchema.model_validate(dados)
            except Exception:
                print("Erro: JSON não corresponde ao Schema esperado!")
                return
            if partida.id != int(dados["dados"]["idPartida"]):
                print("Partida inválida")
                return
            partida.numeroDeFios = int(dados["dados"]["numeroDeFios"])
            partida.fios = dados["dados"]["fios"]

            topico_resposta = f"bombexe/{partida.id}/bomba/server"
            mensagem_resposta = {
                "estado": "AGUARDANDO_JOGADORES",
                "dados": {
                    "idPartida": partida.id
                }
            }

            client.publish(
                topico_resposta,
                json.dumps(mensagem_resposta),
                qos=1
            )
            partida.estado = "AGUARDANDO_JOGADORES"
            print(f"Publicado em: {topico_resposta}")
            print(f"Mensagem: {mensagem_resposta}")

        case "COMECAR_PARTIDA":
            if partida.estado != "AGUARDANDO_JOGADORES":
                print("Partida não está no estado de iniciar partidas")
                return

            try:
                validado = ComecarPartidaSchema.model_validate(dados)
            except Exception:
                print("Erro: JSON não corresponde ao Schema esperado!")
                return

            if partida.id != int(dados["dados"]["idPartida"]):
                print("Partida inválida")
                return

            # ==========================================
            # CONFIGURAÇÃO DA PARTIDA
            # ==========================================

            partida.serialCode, partida.serialPassword = generateSerialAndPasswordCode()

            print("serialPassword", partida.serialPassword)

            # Escolhe aleatoriamente uma das 8 configurações
            partida.chosenLEDsButtonPosition, partida.chosenLEDs = random.choice(
                list(CONFIGURACOES_LED.items())
            )

            print("Configuração escolhida:", partida.chosenLEDsButtonPosition)

            for led in partida.chosenLEDs:
                print(f"LED {led.numero}: {'LIGADO' if led.ligado else 'DESLIGADO'}")

            # ==========================================
            # INICIAR TEMPO
            # ==========================================

            threading.Thread(
                target=iniciarContagemBomba,
                daemon=True
            ).start()

            # ==========================================
            # ALTERAR ESTADO
            # ==========================================

            partida.estado = "EM_PARTIDA"

            # ==========================================
            # INICIAR LOOP DA PARTIDA
            # ==========================================

            threading.Thread(
                target=loopPartida,
                args=(client,),
                daemon=True
            ).start()

            # ==========================================
            # AVISAR QUE A PARTIDA COMEÇOU
            # ==========================================

            topico_resposta = f"bombexe/{partida.id}/bomba/server"

            mensagem_resposta = {
                "estado": "EM_PARTIDA",
                "dados": {
                    "idPartida": partida.id,
                    "numeroDeSerie": partida.serialCode
                }
            }

            client.publish(
                topico_resposta,
                json.dumps(mensagem_resposta),
                qos=1
            )

            print(f"Publicado em: {topico_resposta}")
            print(f"Mensagem: {mensagem_resposta}")

def generateSerialAndPasswordCode():
    # 1. Geração do Código de Série (LNLNLN)
    firstLetter = random.choice(string.ascii_uppercase)
    firstNumber = random.choice(string.digits)
    secondLetter = random.choice(string.ascii_uppercase)
    secondNumber = random.choice(string.digits)
    thirdLetter = random.choice(string.ascii_uppercase)
    thirdNumber = random.choice(string.digits)

    serialCode = firstLetter + firstNumber + secondLetter + secondNumber + thirdLetter + thirdNumber

    # --- Lógica do Password Code ---
    letras = [firstLetter, secondLetter, thirdLetter]
    numeros = [firstNumber, secondNumber, thirdNumber]
    vogais_encontradas = [l for l in letras if l in "AEIOU"]
    qtd_vogais = len(vogais_encontradas)

    # PRIMEIRO DÍGITO (Análise das vogais)
    if qtd_vogais == 0:
        digito1 = "4"
    elif qtd_vogais == 1:
        if vogais_encontradas[0] in "AEI":
            digito1 = "7"
        else:  # O ou U
            digito1 = "2"
    else:  # Duas ou mais vogais
        digito1 = "9"

    # SEGUNDO DÍGITO (Último número do serial - thirdNumber)
    # Nota: string.digits retorna texto, convertemos para int para testar se é par
    if int(thirdNumber) % 2 == 0:
        digito2 = "6"
    else:
        digito2 = "3"

    # TERCEIRO DÍGITO (Repetição de números)
    # set() remove duplicadas. Se tamanho for 3, todos são diferentes. Se for 1, todos são iguais.
    qtd_numeros_unicos = len(set(numeros))
    if qtd_numeros_unicos == 3:
        digito3 = "8"  # Nenhum repetido
    elif qtd_numeros_unicos == 2:
        digito3 = "1"  # Exatamente dois iguais
    else:
        digito3 = "5"  # Três iguais

    # QUARTO DÍGITO (Comparação alfabética entre a primeira e última letra)
    if firstLetter == thirdLetter:
        digito4 = "9"
    elif firstLetter < thirdLetter:  # No Python, 'A' < 'B' (vem antes)
        digito4 = "2"
    else:
        digito4 = "6"

    # Juntando os 4 dígitos do Password Code
    passwordCode = digito1 + digito2 + digito3 + digito4

    return serialCode, passwordCode

def iniciarContagemBomba():
    partida.tempoBomba = 300
    partida.timer_ativo = True

    while partida.tempoBomba > 0 and partida.timer_ativo:

        minutos = partida.tempoBomba // 60
        segundos = partida.tempoBomba % 60

        partida.tempoBombaFormatado = f"{minutos:02d}:{segundos:02d}"

        print("Tempo da bomba:", partida.tempoBombaFormatado)

        time.sleep(1)

        partida.tempoBomba -= 1

    partida.tempoBomba = 0
    partida.tempoBombaFormatado = "00:00"
    partida.timer_ativo = False

    print("TEMPO ESGOTADO!")

def loopPartida(client):

    partida.loop_ativo = True

    print("Loop da partida iniciado.")

    while partida.loop_ativo:

        # ==========================================
        # VERIFICAR TEMPO
        # ==========================================

        if partida.tempoBomba <= 0:

            partida.derrota = True

            print("TEMPO ESGOTADO!")
            print("DERROTA!")

            partida.estado = "DERROTA"

            partida.loop_ativo = False
            break


        # ==========================================
        # VERIFICAR PUZZLES
        # ==========================================

        # Puzzle 1
        if partida.puzzle1:
            print("Puzzle 1 concluído!")


        # Puzzle 2
        if partida.puzzle2:
            print("Puzzle 2 concluído!")


        # Puzzle 3
        if partida.puzzle3:
            print("Puzzle 3 concluído!")


        # ==========================================
        # VERIFICAR VITÓRIA
        # ==========================================

        if (
            partida.puzzle1
            and partida.puzzle2
            and partida.puzzle3
            and partida.puzzle4
            and partida.puzzle5
        ):
            partida.vitoria = True
            partida.estado = "VITORIA"

            print("TODOS OS PUZZLES CONCLUÍDOS!")
            print("VITÓRIA!")

            partida.loop_ativo = False
            break


        # ==========================================
        # AGUARDAR PRÓXIMA VERIFICAÇÃO
        # ==========================================

        time.sleep(0.1)

    print("Loop da partida finalizado.")