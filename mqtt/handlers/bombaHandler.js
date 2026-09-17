const { getDb } = require("../../database/mongodb.js");
const { enviarEEsperarResposta } = require("../mqtt-request.js");

const fimDeJogoSchema = require("../../schemas/fimDeJogoSchema.js");

async function handleBombaMessage(topic, dados, mqttClient) {
    if (dados.estado === "FIM_DE_JOGO") {
        try{
            /*
            * 1. Validar a mensagem recebida
            */
            const { error, value } =
                fimDeJogoSchema.validate(dados);

            if (error) {
                console.error(
                    "Mensagem da da Bomba inválida:",
                    error.details[0].message
                );
                return;
            }

            /*
            * 2. Extrair o idPartida do topic
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
            if (partida.estado !== "EM_PARTIDA") {
                console.error(
                    `Partida ${idPartida} não está no estado "EM_PARTIDA".`
                );
                return;
            }

            const finishedAt = new Date();

            await db.collection("partidas").updateOne(
                {
                    _id: idPartida,
                    estado: "EM_PARTIDA"
                },
                {
                    $set: {
                        estado: "FIM_DE_JOGO",
                        "bomba.erros": value.dados.erros,
                        "bomba.tempo": value.dados.tempo,
                        "bomba.puzzles.chaveDeInicializacao.resolvido": value.dados.puzzles.chaveDeInicializacao,
                        "bomba.puzzles.ajusteDeSintonizacao.resolvido": value.dados.puzzles.ajusteDeSintonizacao,
                        "bomba.puzzles.bussolaDeLeds.resolvido": value.dados.puzzles.bussolaDeLeds,
                        "bomba.puzzles.labirinto.resolvido": value.dados.puzzles.labirinto,
                        "bomba.puzzles.fios.resolvido": value.dados.puzzles.fios,
                        "resultado": value.dados.resultado,
                        "finishedAt": finishedAt
                    }
                }
            );

            const dadosUnity = {
                idPartida: idPartida,

                date: formatarDataParaUnity(finishedAt),

                numero_de_serie: partida.bomba.numeroDeSerie,

                resultado: value.dados.resultado,

                tempo: value.dados.tempo,

                erros: value.dados.erros,

                bomba: {
                    fios: value.dados.puzzles.fios,
                    labirinto: value.dados.puzzles.labirinto,
                    chaveInicializacao:
                        value.dados.puzzles.chaveDeInicializacao,
                    ajusteSintonizacao:
                        value.dados.puzzles.ajusteDeSintonizacao,
                    bussolaLEDs:
                        value.dados.puzzles.bussolaDeLeds
                }
            };

            try {

                const respostaBomba = await enviarEEsperarResposta(
                    mqttClient,

                    `bombexe/${idPartida}/server/bomba`,

                    {
                        estado: "PARTIDA_FINALIZADA",
                        dados: {
                            idPartida: idPartida
                        }
                    },

                    (topicRecebido, dadosRecebidos) => {

                        return (
                            topicRecebido ===
                                `bombexe/${idPartida}/bomba/server` &&

                            dadosRecebidos.estado ===
                                "PARTIDA_FINALIZADA" &&

                            dadosRecebidos.dados?.idPartida ===
                                idPartida 
                        );
                    }
                );

                 const respostaUnity = await enviarEEsperarResposta(
                    mqttClient,

                    `bombexe/${idPartida}/server/unity`,

                    {
                        estado: "FIM_DE_JOGO",
                        dados: dadosUnity
                    },

                    (topicRecebido, dadosRecebidos) => {

                        return (
                            topicRecebido ===
                                `bombexe/${idPartida}/unity/server` &&

                            dadosRecebidos.estado ===
                                "FIM_DE_JOGO" &&

                            dadosRecebidos.dados?.idPartida ===
                                idPartida
                        );
                    }
                );

            } catch (error) {

                console.error(
                `Erro ao finalizar a partida ${idPartida}:`,
                error
            );

            }

            
        }
        catch (error) {
            console.error(
                "Erro ao processar mensagem da Bomba:",
                error.message
            );
        }
    }
}

function formatarDataParaUnity(data) {
    const d = new Date(data);

    const dia = String(d.getDate()).padStart(2, "0");
    const mes = String(d.getMonth() + 1).padStart(2, "0");
    const ano = d.getFullYear();

    const hora = String(d.getHours()).padStart(2, "0");
    const minuto = String(d.getMinutes()).padStart(2, "0");

    return `${dia}-${mes}-${ano} ${hora}:${minuto}`;
}

module.exports = {
    handleBombaMessage
};