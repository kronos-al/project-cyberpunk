const { getDb } = require("../../database/mongodb.js");

const cadastrarJogadoresSchema = require("../../schemas/cadastrarJogadoresSchema.js");
const comecarPartidaSchema = require("../../schemas/comecarPartidaSchema.js");

const { enviarEEsperarResposta } = require("../mqtt-request.js");

async function handleUnityMessage(topic, dados, mqttClient) {

    if (dados.estado === "cadastrar jogadores") {
        try {
            /*
            * 1. Validar a mensagem recebida
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
            if (partida.estado !== "Adicionar Jogadores") {
                console.error(
                    `Partida ${idPartida} não está no estado "Adicionar Jogadores".`
                );
                return;
            }

            console.log(
                `Cadastrando jogadores da partida ${idPartida}...`
            );

            console.log("EDE:", value.dados.EDE);
            console.log("EIT:", value.dados.EIT);

            // ==========================================
            // BLOQUEAR CADASTRAMENTO DE JOGADORES
            // ==========================================

            const bloqueio = await db.collection("partidas").updateOne(
                {
                    _id: idPartida,
                    estado: "Adicionar Jogadores"
                },
                {
                    $set: {
                        estado: "Cadastrando Jogadores"
                    }
                }
            );

            if (bloqueio.modifiedCount === 0) {

                console.error(
                    `Jogadores da partida ${idPartida} já estão sendo cadastrados ou já foram cadastrados.`
                );

                return;
            }


            // ==========================================
            // CADASTRAR JOGADORES
            // ==========================================

            await db.collection("partidas").updateOne(
                {
                    _id: idPartida,
                    estado: "Cadastrando Jogadores"
                },
                {
                    $set: {
                        "jogadores.EDE": value.dados.EDE,
                        "jogadores.EIT": value.dados.EIT,

                        estado: "Aguardando Inicio da Partida"
                    }
                }
            );

            const respostaBomba = await enviarEEsperarResposta(
                mqttClient,

                `bombexe/${idPartida}/server/unity`,

                {
                    estado: "Aguardando Inicio da Partida",
                    dados: {
                        idPartida: idPartida
                    }
                }, 

                (topicRecebido, dadosRecebidos) => {

                    return (
                        topicRecebido ===
                            `bombexe/${idPartida}/unity/server` &&

                        dadosRecebidos.estado ===
                            "Aguardando Inicio da Partida" &&

                        dadosRecebidos.dados?.idPartida ===
                            idPartida
                    );
                }, 15000, 10
                );
        } catch (error) {
            console.error(
                `Erro ao cadastrar jogadores da partida ${idPartida}:`,
                error
            );
        }
        
    }

    if (dados.estado === "Começar Partida") {
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
        if (partida.estado !== "Aguardando Inicio da Partida") {
            console.error(
                `Partida ${idPartida} não está no estado "Aguardando Inicio da Partida".`
            );
            return; 
        }

        await db.collection("partidas").updateOne(
            {
                _id: idPartida
            },
            {
                $set: {
                    estado: "Começar Partida"
                }
            }
        );

        try {

            const respostaBomba = await enviarEEsperarResposta(
                mqttClient,

                `bombexe/${idPartida}/server/bomba`,

                {
                    estado: "Começar Partida",
                    dados: {
                        idPartida: idPartida
                    }
                },

                (topicRecebido, dadosRecebidos) => {

                    return (
                        topicRecebido ===
                            `bombexe/${idPartida}/bomba/server` &&

                        dadosRecebidos.estado ===
                            "Em Partida" &&

                        dadosRecebidos.dados?.idPartida ===
                            idPartida
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
                        estado: "Em Partida",
                        startedAt: new Date()
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