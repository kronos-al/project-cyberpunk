import json
import string
import time
import threading
import random
import pygame
import labyrinth
from dataclasses import dataclass
from schemas import AguardandoPartidaSchema, ConfigBombSchema, ComecarPartidaSchema
from physical_bomb_controller import updateScreenSerieLCD, blinkLCDCursor, setupKeypad, readKeypad, updateFalhas, updatePuzzleLeds



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
        self.fioCorreto = None

        self.chosenLEDs= []
        self.chosenLEDsButtonPosition = None


        self.serialCode = None
        self.serialPassword = None
        self.serialInput = ""

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
setupKeypad()


pygame.mixer.pre_init(
    frequency=44100,
    size=-16,
    channels=2,
    buffer=512
)
pygame.mixer.init()

beepBomb = pygame.mixer.Sound(
    "sounds/beep_bomb.mp3"
)
bombExplosion = pygame.mixer.Sound(
    "sounds/bomb_explosion.mp3"
)

puzzleFail = pygame.mixer.Sound(
    "sounds/fail.mp3"
)

keyboardSound1 = pygame.mixer.Sound(
    "sounds/clickKeyboard1.mp3"
)

keyboardSound2 = pygame.mixer.Sound(
    "sounds/clickKeyboard2.mp3"
)

puzzleSolvedSound = pygame.mixer.Sound(
    "sounds/puzzle_solved.mp3"
)


clickSounds = [keyboardSound1, keyboardSound2]

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

            labyrinth.resetPartida()
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
            blinkLCDCursor(False)
            updateScreenSerieLCD("AGUARDANDO A", 0, 0, True, False)
            updateScreenSerieLCD("PARTIDA", 0, 1, False, False)
            updateFalhas(3)
            updatePuzzleLeds([
                LED(numero, True)
                for numero in range(10)
            ])
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

            # GERANDO CÓDIGO DE SÉRIE E SENHA - PUZZLE 1

            partida.serialCode, partida.serialPassword = generateSerialAndPasswordCode()

            print("serialPassword", partida.serialPassword)

            updateScreenSerieLCD("SERIAL: " + partida.serialCode, 0, 0, True, False)
            updateScreenSerieLCD("" + partida.serialCode, 0, 1, False, False)
            blinkLCDCursor(True)
            updateFalhas(partida.falhas)

            # ESCOLHENDO FIO CORRETO A SER CORTADO - PUZZLE 4
            partida.fioCorreto = escolherFioCorreto()

            print(
                f"Fio correto: posição {partida.fioCorreto['posicao']}, "
                f"cor {partida.fioCorreto['cor']}"
            )

            # GERANDO LEDs e ligando - PUZZLE 3
            # Escolhe aleatoriamente uma das 8 configurações
            partida.chosenLEDsButtonPosition, partida.chosenLEDs = random.choice(
                list(CONFIGURACOES_LED.items())
            )
            updatePuzzleLeds(partida.chosenLEDs)

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

            threading.Thread(
                target=iniciarBeepBomba,
                daemon=True
            ).start()

            labyrinth.iniciarPartida(partida)
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

        case "PARTIDA_FINALIZADA":
            if partida.estado != "DERROTA" and partida.estado != "VITORIA":
                print("Partida não está no estado FINALIZAÇÃO")
                return
            topico_resposta = f"bombexe/{partida.id}/bomba/server"

            mensagem_resposta = {
                "estado": "PARTIDA_FINALIZADA",
                "dados": {
                    "idPartida": partida.id,
                }
            }

            client.publish(
                topico_resposta,
                json.dumps(mensagem_resposta),
                qos=1
            )

def generateSerialAndPasswordCode():
    # 1. Geração do Código de Série (LNLNLN)

    # DEFININDO PRIMEIRA LETRA - CARACTERE 1
    if partida.numeroDeFios == 5 and not any(
            fio["cor"] == "VERDE" for fio in partida.fios
    ):
        firstLetter = random.choice("BCDFGHJKLMNPQRSTVWXYZ")
    else:
        firstLetter = random.choice(string.ascii_uppercase)

    # DEFININDO PRIMEIRO NÚMERO - CARACTERE 2
    firstNumber = random.choice(string.digits)

    # DEFININDO SEGUNDA LETRA - CARACTERE 3
    secondLetter = random.choice(string.ascii_uppercase)

    # DEFININDO SEGUNDO NÚMERO - CARACTERE 4
    if partida.numeroDeFios == 3 and not any(
            fio["cor"] == "VERMELHO" for fio in partida.fios
    ):
        secondNumber = random.choice("13579")
    else:
        secondNumber = random.choice(string.digits)

    # DEFININDO TERCEIRA LETRA - CARACTERE 5
    thirdLetter = random.choice(string.ascii_uppercase)

    # DEFININDO TERCEIRO NUMERO - CARACTERE 6
    if partida.numeroDeFios == 4 and not any(
            fio["cor"] == "AZUL" for fio in partida.fios
    ):
        thirdNumber = random.choice("13579")
    else:
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

