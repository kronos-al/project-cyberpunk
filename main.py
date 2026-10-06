import threading

import labyrinth
from mqtt import conectar


def main():
    print("================================")
    print("        BOMB.EXE - BOMBA")
    print("================================")

    labyrinth.iniciarJogo()

    mqtt_client = conectar()

    print("[BOMB.EXE] Aguardando mensagens...")

    threading.Thread(
        target=mqtt_client.loop_forever,
        daemon=True
    ).start()

    labyrinth.executarJogo()


if __name__ == "__main__":
    main()