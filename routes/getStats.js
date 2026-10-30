const express = require("express");
const router = express.Router();

const { getDb } = require("../database/mongodb.js");
const { exigirOperador } = require("../middlewares/auth-operador.js");
const {
    ESTADO_FINALIZADO,
    RESULTADO_VITORIA,
    PUZZLES,
    ErroHttp,
    handler,
    variantesId,
    construirFiltro,
    inteiroPositivo,
} = require("../utils/filtros.js");

router.use(exigirOperador);

const TIMEZONE = "America/Sao_Paulo";

// ==========================================
// EXPRESSÕES REAIS DE AGREGAÇÃO
// ==========================================

const finalizada = { $eq: ["$estado", ESTADO_FINALIZADO] };
const venceu = { $eq: ["$resultado", RESULTADO_VITORIA] };

const umSe = (condicao) => ({ $cond: [condicao, 1, 0] });

// duração (ms) = finishedAt - startedAt, só para partidas finalizadas
const duracaoMs = {
    $cond: [
        {
            $and: [
                finalizada,
                { $ne: [{ $ifNull: ["$startedAt", null] }, null] },
                { $ne: [{ $ifNull: ["$finishedAt", null] }, null] },
            ],
        },
        { $subtract: ["$finishedAt", "$startedAt"] },
        null,
    ],
};

const taxa = (numerador, denominador) => ({
    $cond: [
        { $gt: [denominador, 0] },
        { $round: [{ $divide: [numerador, denominador] }, 4] },
        null,
    ],
});

// Filtro base das análises: só partidas finalizadas, respeitando de/ate/jogador
function filtroFinalizadas(query, opcoes) {
    return { ...construirFiltro(query, { estado: false, ...opcoes }), estado: ESTADO_FINALIZADO };
}

// Transforma jogadores EDE/EIT em linhas (uma por jogador por partida)
const estagiosParticipantes = [
    {
        $project: {
            resultado: 1,
            erros: "$bomba.erros",
            duracao: duracaoMs,
            participantes: [
                { papel: "EDE", id: "$jogadores.EDE.id", nome: "$jogadores.EDE.nome" },
                { papel: "EIT", id: "$jogadores.EIT.id", nome: "$jogadores.EIT.nome" },
            ],
        },
    },
    { $unwind: "$participantes" },
    { $match: { "participantes.id": { $ne: null } } },
];

// ==========================================
// GET /stats/resumo
// Query: de, ate, jogador
// ==========================================

router.get(
    "/resumo",
    handler(async (req, res) => {
        const filtro = construirFiltro(req.query, { estado: false });

        const [resumo] = await getDb()
            .collection("partidas")
            .aggregate([
                { $match: filtro },
                {
                    $group: {
                        _id: null,
                        totalPartidas: { $sum: 1 },
                        finalizadas: { $sum: umSe(finalizada) },
                        vitorias: { $sum: umSe({ $and: [finalizada, venceu] }) },
                        tempoMedioMs: { $avg: duracaoMs },
                        errosMedios: {
                            $avg: { $cond: [finalizada, "$bomba.erros", null] },
                        },
                    },
                },
                {
                    $project: {
                        _id: 0,
                        totalPartidas: 1,
                        finalizadas: 1,
                        emAndamentoOuAbandonadas: { $subtract: ["$totalPartidas", "$finalizadas"] },
                        vitorias: 1,
                        derrotas: { $subtract: ["$finalizadas", "$vitorias"] },
                        taxaVitoria: taxa("$vitorias", "$finalizadas"),
                        taxaDerrota: taxa({ $subtract: ["$finalizadas", "$vitorias"] }, "$finalizadas"),
                        tempoMedioMs: { $round: ["$tempoMedioMs", 0] },
                        errosMedios: { $round: ["$errosMedios", 2] },
                    },
                },
            ])
            .toArray();

        res.json(
            resumo || {
                totalPartidas: 0,
                finalizadas: 0,
                emAndamentoOuAbandonadas: 0,
                vitorias: 0,
                derrotas: 0,
                taxaVitoria: null,
                taxaDerrota: null,
                tempoMedioMs: null,
                errosMedios: null,
            }
        );
    })
);

// ==========================================
// GET /stats/por-dia
// Query: de, ate, jogador
// ==========================================

