const express = require("express");
const router = express.Router();

const { getDb } = require("../database/mongodb.js");
const { mqttClient } = require("../mqtt/mqtt-client.js");
const { enviarEEsperarResposta } = require("../mqtt/mqtt-request.js");
const { v4: uuidv4 } = require("uuid");

const configBombSchema = require("../schemas/configBombSchema.js");

router.post("/postConfigBomb", async (req, res) => {

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

        if (partida.estado !== "Aguardando Partida") {

            return res.status(409).json({
                erro: "A partida não está disponível para configuração da Bomba"
            });

        }


        // ==========================================
        // BLOQUEAR CONFIGURAÇÕES SIMULTÂNEAS
        // ==========================================

        const bloqueio = await db.collection("partidas").updateOne(
            {
                _id: idPartida,
                estado: "Aguardando Partida"
            },
            {
                $set: {
                    estado: "Configurando Bomba"
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
                    estado: "Configurar Fios",

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
                            "Aguardando Jogadores" &&

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
                    estado: "Configurando Bomba"
                },
                {
                    $set: {
                        "bomba.puzzles.fios.numeroDeFios": numeroDeFios,
                        "bomba.puzzles.fios.fios": fios,

                        uuid: uuid,

                        estado: "Aguardando Jogadores"
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
                    estado: "Configurando Bomba"
                },
                {
                    $set: {
                        estado: "Aguardando Partida"
                    }
                }
            );

            throw error;
        }


        // ==========================================
        // RESPONDER AO ADMIN
        // ==========================================

        return res.status(200).json({

            estado: "Aguardando Jogadores",

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