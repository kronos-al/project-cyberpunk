
function enviarEEsperarResposta(
    mqttClient,
    topic,
    mensagem,
    verificarResposta,
    timeout = 5000,
    maxTentativas = 4
) {
    return new Promise((resolve, reject) => {

        let tentativa = 0;

        function tentarEnviar() {

            tentativa++;

            console.log(
                `Enviando mensagem MQTT (tentativa ${tentativa}/${maxTentativas})`
            );

            const timer = setTimeout(() => {

                mqttClient.removeListener("message", receberResposta);

                if (tentativa < maxTentativas) {

                    console.log(
                        `Nenhuma resposta recebida. Tentando novamente...`
                    );

                    tentarEnviar();

                } else {

                    reject(
                        new Error(
                            `Nenhuma resposta MQTT após ${maxTentativas} tentativas`
                        )
                    );
                }

            }, timeout);


            function receberResposta(topicRecebido, message) {

                let dados;

                try {
                    dados = JSON.parse(message.toString());
                } catch (error) {
                    return;
                }

                if (!verificarResposta(topicRecebido, dados)) {
                    return;
                }

                clearTimeout(timer);

                mqttClient.removeListener(
                    "message",
                    receberResposta
                );

                console.log(
                    `Resposta MQTT recebida na tentativa ${tentativa}`
                );

                resolve(dados);
            }


            mqttClient.on("message", receberResposta);


            mqttClient.publish(
                topic,
                JSON.stringify(mensagem),
                (error) => {

                    if (error) {

                        clearTimeout(timer);

                        mqttClient.removeListener(
                            "message",
                            receberResposta
                        );

                        reject(error);
                    }
                }
            );
        }

        tentarEnviar();
    });
}

module.exports = {
    enviarEEsperarResposta
};