# ==========================================
# ESCOLHER O FIO CORRETO PARA CORTAR
# ==========================================

def escolherFioCorreto():
    """
    Determina o fio correto com base:
    - Na quantidade de fios;
    - No código de série;
    - Na cor dos fios;
    - Na posição física dos fios.

    A posição 1 é o fio mais acima.
    Retorna um dicionário com a posição e a cor do fio.
    """

    fios = sorted(
        partida.fios,
        key=lambda fio: fio["posicao"]
    )

    numeroDeFios = partida.numeroDeFios
    serialCode = partida.serialCode

    # ==========================================
    # BOMBA COM 3 FIOS
    # ==========================================

    if numeroDeFios == 3:

        # Se o 4º caractere for par, cortar o primeiro vermelho
        if int(serialCode[3]) % 2 == 0:
            vermelhos = [
                fio for fio in fios
                if fio["cor"] == "VERMELHO"
            ]

            if vermelhos:
                return vermelhos[0]

        # Caso contrário, ou se não houver vermelho,
        # cortar o último verde, se existir
        verdes = [
            fio for fio in fios
            if fio["cor"] == "VERDE"
        ]

        if verdes:
            return verdes[-1]

        # Caso contrário, cortar o segundo fio
        return fios[1]

    # ==========================================
    # BOMBA COM 4 FIOS
    # ==========================================

    elif numeroDeFios == 4:

        # Se o último número do serial for par,
        # cortar o primeiro azul
        if int(serialCode[-1]) % 2 == 0:
            azuis = [
                fio for fio in fios
                if fio["cor"] == "AZUL"
            ]

            if azuis:
                return azuis[0]

        # Caso contrário, ou se não houver azul,
        # cortar o último laranja, se existir
        laranjas = [
            fio for fio in fios
            if fio["cor"] == "LARANJA"
        ]

        if laranjas:
            return laranjas[-1]

        # Caso contrário, cortar o terceiro fio
        return fios[2]

    # ==========================================
    # BOMBA COM 5 FIOS
    # ==========================================

    elif numeroDeFios == 5:

        # Se a primeira letra do serial for vogal,
        # cortar o primeiro verde
        if serialCode[0] in "AEIOU":
            verdes = [
                fio for fio in fios
                if fio["cor"] == "VERDE"
            ]

            if verdes:
                return verdes[0]

        # Caso contrário, ou se não houver verde,
        # cortar o último marrom, se existir
        marrons = [
            fio for fio in fios
            if fio["cor"] == "MARROM"
        ]

        if marrons:
            return marrons[-1]

        # Caso contrário, cortar o quarto fio
        return fios[3]

    raise ValueError(
        f"Quantidade de fios inválida: {numeroDeFios}"
    )

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

def iniciarBeepBomba():

    while partida.timer_ativo:

        tempo = partida.tempoBomba

        if tempo <= 0:
            break

        # ==========================================
        # VELOCIDADE DO BEEP
        # ==========================================

        if tempo > 40:

            # Mais de 40 segundos
            numeroBeeps = 1
        elif tempo > 35:

            numeroBeeps = 1.2
        elif tempo > 30:

            numeroBeeps = 1.3

        elif tempo > 25:

            # 40 até 21 segundos
            numeroBeeps = 1.5

        elif tempo > 20:

            # 40 até 21 segundos
            numeroBeeps = 1.7

        elif tempo > 15:

            # 20 até 11 segundos
            numeroBeeps = 2

        elif tempo > 10:

            # 20 até 11 segundos
            numeroBeeps = 2.5

        elif tempo > 6:

            # 10 até 4 segundos
            numeroBeeps = 3

        elif tempo > 2:

            # 10 até 4 segundos
            numeroBeeps = 7

        else:

            # Últimos 3 segundos
            numeroBeeps = 10

        # ==========================================
        # DIVIDE OS BEEPS IGUALMENTE
        # ==========================================

        intervalo = 1.0 / numeroBeeps

        beepBomb.play()

        time.sleep(intervalo)

