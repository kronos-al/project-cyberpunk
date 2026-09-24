import os
import ssl
import paho.mqtt.client as mqtt
from bomb_logic import on_mqtt_message
from dotenv import load_dotenv

load_dotenv()

MQTT_HOST = "mqtt.feira-de-jogos.dev.br"
MQTT_PORT = 443

MQTT_USERNAME = "bomba"
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

MQTT_TOPIC = "bombexe/+/server/bomba"

MQTT_PATH = "/mqtt"


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"[MQTT] Conectado. Código: {reason_code}")

    client.subscribe(MQTT_TOPIC)

    print(f"[MQTT] Inscrito em: {MQTT_TOPIC}")


def on_message(client, userdata, message):
    on_mqtt_message(client, message)


def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    print(f"[MQTT] Desconectado. Código: {reason_code}")


def criar_cliente():
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        transport="websockets"
    )

    client.username_pw_set(
        MQTT_USERNAME,
        MQTT_PASSWORD
    )

    # TLS
    client.tls_set(
        cert_reqs=ssl.CERT_REQUIRED
    )

    # WebSocket
    client.ws_set_options(
        path=MQTT_PATH
    )

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    return client


def conectar():
    client = criar_cliente()

    print("[MQTT] Conectando...")

    client.connect(
        MQTT_HOST,
        MQTT_PORT,
        keepalive=60
    )

    return client
