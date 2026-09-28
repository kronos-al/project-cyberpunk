import json
import string

from schemas import AguardandoPartidaSchema, ConfigBombSchema, ComecarPartidaSchema
from physical_bomb_controller import updateScreenSerieLCD
import random
partida_estado = None
partida_id = None
partida_numeroDeFios = None
partida_fios = None
partida_serialCode = None
partida_serialPassword = None

def on_mqtt_message(client, msg):
    global partida_estado
    global partida_id
    global partida_numeroDeFios
    global partida_fios
    global partida_serialCode
    global partida_serialPassword
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

            partida_estado = estado
            partida_id = int(dados["dados"]["idPartida"])
            # ========================================
            # Responde para a partida
            # ========================================

            topico_resposta = f"bombexe/{partida_id}/bomba/server"

            mensagem_resposta = {
                "estado": "AGUARDANDO_PARTIDA",
                "dados": {
                    "idPartida": partida_id
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
            if partida_estado != "AGUARDANDO_PARTIDA":
                print("Partida não está no estado de configurar fios")
                return
            try:
                validado = ConfigBombSchema.model_validate(dados)
            except Exception:
                print("Erro: JSON não corresponde ao Schema esperado!")
                return
            if partida_id != int(dados["dados"]["idPartida"]):
                print("Partida inválida")
                return
            partida_numeroDeFios = int(dados["dados"]["numeroDeFios"])
            partida_fios = dados["dados"]["fios"]

            topico_resposta = f"bombexe/{partida_id}/bomba/server"
            mensagem_resposta = {
                "estado": "AGUARDANDO_JOGADORES",
                "dados": {
                    "idPartida": partida_id
                }
            }

            client.publish(
                topico_resposta,
                json.dumps(mensagem_resposta),
                qos=1
            )
            partida_estado = "AGUARDANDO_JOGADORES"
            print(f"Publicado em: {topico_resposta}")
            print(f"Mensagem: {mensagem_resposta}")
        case "COMECAR_PARTIDA":
            if partida_estado != "AGUARDANDO_JOGADORES":
                print("Partida não está no estado de iniciar partidas")
                return
            try:
                validado = ComecarPartidaSchema.model_validate(dados)
            except Exception:
                print("Erro: JSON não corresponde ao Schema esperado!")
                return
            if partida_id != int(dados["dados"]["idPartida"]):
                print("Partida inválida")
                return

            topico_resposta = f"bombexe/{partida_id}/bomba/server"
            mensagem_resposta = {
                "estado": "EM_PARTIDA",
                "dados": {
                    "idPartida": partida_id
                }
            }

            client.publish(
                topico_resposta,
                json.dumps(mensagem_resposta),
                qos=1
            )
            partida_estado = "EM_PARTIDA"
            print(f"Publicado em: {topico_resposta}")
            print(f"Mensagem: {mensagem_resposta}")
            partida_serialCode, partida_serialPassword = generateSerialAndPasswordCode()
            updateScreenSerieLCD("CODIGO DE SERIE:", 0, 0, True, False)
            updateScreenSerieLCD(partida_serialCode, 0, 1, False, False)
            print("serialPassword", partida_serialPassword)
            # FAZER LOGICA DE PARTIDA AQUI





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




