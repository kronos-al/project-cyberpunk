const express = require("express");
const router = express.Router();

const { getDb } = require("../database/mongodb.js");
const { getNextSequence } = require("../database/counter.js");
const { mqttClient } = require("../mqtt/mqtt-client.js");
const { enviarEEsperarResposta } = require("../mqtt/mqtt-request.js");

router.post("/postWaitingMatch", async (req, res) => {

    try {

        // Gera o próximo ID da partida
        const idPartida = await getNextSequence("partidas");

        // Acessa o banco
        const db = getDb();

        // Cria a partida
        const novaPartida = {
            _id: idPartida,
            uuid: null,

            estado: "AGUARDANDO_PARTIDA",

            jogadores: {
                EDE: {
                    id: null,
                    nome: null
                },
                EIT: { 
                     id: null,
                    nome: null
                },
            },

            dispositivos: {
                bomba: {
                    conectado: false
                },
                unity: {
                    conectado: false
                }
            },

            bomba: {
                erros: 0,
                numeroDeSerie: null,
                tempo: null,

                puzzles: {
                    chaveDeInicializacao: {
                        resolvido: false
                    },

                    ajusteDeSintonizacao: {
                        resolvido: false
                    },

                    bussolaDeLeds: {
                        resolvido: false
                    },

                    labirinto: {
                        resolvido: false
                    },

                    fios: {
                        resolvido: false,
                        numeroDeFios: null,
                        fios: null
                    }
                }
            },

            resultado: null,

            createdAt: new Date(),
            startedAt: null,
            finishedAt: null
        };

        // Salva no MongoDB
        await db.collection("partidas").insertOne(novaPartida);

        // Retorna o ID para quem fez a requisição
        res.status(200).json({
            id_partida: idPartida
        });

        try {

            const respostaBomba = await enviarEEsperarResposta(
                mqttClient,
                `bombexe/${idPartida}/server/bomba`,

            {
                estado: "AGUARDANDO_PARTIDA",
                dados: {
                    idPartida: idPartida
                }
            },

            (topicRecebido, dados) => {
                return (
                    topicRecebido === `bombexe/${idPartida}/bomba/server` &&
                    dados.estado === "AGUARDANDO_PARTIDA" &&
                    dados.dados?.idPartida === idPartida
                );
            }
        );

            console.log("Bomba confirmou a partida:", respostaBomba);
            await db.collection("partidas").updateOne(
                { _id: idPartida },
                {
                    $set: {
                        "dispositivos.bomba.conectado": true
                    }
                }
            );

        } catch (error) {

            console.error(
                `Erro ao iniciar comunicação com a Bomba da partida ${idPartida}:`,
                error.message
            );

        }

        try {

            const respostaUnity = await enviarEEsperarResposta(
                mqttClient,
                `bombexe/${idPartida}/server/unity`,

                {
                    estado: "AGUARDANDO_PARTIDA",
                    dados: {
                        idPartida: idPartida
                    }
                },

                (topicRecebido, dados) => {
                    return (
                        topicRecebido === `bombexe/${idPartida}/unity/server` &&
                        dados.estado === "AGUARDANDO_PARTIDA" &&
                        dados.dados?.idPartida === idPartida
                    );
                }
            );

            console.log("Unity confirmou a partida:", respostaUnity);

            await db.collection("partidas").updateOne(
                { _id: idPartida },
                {
                    $set: {
                        "dispositivos.unity.conectado": true
                    }
                }
            );

        } catch (error) {

            console.error(
                `Erro ao iniciar comunicação com a Unity da partida ${idPartida}:`,
                error.message
            );

        }

    } catch (error) {

        console.error("Erro ao criar partida:", error);

        res.status(500).json({
            erro: "Erro ao criar partida"
        });


    }

});

module.exports = router;