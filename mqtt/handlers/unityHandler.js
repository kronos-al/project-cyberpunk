const { getDb } = require("../../database/mongodb.js");

const cadastrarJogadoresSchema = require("../../schemas/cadastrarJogadoresSchema.js");
const comecarPartidaSchema = require("../../schemas/comecarPartidaSchema.js");

const { enviarEEsperarResposta } = require("../mqtt-request.js");

async function handleUnityMessage(topic, dados, mqttClient) {

    if (dados.estado === "CADASTRAR_JOGADORES") {
        // Fora do try para o catch conseguir usar no log
        let idPartida;

        try {
            /*
            * 1. Validar a mensagem recebida (agora só traz o idPartida)
            */
            const { error, value } =
                cadastrarJogadoresSchema.validate(dados);

            if (error) {
                console.error(
                    "Mensagem da Unity inválida:",
                    error.details[0].message
                );
                return;
            }

            /*
            * 2. Extrair o idPartida do topic
            *
            * bombexe/91/unity/server
            */
            const partes = topic.split("/");

            idPartida = Number(partes[1]);

            /*
            * 3. Conferir idPartida do topic com o payload
            */
            if (value.dados.idPartida !== idPartida) {
                console.error(
                    "idPartida do topic diferente do idPartida da mensagem."
                );
                return;
            }

            /*
            * 4. Procurar a partida no MongoDB
            */
            const db = getDb();

            const partida = await db.collection("partidas").findOne({
                _id: idPartida
            });

            if (!partida) {
                console.error(
                    `Partida ${idPartida} não encontrada.`
                );
                return;
            }

            /*
            * 5. Verificar se a partida está no estado correto
            */
            if (partida.estado !== "ADICIONAR_JOGADORES") {
                console.error(
                    `Partida ${idPartida} não está no estado "ADICIONAR_JOGADORES".`
                );
                return;
            }

            // ==========================================
            // AVANÇAR A PARTIDA
            // Os jogadores já foram salvos pelo postAddPlayer, então aqui
            // só mudamos o estado. A guarda no filtro impede processar a
            // mesma mensagem duas vezes.
            // ==========================================

            const avanco = await db.collection("partidas").updateOne(
                {
                    _id: idPartida,
                    estado: "ADICIONAR_JOGADORES"
                },
                {
                    $set: {
                        estado: "AGUARDANDO_INICIO_DA_PARTIDA"
                    }
                }
            );

            if (avanco.modifiedCount === 0) {
                console.error(
                    `Partida ${idPartida} já avançou do cadastro de jogadores.`
                );
                return;
            }

            const respostaUnity = await enviarEEsperarResposta(
                mqttClient,

                `bombexe/${idPartida}/server/unity`,

                {
                    estado: "AGUARDANDO_INICIO_DA_PARTIDA",
                    dados: {
                        idPartida: idPartida
                    }
                },

                (topicRecebido, dadosRecebidos) => {

                    return (
                        topicRecebido ===
                            `bombexe/${idPartida}/unity/server` &&

                        dadosRecebidos.estado ===
                            "AGUARDANDO_INICIO_DA_PARTIDA" &&

                        dadosRecebidos.dados?.idPartida ===
                            idPartida
                    );
                }, 15000, 10
            );

            console.log(
                `Unity confirmou AGUARDANDO_INICIO_DA_PARTIDA da partida ${idPartida}:`,
                respostaUnity
            );
        } catch (error) {
            console.error(
                `Erro ao avançar jogadores da partida ${idPartida}:`,
                error
            );
        }

    }

    if (dados.estado === "COMECAR_PARTIDA") {
        /*
        * 1. Validar a mensagem recebida
        */
        const { error, value } =
            comecarPartidaSchema.validate(dados);

        if (error) {
            console.error(
                "Mensagem da Unity inválida:",
                error.details[0].message
            );
            return;
        }

        /*
        * 2. Extrair o idPartida do topic
        *
        * bombexe/91/unity/server
        */

        const partes = topic.split("/");

        const idPartida = Number(partes[1]);

        /*
        * 3. Conferir idPartida do topic com o payload
        */
        if (value.dados.idPartida !== idPartida) {
            console.error(
                "idPartida do topic diferente do idPartida da mensagem."
            );
            return;
        }

        /*
        * 4. Procurar a partida no MongoDB
        */
        const db = getDb();

        const partida = await db.collection("partidas").findOne({
            _id: idPartida
        });

        if (!partida) {
            console.error(
                `Partida ${idPartida} não encontrada.`
            );
            return;
        }

        /*
        * 5. Verificar se a partida está no estado correto
        */
        if (partida.estado !== "AGUARDANDO_INICIO_DA_PARTIDA") {
            console.error(
                `Partida ${idPartida} não está no estado "AGUARDANDO_INICIO_DA_PARTIDA".`
            );
            return;
        }

        await db.collection("partidas").updateOne(
            {
                _id: idPartida
            },
            {
                $set: {
                    estado: "COMECAR_PARTIDA"
                }
            }
        );

        try {

            const respostaBomba = await enviarEEsperarResposta(
                mqttClient,

                `bombexe/${idPartida}/server/bomba`,

                {
                    estado: "COMECAR_PARTIDA",
                    dados: {
                        idPartida: idPartida
                    }
                },

                (topicRecebido, dadosRecebidos) => {

                    return (
                        topicRecebido ===
                            `bombexe/${idPartida}/bomba/server` &&

                        dadosRecebidos.estado ===
                            "EM_PARTIDA" &&

                        dadosRecebidos.dados?.idPartida ===
                            idPartida &&

                        typeof dadosRecebidos.dados?.numeroDeSerie ===
                            "string" &&

                        dadosRecebidos.dados.numeroDeSerie.trim().length > 0
                    );
                }
            );

            console.log(
                `Bomba confirmou o início da partida ${idPartida}:`,
                respostaBomba
            );

            await db.collection("partidas").updateOne(
                {
                    _id: idPartida
                },
                {
                    $set: {
                        estado: "EM_PARTIDA",
                        startedAt: new Date(),
                        "bomba.numeroDeSerie":
                            respostaBomba.dados.numeroDeSerie
                    }
                }
            );

        } catch (error) {

            console.error(
                `Erro ao iniciar a partida ${idPartida}:`,
                error
            );

        }

    }

}

module.exports = {
    handleUnityMessage
};