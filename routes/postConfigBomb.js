const express = require("express");
const router = express.Router();

const { getDb } = require("../database/mongodb.js");
const { mqttClient } = require("../mqtt/mqtt-client.js");
const { enviarEEsperarResposta } = require("../mqtt/mqtt-request.js");
const { v4: uuidv4 } = require("uuid");
const axios = require("axios");
const { OAuth2Client } = require("google-auth-library");
const client = new OAuth2Client();
const audience = process.env.GOOGLE_CLIENT_ID.split(" ");

const configBombSchema = require("../schemas/configBombSchema.js");

router.post("/postConfigBomb", async (req, res) => {
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
                "https://feira-de-jogos.dev.br/api/v2/login",
                {
                    token: req.token
                },
                {
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

        const { error, value } = configBombSchema.validate(req.body);

        if (error) {
            return res.status(400).json({
                erro: error.details[0].message
            });
        }


        const {
            estado,
            dados
        } = value;

        const {
            idPartida,
            numeroDeFios,
            fios
        } = dados;

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


        // ==========================================
        // VERIFICAR BOMBA
        // ==========================================

        if (!partida.dispositivos?.bomba?.conectado) {

            return res.status(409).json({
                erro: "A Bomba ainda não confirmou a conexão"
            });

        }


        // ==========================================
        // VERIFICAR UNITY
        // ==========================================

        if (!partida.dispositivos?.unity?.conectado) {

            return res.status(409).json({
                erro: "A Unity ainda não confirmou a conexão"
            });

        }


        // ==========================================
        // VERIFICAR ESTADO DA PARTIDA
        // ==========================================

        if (partida.estado !== "AGUARDANDO_PARTIDA") {

            return res.status(409).json({
                erro: "A partida não está disponível para configuração da Bomba"
            });

        }
        console.log("Codigo continua")

        // ==========================================
        // BLOQUEAR CONFIGURAÇÕES SIMULTÂNEAS
        // ==========================================

        const bloqueio = await db.collection("partidas").updateOne(
            {
                _id: idPartida,
                estado: "AGUARDANDO_PARTIDA"
            },
            {
                $set: {
                    estado: "CONFIGURANDO_BOMBA"
                }
            }
        );

        if (bloqueio.modifiedCount === 0) {

            return res.status(409).json({
                erro: "A configuração da Bomba já está em andamento ou já foi realizada"
            });

        }


        // ==========================================
        // GERAR UUID
        // ==========================================

        const uuid = uuidv4();


        // ==========================================
        // ENVIAR CONFIGURAÇÃO PARA A BOMBA
        // ==========================================

        try {

            const respostaBomba = await enviarEEsperarResposta(
                mqttClient,
                `bombexe/${idPartida}/server/bomba`,

                {
                    estado: "CONFIGURAR_FIOS",

                    dados: {
                        idPartida: idPartida,
                        numeroDeFios: numeroDeFios,
                        fios: fios
                    }
                },

                (topicRecebido, dadosRecebidos) => {

                    return (
                        topicRecebido ===
                            `bombexe/${idPartida}/bomba/server` &&

                        dadosRecebidos.estado ===
                            "AGUARDANDO_JOGADORES" &&

                        dadosRecebidos.dados?.idPartida ===
                            idPartida
                    );

                }
            );


            console.log(
                "Bomba confirmou a configuração:",
                respostaBomba
            );


            // ==========================================
            // SALVAR CONFIGURAÇÃO NO MONGODB
            // ==========================================

            await db.collection("partidas").updateOne(
                {
                    _id: idPartida,
                    estado: "CONFIGURANDO_BOMBA"
                },
                {
                    $set: {
                        "bomba.puzzles.fios.numeroDeFios": numeroDeFios,
                        "bomba.puzzles.fios.fios": fios,

                        uuid: uuid,

                        estado: "AGUARDANDO_JOGADORES"
                    }
                }
            );


        } catch (error) {

            // ==========================================
            // BOMBA NÃO CONFIRMOU
            // ==========================================

            await db.collection("partidas").updateOne(
                {
                    _id: idPartida,
                    estado: "CONFIGURANDO_BOMBA"
                },
                {
                    $set: {
                        estado: "AGUARDANDO_PARTIDA"
                    }
                }
            );

            throw error;
        }


        // ==========================================
        // RESPONDER AO ADMIN
        // ==========================================

        return res.status(200).json({

            estado: "AGUARDANDO_JOGADORES",

            dados: {
                idPartida: idPartida,
                uuid: uuid
            }

        });


    } catch (error) {

        console.error(
            `Erro ao configurar a Bomba da partida ${idPartida}:`,
            error
        );

        return res.status(500).json({
            erro: "Erro ao configurar a Bomba"
        });

    }

});


module.exports = router;