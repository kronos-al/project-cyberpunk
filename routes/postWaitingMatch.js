const express = require("express");
const router = express.Router();

const { getDb } = require("../database/mongodb.js");
const { getNextSequence } = require("../database/counter.js");
const { mqttClient } = require("../mqtt/mqtt-client.js");
const { enviarEEsperarResposta } = require("../mqtt/mqtt-request.js");

router.post("/postWaitingMatch", async (req, res) => {

    try {

        // ==========================================
        // GERAR ID
        // ==========================================

        const idPartida = await getNextSequence("partidas");

        // ==========================================
        // ACESSAR BANCO
        // ==========================================

        const db = getDb();

        // ==========================================
        // CRIAR PARTIDA
        // ==========================================

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
                }
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

        await db.collection("partidas").insertOne(novaPartida);

        // ==========================================
        // COMUNICAR COM A BOMBA
        // ==========================================

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

        console.log(
            "Bomba confirmou a partida:",
            respostaBomba
        );

        await db.collection("partidas").updateOne(
            { _id: idPartida },
            {
                $set: {
                    "dispositivos.bomba.conectado": true
                }
            }
        );

        // ==========================================
        // COMUNICAR COM A UNITY
        // ==========================================

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

        console.log(
            "Unity confirmou a partida:",
            respostaUnity
        );

        await db.collection("partidas").updateOne(
            { _id: idPartida },
            {
                $set: {
                    "dispositivos.unity.conectado": true
                }
            }
        );

        // ==========================================
        // TUDO DEU CERTO
        // ==========================================

        return res.status(200).json({
            estado: "AGUARDANDO_PARTIDA",

            dados: {
                idPartida: idPartida
            }
        });

    } catch (error) {

        console.error(
            `Erro ao iniciar partida:`,
            error
        );

        // ==========================================
        // ERRO
        // ==========================================

        return res.status(500).json({
            erro: "Erro ao iniciar partida",
            mensagem: error.message
        });
    }
});

module.exports = router;