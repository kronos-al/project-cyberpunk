const express = require("express");
const router = express.Router();

const { getDb } = require("../database/mongodb.js");

const addPlayersSchema = require("../schemas/addPlayersSchema.js");

const { mqttClient } = require("../mqtt/mqtt-client.js");
const { enviarEEsperarResposta } = require("../mqtt/mqtt-request.js");

const axios = require("axios");
const { OAuth2Client } = require("google-auth-library");
const client = new OAuth2Client();
const audience = process.env.GOOGLE_CLIENT_ID.split(" ");

router.post("/postAddPlayer", async (req, res) => {
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
        // VALIDAÇÃO
        // ==========================================


        const { error, value } = addPlayersSchema.validate(req.body);

        if (error) {
            return res.status(400).json({
                erro: error.details[0].message
            });
        }


        const { estado, dados: { idPartida } } = value;
    
    

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
            return res.status(404).json({
                erro: "Partida não encontrada"
            });
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