router.get(
    "/por-dia",
    handler(async (req, res) => {
        const filtro = construirFiltro(req.query, { estado: false });

        const dados = await getDb()
            .collection("partidas")
            .aggregate([
                { $match: filtro },
                {
                    $group: {
                        _id: {
                            $dateToString: { format: "%Y-%m-%d", date: "$createdAt", timezone: TIMEZONE },
                        },
                        partidas: { $sum: 1 },
                        finalizadas: { $sum: umSe(finalizada) },
                        vitorias: { $sum: umSe({ $and: [finalizada, venceu] }) },
                    },
                },
                { $sort: { _id: 1 } },
                {
                    $project: {
                        _id: 0,
                        dia: "$_id",
                        partidas: 1,
                        finalizadas: 1,
                        vitorias: 1,
                        taxaSucesso: taxa("$vitorias", "$finalizadas"),
                    },
                },
            ])
            .toArray();

        res.json({ dados });
    })
);

// ==========================================
// GET /stats/puzzles
// Taxa de resolução por puzzle (partidas finalizadas)
// Query: de, ate, jogador
// ==========================================

router.get(
    "/puzzles",
    handler(async (req, res) => {
        const filtro = filtroFinalizadas(req.query);

        const [agg] = await getDb()
            .collection("partidas")
            .aggregate([
                { $match: filtro },
                {
                    $group: {
                        _id: null,
                        total: { $sum: 1 },
                        ...Object.fromEntries(
                            PUZZLES.map((p) => [
                                p,
                                { $sum: umSe({ $eq: [`$bomba.puzzles.${p}.resolvido`, true] }) },
                            ])
                        ),
                    },
                },
            ])
            .toArray();

        if (!agg) return res.json({ totalPartidas: 0, puzzles: [], maisDificil: null });

        const puzzles = PUZZLES.map((p) => ({
            puzzle: p,
            resolvidos: agg[p],
            naoResolvidos: agg.total - agg[p],
            taxaResolucao: Math.round((agg[p] / agg.total) * 10000) / 10000,
        })).sort((a, b) => a.taxaResolucao - b.taxaResolucao); // mais difícil primeiro

        res.json({
            totalPartidas: agg.total,
            maisDificil: puzzles[0].puzzle,
            puzzles,
        });
    })
);

// ==========================================
// GET /stats/erros
// Distribuição de erros por partida (finalizadas)
// Query: de, ate, jogador
// ==========================================

router.get(
    "/erros",
    handler(async (req, res) => {
        const filtro = filtroFinalizadas(req.query);

        const distribuicao = await getDb()
            .collection("partidas")
            .aggregate([
                { $match: filtro },
                {
                    $group: {
                        _id: { $ifNull: ["$bomba.erros", 0] },
                        partidas: { $sum: 1 },
                        vitorias: { $sum: umSe(venceu) },
                    },
                },
                { $sort: { _id: 1 } },
                {
                    $project: {
                        _id: 0,
                        erros: "$_id",
                        partidas: 1,
                        vitorias: 1,
                        taxaVitoria: taxa("$vitorias", "$partidas"),
                    },
                },
            ])
            .toArray();

        const total = distribuicao.reduce((s, d) => s + d.partidas, 0);
        const somaErros = distribuicao.reduce((s, d) => s + d.erros * d.partidas, 0);

        res.json({
            totalPartidas: total,
            errosMedios: total ? Math.round((somaErros / total) * 100) / 100 : null,
            distribuicao: distribuicao.map((d) => ({
                ...d,
                percentual: Math.round((d.partidas / total) * 10000) / 10000,
            })),
        });
    })
);

// ==========================================
// GET /stats/jogadores
// Ranking. Query: de, ate, minPartidas, pagina, limite
// ==========================================

