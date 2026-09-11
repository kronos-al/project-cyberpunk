const express = require("express");
const router = express.Router();

const { getDb } = require("../database/mongodb.js");

const addPlayersSchema = require("../schemas/addPlayersSchema.js");

const { mqttClient } = require("../mqtt/mqtt-client.js");
const { enviarEEsperarResposta } = require("../mqtt/mqtt-request.js");

router.post("/postAddPlayer", async (req, res) => {

    // ==========================================
    // VALIDAÇÃO
    // ==========================================


    const { error, value } = addPlayersSchema.validate(req.body);

   if (error) {
        return res.status(400).json({
            erro: error.details[0].message
        });
    }


    const { estado, dados: { idPartida } } = value;
    
    try {

            const db = getDb();

            // ==========================================
            // VERIFICAR PARTIDA
            // ==========================================

            const partida = await db.collection("partidas").findOne({
                _id: idPartida
            });

            if (!partida) {
                return res.status(404).json({
                    erro: "Partida não encontrada"
                });
            }

             /*
            * 5. Verificar se a partida está no estado correto
            */
            if (partida.estado !== "AGUARDANDO_JOGADORES") {
                console.error(
                    `Partida ${idPartida} não está no estado "AGUARDANDO_JOGADORES".`
                );
                return;
            }


            const respostaUnity = await enviarEEsperarResposta(
                mqttClient,
                `bombexe/${idPartida}/server/unity`,

                {
                    estado: estado,

                    dados: {
                        idPartida: idPartida
                    }
                },

                (topicRecebido, dadosRecebidos) => {

                    return (
                        topicRecebido ===
                            `bombexe/${idPartida}/unity/server` &&

                        dadosRecebidos.estado ===
                            "ADICIONAR_JOGADORES" &&

                        dadosRecebidos.dados?.idPartida ===
                            idPartida
                    );

                }
            );


            console.log(
                "Unity confirmou a configuração:",
                respostaUnity
            );

            // ==========================================
            // ATUALIZAR ESTADO DA PARTIDA
            // ==========================================

            await db.collection("partidas").updateOne(
                { _id: idPartida },
                {
                    $set: {
                        estado: "ADICIONAR_JOGADORES"
                    }
                }
            );

            // ==========================================
            // RESPONDER AO ADMIN
            // ==========================================

            return res.status(200).json({

                estado: "ADICIONAR_JOGADORES",

                dados: {
                    idPartida: idPartida
                }

            });
        } catch (error) {

            console.error(
                `Erro ao adicionar jogadores na partida ${idPartida}:`,
                error
            );

            return res.status(500).json({
                erro: "Erro ao adicionar jogadores"
            });

        }
    });


module.exports = router;