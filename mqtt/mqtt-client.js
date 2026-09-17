const mqtt = require("mqtt");
require("dotenv").config();
const protocol = "wss";
const host = "mqtt.feira-de-jogos.dev.br";
const port = "443";
const path = "/mqtt";

const { handleUnityMessage } = require("./handlers/unityHandler.js");
const { handleBombaMessage } = require("./handlers/bombaHandler.js");

const connectUrl = `${protocol}://${host}:${port}${path}`;

const mqttClient = mqtt.connect(connectUrl, {
  clientId: "servidor_jogo",

  username: "servidor_jogo",
  password: process.env.MQTT_SERVER_PASSWORD,

  clean: true,
  connectTimeout: 4000,
  reconnectPeriod: 1000,
});

mqttClient.on("connect", () => {
  console.log("Servidor conectado ao Broker MQTT com sucesso!");

  // Escuta mensagens enviadas pela Unity
  mqttClient.subscribe("bombexe/+/unity/server", (err) => {
    if (err) {
      console.error("Erro ao se inscrever em bombexe/+/unity/server:", err);
    } else {
      console.log("Inscrito em: bombexe/+/unity/server");
    }
  });

  // Escuta mensagens enviadas pela Bomba
  mqttClient.subscribe("bombexe/+/bomba/server", (err) => {
    if (err) {
      console.error("Erro ao se inscrever em bombexe/+/bomba/server:", err);
    } else {
      console.log("Inscrito em: bombexe/+/bomba/server");
    }
  });
});

// Recebe as mensagens
mqttClient.on("message", async (topic, message) => {

    let dados;

    try {
        dados = JSON.parse(message.toString());
    } catch (error) {
        console.error("Mensagem MQTT não é um JSON válido.");
        return;
    }

    const partes = topic.split("/");

    if (partes.length !== 4) {
        console.error("Topic MQTT inválido:", topic);
        return;
    }

    const [prefixo, idPartida, origem, destino] = partes;

    if (
        prefixo !== "bombexe" ||
        destino !== "server"
    ) {
        console.error("Topic MQTT inválido:", topic);
        return;
    }

    if (origem === "unity") {

      await handleUnityMessage(
          topic,
          dados,
          mqttClient
      );

    } else if (origem === "bomba") {

        await handleBombaMessage(topic, dados, mqttClient);

    } else {

        console.error("Origem MQTT desconhecida:", origem);
    }
});

mqttClient.on("error", (error) => {
  console.error("Erro na conexão MQTT:", error);
});

mqttClient.on("reconnect", () => {
  console.log("Tentando reconectar ao Broker MQTT...");
});

mqttClient.on("close", () => {
  console.log("Conexão MQTT fechada.");
});


module.exports = {
    mqttClient
};