const express = require("express");
const router = express.Router();

const { getDb } = require("../database/mongodb.js");
const { exigirOperador } = require("../middlewares/auth-operador.js");
const {
    ErroHttp,
    handler,
    construirFiltro,
    inteiroPositivo,
} = require("../utils/filtros.js");

router.use(exigirOperador);

// ==========================================
// GET /partidas
// Query: estado, resultado, jogador, de, ate, pagina, limite, ordem (asc|desc)
// ==========================================

router.get(
    "/",
    handler(async (req, res) => {
        const db = getDb();
        const filtro = construirFiltro(req.query);

        const pagina = inteiroPositivo(req.query.pagina, 1);
        const limite = inteiroPositivo(req.query.limite, 20, 100);
        const ordem = req.query.ordem === "asc" ? 1 : -1;

        const colecao = db.collection("partidas");

        const [dados, total] = await Promise.all([
            colecao
                .find(filtro, {
                    projection: {
                        uuid: 1,
                        estado: 1,
                        resultado: 1,
                        jogadores: 1,
                        "bomba.erros": 1,
                        "bomba.tempo": 1,
                        "bomba.numeroDeSerie": 1,
                        createdAt: 1,
                        startedAt: 1,
                        finishedAt: 1,
                    },
                })
                .sort({ createdAt: ordem, _id: ordem })
                .skip((pagina - 1) * limite)
                .limit(limite)
                .toArray(),
            colecao.countDocuments(filtro),
        ]);

        res.json({
            dados,
            paginacao: {
                pagina,
                limite,
                total,
                totalPaginas: Math.ceil(total / limite),
            },
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
