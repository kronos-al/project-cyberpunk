const express = require("express");
const router = express.Router();

const { getDb } = require("../database/mongodb.js");

const addPlayersSchema = require("../schemas/addPlayersSchema.js");

const { mqttClient } = require("../mqtt/mqtt-client.js");
const { enviarEEsperarResposta } = require("../mqtt/mqtt-request.js");

const { exigirOperador } = require("../middlewares/auth-operador.js");
const { buscarUsuario, ErroFeira } = require("../utils/getUsers.js");


router.post("/postAddPlayer", exigirOperador, async (req, res) => {
    // Fora do try para o catch conseguir usar no log
    let idPartida;

    try {
        // ==========================================
        // VALIDAÇÃO
        // ==========================================

        const { error, value } = addPlayersSchema.validate(req.body);

        if (error) {
            return res.status(400).json({
                erro: error.details[0].message
            });
        }

        const { estado, dados } = value;
        idPartida = dados.idPartida;

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

        if (partida.estado !== "AGUARDANDO_JOGADORES") {
            console.error(
                `Partida ${idPartida} não está no estado "AGUARDANDO_JOGADORES".`
            );
            return res.status(409).json({
                erro: `A partida não está aguardando jogadores (estado atual: ${partida.estado}).`
            });
        }

        // ==========================================
        // VALIDAR JOGADORES NA FEIRA DE JOGOS
        // ==========================================

        let ede, eit;

        try {
            [ede, eit] = await Promise.all([
                buscarUsuario(req.token, dados.ede, "EDE"),
                buscarUsuario(req.token, dados.eit, "EIT")
            ]);
        } catch (err) {
            if (err instanceof ErroFeira) {
                return res.status(err.status).json({ erro: err.message });
            }
            throw err;
        }

        console.log("EDE validado:", ede);
        console.log("EIT validado:", eit);

        // ==========================================
        // SALVAR JOGADORES NO BANCO
        // (a guarda de estado impede dois cadastros simultâneos)
        // ==========================================

        const salvamento = await db.collection("partidas").updateOne(
            {
                _id: idPartida,
                estado: "AGUARDANDO_JOGADORES"
            },
            {
                $set: {
                    "jogadores.EDE": ede,
                    "jogadores.EIT": eit,
                    estado: "ADICIONAR_JOGADORES"
                }
            }
        );

        if (salvamento.modifiedCount === 0) {
            return res.status(409).json({
                erro: "Os jogadores desta partida já estão sendo adicionados."
            });
        }

        // ==========================================
        // AVISAR A UNITY
        // ==========================================

        try {
            const respostaUnity = await enviarEEsperarResposta(
                mqttClient,
                `bombexe/${idPartida}/server/unity`,

                {
                    estado: estado,

                    dados: {
                        idPartida: idPartida,
                        EDE: ede.nome,
                        EIT: eit.nome
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
                "Unity confirmou a adição de jogadores:",
                respostaUnity
            );
        } catch (err) {
            // A Unity não respondeu: desfaz o salvamento para o admin tentar de novo.
            // A guarda de estado evita desfazer se a partida já avançou.
            await db.collection("partidas").updateOne(
                {
                    _id: idPartida,
                    estado: "ADICIONAR_JOGADORES"
                },
                {
                    $set: {
                        estado: "AGUARDANDO_JOGADORES",
                        "jogadores.EDE": { id: null, nome: null },
                        "jogadores.EIT": { id: null, nome: null }
                    }
                }
            );

            throw err;
        }

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