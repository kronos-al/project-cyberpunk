const axios = require("axios");
const { OAuth2Client } = require("google-auth-library");

const client = new OAuth2Client();
const audience = process.env.GOOGLE_CLIENT_ID.split(" ");

// Cache curto para não chamar a Feira de Jogos a cada request
const CACHE_TTL_MS = 60 * 1000;
const cache = new Map();

setInterval(() => {
    const agora = Date.now();
    for (const [token, item] of cache) {
        if (item.expiraEm <= agora) cache.delete(token);
    }
}, CACHE_TTL_MS).unref();

/**
 * Exige token Google válido + usuário operador na Feira de Jogos.
 * Depende de req.token.
 * Em caso de sucesso preenche:
 *   req.operador       -> user retornado pela Feira de Jogos
 *   req.googlePayload  -> payload do token Google (substitui o antigo "payload")
 *
 * Em caso de token expirado responde 401 com { codigo: "TOKEN_EXPIRADO" },
 * para o front renovar o token e repetir a requisição.
 */
async function exigirOperador(req, res, next) {
    const token = req.token;

    if (!token) {
        return res.status(401).json({
            erro: "Token não informado.",
            codigo: "TOKEN_AUSENTE",
        });
    }

    const emCache = cache.get(token);
    if (emCache && emCache.expiraEm > Date.now()) {
        req.operador = emCache.user;
        req.googlePayload = emCache.payload;
        return next();
    }

    // 1) Validar token no Google
    let payload;
    try {
        const ticket = await client.verifyIdToken({ audience, idToken: token });
        payload = ticket.getPayload();
    } catch (err) {
        const expirado = /too late|expired/i.test(err.message);

        if (!expirado) console.error("Token do Google inválido:", err.message);

        return res.status(401).json({
            erro: expirado ? "Token expirado." : "Token inválido.",
            codigo: expirado ? "TOKEN_EXPIRADO" : "TOKEN_INVALIDO",
        });
    }

    // 2) Validar usuário na Feira de Jogos
    try {
        const resposta = await axios.post(
            "https://feira-de-jogos.dev.br/api/v2/login",
            {},
            {
                headers: { Authorization: `Bearer ${token}` },
                timeout: 10000,
            }
        );

        const { user, operator } = resposta.data;

        if (!user || !operator) {
            return res.status(403).json({
                erro: "Acesso negado. Apenas operadores podem acessar.",
                codigo: "NAO_OPERADOR",
            });
        }

        // O cache nunca vive além da expiração do próprio token
        const expiraEm = Math.min(
            Date.now() + CACHE_TTL_MS,
            payload.exp * 1000
        );
        cache.set(token, { user, payload, expiraEm });

        req.operador = user;
        req.googlePayload = payload;
        return next();
    } catch (err) {
        console.error(
            "Erro ao validar usuário na Feira de Jogos:",
            err.response?.data || err.message
        );

        if (err.response?.status === 401 || err.response?.status === 403) {
            return res.status(err.response.status).json({
                erro: "Usuário não autorizado.",
                codigo: "NAO_AUTORIZADO",
            });
        }

        return res.status(502).json({
            erro: "Não foi possível validar o usuário na Feira de Jogos.",
            codigo: "FEIRA_INDISPONIVEL",
        });
    }
}

module.exports = { exigirOperador };