router.get(
    "/jogadores",
    handler(async (req, res) => {
        const filtro = filtroFinalizadas(req.query, { jogador: false });
        const minPartidas = inteiroPositivo(req.query.minPartidas, 1);
        const pagina = inteiroPositivo(req.query.pagina, 1);
        const limite = inteiroPositivo(req.query.limite, 20, 100);

        const [resultado] = await getDb()
            .collection("partidas")
            .aggregate([
                { $match: filtro },
                ...estagiosParticipantes,
                {
                    $group: {
                        _id: "$participantes.id",
                        nome: { $last: "$participantes.nome" },
                        partidas: { $sum: 1 },
                        vitorias: { $sum: umSe(venceu) },
                        tempoMedioMs: { $avg: "$duracao" },
                        errosMedios: { $avg: "$erros" },
                    },
                },
                { $match: { partidas: { $gte: minPartidas } } },
                {
                    $project: {
                        _id: 0,
                        id: "$_id",
                        nome: 1,
                        partidas: 1,
                        vitorias: 1,
                        derrotas: { $subtract: ["$partidas", "$vitorias"] },
                        taxaVitoria: taxa("$vitorias", "$partidas"),
                        tempoMedioMs: { $round: ["$tempoMedioMs", 0] },
                        errosMedios: { $round: ["$errosMedios", 2] },
                    },
                },
                { $sort: { vitorias: -1, taxaVitoria: -1, partidas: -1 } },
                {
                    $facet: {
                        dados: [{ $skip: (pagina - 1) * limite }, { $limit: limite }],
                        total: [{ $count: "n" }],
                    },
                },
            ])
            .toArray();

        const total = resultado.total[0]?.n || 0;

        res.json({
            dados: resultado.dados,
            paginacao: { pagina, limite, total, totalPaginas: Math.ceil(total / limite) },
        });
    })
);

// ==========================================
// GET /stats/jogadores/:id
// Desempenho individual + histórico
// Query: de, ate, historico (qtd de partidas recentes, padrão 20)
// ==========================================

router.get(
    "/jogadores/:id",
    handler(async (req, res) => {
        const db = getDb();
        const ids = variantesId(req.params.id);
        const limiteHistorico = inteiroPositivo(req.query.historico, 20, 100);

        const filtroJogador = construirFiltro(
            { ...req.query, jogador: req.params.id },
            { estado: false }
        );

        const [porPapel, historico] = await Promise.all([
            db
                .collection("partidas")
                .aggregate([
                    { $match: { ...filtroFinalizadas(req.query, { jogador: false }), ...{ $or: filtroJogador.$or } } },
                    ...estagiosParticipantes,
                    { $match: { "participantes.id": { $in: ids } } },
                    {
                        $group: {
                            _id: "$participantes.papel",
                            nome: { $last: "$participantes.nome" },
                            partidas: { $sum: 1 },
                            vitorias: { $sum: umSe(venceu) },
                            tempoMedioMs: { $avg: "$duracao" },
                            errosMedios: { $avg: "$erros" },
                            // soma para recalcular médias gerais
                            somaTempo: { $sum: { $ifNull: ["$duracao", 0] } },
                            comTempo: { $sum: umSe({ $ne: [{ $ifNull: ["$duracao", null] }, null] }) },
                            somaErros: { $sum: { $ifNull: ["$erros", 0] } },
                        },
                    },
                ])
                .toArray(),
            db
                .collection("partidas")
                .find(filtroJogador, {
                    projection: {
                        estado: 1,
                        resultado: 1,
                        jogadores: 1,
                        "bomba.erros": 1,
                        createdAt: 1,
                        startedAt: 1,
                        finishedAt: 1,
                    },
                })
                .sort({ createdAt: -1 })
                .limit(limiteHistorico)
                .toArray(),
        ]);

        if (!porPapel.length && !historico.length) {
            throw new ErroHttp(404, "Jogador não encontrado.");
        }

        const soma = (campo) => porPapel.reduce((s, p) => s + p[campo], 0);
        const partidas = soma("partidas");
        const vitorias = soma("vitorias");

        const arred = (v, casas = 4) => (v == null ? null : Math.round(v * 10 ** casas) / 10 ** casas);
        const papel = (p) => {
            const r = porPapel.find((x) => x._id === p);
            return r
                ? {
                      partidas: r.partidas,
                      vitorias: r.vitorias,
                      taxaVitoria: arred(r.vitorias / r.partidas),
                      tempoMedioMs: arred(r.tempoMedioMs, 0),
                      errosMedios: arred(r.errosMedios, 2),
                  }
                : null;
        };

        res.json({
            id: req.params.id,
            nome: porPapel[0]?.nome ?? null,
            geral: {
                partidas,
                vitorias,
                derrotas: partidas - vitorias,
                taxaVitoria: partidas ? arred(vitorias / partidas) : null,
                tempoMedioMs: soma("comTempo") ? Math.round(soma("somaTempo") / soma("comTempo")) : null,
                errosMedios: partidas ? arred(soma("somaErros") / partidas, 2) : null,
            },
            porPapel: { EDE: papel("EDE"), EIT: papel("EIT") },
            historico,
        });
    })
);

module.exports = router;
