import json
from schemas import AguardandoPartidaSchema, ConfigBombSchema, ComecarPartidaSchema
from physical_bomb_controller import updateScreenSerieLCD
partida_estado = None
partida_id = None
partida_numeroDeFios = None
partida_fios = None

def on_mqtt_message(client, msg):
    global partida_estado
    global partida_id
    global partida_numeroDeFios
    global partida_fios
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
            updateScreenSerieLCD("AGUARDANDO", 0, 0, True, False)
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
            updateScreenSerieLCD("CODIGO DE SERIE:", 0, 0, True, False)
            updateScreenSerieLCD("A1C23E", 0, 1, False, False)
            # FAZER LOGICA DE PARTIDA AQUI