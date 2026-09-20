from mqtt import conectar


def main():
    print("================================")
    print("        BOMB.EXE - BOMBA")
    print("================================")

    mqtt_client = conectar()

    print("[BOMB.EXE] Aguardando mensagens...")

    mqtt_client.loop_forever()


if __name__ == "__main__":
    main()
