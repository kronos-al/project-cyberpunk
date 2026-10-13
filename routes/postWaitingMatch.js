const express = require("express");
const router = express.Router();

const { getDb } = require("../database/mongodb.js");
const { getNextSequence } = require("../database/counter.js");
const { mqttClient } = require("../mqtt/mqtt-client.js");
const { enviarEEsperarResposta } = require("../mqtt/mqtt-request.js");
const axios = require("axios");
const { OAuth2Client } = require("google-auth-library");
const client = new OAuth2Client();
const audience = process.env.GOOGLE_CLIENT_ID.split(" ");

router.post("/postWaitingMatch", async (req, res) => {
    let payload;

    try {
        try {
            const ticket = await client.verifyIdToken({
                audience,
                idToken: req.token,
            });

            payload = ticket.getPayload();

        } catch (err) {
            console.error("Token do Google inválido:", err);
            return res.sendStatus(401);
        }

        // ==========================================
        // VALIDAR USUÁRIO NA FEIRA DE JOGOS
        // ==========================================

        try {
            const resposta = await axios.post(
                'https://feira-de-jogos.dev.br/api/v2/login',
                {}, // O corpo (body) fica vazio, se a API só pedir o token no header
                {
                headers: {
                    'Authorization': `Bearer ${req.token}`
                },
                timeout: 10000
                }
            );

            const { user, operator } = resposta.data;

            // Verificar se o usuário existe e é operador
            if (!user || !operator) {
                return res.status(403).json({
                    erro: "Acesso negado. Apenas operadores podem criar partidas."
                });
            }

            console.log("Operador autenticado:", user);

        } catch (err) {
            console.error(
                "Erro ao validar usuário na Feira de Jogos:",
                err.response?.data || err.message
            );

            if (err.response?.status === 401 || err.response?.status === 403) {
                return res.status(err.response.status).json({
                    erro: "Usuário não autorizado."
                });
            }

            return res.status(502).json({
                erro: "Não foi possível validar o usuário na Feira de Jogos."
            });
        }

        // ==========================================
        // CONTINUAR COM A CRIAÇÃO DA PARTIDA
        // ==========================================

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