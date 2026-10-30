// ==========================================
// CONSTANTES (ajuste aqui se necessário)
// ==========================================

const ESTADO_FINALIZADO = "FIM_DE_JOGO";

// "resultado" pode ser "VITORIA" ou "DERROTA"
const RESULTADO_VITORIA = "VITORIA";

const PUZZLES = [
    "chaveDeInicializacao",
    "ajusteDeSintonizacao",
    "bussolaDeLeds",
    "labirinto",
    "fios",
];

// ==========================================
// ERRO HTTP
// ==========================================

class ErroHttp extends Error {
    constructor(status, mensagem) {
        super(mensagem);
        this.status = status;
    }
}

// Wrapper para rotas async com tratamento de erro padronizado
function handler(fn) {
    return async (req, res) => {
        try {
            await fn(req, res);
        } catch (err) {
            if (err instanceof ErroHttp) {
                return res.status(err.status).json({ erro: err.message });
            }
            console.error(`Erro em ${req.method} ${req.originalUrl}:`, err);
            return res.status(500).json({ erro: "Erro interno do servidor" });
        }
    };
}

// ==========================================
// HELPERS DE FILTRO
// ==========================================

// O id do jogador pode estar salvo como string ou número
function variantesId(id) {
    const variantes = [String(id)];
    if (/^\d+$/.test(String(id))) variantes.push(Number(id));
    return variantes;
}

function parseData(valor, nome, fimDoDia = false) {
    const somenteData = /^\d{4}-\d{2}-\d{2}$/.test(valor);
    const data = new Date(somenteData ? `${valor}T00:00:00-03:00` : valor);

    if (isNaN(data.getTime())) {
        throw new ErroHttp(400, `Parâmetro "${nome}" inválido. Use YYYY-MM-DD ou ISO 8601.`);
    }

    // "ate=2026-10-28" deve incluir o dia inteiro
    if (fimDoDia && somenteData) {
        data.setDate(data.getDate() + 1);
        return { data, exclusivo: true };
    }

    return { data, exclusivo: false };
}

/**
 * Monta o filtro do MongoDB a partir da query string.
 * Query suportada: estado (pode ser lista separada por vírgula), resultado,
 * jogador (id), de, ate (sobre createdAt).
 */
function construirFiltro(query, { estado = true, jogador = true } = {}) {
    const filtro = {};

    if (estado) {
        if (query.estado) {
            const estados = String(query.estado).split(",").map((e) => e.trim());
            filtro.estado = estados.length > 1 ? { $in: estados } : estados[0];
        }
        if (query.resultado) filtro.resultado = String(query.resultado);
    }

    if (jogador && query.jogador) {
        const ids = variantesId(query.jogador);
        filtro.$or = [
            { "jogadores.EDE.id": { $in: ids } },
            { "jogadores.EIT.id": { $in: ids } },
        ];
    }

    // Busca por nome (parcial, sem diferenciar maiúsculas) em EDE ou EIT
    if (jogador && query.nome && String(query.nome).trim()) {
        const rx = new RegExp(String(query.nome).trim().replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "i");
        filtro.$and = [
            ...(filtro.$and || []),
            { $or: [{ "jogadores.EDE.nome": rx }, { "jogadores.EIT.nome": rx }] },
        ];
    }

    if (query.de || query.ate) {
        filtro.createdAt = {};

        if (query.de) {
            filtro.createdAt.$gte = parseData(String(query.de), "de").data;
        }
        if (query.ate) {
            const { data, exclusivo } = parseData(String(query.ate), "ate", true);
            filtro.createdAt[exclusivo ? "$lt" : "$lte"] = data;
        }
    }

    return filtro;
}

function inteiroPositivo(valor, padrao, max = Infinity) {
    const n = parseInt(valor, 10);
    if (isNaN(n) || n < 1) return padrao;
    return Math.min(n, max);
}

module.exports = {
    ESTADO_FINALIZADO,
    RESULTADO_VITORIA,
    PUZZLES,
    ErroHttp,
    handler,
    variantesId,
    construirFiltro,
    inteiroPositivo,
};