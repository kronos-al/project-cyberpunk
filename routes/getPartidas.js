const express = require("express");
const router = express.Router();

const { getDb } = require("../database/mongodb.js");
const { exigirOperador } = require("../middlewares/auth-operador.js");
const { ErroHttp, handler, construirFiltro, inteiroPositivo } = require("../utils/filtros.js");

router.use(exigirOperador);

const duracaoMs = {
    $cond: [
        {
            $and: [
                { $ne: [{ $ifNull: ["$startedAt", null] }, null] },
                { $ne: [{ $ifNull: ["$finishedAt", null] }, null] },
            ],
        },
        { $subtract: ["$finishedAt", "$startedAt"] },
        null,
    ],
};

const ORDENS = {
    recentes: { createdAt: -1, _id: -1 },
    antigas: { createdAt: 1, _id: 1 },
    rapidas: { duracaoMs: 1, _id: 1 },
    lentas: { duracaoMs: -1, _id: 1 },
    erros: { "bomba.erros": -1, _id: 1 },
};

// ==========================================
// GET /partidas
// Query: estado, resultado, jogador (id), nome, de, ate, pagina, limite,
//        ordenarPor (recentes|antigas|rapidas|lentas|erros)
// ==========================================
router.get(
    "/",
    handler(async (req, res) => {
        const filtro = construirFiltro(req.query);
        const pagina = inteiroPositivo(req.query.pagina, 1);
        const limite = inteiroPositivo(req.query.limite, 20, 100);

        const chave = ORDENS[req.query.ordenarPor]
            ? req.query.ordenarPor
            : req.query.ordem === "asc" ? "antigas" : "recentes";

        // Ordenar por duração só faz sentido para partidas com início e fim
        if (chave === "rapidas" || chave === "lentas") {
            filtro.startedAt = { $ne: null };
            filtro.finishedAt = { $ne: null };
        }

        const colecao = getDb().collection("partidas");

        const [dados, total] = await Promise.all([
            colecao
                .aggregate([
                    { $match: filtro },
                    { $addFields: { duracaoMs } },
                    { $sort: ORDENS[chave] },
                    { $skip: (pagina - 1) * limite },
                    { $limit: limite },
                    {
                        $project: {
                            uuid: 1, estado: 1, resultado: 1, jogadores: 1,
                            "bomba.erros": 1, "bomba.tempo": 1, "bomba.numeroDeSerie": 1,
                            createdAt: 1, startedAt: 1, finishedAt: 1, duracaoMs: 1,
                        },
                    },
                ])
                .toArray(),
            colecao.countDocuments(filtro),
        ]);

        res.json({
            dados,
            paginacao: { pagina, limite, total, totalPaginas: Math.ceil(total / limite) },
        });
    })
);

// ==========================================
// GET /partidas/:id
// ==========================================
router.get(
    "/:id",
    handler(async (req, res) => {
        const id = parseInt(req.params.id, 10);
        if (isNaN(id)) throw new ErroHttp(400, "ID de partida inválido.");

        const partida = await getDb().collection("partidas").findOne({ _id: id });
        if (!partida) throw new ErroHttp(404, "Partida não encontrada.");

        res.json(partida);
    })
);

module.exports = router;