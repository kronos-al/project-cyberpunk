const axios = require("axios");

// Ajuste se o caminho da rota na Feira de Jogos for diferente
const FEIRA_API = "https://feira-de-jogos.dev.br/api/v2";

// Logs de diagnóstico. Coloque false quando achar o problema.
const DEBUG = true;
const log = (...args) => DEBUG && console.log("[CREDITOS]", ...args);

// ==========================================
// TABELA DE PREMIAÇÃO (TJL)
// Cada faixa vai "até" X segundos; valores = [0 erros, 1 erro, 2 erros]
// ==========================================
const FAIXAS = [
    { ate: 120, valores: [700, 650, 600] },        // até 2min
    { ate: 180, valores: [550, 500, 450] },        // 2min01s a 3min
    { ate: 240, valores: [450, 400, 350] },        // 3min01s a 4min
    { ate: 300, valores: [350, 300, 300] },        // 4min01s a 5min
    { ate: Infinity, valores: [300, 250, 200] }    // acima de 5min
];

/**
 * Valor (TJL) que CADA jogador recebe.
 * Bomba explodida (qualquer resultado diferente de VITORIA) = 0.
 */
function calcularCreditos({ resultado, tempo, erros }) {
    log("calcular - entrada:", {
        resultado,
        tempo, tipoTempo: typeof tempo,
        erros, tipoErros: typeof erros
    });

    if (resultado !== "VITORIA") {
        log(`calcular - resultado "${resultado}" diferente de "VITORIA" -> 0 TJL`);
        return 0;
    }

    // Aceita número ou texto numérico ("120"); ausente/inválido vira o pior caso
    const bruto = (tempo === null || tempo === undefined || tempo === "") ? NaN : Number(tempo);
    const segundos = Number.isFinite(bruto) ? bruto : Infinity;

    if (!Number.isFinite(bruto)) {
        log(`calcular - AVISO: tempo inválido (${tempo}); usando a faixa mais lenta`);
    } else if (segundos > 3600) {
        log(`calcular - AVISO: tempo = ${segundos}; parece estar em milissegundos, não em segundos`);
    }

    const faixa = FAIXAS.find((f) => segundos <= f.ate);

    // Vitória só acontece com 0, 1 ou 2 erros (3 = explosão)
    const indice = Math.min(Math.max(Number(erros) || 0, 0), 2);
    const valor = faixa.valores[indice];

    log(`calcular - segundos=${segundos} | faixa até ${faixa.ate}s | índice de erros=${indice} | valor=${valor} TJL`);

    return valor;
}

// Chama a rota gameCredit da Feira de Jogos. Retorna o operationId.
async function creditarJogador(userId, price) {
    const url = `${FEIRA_API}/gameCredit`;

    log(`POST ${url}`, { userId, price, FEIRA_SECRET_definido: Boolean(process.env.FEIRA_SECRET) });

    try {
        const resposta = await axios.post(
            url,
            { userId, price },
            {
                headers: { Authorization: `Bearer ${process.env.FEIRA_SECRET}` },
                timeout: 10000
            }
        );

        log(`resposta da Feira (userId ${userId}): HTTP ${resposta.status}`, JSON.stringify(resposta.data));

        return resposta.data.operationId;
    } catch (err) {
        log(
            `erro da Feira (userId ${userId}): HTTP ${err.response?.status} |`,
            `corpo=${JSON.stringify(err.response?.data)} | msg=${err.message}`
        );
        throw err;
    }
}

/**
 * Credita EDE e EIT ao fim da partida e registra o resultado na partida
 * (campo "creditos"), para dar para auditar e reprocessar falhas.
 * Nunca lança erro: uma falha aqui não pode atrapalhar o fim de jogo.
 */
async function creditarPartida(db, idPartida, jogadores, dadosFim) {
    log(`===== partida ${idPartida} =====`);
    log("dados do fim de jogo:", JSON.stringify({
        resultado: dadosFim?.resultado,
        tempo: dadosFim?.tempo,
        erros: dadosFim?.erros
    }));
    log("jogadores:", JSON.stringify({
        EDE: jogadores?.EDE?.id,
        EIT: jogadores?.EIT?.id
    }));

    // Compara o "tempo" da bomba com a duração real (finishedAt - startedAt)
    try {
        const p = await db.collection("partidas").findOne(
            { _id: idPartida },
            { projection: { startedAt: 1, finishedAt: 1 } }
        );

        if (p?.startedAt && p?.finishedAt) {
            const real = Math.round((new Date(p.finishedAt) - new Date(p.startedAt)) / 1000);
            const informado = Number(dadosFim?.tempo);

            log(`duração real (finishedAt - startedAt) = ${real}s | tempo informado pela bomba = ${informado}`);

            if (Number.isFinite(informado) && Math.abs(real - informado) > 10) {
                log(
                    "AVISO: o tempo da bomba difere muito da duração real.",
                    "Pode ser tempo RESTANTE (e não decorrido), outra unidade ou atraso na mensagem."
                );
            }
        } else {
            log("startedAt/finishedAt ausentes; não deu para comparar com a duração real.");
        }
    } catch (err) {
        log("não foi possível checar a duração real:", err.message);
    }

    const valor = calcularCreditos(dadosFim);
    const creditos = { valor, EDE: null, EIT: null };

    log(`valor final por jogador: ${valor} TJL`);

    try {
        if (valor > 0) {
            await Promise.all(
                ["EDE", "EIT"].map(async (papel) => {
                    const userId = jogadores?.[papel]?.id;

                    if (!userId) {
                        log(`${papel}: sem id cadastrado, nada a creditar`);
                        creditos[papel] = { ok: false, erro: "jogador não cadastrado" };
                        return;
                    }

                    try {
                        const operationId = await creditarJogador(userId, valor);
                        log(`${papel} (id ${userId}) creditado com ${valor} TJL, operationId=${operationId}`);
                        creditos[papel] = { ok: true, userId, operationId };
                    } catch (err) {
                        const motivo = err.response?.status
                            ? `HTTP ${err.response.status}`
                            : err.message;

                        console.error(
                            `Falha ao creditar ${papel} (id ${userId}) na partida ${idPartida}: ${motivo}`
                        );
                        creditos[papel] = { ok: false, userId, erro: motivo };
                    }
                })
            );
        } else {
            log("valor 0: nenhuma chamada à Feira será feita");
        }

        await db.collection("partidas").updateOne(
            { _id: idPartida },
            { $set: { creditos } }
        );

        log(`resumo salvo na partida ${idPartida}:`, JSON.stringify(creditos));
    } catch (err) {
        console.error(`Erro ao registrar créditos da partida ${idPartida}:`, err);
    }

    return creditos;
}

module.exports = { calcularCreditos, creditarPartida };