# ==========================================
# PUZZLE 1 - ENTRADA DA SENHA PELO TECLADO
# ==========================================

def processarTecladoPuzzle1():
    # Só permite digitar durante uma partida ativa
    if partida.estado != "EM_PARTIDA":
        return

    # Não aceita mais entradas depois de resolver o puzzle
    if partida.puzzle1:
        return

    tecla = readKeypad()

    if tecla is None:
        return

    # ------------------------------------------
    # DIGITAR NÚMEROS
    # ------------------------------------------

    if tecla.isdigit():
        # Limita a entrada ao tamanho da senha
        if (
            partida.serialPassword is not None
            and len(partida.serialInput) < len(partida.serialPassword)
        ):
            partida.serialInput += tecla
            random.choice(clickSounds).play()
            updateScreenSerieLCD(
                partida.serialInput,
                0,
                1,
                False,
                True
            )

            print(
                f"[PUZZLE 1] Entrada atual: "
                f"{partida.serialInput}"
            )

    # ------------------------------------------
    # * - APAGAR O ÚLTIMO DÍGITO
    # ------------------------------------------

    elif tecla == "*":

        partida.serialInput = partida.serialInput[:-1]
        random.choice(clickSounds).play()
        updateScreenSerieLCD(
            partida.serialInput,
            0,
            1,
            False,
            True
        )

        print(
            f"[PUZZLE 1] Dígito apagado. "
            f"Entrada atual: {partida.serialInput}"
        )

    # ------------------------------------------
    # # - CONFIRMAR A SENHA
    # ------------------------------------------

    elif tecla == "#":
        random.choice(clickSounds).play()
        # Verifica se a senha digitada está correta
        if partida.serialInput == partida.serialPassword:

            partida.puzzle1 = True
            puzzleSolvedSound.play()
            blinkLCDCursor(False)
            updateScreenSerieLCD(
                "",
                0,
                1,
                True,
                False
            )
            print("[PUZZLE 1] Senha correta! Puzzle concluído.")

        else:

            partida.falhas += 1
            updateFalhas(partida.falhas)
            puzzleFail.play()
            partida.serialInput = ""

            # Limpa a segunda linha do LCD, sem exibir mensagem
            updateScreenSerieLCD(
                "",
                0,
                1,
                False,
                True
            )

            print(
                f"[PUZZLE 1] Senha incorreta! "
                f"Falhas: {partida.falhas}"
            )
def loopPartida(client):
    estadoAnteriorFalhas = 0
    partida.loop_ativo = True

    print("Loop da partida iniciado.")

    while partida.loop_ativo:

        # ==========================================
        # VERIFICAR FALHAS
        # ==========================================

        if partida.falhas > estadoAnteriorFalhas:
            print(partida.falhas, "Falhas")
            estadoAnteriorFalhas = partida.falhas
        elif partida.falhas < estadoAnteriorFalhas:
            print(partida.falhas, "Falhas.")
            print("Falhas resetadas!")
            estadoAnteriorFalhas = partida.falhas

        # ==========================================
        # VERIFICAR TEMPO
        # ==========================================

        if partida.tempoBomba <= 0 or partida.falhas >= 3:

            partida.derrota = True

            print("TEMPO ESGOTADO OU FALHAS EXCEDIDAS!")
            print("DERROTA!")

            partida.estado = "DERROTA"

            # ========================================
            # Responde para a partida
            # ========================================

            topico_resposta = f"bombexe/{partida.id}/bomba/server"

            mensagem_resposta = {
                "estado": "FIM_DE_JOGO",
                "dados": {
                    "idPartida": partida.id,
                    "erros": partida.falhas,
                    "tempo": partida.tempoBomba,
                    "resultado": "DERROTA",
                    "puzzles": {
                        "chaveDeInicializacao": partida.puzzle1,
                        "ajusteDeSintonizacao": partida.puzzle2,
                        "bussolaDeLeds": partida.puzzle3,
                        "fios": partida.puzzle4,
                        "labirinto": partida.puzzle5
                        }
                }
            }

            client.publish(
                topico_resposta,
                json.dumps(mensagem_resposta),
                qos=1
            )
            bombExplosion.play()
            partida.timer_ativo = False
            partida.loop_ativo = False
            break

        # ==========================================
        # VERIFICAR PUZZLES
        # ==========================================

        # ==========================================
        # PUZZLE 1 - CHAVE DE INICIALIZAÇÃO
        # ==========================================

        if not partida.puzzle1:
            processarTecladoPuzzle1()



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